from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from logging import Logger
from typing import Any, Literal

import pybotters
from hyperquant.logkit import get_logger

from hyperquant.broker.deepcoin import DeepCoin
from hyperquant.broker.models.deepcoin import DeepCoinDataStore


def _to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _extract_order_id(payload: Any) -> str | None:
    if payload is None:
        return None
    if isinstance(payload, dict):
        for key in ("ordId", "ordID", "order_id"):
            raw = payload.get(key)
            if raw:
                return str(raw)
        data = payload.get("data")
        if isinstance(data, dict):
            return _extract_order_id(data)
    return None


def _extract_order_filled(snapshot: dict[str, Any] | None) -> float:
    if not snapshot:
        return 0.0
    return _to_float(
        snapshot.get("accFillSz")
        or snapshot.get("fillSz")
        or snapshot.get("filledQty")
        or snapshot.get("filled")
        or snapshot.get("sz")
    )


def _extract_order_avg_price(snapshot: dict[str, Any] | None) -> float:
    if not snapshot:
        return 0.0
    return _to_float(snapshot.get("avgPx") or snapshot.get("fillPx") or snapshot.get("px"))


def _extract_position_contracts(snapshot: dict[str, Any] | None) -> float:
    if not snapshot:
        return 0.0
    return _to_float(snapshot.get("pos") or snapshot.get("position") or snapshot.get("qty"))


def _extract_position_avg_price(snapshot: dict[str, Any] | None) -> float:
    if not snapshot:
        return 0.0
    return _to_float(snapshot.get("avgPx") or snapshot.get("avgPrice") or snapshot.get("px"))


def _extract_position_id(snapshot: dict[str, Any] | None) -> str | None:
    if not snapshot:
        return None
    raw = snapshot.get("posId") or snapshot.get("positionId")
    if raw is None:
        return None
    return str(raw)


def _contract_value(detail: dict[str, Any] | None) -> float:
    if not detail:
        return 1.0
    value = detail.get("ctVal") or detail.get("contractValue") or detail.get("faceValue")
    result = _to_float(value)
    return result if result > 0 else 1.0


@dataclass
class OrderSyncResult:
    position: dict[str, Any]
    order: dict[str, Any]
    before_contracts: float
    after_contracts: float


async def order_sync_polling(
    broker: DeepCoin,
    *,
    inst_id: str,
    place_task: Any,
    cancel_retry: int = 3,
    wait_timeout: float = 3.0,
    logger: Logger | None = None,
) -> OrderSyncResult:
    """Submit order and synchronise order/position snapshots for DeepCoin."""

    inst_id_norm = str(inst_id)
    await broker.update("positions")

    def _pick_position() -> dict[str, Any]:
        entries = broker.store.position.find({"instId": inst_id_norm}) or []
        if not entries:
            return {}
        entries_sorted = sorted(
            entries,
            key=lambda e: abs(_extract_position_contracts(e)),
            reverse=True,
        )
        return entries_sorted[0] if entries_sorted else {}

    baseline = _pick_position()
    before_contracts = _extract_position_contracts(baseline)

    order_snapshot: dict[str, Any] = {}
    ord_id: str | None = None

    async def _refresh_position() -> dict[str, Any]:
        await broker.update("positions")
        return _pick_position()

    stream_cm = None
    stream = None
    try:
        try:
            stream_cm = broker.store.orders.watch()
            stream = stream_cm.__enter__()
        except Exception as exc:
            stream_cm = None
            stream = None
            if logger:
                logger.debug(f"orders.watch unavailable: {exc}")

        started_at = time.time() * 1000
        try:
            response = await place_task
        except Exception as exc:
            if logger:
                logger.warning(f"Order placement failed: {exc}")
            return OrderSyncResult(
                position=baseline,
                order={},
                before_contracts=before_contracts,
                after_contracts=before_contracts,
            )

        latency = int(time.time() * 1000 - started_at)
        if logger:
            logger.info(f"Order latency {latency} ms")

        ord_id = _extract_order_id(response)
        if not ord_id:
            if logger:
                logger.warning(f"Failed to extract ordId from response: {response}")
            return OrderSyncResult(
                position=baseline,
                order=response if isinstance(response, dict) else {},
                before_contracts=before_contracts,
                after_contracts=before_contracts,
            )

        if stream is not None:
            try:
                async with asyncio.timeout(wait_timeout):
                    async for change in stream:
                        data = getattr(change, "data", None) or getattr(change, "source", None) or {}
                        if str(data.get("ordId")) != str(ord_id):
                            continue
                        order_snapshot = data
                        state = str(order_snapshot.get("state") or "").lower()
                        operation = getattr(change, "operation", "")
                        if operation == "delete" or state in {"filled", "canceled", "cancelled"}:
                            break
            except asyncio.TimeoutError:
                if logger:
                    logger.debug(f"Order sync timeout, ordId={ord_id}")
    finally:
        if stream_cm is not None:
            stream_cm.__exit__(None, None, None)

    if ord_id:
        try:
            await broker.update("orders", inst_id=inst_id_norm)
        except Exception as exc:
            if logger:
                logger.debug(f"Refresh orders failed: {exc}")
        stored = broker.store.orders.get({"ordId": str(ord_id)})
        if stored:
            order_snapshot = stored

    if ord_id and order_snapshot:
        state = str(order_snapshot.get("state") or "").lower()
        if state not in {"filled", "canceled", "cancelled"}:
            for attempt in range(cancel_retry):
                try:
                    await broker.cancel_order(inst_id=inst_id_norm, ord_id=str(ord_id))
                    break
                except Exception as exc:
                    if logger:
                        logger.warning(f"Cancel attempt {attempt + 1} failed: {exc}")
                    await asyncio.sleep(1.0)

    position_snapshot = await _refresh_position()
    after_contracts = _extract_position_contracts(position_snapshot)

    return OrderSyncResult(
        position=position_snapshot,
        order=order_snapshot,
        before_contracts=before_contracts,
        after_contracts=after_contracts,
    )


async def test_order_sync_once(
    *,
    apis: str = "./apis.json",
    symbol: str,
    side: Literal["long", "short"],
    qty_base: float,
    price: float | None = None,
    wait_timeout: float = 3.0,
) -> OrderSyncResult:
    """Quick helper to exercise DeepCoin order_sync_polling with a single order.

    This will PLACE a real order on the exchange using the provided credentials.
    Use small sizes and a sandbox account when validating behaviour.
    """
    order_side = "buy" if side == "long" else "sell"
    ord_type: Literal["limit", "market", "post_only", "ioc"]
    if price is None:
        ord_type = "market"
    else:
        ord_type = "ioc"

    async with pybotters.Client(apis) as client:
        async with DeepCoin(client=client) as broker:
            try:
                await broker.sub_private()
            except Exception:
                pass

            inst_id = broker.symbol_to_inst_id(symbol)
            place_task = broker.place_order(
                inst_id=inst_id,
                side=order_side,
                ord_type=ord_type,
                qty_base=qty_base,
                price=price,
                td_mode='isolated'
            )
            return await order_sync_polling(
                broker=broker,
                inst_id=inst_id,
                place_task=place_task,
                wait_timeout=wait_timeout,
                cancel_retry=3,
                logger=get_logger("deepcoin_order_sync_test"),
            )



if __name__ == "__main__":
    try:
        asyncio.run(test_order_sync_once(symbol='USELESSUSDT', side='long', qty_base=120, price=0.15))
    except KeyboardInterrupt:
        print("\n👋 收到 Ctrl+C，程序已安全退出。")
    except Exception as exc:
        import traceback

        print(f"❌ 程序运行异常: {exc}")
        traceback.print_exc()

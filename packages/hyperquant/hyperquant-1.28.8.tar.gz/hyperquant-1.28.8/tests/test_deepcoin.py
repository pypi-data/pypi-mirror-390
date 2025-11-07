from dataclasses import dataclass
from logging import Logger
import time
from typing import Any
from hyperquant.broker.deepcoin import DeepCoin
import pybotters


async def test_detail():
    async with pybotters.Client() as client:
        async with DeepCoin(client) as broker:
            # print(broker.store.detail.find({
            #     's':'BLUAIUSDT'
            # }))
            print(broker.symbol_to_inst_id('MLBCUSDT'))

async def test_update():
    async with pybotters.Client(apis="./apis.json") as client:
        async with DeepCoin(client) as broker:
            # await broker.update('balances')
            # print(broker.store.balance.find())
            await broker.update("positions")
            print(broker.store.position.find())
            # await broker.update("orders-history")
            # print(broker.store.orders.find())


async def test_subbook():
    async with pybotters.Client() as client:
        async with DeepCoin(client) as broker:
            await broker.sub_orderbook(["SOLUSDT"])
            with broker.store.book.watch() as stream:
                async for change in stream:
                    print(change.data)



async def test_subbook_more():
    async with pybotters.Client() as client:
        async with DeepCoin(client) as broker:
            detail = broker.store.detail.find()
            symbols = [d["s"] for d in detail]
            await broker.sub_orderbook(symbols[:30])
            with broker.store.book.watch() as stream:
                async for change in stream:
                    print(change.data)



async def test_place():
    async with pybotters.Client(apis="./apis.json") as client:
        async with DeepCoin(client) as broker:
            # symbol='USELESSUSDT', side='long', qty_base=120, price=0.15
            order = await broker.place_order(
                symbol="DOTUSDT", side="buy", ord_type="limit", qty_base=2, price=2.3
            )
            print(order)
            # await broker.place_order(
            #     symbol='USELESSUSDT', side='buy', ord_type='ioc', qty_base=120, price=0.15, td_mode='isolated'
            # )


async def test_place_speed():
    async with pybotters.Client(apis="./apis.json") as client:
        async with DeepCoin(client) as broker:
            latencies = []
            while True:
                start = time.time() * 1000
                order = await broker.place_order(
                    symbol="DOTUSDT",
                    side="buy",
                    ord_type="limit",
                    qty_contract=2,
                    price=2.3,
                )
                end = time.time() * 1000
                print(f"{end - start} ms")
                await asyncio.sleep(2)
                latencies.append(end - start)
                if len(latencies) > 4:
                    break
            print(f"avg: {sum(latencies) / len(latencies)} ms")


async def test_sub_private():
    async with pybotters.Client(apis="./apis.json") as client:
        async with DeepCoin(client) as broker:
            await broker.sub_private()
            # print(broker.store.orders.find())
            with broker.store.orders.watch() as stream:
                async for change in stream:
                    print(change.data)

            # with broker.store.position.watch() as stream:
            #     async for change in stream:
            #         print(change)


async def get_price_list():
    async with pybotters.Client() as client:
        async with DeepCoin(client) as broker:
            prices = await broker.get_price_list()
            print(prices)


@dataclass
class OrderSyncResult:
    position: dict[str, Any]
    order: dict[str, Any]


async def order_sync_polling(
    broker: DeepCoin,
    *,
    place_task: Any,
    inst_id: str,
    cancel_retry: int = 3,
    logger: Logger | None = None,
) -> OrderSyncResult | None:
    """DeepCoin order watcher: wait for deletion event, then refresh positions."""

    payload: dict[str, Any] | None = None
    stream_cm = broker.store.orders.watch()
    stream = stream_cm.__enter__()

    try:
        try:
            resp: dict[str, Any] = await place_task
        except Exception as exc:
            if logger:
                logger.warning(f"Order placement failed: {exc}")
            stream_cm.__exit__(None, None, None)
            return None

        ord_id = resp.get("ordId")
        if not ord_id:
            if logger:
                logger.warning("Failed to get ordId from place order response")
            stream_cm.__exit__(None, None, None)
            return None

        try:
            async with asyncio.timeout(3):
                async for change in stream:
                    data = change.source or change.data
                    if not isinstance(data, dict):
                        continue
                    payload = data
                    oid = data.get("ordId")
                    if change.operation == "delete" and str(oid) == str(ord_id):
                        break

        except asyncio.TimeoutError:
            for attempt in range(cancel_retry):
                try:
                    await broker.cancel_order(inst_id=inst_id, ord_id=ord_id)
                    break
                except Exception as exc:
                    if logger:
                        logger.warning(f"Cancel attempt {attempt + 1} failed: {exc}")
                    await asyncio.sleep(1)
    finally:
        stream_cm.__exit__(None, None, None)

    async def sync_pos():
        await asyncio.sleep(0.5)
        positions = broker.store.position.find({"instId": str(inst_id)}) or []
        position_snapshot = positions[0] if positions else {}
        return position_snapshot
   
    position_snapshot = await sync_pos()

    if payload.get('VT') != 0 and position_snapshot == {}:
        logger.warning(f'订单同步再次确认, 等待...')

        position_snapshot = await sync_pos()
        if position_snapshot == {}:
            logger.error(f'订单同步失败, 请手动确认订单状态 ordId={ord_id} pos={position_snapshot} order={payload} ')

    return OrderSyncResult(position=position_snapshot, order=payload or {})


async def test_sync_order():
    logger = Logger('test')
    async with pybotters.Client(apis="./apis.json") as client:
        async with DeepCoin(client) as broker:
            await broker.sub_private()
            await asyncio.sleep(1)
            # order_payload = await sync_order(broker)
            # print("Order payload after sync_order:", order_payload)
            task = broker.place_order(
                symbol="DOT-USDT-SWAP", side="buy", ord_type="market", qty_contract=5, price=2.3, td_mode='cross'
            )
            result = await order_sync_polling(
                broker,
                place_task=task,
                inst_id="DOT-USDT-SWAP",
                cancel_retry=2,
                logger=logger,
            )

            print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_detail())

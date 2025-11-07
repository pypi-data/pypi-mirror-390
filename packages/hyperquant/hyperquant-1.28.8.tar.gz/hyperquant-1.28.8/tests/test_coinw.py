import asyncio
import time
from typing import Sequence, Literal, Any

import pybotters

from hyperquant.broker.coinw import Coinw


async def test_update() -> None:
    """Fetch instrument metadata via REST."""
    async with pybotters.Client() as client:
        async with Coinw(client) as cw:
            # detail = cw.store.detail.find({
            #     'symbol': 'SOL_USDT'
            # })
            # print(detail)
            await cw.update('ticker')
            print(cw.store.ticker.find())


async def test_update_private() -> None:
    """Refresh private endpoints (requires ./apis.json with coinw credentials)."""
    async with pybotters.Client(apis="./apis.json") as client:
        async with Coinw(client) as cw:
            # await cw.update("balance")
            # print(cw.store.balance.find())
            await cw.update("position")
            print(cw.store.position.find())
            
            # await cw.update("position", instrument="BTC")
            # print(cw.store.position.find())
            # await cw.update("orders", instrument="BTC")
            # print(cw.store.orders.find())


async def test_sub_orderbook(
    symbols: Sequence[str] = ("BTC",),
    depth: int = 1,
    interval: float = 1.0,
) -> None:
    """Subscribe CoinW order book and print snapshots."""
    start = time.time()
    print(f"订阅开始: {start:.3f}")

    symbols = ['NMR_USDT', 'TRB_USDT', 'MELANIA_USDT', 'INJ_USDT', 'LTC_USDT', 'AUCTION_USDT']

    # 去掉USDT
    symbols = [s[:-5] if s.endswith('_USDT') else s for s in symbols]

    async with pybotters.Client() as client:
        async with Coinw(client) as cw:
            await cw.sub_orderbook(symbols, depth_limit=depth)
            with cw.store.book.watch() as watcher:
                while True:
                    try:
                        change = await asyncio.wait_for(watcher.__anext__(), timeout=15.0)
                    except asyncio.TimeoutError:
                        print("超过15秒未收到新数据，退出订阅。")
                        break
                    else:
                        print(change.data)

    end = time.time()
    print(f"订阅结束: {end:.3f}, 耗时: {(end - start):.3f} 秒")


async def test_place_cancel() -> None:
    """Demonstrate place/cancel flow (requires credentials and tradable environment)."""
    async with pybotters.Client(apis="./apis.json") as client:
        async with Coinw(client) as cw:
            start = time.time()
            # order = await cw.place_order(
            #     instrument="SOL",
            #     direction="long",
            #     quantity_unit=1,
            #     leverage=25,
            #     quantity=2,
            #     position_type="plan",
            #     price=175,
            #     position_model="cross",
            # )
            # latency = time.time() - start
            # print(f'下单延迟: {latency*1000:.2f} ms')
            # order_id = order.get("value") or order.get("data")
            # print("place_order response:", order)
            # if order_id:
            #     await asyncio.sleep(1)
            #     cancel_resp = await cw.cancel_order(order_id)
            #     print("cancel_order response:", cancel_resp)

            # {'instrument': 'JUP', 'direction': 'short', 'leverage': 50, 'quantityUnit': 1, 'quantity': '57', 'positionModel': 1, 'positionType': 'plan', 'openPrice': 0.3527}
            await cw.place_order(
                instrument="JUP",
                direction="short",
                quantity_unit=1,
                leverage=50,
                quantity="57",
                position_type="plan",
                price=0.3527,
                position_model=1,
            )

async def test_close_position():
    async with pybotters.Client(apis="./apis.json") as client:
        async with Coinw(client) as cw:
            # await cw.update('position')
            await cw.sub_personal()
            with cw.store.position.watch() as watcher:
                # 2435521222638707402
                resp = await cw.place_order(
                    instrument="JUP",
                    direction="long",
                    quantity_unit=1,
                    leverage=10,
                    quantity=1,
                    position_model='cross',
                    position_type='execute'
                )
                print("开仓响应:", resp)

                await asyncio.sleep(2)

                for position in cw.store.position.find():
                    open_id = position.get('openId')
                    print(f'关闭持仓: {open_id}')
                    resp = await cw.close_position(open_id, position_type='execute', close_num=1)
                    print(resp)

                async for change in watcher:
                    print(change)
                    print('\n\n----\n\n')

async def test_place_web() -> None:
    """Use the web interface to place an order (requires device/token)."""
    async with pybotters.Client(apis="./apis.json") as client:
        async with Coinw(client) as cw:
            device_id = '4f5ddd75b019fa4d64a24febc95442c1'
            token = '2BBD54A6463281D563F1C956A41D13D7web_1761054928090_26370305'
            start = time.time()
            resp = await cw.place_order_web(
                instrument="SOL",
                direction="long",
                leverage="50",
                quantity_unit=1,
                quantity="1",
                position_model=1,
                position_type="plan",
                open_price="175",
                device_id=device_id,
                token=token,
            )
            print("place_order_web response:", resp)
            latency = time.time() - start
            print(f'下单延迟: {latency*1000:.2f} ms')


async def order_sync_polling(
    broker: Coinw,
    *,
    instrument: str,
    direction: Literal["long", "short"] = "long",
    leverage: int | str = 50,
    quantity: str | float | int = "1",
    quantity_unit: Literal[0, 1, 2] = 0,
    position_model: Literal[0, 1] = 1,
    position_type: Literal["plan", "planTrigger", "execute"] = "plan",
    open_price: str | float | None = None,
    window_sec: float = 5.0,
    cancel_retry: int = 3,
) -> dict[str, Any]:
    """
    CoinW 订单轮询：在 window_sec 内等待订单终态，超时后尝试撤单。
    """

    order_id: str | None = None
    snapshot: dict[str, Any] | None = None

    try:
        async with asyncio.timeout(window_sec):
            with broker.store.position.watch() as stream:
                started = int(time.time() * 1000)
                resp = await broker.place_order(
                    instrument=instrument,
                    direction=direction,
                    leverage=leverage,
                    quantity_unit=quantity_unit,
                    quantity=quantity,
                    position_model=position_model,
                    position_type=position_type,
                    price=open_price,
                )
                print(resp)
                latency = int(time.time() * 1000) - started
                print(f"下单延迟 {latency} ms")

                raw_id = (
                    resp.get("value")
                    or resp.get("orderId")
                    or resp.get("data")
                    or (
                        resp.get("data", {}).get("value")
                        if isinstance(resp.get("data"), dict)
                        else None
                    )
                )
                if not raw_id:
                    raise RuntimeError(f"place_order 返回缺少 order_id: {resp}")
                order_id = str(raw_id)

                async for change in stream:
                    print(change.data)
                    data = change.data or {}
                    if str(data.get("orderId")) != order_id:
                        continue
                    snapshot = data
                    order_finish = data.get('orderStatus') == 'finish'
                    if order_finish:
                        return snapshot
                    
    except TimeoutError:
        pass

    if order_id:
        for attempt in range(cancel_retry):
            try:
                await broker.cancel_order(order_id)
                break
            except Exception as exc:
                print(f"撤单异常({attempt + 1}/{cancel_retry}): {exc}")
            await asyncio.sleep(1.0)

    return snapshot or {"order_id": order_id, "status": "timeout"}

async def test_subp() -> None:
    """Subscribe to private channels (requires credentials)."""
    async with pybotters.Client(apis="./apis.json") as client:
        async with Coinw(client) as cw:
            await cw.sub_personal()
            await asyncio.sleep(1.0)
            print(cw.store.position.find())
            # with cw.store.position.watch() as watcher:
            #     async for change in watcher:
            #         print(change)
            #         print('\n\n----\n\n')


async def test_order_sync_polling() -> None:
    """Test the order_sync_polling function (requires credentials)."""
    async with pybotters.Client(apis="./apis.json") as client:
        async with Coinw(client) as cw:
            await cw.sub_personal()
            print("Placing order with order_sync_polling...")
            result = await order_sync_polling(
                broker=cw,
                instrument="JUP",
                direction="long",
                leverage=10,
                quantity=1,
                quantity_unit=1,
                position_model="cross",
                position_type="execute",
                open_price=None,
                window_sec=3,
                cancel_retry=2,
            )
            print("order_sync_polling result:", result)

if __name__ == "__main__":
    asyncio.run(test_close_position())

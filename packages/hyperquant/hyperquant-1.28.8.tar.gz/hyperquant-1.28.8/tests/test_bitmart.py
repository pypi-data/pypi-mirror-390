import pybotters

from hyperquant.broker.lighter import Lighter
import asyncio
from logging import Logger
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Literal
from hyperquant.logkit import get_logger
from hyperquant.broker.bitmart import Bitmart


async def test_update():
    async with pybotters.Client(apis="./apis.json") as client:
        async with Bitmart(client=client) as broker:
            # print(broker.store.detail.find()[0])
            # await broker.update('balances')
            # print(broker.store.balances.find())
            # await broker.update('ticker')
            # print(broker.store.ticker.find())

            # await broker.update('history_orders')
            # print(broker.store.orders.find())
            # print(broker.store.orders.get({'order_id':3000237069605967}))
            # await broker.update("ticker")
            symbols = [d["name"] for d in broker.store.detail.find()]
            # print(symbols)
            channels: list[str] = []
            for symbol in symbols:
                channels.append(f"futures/depthAll5:{symbol}@100ms")
            # print(broker.store.positions.find())

            # print(broker.store.detail.find({'name':'PUMPUSDT'}))


async def test_place():
    async with pybotters.Client(apis="./apis.json") as client:
        async with Bitmart(client=client) as broker:
            # [2025-10-31 17:34:15] 🔵 准备建仓: VIRTUAL_USDT entry=short qty=20.498804 lag_px=1.4635 lead=binance
            # [2025-11-01 01:33:22] 🔵 准备建仓: PUMP_USDT entry=long qty=18872.375560 lag_px=0.004239 lead=binance
            # [2025-11-01 01:33:22] 🔔 Order placement failed: Bitmart submitOrder error: {'errno': 'ORDER_LEVERAGE_INFO_NOT_SYNCHRONIZED', 'message': 'Leverage info not synchronized, please place your order later or re
            for i in range(2):
                start = time.time()
                oid = await broker.place_order(
                    symbol="PUMPUSDT",
                    side="sell",
                    category="limit",
                    price=0.004239,
                    qty=18872.375560,
                    mode="ioc",
                    leverage=40,
                    # qty_contract=1
                )

                print(
                    f"Placed order ID: {oid}, 下单毫秒数: {(time.time() - start)*1000:.2f} ms"
                )

                # resp = await broker.cancel_order(
                #     symbol='VIRTUALUSDT',
                #     order_ids=[oid],
                # )

                # print(f"Cancel response: {resp}")


@dataclass
class OrderSyncResult:
    position: dict[str, Any]
    order: dict[str, Any]


async def order_sync_polling(
    broker: Bitmart,
    *,
    symbol: str,
    place_task: Any,
    cancel_retry: int = 3,
    logger: Logger | None = None,
) -> OrderSyncResult:
    """Bitmart order sync flow based on doc/bitmart.md.

    - Awaits the placement task to obtain order id
    - Updates history orders and positions to fetch snapshots
    - If IOC, returns immediately after one sync
    - Otherwise polls and attempts cancel on timeout
    """
    oid = None
    try:
        started = int(time.time() * 1000)
        oid = await place_task
        latency = int(time.time() * 1000) - started
        if logger:
            logger.info(f"Order placed, id={oid}, latency={latency} ms")
    except Exception as e:  # pragma: no cover - defensive logging
        if logger:
            logger.warning(f"Order placement failed: {e}")
        return OrderSyncResult(position={}, order={})

    async def sync() -> OrderSyncResult:
        await broker.update("history_orders")
        await broker.update("positions")
        order = broker.store.orders.get({"order_id": oid}) if oid else None
        position: dict[str, Any] = {}
        if order:
            contract_id = order.get("contract_id")
            if contract_id is not None:
                positions = broker.store.positions.find({"contract_id": contract_id})
                if positions:
                    position = positions[0]
        return OrderSyncResult(position=position or {}, order=order or {})

    for attempt in range(cancel_retry):
        await asyncio.sleep(1)
        await broker.update("history_orders")
        order = broker.store.orders.get({"order_id": oid}) if oid else None
        # 说明订单已经置入历史委托
        if order:
            return await sync()
        else:
            try:
                # 撤单需要 symbol + order_ids
                await broker.cancel_order(symbol, order_ids=[oid])
            except Exception as e:  # pragma: no cover - defensive logging
                if logger:
                    logger.warning(
                        f"Order cancellation attempt {attempt + 1} failed: {e}"
                    )

    return OrderSyncResult(position={}, order={})


async def test_sub_book():
    async with pybotters.Client() as client:
        async with Bitmart(client=client) as broker:
            broker.store.book.limit = 1
            await broker.sub_orderbook(["ASRUSDT"])
            while True:
                asks = broker.store.book.find({"S": "a", "s": "ASRUSDT"})
                bids = broker.store.book.find({"S": "b", "s": "ASRUSDT"})
                # 订单薄format化输出
                print("Asks:")
                for ask in asks:
                    print(f"Price: {ask['p']}, Quantity: {ask['q']}")
                print("Bids:")
                for bid in bids:
                    print(f"Price: {bid['p']}, Quantity: {bid['q']}")
                print("-" * 30)
                await asyncio.sleep(1)

async def test_auto_refresh():
    async with pybotters.Client(apis="./apis.json") as client:
        async with Bitmart(client=client, apis="./apis.json") as broker:
            await broker.auto_refresh(0, test=True)
            await asyncio.sleep(2)


async def test_sync_place():
    logger = get_logger("test_sync_place")
    async with pybotters.Client(apis="./apis.json") as client:
        async with Bitmart(client=client) as broker:
            # place_task = broker.place_order(
            #     symbol='VIRTUALUSDT',
            #     side='sell',
            #     category='limit',
            #     mode='ioc',
            #     price=1.38,
            #     qty=0.1,
            # )

            place_task = broker.place_order(  # type: ignore[attr-defined]
                symbol="VELODROMEUSDT",
                side="sell",
                qty_contract=int(round(1.000000)),
                price=0.040645,
                category="market",
            )
            result = await order_sync_polling(
                broker,
                place_task=place_task,
                is_ioc=False,
                cancel_retry=2,
                symbol="VELODROMEUSDT",
                logger=logger,
            )
            logger.info(f"Order Sync Result: {result}")


async def test_set_leverage():
    async with pybotters.Client(apis="./apis.json") as client:
        async with Bitmart(client=client) as broker:
            await broker.bind_leverage(symbol="BTCUSDT", leverage=10)
            # get current leverage
            lev_info = await broker.get_leverage(symbol="BTCUSDT")
            print(lev_info)




async def test_sub_book_compare():
    async with pybotters.Client() as client:
        async with Bitmart(client=client) as broker:
            mst_t = None
            a_counter = 0
            a_last_time = None
            a_total_interval = 0.0

            def book_handler(msg: dict, ws):
                nonlocal mst_t
                nonlocal a_counter
                nonlocal a_last_time
                nonlocal a_total_interval
                a_counter += 1
                now = time.time() * 1000  # ms
                if a_last_time is not None:
                    a_total_interval += (now - a_last_time)
                a_last_time = now
                mst_t = msg.get("data", {}).get("ms_t", None)

            b_counter = 0
            b_last_time = None
            b_total_interval = 0.0

            def book_handler_2(msg: dict, ws):
                nonlocal mst_t
                nonlocal b_counter
                nonlocal b_last_time
                nonlocal b_total_interval
                way = msg.get("data", {}).get("way", None)
                if way == 1:
                    b_counter += 1
                    now = time.time() * 1000  # ms
                    if b_last_time is not None:
                        b_total_interval += (now - b_last_time)
                    b_last_time = now
                mst_t = msg.get("data", {}).get("ms_t", None)

                

            await client.ws_connect(
                url="wss://openapi-ws-v2.bitmart.com/api?protocol=1.1",
                send_json=[
                    {"action": "subscribe", "args": ["futures/depth5:BTCUSDT@100ms"]}
                ],
                hdlr_json=book_handler,
            )


            await client.ws_connect(
                url="wss://contract-ws-v2.bitmart.com/v1/ifcontract/realTime",
                send_json=[
                    {
                        "action": "subscribe",
                        "args": [
                            "Depth:1",
                        ],
                    }
                ],
                hdlr_json=book_handler_2,
            )

            await asyncio.sleep(10)
            print(f"Handler A received {a_counter} messages.")
            if a_counter > 1:
                print(f"Handler A average interval: {a_total_interval / (a_counter - 1):.2f} ms")
            else:
                print("Handler A average interval: N/A")

            print(f"Handler B received {b_counter} messages.")
            if b_counter > 1:
                print(f"Handler B average interval: {b_total_interval / (b_counter - 1):.2f} ms")
            else:
                print("Handler B average interval: N/A")

async def test_sub_book_speed():


    async with pybotters.Client() as client:
        async with Bitmart(client=client) as broker:
            symbols = [d["name"] for d in broker.store.detail.find()]
            channels: list[str] = []
            
            cp = 0
            # for symbol in symbols[:30]:
            #     channels.append(f"futures/depthIncrease5:{symbol}@100ms")

            for symbol in [symbols[cp]]:
                channels.append(f"futures/depthIncrease5:{symbol}@100ms")

            # for symbol in [symbols[cp]]:
            #     channels.append(f"futures/depthAll5:{symbol}@100ms")
                      
            print(f'检查订阅的交易对: {symbols[cp]}')

            lat = []
            next_msg_time = None
            def book_handler(msg: dict, ws):
                symbol = msg.get("data", {}).get("symbol", "Unknown")
                if symbol != symbols[cp]:
                    return  # 只处理特定交易对的消息
                
                nonlocal next_msg_time
                now_ms = time.time() * 1000
                if next_msg_time is not None:
                    interval = now_ms - next_msg_time
                    print(f"Received message after {interval:.2f} ms")
                    lat.append(interval)
                next_msg_time = now_ms
            


            client.ws_connect(
                'wss://openapi-ws-v2.bitmart.com/api?protocol=1.1',
                send_json=[
                    {"action": "subscribe", "args": channels}
                ],
                hdlr_json=book_handler
            )

            await asyncio.sleep(15)  # 运行15秒以收集数据
            print('平均延迟: {}'.format(sum(lat) / len(lat) if lat else 0))

async def test_place_api():
    async with pybotters.Client(apis="./apis.json") as client:
        async with Bitmart(client=client) as broker:
            oid = await broker.place_order(
                symbol="TRXUSDT",
                side="buy",
                category="limit",
                qty_contract=1,
                price=0.285,
                mode="gtc",
                use_api=True
            )
            print(f"Placed order ID via API: {oid}")

async def test_place_api_latency():
    """Place the same order 5 times via official API and measure latency (ms)."""
    async with pybotters.Client(apis="./apis.json") as client:
        async with Bitmart(client=client) as broker:
            latencies: list[float] = []
            for i in range(5):
                start_ms = time.time() * 1000.0
                try:
                    oid = await broker.place_order(
                        symbol="TRXUSDT",
                        side="buy",
                        category="limit",
                        qty_contract=1,
                        price=0.285,
                        mode="gtc",
                        use_api=False,
                    )
                    elapsed = time.time() * 1000.0 - start_ms
                    latencies.append(elapsed)
                    print(f"[{i+1}/5] Placed id={oid}, latency={elapsed:.2f} ms")
                except Exception as e:
                    elapsed = time.time() * 1000.0 - start_ms
                    latencies.append(elapsed)
                    print(f"[{i+1}/5] Failed: {e}, latency={elapsed:.2f} ms")
                await asyncio.sleep(0.1)

            if latencies:
                avg = sum(latencies) / len(latencies)
                summary = ", ".join(f"{x:.2f}" for x in latencies)
                print(f"Avg latency={avg:.2f} ms; samples=[{summary}]")

if __name__ == "__main__":
    asyncio.run(test_sub_book_speed())

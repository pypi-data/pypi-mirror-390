import zlib
import pybotters
import logging
import os
from hyperquant.broker.lighter import Lighter
import asyncio


apis = {
    "l1_address": "0x5B3f0AdDfaf4c1d8729e266b22093545EFaE6c0e",
    "secret": "0x56c10a3dfa3e9d27a69044b16300bd529b1d073774fedc138433aa16328b56e3813026b60e396500",
}


async def test_update():
    async with pybotters.Client() as client:
        print("开始测试Lighter数据更新")
        async with Lighter(client=client, **apis) as broker:
            # print(broker.store.detail.find())
            # await broker.update('positions')
            # print(broker.store.positions.find())
            await broker.update('account')
            print(broker.store.accounts.find())

async def test_sub_book():
    async with pybotters.Client() as client:
        async with Lighter(client=client) as broker:
            broker.store.book.limit = 1

            await broker.sub_orderbook("VVV")
            i = 0
            try:
                async with asyncio.timeout(15):
                    while True:
                        await broker.store.book.wait()
                        # print(broker.store.book.find())
                        asks = broker.store.book.find({"S": "a"})
                        bids = broker.store.book.find({"S": "b"})
                        # 订单薄format化输出
                        print("Asks:")
                        for ask in asks:
                            print(
                                f"Price: {ask['p']}, Size: {ask['s']}, Symbol: {ask['s']} quantity: {ask['q']}"
                            )
                        print("Bids:")
                        for bid in bids:
                            print(
                                f"Price: {bid['p']}, Size: {bid['s']}, Symbol: {bid['s']} quantity: {bid['q']}"
                            )
                        print("-" * 20)

            except asyncio.TimeoutError:
                print("测试结束")
                exit(0)


async def test_place():
    async with pybotters.Client() as client:
        async with Lighter(client=client, **apis) as broker:
            order = await broker.place_order(
                symbol="DOLO",
                base_amount=146.7,
                price=0.075,
                is_ask=False,
                order_type="limit",
            )
            print(order)


async def test_place_cancel():
    async with pybotters.Client() as client:
        async with Lighter(client=client, **apis) as broker:

            order = await broker.place_order(
                symbol="DOLO",
                base_amount=146.3,
                price=0.064,
                is_ask=False,
                order_type="limit",
                client_order_index=115,
            )
            print(order)
            await broker.update("orders", symbol="DOLO")
            print(broker.store.orders.find())
            await asyncio.sleep(5)

            res = await broker.cancel_order("DOLO", order_index=115)
            print(res)


async def test_orders_stream():
    async with pybotters.Client() as client:
        async with Lighter(client=client, **apis) as broker:
            await broker.sub_orders()

            with broker.store.orders.watch() as stream:
                async for change in stream:
                    print(f"Order {change.operation}:")
                    print(change.data)

async def test_orders_stream():
    async with pybotters.Client() as client:
        async with Lighter(client=client, **apis) as broker:
            await broker.sub_orders()

            with broker.store.orders.watch() as stream:
                async for change in stream:
                    print(f"Order {change.operation}:")
                    print(change.data)

async def test_kline():
    async with pybotters.Client() as client:
        async with Lighter(
            client=client,
        ) as broker:
            # 需要5个K线数据
            start = (time.time() - 60 * 5 - 100) * 1000
            end = (time.time()) * 1000
            await broker.update_kline(
                symbol="DOLO",
                resolution="1m",
                start_timestamp=int(start),
                end_timestamp=int(end),
                count_back=5,
            )
            print(broker.store.klines.find())


async def test_sub_k():
    async with pybotters.Client() as client:
        async with Lighter(client=client) as br:

            await br.sub_kline(["YZY"], resolutions=["1m"])

            with br.store.klines.watch() as stream:
                async for change in stream:
                    print(f"Kline {change.operation}:")
                    print(change.data)




# 3秒未成交则撤单
async def test_sync_order():
    async with pybotters.Client() as client:
        async with Lighter(client=client, **apis) as broker:
            await broker.sub_orders()

            with broker.store.orders.watch() as stream:
                
                await broker.place_order(
                    symbol="SOL",
                    base_amount=0.03,
                    price=155,
                    is_ask=False,
                    order_type="market",
                    time_in_force='ioc',
                    client_order_index=140,
                )
                
                # 设置3秒超时
                try:
                    async with asyncio.timeout(3):
                        async for change in stream:
                            if change.operation == 'delete':
                                data = change.source
                                if data['client_order_index'] == 140:
                                    print("Order filled!")
                                    break
                
                except asyncio.TimeoutError:
                    print("Order not filled in time, cancelling...")
                    res = await broker.cancel_order("SOL", order_index=140)
                    print(res)



if __name__ == "__main__":
    import asyncio

    asyncio.run(test_update())

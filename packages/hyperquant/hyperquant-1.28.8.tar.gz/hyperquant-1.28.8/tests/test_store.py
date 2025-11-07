import random
import time
from typing import Any, Literal

from pybotters import DataStore


class Book(DataStore):
    """Bitmart 合约深度数据。"""

    _KEYS = ["s", "S"]

    def _init(self) -> None:
        self.limit: int | None = None

    def _on_message_api(self, msg: dict[str, Any]) -> None:
        data = msg.get("data")
        if not isinstance(data, dict):
            return
        # Some callers embed symbol at top-level; prefer msg["symbol"] when present
        symbol = msg.get("symbol") or data.get("symbol")
        asks = data.get("asks") or []
        bids = data.get("bids") or []

        self._insert(
            [
                {
                    "s": symbol,
                    "S": "a",
                    "p": asks[0][0],
                    "q": asks[0][1],
                },
                {
                    "s": symbol,
                    "S": "b",
                    "p": bids[0][0],
                    "q": bids[0][1],
                },
            ]
        )

book = Book()

sub_symbols = []
sub_len = 100
# 随机生成订阅的交易对
for _ in range(sub_len):
    base = random.randint(10000, 50000)
    sub_symbols.append(f"COIN_{base}")

book.limit = 1
for symbol in sub_symbols:
    base = random.randint(10000, 50000)
    book._on_message_api(
        {
            "symbol": symbol,
            "data": {
                "asks": [[f"{base + 100}", "0.5", "1627849923"]],
                "bids": [[f"{base - 100}", "1.0", "1627849923"]],
                "timestamp": "1627849923000",
            },
        }
    )

# 100ms内处理100条更新, 模拟1秒
start = time.time()
for _ in range(sub_len):
    symbol = random.choice(sub_symbols)
    base = random.randint(10000, 50000)
    book._on_message_api(
        {
            "symbol": symbol,
            "data": {
                "asks": [[f"{base + 150}", "0.3", "1627849933"]],
                "bids": [[f"{base - 150}", "0.8", "1627849933"]],
                "timestamp": "1627849933000",
            },
        }
    )
end = time.time()
# 输出耗时毫秒
print(f"Processed {sub_len} updates in {(end - start) * 1000:.2f} ms")


# 新Book store 部分


import random
import time
from hyperquant.broker.models.bitmart import Book

book = Book()

# {
#     "data": {
#         "symbol": "BTCUSDT",
#         "asks": [
#             {
#                 "price": "70294.4",
#                 "vol": "455"
#             }
#         ],
#         "bids": [
#             {
#                 "price": "70293.9",
#                 "vol": "1856"
#             }
#         ],
#         "ms_t": 1730399750402
#     },
#     "group": "futures/depthAll20:BTCUSDT@200ms"
# }

class Bookv2():
    def __init__(self):
        self.store = {}
    
    def on_message(self, msg: dict[str, Any]) -> None:
        data = msg.get("data")
        if not isinstance(data, dict):
            return
        symbol = data.get("symbol")
        self.store[symbol] = data
    
    def find(self, query: dict[str, Any]) -> dict[str, Any] | None:
        s = query.get("s")
        S = query.get("S")
        item = self.store.get(s)
        if item:
            if S == "a":
                return {"s": s, "S": "a", "p": item["asks"][0][0], "q": item["asks"][0][1]}
            elif S == "b":
                return {"s": s, "S": "b", "p": item["bids"][0][0], "q": item["bids"][0][1]}

book = Bookv2()
sub_symbols = []
sub_len = 100
# 随机生成订阅的交易对
for _ in range(sub_len):
    base = random.randint(10000, 50000)
    sub_symbols.append(f"COIN_{base}")

for symbol in sub_symbols:
    base = random.randint(10000, 50000)
    # data =  {
    #     "symbol": symbol,
    #     "asks": [[f"{base + 100}", "0.5", "1627849923"]],
    #     "bids": [[f"{base - 100}", "1.0", "1627849923"]],
    #     "timestamp": "1627849923000",
    # }
    book.on_message(
        {
            "data": {
                "symbol": symbol,
                "asks": [[f"{base + 100}", "0.5", "1627849923"]],
                "bids": [[f"{base - 100}", "1.0", "1627849923"]],
                "timestamp": "1627849923000",
            }
        }
    )

# print(book.find({"s": sub_symbols[0], "S": "a"}))
print(book.find({"s": sub_symbols[0], "S": "b"}))
    

# # 100ms内处理100条更新, 模拟1秒
# start = time.time()
# for _ in range(sub_len):
#     symbol = random.choice(sub_symbols)
#     base = random.randint(10000, 50000)
#     book.on_message(
#         {
#             symbol: {
#                 "asks": [[f"{base + 150}", "0.3", "1627849933"]],
#                 "bids": [[f"{base - 150}", "0.8", "1627849933"]],
#                 "timestamp": "1627849933000",
#             }
#         }
#     )
# end = time.time()
# # 输出耗时毫秒
# print(f"Processed {sub_len} updates in {(end - start) * 1000:.2f} ms")

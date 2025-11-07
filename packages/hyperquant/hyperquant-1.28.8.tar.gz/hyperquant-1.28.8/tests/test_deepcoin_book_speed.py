import asyncio
import time
from collections import defaultdict
from statistics import StatisticsError, mean, median
from aiohttp import ClientWebSocketResponse
import pybotters
next_tt = None

def callback(msg:dict, ws: ClientWebSocketResponse = None):
    global next_tt
    if not isinstance(msg, dict):
        return
    tt = msg.get('tt')
    a = msg.get('a')
    # Order book best price snapshot/incremental
    if a == 'PO':
        ticks = msg.get('r', [])
        if not ticks:
            return
        tick = ticks[0].get('d', {})
        ask_p1 = tick.get('AP1')
        bid_p1 = tick.get('BP1')
        print(f'PO ask_p1: {ask_p1}, bid_p1: {bid_p1}')
        if tt and next_tt:
            print(f'latency tt {tt-next_tt}')
        next_tt = tt
    # 25-level incremental (TopicID 25)
    elif a == 'PMO':
        rows = msg.get('r', [])
        for it in rows:
            d = it.get('d', {}) if isinstance(it, dict) else {}
            if not d:
                continue
            # I: symbol, D: side, P: price, V: size
            print(f"PMO I={d.get('I')} D={d.get('D')} P={d.get('P')} V={d.get('V')}")

async def auto_ping(ws: ClientWebSocketResponse):
    while True:
        await asyncio.sleep(5)
        await ws.send_str('ping')

async def subway_1():
    async with pybotters.Client() as client:
        # webData2
        wsapp = client.ws_connect(
            "wss://stream.deepcoin.com/streamlet/trade/public/swap?platform=api",
            send_json={"SendTopicAction":{"Action":"1","FilterValue":"DeepCoin_MILKUSDT","LocalNo":9,"ResumeNo":-2,"TopicID":"7"}},
            hdlr_json=callback
        )
        await wsapp._event.wait()
        asyncio.create_task(auto_ping(wsapp.current_ws))

        while True:
            await asyncio.sleep(1)
            # print("Waiting for messages…")

async def subway_2():
    """Subscribe 25-depth incremental (TopicID=25) on mainnet public WS."""
    async with pybotters.Client() as client:
        wsapp = client.ws_connect(
            "wss://stream.deepcoin.com/streamlet/trade/public/swap?platform=api",
            send_json={
                "SendTopicAction": {
                    "Action": "1",
                    "FilterValue": "DeepCoin_BTCUSDT_0.1",
                    "LocalNo": 6,
                    "ResumeNo": -1,
                    "TopicID": "25",
                }
            },
            hdlr_json=callback,
        )
        await wsapp._event.wait()
        asyncio.create_task(auto_ping(wsapp.current_ws))

        while True:
            await asyncio.sleep(1)


async def test_compare_best1(
    symbol: str = "BTCUSDT",
    duration_sec: int = 30,
    pmo_filter_suffix: str = "0.1",
    resume_no: int = -1,
):
    """Compare best1 update speed/latency between PO and PMO channels.

    Args:
        symbol: Trading pair, e.g. "BTCUSDT".
        duration_sec: Observation window.
        pmo_filter_suffix: Period parameter used in PMO FilterValue.
        resume_no: Resume position for subscription (default -1 => latest).
    """

    channels = ["PO", "PMO"]
    current_best = {ch: {"ask": None, "bid": None} for ch in channels}
    first_seen_ts = {ch: {"ask": None, "bid": None} for ch in channels}
    change_counts = {ch: 0 for ch in channels}
    side_counts = {side: {ch: 0 for ch in channels} for side in ("ask", "bid")}

    pending = {side: {} for side in ("ask", "bid")}
    latest_price = {side: {ch: None for ch in channels} for side in ("ask", "bid")}
    lead_samples = {side: {ch: [] for ch in channels} for side in ("ask", "bid")}

    pmo_levels: dict[str, dict[float, float]] = defaultdict(dict)
    pmo_side_map: dict[str, str] = {}

    def infer_side_map() -> None:
        nonlocal pmo_side_map
        if pmo_side_map and all(side in pmo_side_map.values() for side in ("ask", "bid")):
            return

        non_empty = [(k, lv) for k, lv in pmo_levels.items() if lv]
        if len(non_empty) < 2:
            return

        min_prices = {k: min(levels) for k, levels in non_empty}
        max_prices = {k: max(levels) for k, levels in non_empty}

        po_ask = current_best["PO"]["ask"]
        po_bid = current_best["PO"]["bid"]

        ask_key = None
        if po_ask is not None:
            ask_key = min(min_prices, key=lambda k: abs(min_prices[k] - po_ask))
        elif min_prices:
            ask_key = min(min_prices, key=min_prices.get)

        remaining_keys = [k for k in min_prices if k != ask_key]
        bid_key = None
        if po_bid is not None and remaining_keys:
            bid_key = min(remaining_keys, key=lambda k: abs(max_prices[k] - po_bid))
        elif max_prices:
            candidates = remaining_keys if remaining_keys else list(max_prices)
            bid_key = max(candidates, key=max_prices.get)

        if ask_key is None or bid_key is None or ask_key == bid_key:
            ordered = sorted(min_prices, key=min_prices.get)
            if len(ordered) >= 2:
                ask_key, bid_key = ordered[0], ordered[-1]
            else:
                return

        pmo_side_map = {ask_key: "ask", bid_key: "bid"}

    def record_change(channel: str, side: str, price: float, now: float) -> None:
        if price is None:
            return
        prev_price = current_best[channel][side]
        if prev_price == price:
            return

        current_best[channel][side] = price
        change_counts[channel] += 1
        side_counts[side][channel] += 1
        if first_seen_ts[channel][side] is None:
            first_seen_ts[channel][side] = now

        # Remove previous pending entry for this channel/side
        prev = latest_price[side][channel]
        if prev is not None:
            entry = pending[side].get(prev)
            if entry and entry[0] == channel:
                pending[side].pop(prev, None)

        latest_price[side][channel] = price

        match = pending[side].pop(price, None)
        if match and match[0] != channel:
            first_channel, first_time = match
            dt = now - first_time
            lead_samples[side][first_channel].append(dt)
        else:
            pending[side][price] = (channel, now)

    def on_msg(msg: dict, ws: ClientWebSocketResponse = None):
        nonlocal pmo_side_map
        if not isinstance(msg, dict):
            return
        kind = msg.get("a")
        now = time.monotonic()

        if kind == "PO":
            rows = msg.get("r", [])
            if not rows:
                return
            data = rows[0].get("d", {})
            ap1 = data.get("AP1")
            bp1 = data.get("BP1")
            try:
                ap1_f = float(ap1) if ap1 is not None else None
                bp1_f = float(bp1) if bp1 is not None else None
            except Exception:
                return
            record_change("PO", "ask", ap1_f, now)
            record_change("PO", "bid", bp1_f, now)

        elif kind == "PMO":
            rows = msg.get("r", [])
            updated = False
            for item in rows:
                data = item.get("d", {}) if isinstance(item, dict) else {}
                if not data:
                    continue
                side_key = str(data.get("D", ""))
                try:
                    price = float(data.get("P"))
                    size = float(data.get("V"))
                except Exception:
                    continue

                levels = pmo_levels[side_key]
                if size <= 0:
                    levels.pop(price, None)
                else:
                    levels[price] = size
                updated = True

            if not updated:
                return

            infer_side_map()

            ask_prices: list[float] = []
            bid_prices: list[float] = []
            for key, levels in pmo_levels.items():
                if not levels:
                    continue
                mapped_side = pmo_side_map.get(key)
                prices = list(levels.keys())
                if mapped_side == "ask":
                    ask_prices.extend(prices)
                elif mapped_side == "bid":
                    bid_prices.extend(prices)

            # Fallback to numeric ordering if mapping still unresolved or only one side mapped
            if not ask_prices and pmo_levels:
                ask_prices = [price for levels in pmo_levels.values() for price in levels.keys()]
            if not bid_prices and pmo_levels:
                bid_prices = [price for levels in pmo_levels.values() for price in levels.keys()]

            new_ask = min(ask_prices) if ask_prices else None
            new_bid = max(bid_prices) if bid_prices else None

            record_change("PMO", "ask", new_ask, now)
            record_change("PMO", "bid", new_bid, now)

    async with pybotters.Client() as client:
        filter_po = f"DeepCoin_{symbol}"
        filter_pmo = f"DeepCoin_{symbol}_{pmo_filter_suffix}"
        wsapp = client.ws_connect(
            "wss://stream.deepcoin.com/streamlet/trade/public/swap?platform=api",
            send_json=[
                {
                    "SendTopicAction": {
                        "Action": "1",
                        "FilterValue": filter_po,
                        "LocalNo": 1,
                        "ResumeNo": resume_no,
                        "TopicID": "7",
                    }
                },
                {
                    "SendTopicAction": {
                        "Action": "1",
                        "FilterValue": filter_pmo,
                        "LocalNo": 2,
                        "ResumeNo": resume_no,
                        "TopicID": "25",
                    }
                },
            ],
            hdlr_json=on_msg,
        )
        await wsapp._event.wait()
        asyncio.create_task(auto_ping(wsapp.current_ws))

        start = time.monotonic()
        try:
            async with asyncio.timeout(duration_sec):
                while True:
                    await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            pass

        elapsed = max(1e-6, time.monotonic() - start)

        print("=== Best1 Update Speed Summary ===")
        print(f"Symbol: {symbol} | Duration: {elapsed:.2f}s | PMO suffix={pmo_filter_suffix}")

        def format_offset(ts: float | None) -> str:
            return f"{ts - start:.3f}s" if ts is not None else "N/A"

        for ch in channels:
            rate = change_counts[ch] / elapsed
            ask_first = first_seen_ts[ch]["ask"]
            bid_first = first_seen_ts[ch]["bid"]
            print(
                f"{ch:<3} total changes: {change_counts[ch]:<4} | rate: {rate:.2f}/s | "
                f"ask_first@ {format_offset(ask_first)} | bid_first@ {format_offset(bid_first)}"
            )

        lead_summary = []
        for side in ("ask", "bid"):
            side_line = [f"{side.upper()} lead stats:"]
            for ch in channels:
                samples = lead_samples[side][ch]
                if samples:
                    try:
                        side_line.append(
                            f"{ch} leads {len(samples)}× | mean={mean(samples):.4f}s | median={median(samples):.4f}s"
                        )
                    except StatisticsError:
                        side_line.append(f"{ch} leads {len(samples)}× | mean=median=N/A")
                else:
                    side_line.append(f"{ch} leads 0×")
            lead_summary.append("; ".join(side_line))

        for line in lead_summary:
            print(line)

        faster = max(channels, key=lambda ch: change_counts[ch])
        if all(change_counts[ch] == change_counts[channels[0]] for ch in channels):
            faster = "TIE"
        print(f"Most frequent updater by count: {faster}")

if __name__ == "__main__":
    asyncio.run(test_compare_best1("BTCUSDT", 20))

# detail (注意 store需要将 contract,risk_limit等字段全部提取合并 )
curl 'https://contract-v2.bitmart.com/v1/ifcontract/contracts_all' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'cache-control: no-cache' \
  -H 'origin: https://derivatives.bitmart.com' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://derivatives.bitmart.com/' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'

{
    "errno": "OK",
    "message": "Success",
    "data": {
        "contracts": [
            {
                "contract": {
                    "contract_id": 1,
                    "index_id": 1,
                    "name": "BTCUSDT",
                    "display_name": "BTCUSDT 永续合约",
                    "display_name_en": "BTCUSDT_SWAP",
                    "contract_type": 1,
                    "base_coin": "BTC",
                    "quote_coin": "USDT",
                    "price_coin": "BTC",
                    "exchange": "*",
                    "contract_size": "0.001",
                    "begin_at": "2022-02-27T16:00:00Z",
                    "end_at": "2020-01-01T00:00:00Z",
                    "delive_at": "2018-10-01T02:00:00Z",
                    "delivery_cycle": 28800,
                    "min_leverage": "1",
                    "max_leverage": "200",
                    "price_unit": "0.1",
                    "vol_unit": "1",
                    "value_unit": "0.1",
                    "min_vol": "1",
                    "max_vol": "500000",
                    "liquidation_warn_ratio": "0.85",
                    "fast_liquidation_ratio": "0.8",
                    "settle_type": 1,
                    "open_type": 3,
                    "compensate_type": 1,
                    "status": 3,
                    "block": 1,
                    "rank": 1,
                    "created_at": "2018-07-12T09:16:57Z",
                    "depth_bord": "0.0375",
                    "base_coin_zh": "",
                    "base_coin_en": "",
                    "max_rate": "0.0375",
                    "min_rate": "-0.0375",
                    "market_status": 0,
                    "hedge_name": "binance",
                    "icon_url": "/static-file/public/coin/BTC-20200604060942.png",
                    "robot_risk_threshold": "0",
                    "fund_rate_threshold": "0",
                    "fund_rate_switch": 0,
                    "fund_rate_config": "0",
                    "market_price_rate": "0.003",
                    "robot_fund_rate_offset": "0",
                    "credit_max_leverage": 20,
                    "limit_ratio": "0.05",
                    "max_order_num": 200,
                    "min_trade_val": "5",
                    "bind_order_flag": false,
                    "market_max_vol": "80000",
                    "quote_type": 1
                },
                "risk_limit": {
                    "contract_id": 1,
                    "base_limit": "1000000",
                    "step": "1000000",
                    "maintenance_margin": "0.0025",
                    "initial_margin": "0.005",
                    "status": 1
                },
                "fee_config": {
                    "contract_id": 1,
                    "maker_fee": "0.0002",
                    "taker_fee": "0.0006",
                    "settlement_fee": "0",
                    "created_at": "2018-07-12T20:47:22Z"
                },
                "contract_tag_detail": {
                    "tag_id": 1,
                    "tag_name": "hot"
                },
                "plan_order_config": {
                    "contract_id": 0,
                    "min_scope": "0.001",
                    "max_scope": "2",
                    "max_count": 100,
                    "min_life_cycle": 24,
                    "max_life_cycle": 438000
                }
            }
            ///....
        ]
    },
    "success": true
}

# book
wss://contract-ws-v2.bitmart.com/v1/ifcontract/realTime

深度方向
- 1=买方
- 2=卖方

{"action":"subscribe","args":["DepthP3:37"]}

{"data":{"way":1,"depths":[{"price":"1.958","vol":"33412"},{"price":"1.957","vol":"44618"},{"price":"1.956","vol":"42111"},{"price":"1.954","vol":"26512"},{"price":"1.953","vol":"36803"}....]},"group":"DepthP3:37","uuid":7372715890,"ms_t":1761724043519}

{"data":{"way":2,"depths":[{"price":"1.963","vol":"27584"},{"price":"1.964","vol":"49443"}...]},"group":"DepthP3:37","uuid":7372715879,"ms_t":1761724043519}

# ticker

https://contract-v2.bitmart.com/v1/ifcontract/tickers

{
    "errno": "OK",
    "message": "Success",
    "data": {
        "tickers": [
            {
                "last_price": "0.002296",
                "open": "0.002347",
                "close": "0.002296",
                "low": "0.00224",
                "high": "0.002394",
                "avg_price": "0.0023197328648874",
                "volume": "6",
                "total_volume": "200110472",
                "timestamp": 1761812348,
                "rise_fall_rate": "-0.0217298679164891",
                "rise_fall_value": "-0.000051",
                "contract_id": 33125,
                "contract_name": "IOSTUSDT",
                "position_size": "",
                "volume24": "229630336",
                "amount24": "533620.3631860018137124",
                "high_price_24": "0.002394",
                "low_price_24": "0.00224",
                "base_coin_volume": "200110472",
                "quote_coin_volume": "464202.8385065298408528",
                "ask_price": "0.002302",
                "ask_vol": "6396074",
                "bid_price": "0.002289",
                "bid_vol": "3214783",
                "index_price": "0.00229906",
                "fair_price": "0.002296",
                "depth_price": {
                    "bid_price": "0",
                    "ask_price": "0",
                    "mid_price": "0"
                },
                "fair_basis": "",
                "fair_value": "",
                "rate": {
                    "quote_rate": "0",
                    "base_rate": "0",
                    "interest_rate": "0"
                },
                "premium_index": "",
                "funding_rate": "-0.0000601",
                "next_funding_rate": "",
                "next_funding_at": "2025-10-30T16:00:00Z",
                "pps": "0",
                "quote_coin": "USDT",
                "base_coin": "IOST"
            }...
        ]
    },
    "success": true
}


# Position（sentry header需要分析

curl 'https://derivatives.bitmart.com/gw-api/contract-tiger/forward/v1/ifcontract/userPositions?status=1' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'baggage: sentry-environment=production,sentry-release=5e13905,sentry-public_key=42eada5febd1737fdcb9413516bdb44f,sentry-trace_id=d6b12d5bd7984f6c827f6e28751007cc,sentry-sampled=false,sentry-sample_rand=0.6247963558518189,sentry-sample_rate=0.2' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://derivatives.bitmart.com/zh-CN/futures/QTUMUSDT?theme=dark' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: d6b12d5bd7984f6c827f6e28751007cc-a32167f2f292ed33-0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-client: WEB' \
  -H 'x-bm-contract: 2' \
  -H 'x-bm-device: 1c0886dd192a1dd0f23f71f7ab577a45' \
  -H 'x-bm-tag;' \
  -H 'x-bm-timezone: Asia/Shanghai' \
  -H 'x-bm-timezone-offset: -480' \
  -H 'x-bm-ua: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-version: 5e13905'

  {
    "errno": "OK",
    "message": "Success",
    "data": {
        "positions": [
            {
                "position_id": 3000236533088511,
                "account_id": 2008001004625862,
                "contract_id": 72,
                "hold_vol": "1",
                "freeze_vol": "0",
                "close_vol": "0",
                "hold_avg_price": "0.2964901",
                "open_avg_price": "0.2964901",
                "close_avg_price": "0",
                "oim": "0.02982690406",
                "im": "0.02982690406",
                "mm": "0.000741261625",
                "realised_profit": "-0.00017789406",
                "earnings": "-0.00017789406",
                "hold_fee": "0",
                "open_type": 2,
                "position_type": 1,
                "status": 1,
                "errno": 0,
                "created_at": "2025-10-29T11:16:37.63704Z",
                "updated_at": "2025-10-29T11:16:37.63704Z",
                "notional_value": "0.2964901",
                "fair_value": "0.29650465",
                "current_value": "0.2965151",
                "liquidation_value": "-10.702412850255",
                "bankruptcy_value": "0",
                "close_able_vol": "1",
                "bankruptcy_fee": "0.00017789406",
                "current_un_earnings": "0.000025",
                "fair_un_earnings": "0.00001455",
                "liquidate_price": "0",
                "current_roe": "0.0008431570971989815",
                "fair_roe": "0.0004907174305698073",
                "current_notional_roe": "0.0008431984744178642",
                "fair_notional_roe": "0.000490741512111197",
                "leverage": "0.0269540457075690273",
                "bind_leverage": "10",
                "account_type": 0,
                "position_mode": 0,
                "fee": "-0.00017789406"
            }
        ]
    },
    "success": true
}

# Orders

curl 'https://derivatives.bitmart.com/gw-api/contract-tiger/forward/v1/ifcontract/userAllOrders?status=3&size=1000&orderType=0&offset=0&direction=0&type=1' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'baggage: sentry-environment=production,sentry-release=5e13905,sentry-public_key=42eada5febd1737fdcb9413516bdb44f,sentry-trace_id=d6b12d5bd7984f6c827f6e28751007cc,sentry-sampled=false,sentry-sample_rand=0.6247963558518189,sentry-sample_rate=0.2' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://derivatives.bitmart.com/zh-CN/futures/QTUMUSDT?theme=dark' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: d6b12d5bd7984f6c827f6e28751007cc-a09b980305e164fb-0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-client: WEB' \
  -H 'x-bm-contract: 2' \
  -H 'x-bm-device: 1c0886dd192a1dd0f23f71f7ab577a45' \
  -H 'x-bm-tag;' \
  -H 'x-bm-timezone: Asia/Shanghai' \
  -H 'x-bm-timezone-offset: -480' \
  -H 'x-bm-ua: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-version: 5e13905'

{
    "errno": "OK",
    "message": "Success",
    "data": {
        "orders": [
            {
                "order_id": 3000236525013551,
                "contract_id": 72,
                "position_id": 0,
                "account_id": 2008001004625862,
                "price": "0.25",
                "vol": "1",
                "done_vol": "0",
                "done_avg_price": "0",
                "way": 1,
                "category": 1,
                "make_fee": "0",
                "take_fee": "0",
                "origin": "web",
                "created_at": "2025-10-29T08:23:20.745717Z",
                "updated_at": "2025-10-29T08:23:20.753482Z",
                "finished_at": "",
                "status": 2,
                "errno": 0,
                "mode": 1,
                "leverage": "10",
                "open_type": 2,
                "order_type": 0,
                "extends": {
                    "remark": "default",
                    "broker_id": "",
                    "order_type": 0,
                    "bonus_only": false,
                    "request_trace_id": "",
                    "trigger_ratio_type": 0,
                    "is_guaranteed_sl_or_tp": false,
                    "is_market_zero_slippage": false,
                    "zero_slippage_ratio": ""
                },
                "client_order_id": "",
                "executive_price": "",
                "life_cycle": 0,
                "price_type": 0,
                "price_way": 0,
                "plan_category": 0,
                "activation_price": "",
                "callback_rate": "",
                "executive_order_id": 0,
                "bind_leverage": "",
                "pre_plan_order_id": 0,
                "stop_profit_executive_price": "",
                "stop_profit_price_type": 0,
                "stop_loss_executive_price": "",
                "stop_loss_price_type": 0,
                "liquidation_fee": "",
                "account_type": 0,
                "pnl": "",
                "data_type": "",
                "position_mode": 1,
                "pnl_rate": "",
                "preset_is_guaranteed_sl": false,
                "preset_is_guaranteed_tp": false
            }
        ],
        "total": 1
    },
    "success": true
}

# Account

curl 'https://derivatives.bitmart.com/gw-api/contract-tiger/forward/v1/ifcontract/copy/trade/user/info' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'baggage: sentry-environment=production,sentry-release=5e13905,sentry-public_key=42eada5febd1737fdcb9413516bdb44f,sentry-trace_id=d6b12d5bd7984f6c827f6e28751007cc,sentry-sampled=false,sentry-sample_rand=0.6247963558518189,sentry-sample_rate=0.2' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/x-www-form-urlencoded;charset=UTF-8' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://derivatives.bitmart.com/zh-CN/futures/QTUMUSDT?theme=dark' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: d6b12d5bd7984f6c827f6e28751007cc-b18820faad7b0a18-0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-client: WEB' \
  -H 'x-bm-contract: 2' \
  -H 'x-bm-device: 1c0886dd192a1dd0f23f71f7ab577a45' \
  -H 'x-bm-tag;' \
  -H 'x-bm-timezone: Asia/Shanghai' \
  -H 'x-bm-timezone-offset: -480' \
  -H 'x-bm-ua: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-version: 5e13905'

{
    "errno": "OK",
    "message": "Success",
    "data": {
        "account_id": "14794011",
        "name": "",
        "identity": 0,
        "status": 0,
        "follower_num": 0,
        "is_hidden": false,
        "open_copy": 0,
        "show_followers_profit": 0,
        "copy_permission": 0,
        "assets": [
            {
                "account_id": 14794011,
                "coin_code": "USDT",
                "available_vol": "0",
                "cash_vol": "0",
                "freeze_vol": "0",
                "realised_vol": "0",
                "un_realised_vol": "0",
                "earnings_vol": "0",
                "total_im": "",
                "margin_balance": "",
                "available_balance": "",
                "trans_out_balance": "",
                "status": 0,
                "total_balance": "",
                "account_rights": "0",
                "bonus_voucher_vol": "",
                "freeze_bonus_voucher_vol": ""
            }
        ],
        "updated_time": -62135596800,
        "verified": 0,
        "show_trade_history_profit": 0,
        "asset_ratio_recommend": "0",
        "fixed_multiple_recommend": "0",
        "fixed_margin_recommend": "0",
        "position_ratio_recommend": "0",
        "position_ratio_mode_recommend": 0,
        "apply_info": {
            "name": "",
            "avatar": "",
            "introduction": "",
            "apply_status": 0
        },
        "show_current_position": 0,
        "show_trading_history": 0
    },
    "success": true
}

# 订单部分

category 1 限价单 2 市价单

status 4 系统取消

## limit gtc
curl 'https://derivatives.bitmart.com/gw-api/contract-tiger/forward/v1/ifcontract/submitOrder' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'baggage: sentry-environment=production,sentry-release=5e13905,sentry-public_key=42eada5febd1737fdcb9413516bdb44f,sentry-trace_id=295c4439688b493095043ec4298b374b,sentry-sampled=true,sentry-sample_rand=0.17076608051357256,sentry-sample_rate=0.2' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -H 'expires: 0' \
  -H 'origin: https://derivatives.bitmart.com' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://derivatives.bitmart.com/zh-CN/futures/TRXUSDT?theme=dark' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: 295c4439688b493095043ec4298b374b-9329122dc489cb1c-1' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-client: WEB' \
  -H 'x-bm-contract: 2' \
  -H 'x-bm-device: 1c0886dd192a1dd0f23f71f7ab577a45' \
  -H 'x-bm-tag;' \
  -H 'x-bm-timezone: Asia/Shanghai' \
  -H 'x-bm-timezone-offset: -480' \
  -H 'x-bm-ua: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-version: 5e13905' \
  --data-raw '{"place_all_order":false,"contract_id":72,"category":1,"price":0.25,"vol":1,"way":1,"mode":1,"open_type":2,"leverage":10,"reverse_vol":0,"custom_id":176172620051198850}'

{"errno":"OK","message":"Success","data":{"order_id":3000236525013551},"success":true}

### 参考(此为apikey版本的,不一定和front api完全一样)
ymbol	String	必填	合约交易对（如BTCUSDT）
client_order_id	String	选填	用户自定义ID, 字母（区分大小写）与数字的组合，可以是纯字母、纯数字且长度要在1-32位之间
type	String	选填	订单类型
-limit=限价单(默认)
-market=市价单
side	Int	必填	订单方向
双向持仓
-1=开多
-2=平空
-3=平多
-4=开空
单向持仓
-1=买入
-2=买入（只减仓）
-3=卖出（只减仓）
-4=卖出
leverage	String	选填	杠杆下单倍数
open_type	String	选填	开仓类型
-cross=全仓
-isolated=逐仓
mode	Int	选填	下单方式
-1=GTC(默认)
-2=FOK
-3=IOC
-4=Maker Only
price	String	必填	下单价格，限价单模式必填。
size	Int	必填	订单数量 张数
preset_take_profit_price_type	Int	选填	预设止盈委托价格类型
-1=最新成交价(默认)
-2=标记价格
preset_stop_loss_price_type	Int	选填	预设止损委托价格类型
-1=最新成交价(默认)
-2=标记价格
preset_take_profit_price	String	选填	预设止盈价格
preset_stop_loss_price	String	选填	预设止损价格
stp_mode	Int	选填	自成交保护模式
-1=cancel_maker(默认)
-2=cancel_taker
-3=cancel_both


## limit ioc

curl 'https://derivatives.bitmart.com/gw-api/contract-tiger/forward/v1/ifcontract/submitOrder' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'baggage: sentry-environment=production,sentry-release=5e13905,sentry-public_key=42eada5febd1737fdcb9413516bdb44f,sentry-trace_id=295c4439688b493095043ec4298b374b,sentry-sampled=true,sentry-sample_rand=0.17076608051357256,sentry-sample_rate=0.2' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -H 'expires: 0' \
  -H 'origin: https://derivatives.bitmart.com' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://derivatives.bitmart.com/zh-CN/futures/TRXUSDT?theme=dark' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: 295c4439688b493095043ec4298b374b-896b89efbfff20fd-1' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-client: WEB' \
  -H 'x-bm-contract: 2' \
  -H 'x-bm-device: 1c0886dd192a1dd0f23f71f7ab577a45' \
  -H 'x-bm-tag;' \
  -H 'x-bm-timezone: Asia/Shanghai' \
  -H 'x-bm-timezone-offset: -480' \
  -H 'x-bm-ua: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-version: 5e13905' \
  --data-raw '{"place_all_order":false,"contract_id":72,"category":1,"price":0.29,"vol":1,"way":1,"mode":3,"open_type":2,"leverage":10,"reverse_vol":0,"custom_id":176172650932643970}'

{
    "errno": "OK",
    "message": "Success",
    "data": {
        "order_id": 3000236533015210
    },
    "success": true
}


## 取消订单

curl 'https://derivatives.bitmart.com/gw-api/contract-tiger/forward/v1/ifcontract/cancelOrders' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'baggage: sentry-environment=production,sentry-release=5e13905,sentry-public_key=42eada5febd1737fdcb9413516bdb44f,sentry-trace_id=295c4439688b493095043ec4298b374b,sentry-sampled=true,sentry-sample_rand=0.17076608051357256,sentry-sample_rate=0.2' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -H 'expires: 0' \
  -H 'origin: https://derivatives.bitmart.com' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://derivatives.bitmart.com/zh-CN/futures/TRXUSDT?theme=dark' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: 295c4439688b493095043ec4298b374b-ac021a9afb23715a-1' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-client: WEB' \
  -H 'x-bm-contract: 2' \
  -H 'x-bm-device: 1c0886dd192a1dd0f23f71f7ab577a45' \
  -H 'x-bm-tag;' \
  -H 'x-bm-timezone: Asia/Shanghai' \
  -H 'x-bm-timezone-offset: -480' \
  -H 'x-bm-ua: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-version: 5e13905' \
  --data-raw '{"orders":[{"contract_id":72,"orders":[3000236525013551]}],"nonce":1761726407}'

{
"errno": "OK",
"message": "Success",
"data": {
    "succeed": [
        3000236525013551
    ],
    "failed": null
},
"success": true
}

## test
curl 'https://derivatives.bitmart.com/gw-api/contract-tiger/forward/v1/ifcontract/userAllOrders?offset=0&status=60&size=20&type=1' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'baggage: sentry-environment=production,sentry-release=5e13905,sentry-public_key=42eada5febd1737fdcb9413516bdb44f,sentry-trace_id=3a6010a4019d4805ad531d53ba796cff,sentry-sampled=false,sentry-sample_rand=0.23643568961036154,sentry-sample_rate=0.2' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -b 'sajssdk_2015_cross_new_user=1; currentCurrency=USD; _gcl_au=1.1.1444943330.1761721307; afUserId=4fee9c5e-597c-44dc-a0fa-18c1b9ce9dce-p; AF_SYNC=1761721307647; __adroll_fpc=e218cf5c8f26f43bc02e0d97bbe78ffe-1761721308350; _gid=GA1.2.442200763.1761721616; _ym_uid=1761721815966416165; _ym_d=1761721815; _ym_isad=2; _cfuvid=KYJBoKVgzzxA2Extq7iEpiHz4AD_cvjR3db.WknBSIU-1761744109810-0.0.1.1-604800000; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2214794011%22%2C%22first_id%22%3A%2219a2ec43555a-0c2b3183afef25-7e433c49-1484784-19a2ec435561389%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTlhMmVjNDM1NTVhLTBjMmIzMTgzYWZlZjI1LTdlNDMzYzQ5LTE0ODQ3ODQtMTlhMmVjNDM1NTYxMzg5IiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiMTQ3OTQwMTEifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2214794011%22%7D%2C%22%24device_id%22%3A%2219a2ec43555a-0c2b3183afef25-7e433c49-1484784-19a2ec435561389%22%7D; accessKey=eyJoZWFkZXIiOnsidHlwIjoiQml0TWFydCIsImFsZyI6IkJNQVBJU0lYIn0sInBheWxvYWQiOnsiamlkIjoiNzE5NTJmMTc5NDAzNGQyY2E0ZGFlMTdjMDQxYWU1ZjciLCJ2ZXJzaW9uIjoiMjAyNTEwMjkiLCJleHBpcmVzQXQiOjE3NjE4MzIyNTQyOTEsImJtIjoiMGhDUzRocmsybEYxYWM4d1dmMUx5ZWhhRkFrQVM4K0cvZk1ncXhPeHZRLzFrWFJiQzllQlY3WGlQREw2d1Nsb3BtZFdGZHZpR3YzMkZXRk0rUFJqWkhld1ZHc1NSb1VHazlyMG04N1BPeGtyWFlZOGxJemZhbDgrYWFtVUJjb0pkMjJ0VjRReU1HNk1PR0MzK1I3eG5sKzgwYUxBbFF1aGk0anBLNmZWZkNGcTdZaWZBYkpCcVI2Y1RsOTNkWXJJYS84QXNzQjl2UDlocVVjSjNZbDY0b1NTZktUdHFUODdwWDEzOHEwVUtRM1pMUEZ2c2dDM1ZnSWs4MmJvQUQ5SE9iSDFGZ0dxZWxMTGwrVVpjdVNKM1JjYlAycHA3WE1DNGJxV2RLbG5KUithN1BsS1ZMV2pVb2NtRGJLQTNkdW16bTk4YzUzNlo3U253bWUwQ2c4UnZoeVBQRGFRclVwdU9KVHJvUmQ2aWtIcnBGaDRwcXhqcDY1OERRSDF3Y21nIn0sInNpZ25hdHVyZSI6ImRGTEVndDFSUituVjNFZTRUSEJycW81cWhhZmg4cEFwRHpVUDN2a09QZmZxTVRLRzVlejhoK2E0TGFyWXNEM3A2RmJqR3ZDVEt1alg4ZDZtczhwVXZnPT0ifQ==; accessSalt=1UwiT974jJGn3fiqWuH2mVtrlzAwjxS8; tokenAt=1761832254291; tokenSt=1761745854210; _ym_visorc=w; golang=cn; hasDelegation=false; delegationType=0; delegationTypeList=[]; _ga=GA1.1.1486148889.1761721308; _ga_R8QWWJS24Y=GS2.1.s1761743959$o5$g1$t1761746820$j60$l0$h0; _ga_PJBF32MZ6E=GS2.1.s1761743959$o5$g1$t1761746820$j60$l0$h0; _ga_7BWH3BJ925=GS2.1.s1761743959$o5$g1$t1761746820$j60$l0$h0; _ga_0V649X1YZB=GS2.1.s1761743959$o4$g1$t1761746820$j60$l0$h0; __cf_bm=pzbRGRaXhCwhGPAg44rQtusewFhbRFXfA0_ZWPnmyBE-1761746824-1.0.1.1-1sXZxph6P.iq2ytu2G2KObleMhPdLMq69lsPxlzRgUd5ry3ANiJYIBnCWBkH62apyi3RiVf.KzUqW6qjNic5bXYAQv4_SuJExc0a67wJfwc' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://derivatives.bitmart.com/zh-CN/futures/BTCUSDT?theme=dark' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: 3a6010a4019d4805ad531d53ba796cff-b876ef3cc9babbaa-0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-client: WEB' \
  -H 'x-bm-contract: 2' \
  -H 'x-bm-device: 1c0886dd192a1dd0f23f71f7ab577a45' \
  -H 'x-bm-tag;' \
  -H 'x-bm-timezone: Asia/Shanghai' \
  -H 'x-bm-timezone-offset: -480' \
  -H 'x-bm-ua: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-version: 5e13905'

# auth部分
私有api cookie需要以下字段  x-bm-device 也为必须

    "cookie": "accessKey=eyJoZWFkZXIiOnsidHlwIjoiQml0TWFydCIsImFsZyI6IkJNQVBJU0lYIn0sInBheWxvYWQiOnsiamlkIjoiNDZjOWViZTViMTM0NGNkOTkyYTY3YTQ5NWNlYzMwZDkiLCJ2ZXJzaW9uIjoiMjAyNTEwMjkiLCJleHBpcmVzQXQiOjE3NjE4MjI5Mzk2MzYsImJtIjoiMGhDUzRocmsybEYxYWM4d1dmMUx5ZWhhRkFrQVM4K0cvZk1ncXhPeHZRLzFrWFJiQzllQlY3WGlQREw2d1Nsb0xaVmxIY2x4QWt5ZGl6cUpwdkpJZTVZa0p2S1hRelVHVEJrbWlLdHV6eHBIRFZSekR6NWMzWWMvNWJ1bU92RmplSlBURGVQdnBOdzVwQ1J2MjlsQzZqZkdpRVR6M3hHRmtaMmRQM0x4WjV0OHFveGd2SUxDTEFvMnQwbmNielJtYlNIVE5ydmd1NTVmMjhEMWlEMXBDMXlTQmd4TmRUMTNxRTZvNTdxKzRzdVFpcHBDY3hGeTVESFRVNXo3NldkaXBlbUxpSGIwVEd3cDdraFVKcElmRmVSSFhMZkdXbW5ZL0RwejhRN0drWXhUNVNlbGhvZGlsZ3kwQkF2UEtUaEorUHJrT3VqKzZXMHExM2xMeldET2JsTWJNVXFGQlhYSmowemx6bGpQY1JvZVUxMHpVVThzekppWlVPc3dxbEw3bU9WbFhhR0QrL3BVTXVLOFhkZTJ0Zz09In0sInNpZ25hdHVyZSI6IjVQUGdoMENla3dxeHdxWkxQTTdZRFg1enMzRVZzd04vcDdjZndUT1gxY0cvTVQzaVdyVzlEVXIybEw1bHU2OVNnTkc4Mzh4YkMyOVk0RC9teEpLSTF3PT0ifQ==; accessSalt=bv5wp0wMPMAtEbzEolJ1RtnWf0NQbepuiT; hasDelegation=false; delegationType=0; delegationTypeList=[];",

"x-bm-client": "WEB",
"x-bm-contract": "2",
"x-bm-device": "1c0886dd192a1dd0f23f71f7ab577a45",
"x-bm-timezone": "Asia/Shanghai",
"x-bm-timezone-offset": "-480",

## 自动鉴权具体参照 src/hyperquant/broker/auth.py
我们 client._session.__dict__["_apis"]['bitmart']
[accessKey, accessSalt, device]

## 续签
https://derivatives.bitmart.com/gw-api/gateway/token/v2/renew
curl 'https://derivatives.bitmart.com/gw-api/gateway/token/v2/renew' \
  -X 'POST' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'baggage: sentry-environment=production,sentry-release=5e13905,sentry-public_key=42eada5febd1737fdcb9413516bdb44f,sentry-trace_id=981122ccc69b4fef9c53d5024487e005,sentry-sampled=false,sentry-sample_rand=0.8927676402133862,sentry-sample_rate=0.2' \
  -H 'cache-control: no-cache' \
  -H 'content-length: 0' \
  -b 'currentCurrency=USD; _gcl_au=1.1.1444943330.1761721307; afUserId=4fee9c5e-597c-44dc-a0fa-18c1b9ce9dce-p; AF_SYNC=1761721307647; __adroll_fpc=e218cf5c8f26f43bc02e0d97bbe78ffe-1761721308350; _gid=GA1.2.442200763.1761721616; _ym_uid=1761721815966416165; _ym_d=1761721815; _ym_isad=2; _cfuvid=KYJBoKVgzzxA2Extq7iEpiHz4AD_cvjR3db.WknBSIU-1761744109810-0.0.1.1-604800000; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2214794011%22%2C%22first_id%22%3A%2219a2ec43555a-0c2b3183afef25-7e433c49-1484784-19a2ec435561389%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTlhMmVjNDM1NTVhLTBjMmIzMTgzYWZlZjI1LTdlNDMzYzQ5LTE0ODQ3ODQtMTlhMmVjNDM1NTYxMzg5IiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiMTQ3OTQwMTEifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2214794011%22%7D%2C%22%24device_id%22%3A%2219a2ec43555a-0c2b3183afef25-7e433c49-1484784-19a2ec435561389%22%7D; golang=cn; accessKey=eyJoZWFkZXIiOnsidHlwIjoiQml0TWFydCIsImFsZyI6IkJNQVBJU0lYIn0sInBheWxvYWQiOnsiamlkIjoiMzMwMGI4MjlhMzk2NGQ4NTkwODM4YWZkZTVmNmEyMGQiLCJ2ZXJzaW9uIjoiMjAyNTEwMjkiLCJleHBpcmVzQXQiOjE3NjE4MzU4NjM1MzksImJtIjoiMGhDUzRocmsybEYxYWM4d1dmMUx5ZWhhRkFrQVM4K0cvZk1ncXhPeHZRLzFrWFJiQzllQlY3WGlQREw2d1Nsb3IwSW5TN1BKYUFaOG9ybUgzbDBDMlVuVkRXUERnUWlJWExsMUFLY3ZmTkJTVGpvTE5SRUVneE93akwrRG9VOGUvVGFwUXpHWlZybmJXbHJTNDR3enFrdUN5THExZlo5bWhXY2krKzd1NjhKL2VSWGp4NUMrVTBnQ2toaFI4MFVkR1R0bm5ManFxQjk3aC9yRHdraWxzTXhoVEF5T1Z3a2FJMVRmUGRQRUUzSlV5Mkd1YjFXTHh5SklKMXhDeCtQNjI3ZHlhb3IzNEVHUGQrMlFNYVN6c0VPcXVVSjNFTlRyanZOMWhvVFhaMWgyNnNadytienI0TU5yendiRzQyZEdQaDRscEhHdkd3VXlIKzd1VzUyUXFnZGFWZ2dxRXpscWtZMU03QXFDRWV0RkdUOEdnc0FKN0VZTTBlN2lXNnU0In0sInNpZ25hdHVyZSI6Ik42SzFqdnNScHZIRDhIZTluUFJJUnhjOXRtUnY2YVlPVkpBSVdXRmxLV2VxQTVMU0ZCbU9tdkZjaTJMWSs0a094aEpZWDlzTUlucTlYSVVLVjZLVkJBPT0ifQ==; accessSalt=yj5YC8BvprQgsYvooTpvTKZbYyNgjjprXde; tokenAt=1761835863539; tokenSt=1761749463510; hasDelegation=false; delegationType=0; delegationTypeList=[]; _ga=GA1.1.1486148889.1761721308; _ga_R8QWWJS24Y=GS2.1.s1761743959$o5$g1$t1761751260$j57$l0$h0; _ga_7BWH3BJ925=GS2.1.s1761743959$o5$g1$t1761751260$j57$l0$h0; _ga_PJBF32MZ6E=GS2.1.s1761743959$o5$g1$t1761751260$j57$l0$h0; _ga_0V649X1YZB=GS2.1.s1761751257$o5$g1$t1761751260$j57$l0$h0; renewing=1' \
  -H 'origin: https://derivatives.bitmart.com' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://derivatives.bitmart.com/zh-CN/futures/TRXUSDT?theme=dark' \
  -H 'sec: 1' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: 981122ccc69b4fef9c53d5024487e005-8f8c563433e45da4-0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-client: WEB' \
  -H 'x-bm-contract: 2' \
  -H 'x-bm-device: 1c0886dd192a1dd0f23f71f7ab577a45' \
  -H 'x-bm-tag;' \
  -H 'x-bm-timezone: Asia/Shanghai' \
  -H 'x-bm-timezone-offset: -480' \
  -H 'x-bm-ua: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-version: 5e13905'

{
    "code": 0,
    "msg": "Success",
    "success": true,
    "data": {
        "accessToken": "eyJoZWFkZXIiOnsidHlwIjoiQml0TWFydCIsImFsZyI6IkJNQVBJU0lYIn0sInBheWxvYWQiOnsiamlkIjoiZDY5NTI1ZmQ1ZmZlNDM5ZTk1Mjg0YzBiZjc4YzlkMzQiLCJ2ZXJzaW9uIjoiMjAyNTEwMjkiLCJleHBpcmVzQXQiOjE3NjE4NDEwMDQwMjYsImJtIjoiMGhDUzRocmsybEYxYWM4d1dmMUx5ZWhhRkFrQVM4K0cvZk1ncXhPeHZRLzFrWFJiQzllQlY3WGlQREw2d1Nsb3VlRDg3ZXlvWlJzZ0JETU9FVGxqQlJxem5wRTEyblBVQktabStzd2Y2VHRFbGJiaXA2L2dGUkIxQ3dGTUhibHBDdlRYWHUzdWY5d09VeUtMeU1IZ1RiRVQvUUM4NzRXM2F4V2pYREVUdFJsRmFCckIzTWFhZkl3MHVxN0J5Q2FTb3VsbndNNEJGdTlaTG9vRXh3WDBZTTZpR0VIbEl0MG1pSzNFT29oL3VMQlFHR1dhSC9MTGZjakgwaWpFSEhoTWhFMmVUTWo4QVdYTkZOenRLZ1kwTUs0QUpYcXZmSE5acmdPdW83aDhpRzcrekpDWUZVSUtPUVNYY2R6VC9xRTlQclhPTDNTQXpGWnlKYTJGRkNaaEltL1VKZHBtNVVxZUlQZlNYY241K1lDWjFsVFh5a0lqQzMxaWVzM2R2eGVKIn0sInNpZ25hdHVyZSI6IjlqYkhGVERIUTE5aTBLOTBoR0Zhb3NvSmR2ck9kRnE1bUoxRXpueXBPZWE4eU0zK29LdFNXajFaSWZuSmMrc0ZWWG0xYUp6aGxJckM1eU5tNlkrdEVnPT0ifQ==",
        "accessSalt": "TMHoRbLnI2owFbTfC3R5oriOTaw86wxj6W7r",
        "expiresAt": 1761841004026
    }
}

## 可疑
## 可能的功能：申请用户账户 WebSocket 的 listenKey
curl 'https://derivatives.bitmart.com/gw-api/contract-tiger/account/listenKey' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'baggage: sentry-environment=production,sentry-release=5e13905,sentry-public_key=42eada5febd1737fdcb9413516bdb44f,sentry-trace_id=981122ccc69b4fef9c53d5024487e005,sentry-sampled=false,sentry-sample_rand=0.8927676402133862,sentry-sample_rate=0.2' \
  -H 'cache-control: no-cache' \
  -b 'currentCurrency=USD; _gcl_au=1.1.1444943330.1761721307; afUserId=4fee9c5e-597c-44dc-a0fa-18c1b9ce9dce-p; AF_SYNC=1761721307647; __adroll_fpc=e218cf5c8f26f43bc02e0d97bbe78ffe-1761721308350; _gid=GA1.2.442200763.1761721616; _ym_uid=1761721815966416165; _ym_d=1761721815; _ym_isad=2; _cfuvid=KYJBoKVgzzxA2Extq7iEpiHz4AD_cvjR3db.WknBSIU-1761744109810-0.0.1.1-604800000; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2214794011%22%2C%22first_id%22%3A%2219a2ec43555a-0c2b3183afef25-7e433c49-1484784-19a2ec435561389%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTlhMmVjNDM1NTVhLTBjMmIzMTgzYWZlZjI1LTdlNDMzYzQ5LTE0ODQ3ODQtMTlhMmVjNDM1NTYxMzg5IiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiMTQ3OTQwMTEifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2214794011%22%7D%2C%22%24device_id%22%3A%2219a2ec43555a-0c2b3183afef25-7e433c49-1484784-19a2ec435561389%22%7D; golang=cn; hasDelegation=false; delegationType=0; delegationTypeList=[]; _ga=GA1.1.1486148889.1761721308; _ga_R8QWWJS24Y=GS2.1.s1761743959$o5$g1$t1761751260$j57$l0$h0; _ga_7BWH3BJ925=GS2.1.s1761743959$o5$g1$t1761751260$j57$l0$h0; _ga_PJBF32MZ6E=GS2.1.s1761743959$o5$g1$t1761751260$j57$l0$h0; _ga_0V649X1YZB=GS2.1.s1761751257$o5$g1$t1761751260$j57$l0$h0; accessKey=eyJoZWFkZXIiOnsidHlwIjoiQml0TWFydCIsImFsZyI6IkJNQVBJU0lYIn0sInBheWxvYWQiOnsiamlkIjoiZDY5NTI1ZmQ1ZmZlNDM5ZTk1Mjg0YzBiZjc4YzlkMzQiLCJ2ZXJzaW9uIjoiMjAyNTEwMjkiLCJleHBpcmVzQXQiOjE3NjE4NDEwMDQwMjYsImJtIjoiMGhDUzRocmsybEYxYWM4d1dmMUx5ZWhhRkFrQVM4K0cvZk1ncXhPeHZRLzFrWFJiQzllQlY3WGlQREw2d1Nsb3VlRDg3ZXlvWlJzZ0JETU9FVGxqQlJxem5wRTEyblBVQktabStzd2Y2VHRFbGJiaXA2L2dGUkIxQ3dGTUhibHBDdlRYWHUzdWY5d09VeUtMeU1IZ1RiRVQvUUM4NzRXM2F4V2pYREVUdFJsRmFCckIzTWFhZkl3MHVxN0J5Q2FTb3VsbndNNEJGdTlaTG9vRXh3WDBZTTZpR0VIbEl0MG1pSzNFT29oL3VMQlFHR1dhSC9MTGZjakgwaWpFSEhoTWhFMmVUTWo4QVdYTkZOenRLZ1kwTUs0QUpYcXZmSE5acmdPdW83aDhpRzcrekpDWUZVSUtPUVNYY2R6VC9xRTlQclhPTDNTQXpGWnlKYTJGRkNaaEltL1VKZHBtNVVxZUlQZlNYY241K1lDWjFsVFh5a0lqQzMxaWVzM2R2eGVKIn0sInNpZ25hdHVyZSI6IjlqYkhGVERIUTE5aTBLOTBoR0Zhb3NvSmR2ck9kRnE1bUoxRXpueXBPZWE4eU0zK29LdFNXajFaSWZuSmMrc0ZWWG0xYUp6aGxJckM1eU5tNlkrdEVnPT0ifQ==; accessSalt=TMHoRbLnI2owFbTfC3R5oriOTaw86wxj6W7r; tokenAt=1761841004026; tokenSt=1761754604254; __cf_bm=_LAUsZLS6lCulZGe35LKC8IB4Q8zSIHfUxC7Rad4z80-1761754607-1.0.1.1-sKz928NRcAoV1oNbL5k2Hsu5J9a2kpRiOzjrUQnf_gJ9fjFQ9EUQhmY2ro2KwkvoNtEIbIbH7LDLELPVmwTUtFH8ncKxMr3Q0LmM_54ZvQs' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://derivatives.bitmart.com/zh-CN/futures/TRXUSDT?theme=dark' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sentry-trace: 981122ccc69b4fef9c53d5024487e005-83ec4385c42d0594-0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  -H 'x-bm-client: WEB' \
  -H 'x-bm-device: 1' \
  -H 'x-bm-version: 1.0.0'

  {
    "code": 0,
    "msg": "Success",
    "data": {
        "ts": "1761754613714000",
        "accessKey": "9ab9de4c-dad3-4213-a4ef-baaabb1fb423",
        "sign": "fcb7e98b43ba5f3729c0ad2f2e98f779",
        "expireTs": "1762100213714000"
    },
    "errorData": null,
    "success": true
}
# detail

POST

https://www.coinup.io/fe-co-api/common/public_info
{
    "uaTime": "2025-10-24 11:03:27",
    "securityInfo": "{\"log_BSDeviceFingerprint\":\"0\",\"log_original\":\"0\",\"log_CHFIT_DEVICEID\":\"0\"}"
}


{
    "id": 117,
    "contractName": "E-RESOLV-USDT",
    "symbol": "RESOLV-USDT",
    "contractType": "E",
    "coType": "E",
    "contractShowType": "USDT合约",
    "deliveryKind": "0",
    "contractSide": 1,
    "multiplier": 22.8000000000000000,
    "multiplierCoin": "RESOLV",
    "marginCoin": "USDT",
    "originalCoin": "USDT",
    "marginRate": 1.00000000,
    "capitalStartTime": 0,
    "capitalFrequency": 8,
    "settlementFrequency": 1,
    "brokerId": 1,
    "base": "RESOLV",
    "quote": "USDT",
    "coinResultVo": {
        "symbolPricePrecision": 5,
        "depth": [
            "5",
            "4",
            "3"
        ],
        "minOrderVolume": 1,
        "minOrderMoney": 1,
        "maxMarketVolume": 5000000,
        "maxMarketMoney": 6411360,
        "maxLimitVolume": 5000000,
        "maxLimitMoney": 5000000.0000000000000000,
        "priceRange": 0.3000000000,
        "marginCoinPrecision": 4,
        "fundsInStatus": 1,
        "fundsOutStatus": 1
    },
    "sort": 100,
    "maxLever": 75,
    "minLever": 1,
    "contractOtherName": "RESOLV/USDT",
    "subSymbol": "e_resolvusdt",
    "classification": 1,
    "nextCapitalSettTime": 1761292800000
}

# position + Balance

https://futures.coinup.io/fe-co-api/position/get_assets_list POST
{
    "uaTime": "2025-10-24 11:48:36",
    "securityInfo": "{\"log_BSDeviceFingerprint\":\"0\",\"log_original\":\"0\",\"log_CHFIT_DEVICEID\":\"0\"}"
}

{
    "code": "0",
    "msg": "成功",
    "data": {
        "positionList": [
            {
                "id": 256538,
                "contractId": 169,
                "contractName": "E-WLFI-USDT",
                "contractOtherName": "WLFI/USDT",
                "symbol": "WLFI-USDT",
                "positionVolume": 1.0,
                "canCloseVolume": 1.0,
                "closeVolume": 0.0,
                "openAvgPrice": 0.1409,
                "indexPrice": 0.14040034,
                "reducePrice": -0.9769279224708908,
                "holdAmount": 16.53718437074,
                "marginRate": 7.852395215348719,
                "realizedAmount": 0.0,
                "returnRate": -0.0177310149041873,
                "orderSide": "BUY",
                "positionType": 1,
                "canUseAmount": 16.11598335074,
                "canSubMarginAmount": 0,
                "openRealizedAmount": -0.0074949,
                "keepRate": 0.015,
                "maxFeeRate": 2.0E-4,
                "unRealizedAmount": -0.0074949,
                "leverageLevel": 5,
                "positionBalance": 2.1060051,
                "tradeFee": "-0.0004",
                "capitalFee": "0",
                "closeProfit": "0",
                "settleProfit": "0",
                "shareAmount": "0",
                "historyRealizedAmount": "-0.0004227",
                "profitRealizedAmount": "-0.0004",
                "openAmount": 0.4227,
                "adlLevel": 2
            }
        ],
        "accountList": [
            {
                "symbol": "USDT",
                "originalCoin": "USDT",
                "unRealizedAmount": "-0.0074949",
                "realizedAmount": "0",
                "totalMargin": "16.53718437074",
                "totalAmount": "16.53718437074",
                "canUseAmount": 16.11598335074,
                "availableAmount": 16.11598335074,
                "isolateMargin": "0",
                "walletBalance": "16.54467927074",
                "lockAmount": "0",
                "accountNormal": "16.54467927074",
                "totalMarginRate": "7.8523952153487187"
            },
            {
                "symbol": "ETH",
                "originalCoin": "ETH",
                "unRealizedAmount": "0",
                "realizedAmount": "0",
                "totalMargin": "0",
                "totalAmount": "0",
                "canUseAmount": 0.0,
                "availableAmount": 0.0,
                "isolateMargin": "0",
                "walletBalance": "0",
                "lockAmount": "0",
                "accountNormal": "0",
                "totalMarginRate": "0"
            }
        ],
        "totalBalanceSymbol": "BTC",
        "totalBalance": 0.0001499773787767
    },
    "msgData": null,
    "succ": true
}



# balance + position(备用)
curl 'https://futures.coinup.io/fe-co-api/position/wallet_and_unrealized' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -b 'lan=zh_CN; jpSpotSwitch=0; cusSkin=2; newTrade_layout=ord; isLogin=true; _gid=GA1.2.1647203863.1761206717; token=948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0; cf_clearance=LuJRjj5Jd5onNhrq98dNWN3zupD93grH35zxtJG2U_A-1761274982-1.2.1.1-LNxmsRKMeaCOZWpxgd1nYPhVyeGTb7akCBaCYai7s6eLVwDTWGlcixyCM8FSCaDG1Q_SXc37JKRn3yDpirQsBFgYyDt9Bh5RjimvyFJgdv7O73q26_JxRyqFKU9yHXdyXZndip0C1gTnsAW1dgoaeVODy11PkpLHK_F_COcaDLjKHbR1kjR7O03I9NtWypjb62wO71n_l1AX.xK6TSdUt7Y08U1UyQBgH_R.1VqUkF8; _gat_gtag_UA_149942350_1=1; _ga_01HC17N7QQ=GS2.1.s1761276964$o7$g0$t1761276964$j60$l0$h0; _ga=GA1.1.1696620034.1761206716; _ga_4JHJ4YPRL8=GS2.1.s1761273055$o5$g1$t1761277022$j48$l0$h0' \
  -H 'device;' \
  -H 'exchange-client: pc' \
  -H 'exchange-language: zh_CN' \
  -H 'exchange-token: 948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0' \
  -H 'origin: https://futures.coinup.io' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://futures.coinup.io/zh_CN/trade' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  --data-raw '{"coin":"USDT","priceBasis":0,"uaTime":"2025-10-24 11:37:02","securityInfo":"{\"log_BSDeviceFingerprint\":\"0\",\"log_original\":\"0\",\"log_CHFIT_DEVICEID\":\"0\"}"}'

{
    "code": "0",
    "msg": "成功",
    "data": {
        "walletAmount": 16.54467927074,
        "unRealizedAmount": -0.0015,
        "equity": 16.54317927074,
        "positionVos": [
            {
                "E-WLFI-USDT": {
                    "tagPrice": 0.1409,
                    "lastPrice": 0.1408,
                    "buyOne": 0.1408,
                    "sellOne": 0.1409
                }
            }
        ]
    },
    "msgData": null,
    "succ": true
}

# 市价单平仓（cookie暂时忽略

curl 'https://futures.coinup.io/fe-co-api/order/order_create' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -b 'lan=zh_CN; jpSpotSwitch=0; cusSkin=2; newTrade_layout=ord; isLogin=true; token=948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0; _gid=GA1.2.679822732.1761486956; _ga=GA1.1.1696620034.1761206716; _ga_01HC17N7QQ=GS2.1.s1761540886$o10$g1$t1761540899$j47$l0$h0; cf_clearance=zNTAplBpXoMkVhmls3nPtu3_.9I1JZH8JO0wGWLm3bc-1761561996-1.2.1.1-qfaPFTp6IfY8qV6iGDlKSVmP5_tAOiQU7amNq8pKoU0EtcJFxksT6Y.KOgNyQCN9Uph.pQ_5ws4Zj_CoOEAZinzwHvr8smIwSawgbV4NH4Z5eXSf7_eMFDf5lOMiNT0mS.UYiMMelWZw0Z32UrJTHKgsdJCvfspXtUL9zUlYAxJSLRdJP0RHvsrHdUF.JlSZkIbTltkhNO60ngB5m2WV7YBJV8u0n2vw76dqmcGau70; _ga_4JHJ4YPRL8=GS2.1.s1761561877$o8$g1$t1761562041$j24$l0$h0' \
  -H 'device;' \
  -H 'exchange-client: pc' \
  -H 'exchange-language: zh_CN' \
  -H 'exchange-token: 948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0' \
  -H 'origin: https://futures.coinup.io' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://futures.coinup.io/zh_CN' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-arch: "arm"' \
  -H 'sec-ch-ua-bitness: "64"' \
  -H 'sec-ch-ua-full-version: "141.0.3537.92"' \
  -H 'sec-ch-ua-full-version-list: "Microsoft Edge";v="141.0.3537.92", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.108"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-model: ""' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-ch-ua-platform-version: "15.6.0"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  --data-raw '{"contractId":169,"positionType":1,"side":"SELL","leverageLevel":5,"price":0,"volume":"1","open":"CLOSE","type":2,"triggerPrice":null,"isConditionOrder":false,"orderUnit":2,"secret":"c1eb51bc4f81b404cfb0485f6acc2054","uaTime":"2025-10-27 18:47:21","securityInfo":"{\"log_BSDeviceFingerprint\":\"0\",\"log_original\":\"0\",\"log_CHFIT_DEVICEID\":\"0\"}"}'


  {
    "code": "0",
    "msg": "成功",
    "data": {
        "triggerIds": [],
        "ids": [
            "2951913310096288573"
        ],
        "cancelIds": []
    },
    "msgData": null,
    "succ": true
}

# 市价单开仓

curl 'https://futures.coinup.io/fe-co-api/order/order_create' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -H 'device;' \
  -H 'exchange-client: pc' \
  -H 'exchange-language: zh_CN' \
  -H 'exchange-token: 948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0' \
  -H 'origin: https://futures.coinup.io' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://futures.coinup.io/zh_CN' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-arch: "arm"' \
  -H 'sec-ch-ua-bitness: "64"' \
  -H 'sec-ch-ua-full-version: "141.0.3537.92"' \
  -H 'sec-ch-ua-full-version-list: "Microsoft Edge";v="141.0.3537.92", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.108"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-model: ""' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-ch-ua-platform-version: "15.6.0"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  --data-raw '{"contractId":169,"positionType":1,"side":"BUY","leverageLevel":5,"price":0,"volume":3,"triggerPrice":null,"open":"OPEN","type":2,"isConditionOrder":false,"isOto":false,"takerProfitTrigger":null,"takerProfitPrice":0,"takerProfitType":2,"stopLossTrigger":null,"stopLossPrice":0,"stopLossType":2,"isCheckLiq":1,"orderUnit":2,"secret":"7835cf6141a0a6c45cdf4bb1b1dada9d","uaTime":"2025-10-27 18:49:17","securityInfo":"{\"log_BSDeviceFingerprint\":\"0\",\"log_original\":\"0\",\"log_CHFIT_DEVICEID\":\"0\"}"}'


{
    "code": "0",
    "msg": "成功",
    "data": {
        "triggerIds": [],
        "ids": [
            "2951791298665186909"
        ],
        "cancelIds": []
    },
    "msgData": null,
    "succ": true
}

# 限价单开仓(多)

curl 'https://futures.coinup.io/fe-co-api/order/order_create' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -H 'device;' \
  -H 'exchange-client: pc' \
  -H 'exchange-language: zh_CN' \
  -H 'exchange-token: 948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0' \
  -H 'origin: https://futures.coinup.io' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://futures.coinup.io/zh_CN' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-arch: "arm"' \
  -H 'sec-ch-ua-bitness: "64"' \
  -H 'sec-ch-ua-full-version: "141.0.3537.92"' \
  -H 'sec-ch-ua-full-version-list: "Microsoft Edge";v="141.0.3537.92", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.108"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-model: ""' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-ch-ua-platform-version: "15.6.0"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  --data-raw '{"contractId":169,"positionType":1,"side":"BUY","leverageLevel":5,"price":0.13,"volume":"1","triggerPrice":null,"open":"OPEN","type":1,"isConditionOrder":false,"isOto":false,"takerProfitTrigger":null,"takerProfitPrice":0,"takerProfitType":2,"stopLossTrigger":null,"stopLossPrice":0,"stopLossType":2,"isCheckLiq":1,"orderUnit":2,"secret":"78b241867e8253eee4aa7fee8b673369","uaTime":"2025-10-27 18:50:40","securityInfo":"{\"log_BSDeviceFingerprint\":\"0\",\"log_original\":\"0\",\"log_CHFIT_DEVICEID\":\"0\"}"}'

# 限价单开仓(空)
...省略
{
    "contractId": 169,
    "positionType": 1,
    "side": "SELL",
    "leverageLevel": 5,
    "price": 0.15,
    "volume": "1",
    "triggerPrice": null,
    "open": "OPEN",
    "type": 1,
    "isConditionOrder": false,
    "isOto": false,
    "takerProfitTrigger": null,
    "takerProfitPrice": 0,
    "takerProfitType": 2,
    "stopLossTrigger": null,
    "stopLossPrice": 0,
    "stopLossType": 2,
    "isCheckLiq": 1,
    "orderUnit": 2,
    "secret": "65fb4c7cc0b4238386bd03b75512cf54",
    "uaTime": "2025-10-27 18:54:59",
    "securityInfo": "{\"log_BSDeviceFingerprint\":\"0\",\"log_original\":\"0\",\"log_CHFIT_DEVICEID\":\"0\"}"
}

# 取消订单
curl 'https://futures.coinup.io/fe-co-api/order/order_cancel' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -b 'lan=zh_CN; jpSpotSwitch=0; cusSkin=2; newTrade_layout=ord; isLogin=true; token=948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0; _gid=GA1.2.679822732.1761486956; _ga=GA1.1.1696620034.1761206716; _ga_01HC17N7QQ=GS2.1.s1761540886$o10$g1$t1761540899$j47$l0$h0; cf_clearance=zNTAplBpXoMkVhmls3nPtu3_.9I1JZH8JO0wGWLm3bc-1761561996-1.2.1.1-qfaPFTp6IfY8qV6iGDlKSVmP5_tAOiQU7amNq8pKoU0EtcJFxksT6Y.KOgNyQCN9Uph.pQ_5ws4Zj_CoOEAZinzwHvr8smIwSawgbV4NH4Z5eXSf7_eMFDf5lOMiNT0mS.UYiMMelWZw0Z32UrJTHKgsdJCvfspXtUL9zUlYAxJSLRdJP0RHvsrHdUF.JlSZkIbTltkhNO60ngB5m2WV7YBJV8u0n2vw76dqmcGau70; _ga_4JHJ4YPRL8=GS2.1.s1761561877$o8$g1$t1761562548$j11$l0$h0' \
  -H 'device;' \
  -H 'exchange-client: pc' \
  -H 'exchange-language: zh_CN' \
  -H 'exchange-token: 948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0' \
  -H 'origin: https://futures.coinup.io' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://futures.coinup.io/zh_CN' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-arch: "arm"' \
  -H 'sec-ch-ua-bitness: "64"' \
  -H 'sec-ch-ua-full-version: "141.0.3537.92"' \
  -H 'sec-ch-ua-full-version-list: "Microsoft Edge";v="141.0.3537.92", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.108"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-model: ""' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-ch-ua-platform-version: "15.6.0"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  --data-raw '{"contractId":169,"orderId":"2951913395995535853","isConditionOrder":false,"uaTime":"2025-10-27 18:55:49","securityInfo":"{\"log_BSDeviceFingerprint\":\"0\",\"log_original\":\"0\",\"log_CHFIT_DEVICEID\":\"0\"}"}'

{
    "code": "0",
    "msg": "成功",
    "data": null,
    "msgData": null,
    "succ": true
}

# 获取订单

curl 'https://futures.coinup.io/fe-co-api/order/current_order_list' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -b 'lan=zh_CN; jpSpotSwitch=0; cusSkin=2; newTrade_layout=ord; isLogin=true; token=948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0; _gid=GA1.2.679822732.1761486956; _ga=GA1.1.1696620034.1761206716; _ga_01HC17N7QQ=GS2.1.s1761540886$o10$g1$t1761540899$j47$l0$h0; cf_clearance=F4Pg8qr.OXBna_Ldf81xZ5TOCYn3.fmBzKIWk2mYbrA-1761562681-1.2.1.1-ax9X2hkj_ZxHehvBL8b3GPmO6oYAYku0fzZqk7ZB.hVt0lzOOSrSHrEKoxShxCI7Piz2ZcKamCFB8XMT6xu2HWSfrRe0ADlotIHnc1XPVLB7pdC940PNAn0leLX_c7waq3Zd.93KnQhoCbzeivHIc2lfWxKl4jUrkK0pWKZZ..fAzZXw59eWsjQekVSnAFQCA6Eb7fZ5LVWrkn6GwPb5DoosBDvQYvVHASCVt0ddPjbFgM16pd3J87kkHuy2jqPq; _ga_4JHJ4YPRL8=GS2.1.s1761561877$o8$g1$t1761562682$j58$l0$h0' \
  -H 'device;' \
  -H 'exchange-client: pc' \
  -H 'exchange-language: zh_CN' \
  -H 'exchange-token: 948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0' \
  -H 'origin: https://futures.coinup.io' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://futures.coinup.io/zh_CN' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-arch: "arm"' \
  -H 'sec-ch-ua-bitness: "64"' \
  -H 'sec-ch-ua-full-version: "141.0.3537.92"' \
  -H 'sec-ch-ua-full-version-list: "Microsoft Edge";v="141.0.3537.92", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.108"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-model: ""' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-ch-ua-platform-version: "15.6.0"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  --data-raw '{"contractId":"","uaTime":"2025-10-27 18:58:02","securityInfo":"{\"log_BSDeviceFingerprint\":\"0\",\"log_original\":\"0\",\"log_CHFIT_DEVICEID\":\"0\"}"}'

  {
    "code": "0",
    "msg": "成功",
    "data": {
        "count": 1,
        "orderList": [
            {
                "symbol": "WLFI-USDT",
                "contractOtherName": "WLFI/USDT",
                "positionType": 1,
                "orderId": "2951913499074783723",
                "avgPrice": 0,
                "tradeFee": 0,
                "memo": 0,
                "type": 1,
                "mtime": 1761562500000,
                "quote": "USDT",
                "liqPositionMsg": "",
                "dealVolume": 0,
                "price": 0.15,
                "ctime": 1761562500000,
                "contractName": "E-WLFI-USDT",
                "id": "263457",
                "contractSide": 1,
                "pricePrecision": 4,
                "side": "SELL",
                "multiplier": 15,
                "marginCoin": "USDT",
                "isAdd": false,
                "volume": 1,
                "isCompensate": false,
                "contractId": 169,
                "orderBalance": 2.25,
                "open": "OPEN",
                "base": "WLFI",
                "status": 0
            }
        ]
    },
    "msgData": null,
    "succ": true
}

# 获取历史订单
curl 'https://futures.coinup.io/fe-co-api/order/history_order_list' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json;charset=UTF-8' \
  -b 'lan=zh_CN; jpSpotSwitch=0; cusSkin=2; newTrade_layout=ord; isLogin=true; token=948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0; _gid=GA1.2.679822732.1761486956; _ga=GA1.1.1696620034.1761206716; _ga_01HC17N7QQ=GS2.1.s1761540886$o10$g1$t1761540899$j47$l0$h0; cf_clearance=Xu0QcQAsWLQ4kbTcwNGb5AhFHoZpe8JOlLzOP.mIonU-1761573045-1.2.1.1-CGz516KjOZRiWl44JB7_y6A6aUYTUoyxMQG3XgALQUPmNaZ8zX2JPTmzCuhFSjZmHoYh_tMDjuDfX_.Gwyjaa.FVKGEGE_hORNF9TGDaJ1GgJe4eWEIVooBSoq2KK_pNzh9JkWkrV1Rmo_zdxQV8SEsuB6QXaCKsU.cWJ4AR.1pC38qpUzwH2n3rrSYRmpDJqs7o3caOHMVZiSg0HtwIRqGccjRcesmkWtZUUvHj6_MX7KBXQojfs1I2rjaJnTDe; _ga_4JHJ4YPRL8=GS2.1.s1761572082$o9$g1$t1761573203$j60$l0$h0' \
  -H 'device;' \
  -H 'exchange-client: pc' \
  -H 'exchange-language: zh_CN' \
  -H 'exchange-token: 948a3841361bd38c30fc37355c3fb01a35135042c1c44698bed6f9cd6262cce0' \
  -H 'origin: https://futures.coinup.io' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://futures.coinup.io/zh_CN' \
  -H 'sec-ch-ua: "Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"' \
  -H 'sec-ch-ua-arch: "arm"' \
  -H 'sec-ch-ua-bitness: "64"' \
  -H 'sec-ch-ua-full-version: "141.0.3537.92"' \
  -H 'sec-ch-ua-full-version-list: "Microsoft Edge";v="141.0.3537.92", "Not?A_Brand";v="8.0.0.0", "Chromium";v="141.0.7390.108"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-model: ""' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-ch-ua-platform-version: "15.6.0"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0' \
  --data-raw '{"contractId":"","uaTime":"2025-10-27 21:53:25","securityInfo":"{\"log_BSDeviceFingerprint\":\"0\",\"log_original\":\"0\",\"log_CHFIT_DEVICEID\":\"0\"}"}'

  {
    "code": "0",
    "msg": "成功",
    "data": {
        "count": 69,
        "orderList": [
            {
                "symbol": "WLFI-USDT",
                "contractOtherName": "WLFI/USDT",
                "positionType": 1,
                "orderId": "2951916505551949315",
                "avgPrice": 0,
                "tradeFee": 0,
                "realizedAmount": 0,
                "memo": 1,
                "type": 1,
                "mtime": 1761573204000,
                "quote": "USDT",
                "liqPositionMsg": "",
                "dealVolume": 0,
                "price": 0.13,
                "ctime": 1761573088000,
                "contractName": "E-WLFI-USDT",
                "id": "263462",
                "contractSide": 1,
                "pricePrecision": 4,
                "side": "BUY",
                "multiplier": 15,
                "marginCoin": "USDT",
                "isAdd": false,
                "volume": 1,
                "isCompensate": false,
                "contractId": 169,
                "orderBalance": 1.95,
                "open": "OPEN",
                "base": "WLFI",
                "status": 4 
            },
            {
                "symbol": "WLFI-USDT",
                "contractOtherName": "WLFI/USDT",
                "positionType": 1,
                "orderId": "2951914495507231793",
                "avgPrice": 0.1457,
                "tradeFee": 0.0004371,
                "realizedAmount": -0.0015,
                "memo": 0,
                "type": 2,
                "mtime": 1761565386000,
                "quote": "USDT",
                "liqPositionMsg": "",
                "dealVolume": 1,
                "price": 0,
                "ctime": 1761565385000,
                "contractName": "E-WLFI-USDT",
                "id": "263310",
                "contractSide": 1,
                "pricePrecision": 4,
                "side": "SELL",
                "multiplier": 15,
                "marginCoin": "USDT",
                "isAdd": false,
                "volume": 1,
                "isCompensate": false,
                "contractId": 169,
                "orderBalance": -1.1855,
                "open": "CLOSE",
                "base": "WLFI",
                "status": 2 
            }
        ]
    },
    "msgData": null,
    "succ": true
}
import base64
import hmac
import urllib.parse
import time
import hashlib
from typing import Any
from aiohttp import ClientWebSocketResponse, FormData, JsonPayload
from multidict import CIMultiDict
from yarl import URL
import pybotters
import json as pyjson
from urllib.parse import urlencode
from datetime import datetime, timezone


def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()



def serialize(obj, prefix=''):
    """
    Python 版 UK/v：递归排序 + urlencode + 展平
    """
    def _serialize(obj, prefix=''):
        if obj is None:
            return []
        if isinstance(obj, dict):
            items = []
            for k in sorted(obj.keys()):
                v = obj[k]
                n = f"{prefix}[{k}]" if prefix else k
                items.extend(_serialize(v, n))
            return items
        elif isinstance(obj, list):
            # JS style: output key once, then join values by &
            values = []
            for v in obj:
                if isinstance(v, dict):
                    # Recursively serialize dict, but drop key= part (just use value part)
                    sub = _serialize(v, prefix)
                    # sub is a list of key=value, but we want only value part
                    for s in sub:
                        # s is like 'key=value', need only value
                        parts = s.split('=', 1)
                        if len(parts) == 2:
                            values.append(parts[1])
                        else:
                            values.append(parts[0])
                else:
                    # Handle booleans and empty strings
                    if isinstance(v, bool):
                        val = "true" if v else "false"
                    elif v == "":
                        val = ""
                    else:
                        val = str(v)
                    values.append(val)
            return [f"{urllib.parse.quote(str(prefix))}={'&'.join(values)}"]
        else:
            # Handle booleans and empty strings
            if isinstance(obj, bool):
                val = "true" if obj else "false"
            elif obj == "":
                val = ""
            else:
                val = str(obj)
            return [f"{urllib.parse.quote(str(prefix))}={val}"]
    return "&".join(_serialize(obj, prefix))

# 🔑 Ourbit 的鉴权函数
class Auth:
    @staticmethod
    def edgex(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data = kwargs.get("data") or {}
        headers: CIMultiDict = kwargs["headers"]

        session = kwargs["session"]
        api_key:str = session.__dict__["_apis"][pybotters.auth.Hosts.items[url.host].name][0]
        secret = session.__dict__["_apis"][pybotters.auth.Hosts.items[url.host].name][1]
        passphrase:str = session.__dict__["_apis"][pybotters.auth.Hosts.items[url.host].name][2]
        passphrase = passphrase.split("-")[0]
        timestamp = str(int(time.time() * 1000))
        # timestamp = "1758535055061"

        raw_body = ""
        if data and method.upper() in ["POST", "PUT", "PATCH"] and data:
            raw_body = serialize(data)
        else:
            raw_body = serialize(dict(url.query.items()))


        secret_quoted = urllib.parse.quote(secret, safe="")
        b64_secret = base64.b64encode(secret_quoted.encode("utf-8")).decode()
        message = f"{timestamp}{method.upper()}{url.raw_path}{raw_body}"
        sign = hmac.new(b64_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
        
        sigh_header =  {
                "X-edgeX-Api-Key": api_key,
                "X-edgeX-Passphrase": passphrase,
                "X-edgeX-Signature": sign,
                "X-edgeX-Timestamp": timestamp,
        }
        # ws单独进行签名
        if headers.get("Upgrade") == "websocket":
            json_str = pyjson.dumps(sigh_header, separators=(",", ":"))
            b64_str = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
            b64_str.replace("=", "")
            headers.update({"Sec-WebSocket-Protocol": b64_str})
        else:
            headers.update(sigh_header)

        if data:
            kwargs.update({"data": JsonPayload(data)})

        return args
    
    @staticmethod
    def ourbit(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data = kwargs.get("data") or {}
        headers: CIMultiDict = kwargs["headers"]

        # 从 session 里取 token
        session = kwargs["session"]
        token = session.__dict__["_apis"][pybotters.auth.Hosts.items[url.host].name][0]

        # 时间戳 & body
        now_ms = int(time.time() * 1000)
        raw_body_for_sign = (
            data
            if isinstance(data, str)
            else pyjson.dumps(data, separators=(",", ":"), ensure_ascii=False)
        )

        # 签名
        mid_hash = md5_hex(f"{token}{now_ms}")[7:]
        final_hash = md5_hex(f"{now_ms}{raw_body_for_sign}{mid_hash}")

        # 设置 headers
        headers.update(
            {
                "Authorization": token,
                "Language": "Chinese",
                "language": "Chinese",
                "Content-Type": "application/json",
                "x-ourbit-sign": final_hash,
                "x-ourbit-nonce": str(now_ms),
            }
        )

        # 更新 kwargs.body，保证发出去的与签名一致
        kwargs.update({"data": raw_body_for_sign})

        return args

    @staticmethod
    def ourbit_spot(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data = kwargs.get("data") or {}
        headers: CIMultiDict = kwargs["headers"]

        # 从 session 里取 token
        session = kwargs["session"]
        token = session.__dict__["_apis"][pybotters.auth.Hosts.items[url.host].name][0]
        cookie = f"uc_token={token}; u_id={token}; "
        headers.update({"cookie": cookie})
        return args

    @staticmethod
    def lbank(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        data = kwargs.get("data") or {}
        headers: CIMultiDict = kwargs["headers"]

        # 从 session 里取 api_key & secret
        session = kwargs["session"]
        token = session.__dict__["_apis"][pybotters.auth.Hosts.items[url.host].name][0]


        # 设置 headers
        headers.update(
            {
                "ex-language": 'zh-TW',
                "ex-token": token,
                "source": "4",
                "versionflage": "true",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
            }
        )

        # 更新 kwargs.body，保证发出去的与签名一致
        # kwargs.update({"data": raw_body_for_sign})

        return args

    @staticmethod
    def deepcoin(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0].upper()
        url: URL = args[1]
        headers: CIMultiDict = kwargs["headers"]

        session = kwargs["session"]
        creds = session.__dict__["_apis"][pybotters.auth.Hosts.items[url.host].name]
        if len(creds) < 3:
            raise RuntimeError("DeepCoin credentials must include api_key, secret, passphrase")
        api_key, secret, passphrase = creds[0], creds[1], creds[2]

        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

        body_str = ""
        json_body = kwargs.pop("json", None)
        data_body = kwargs.get("data")
        if method in {"POST", "PUT", "PATCH"}:
            payload = json_body if json_body is not None else data_body
            if payload is not None:
                if isinstance(payload, (dict, list)):
                    body_str = pyjson.dumps(payload, separators=(",", ":"), ensure_ascii=False)
                    kwargs["data"] = body_str
                else:
                    body_str = str(payload)
                    kwargs["data"] = body_str
            else:
                kwargs["data"] = body_str
        else:
            if json_body is not None:
                # GET requests should not carry JSON bodies
                kwargs.pop("json", None)
            if data_body is not None:
                kwargs["data"] = data_body

        request_path = url.raw_path_qs or url.raw_path
        message = f"{timestamp}{method}{request_path}{body_str}"
        secret_bytes = secret.encode("utf-8") if isinstance(secret, str) else secret
        signature = hmac.new(secret_bytes, message.encode("utf-8"), hashlib.sha256).digest()
        sign_b64 = base64.b64encode(signature).decode()

        headers.update(
            {
                "DC-ACCESS-KEY": api_key,
                "DC-ACCESS-PASSPHRASE": passphrase,
                "DC-ACCESS-TIMESTAMP": timestamp,
                "DC-ACCESS-SIGN": sign_b64,
                "Content-Type": headers.get("Content-Type", "application/json"),
            }
        )

        return args

    @staticmethod
    def bitmart(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        headers: CIMultiDict = kwargs["headers"]

        session = kwargs["session"]
        host_key = url.host
        try:
            api_name = pybotters.auth.Hosts.items[host_key].name
        except (KeyError, AttributeError):
            api_name = host_key

        creds = session.__dict__.get("_apis", {}).get(api_name)
        if not creds or len(creds) < 3:
            raise RuntimeError("Bitmart credentials (accessKey, accessSalt, device) are required")

        access_key = creds[0]
        access_salt = creds[1]
        access_salt = access_salt.decode("utf-8")
        device = creds[2]
        extra_cookie = creds[3] if len(creds) > 3 else None

        cookie_parts = [
            f"accessKey={access_key}",
            f"accessSalt={access_salt}",
            "hasDelegation=false",
            "delegationType=0",
            "delegationTypeList=[]",
        ]
        if extra_cookie:
            if isinstance(extra_cookie, str) and extra_cookie:
                cookie_parts.append(extra_cookie.strip(";"))

        headers["cookie"] = "; ".join(cookie_parts)

        headers.setdefault("x-bm-client", "WEB")
        headers.setdefault("x-bm-contract", "2")
        headers.setdefault("x-bm-device", device)
        headers.setdefault("x-bm-timezone", "Asia/Shanghai")
        headers.setdefault("x-bm-timezone-offset", "-480")
        headers.setdefault("x-bm-tag", "")
        headers.setdefault("x-bm-version", "5e13905")
        headers.setdefault('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0')

        ua = headers.get("User-Agent") or headers.get("user-agent")
        if ua:
            headers.setdefault("x-bm-ua", ua)

        return args

    @staticmethod
    def bitmart_api(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        """Bitmart OpenAPI (futures v2) signing for api-cloud-v2.bitmart.com.

        Spec per docs:
        X-BM-SIGN = hex_lower(HMAC_SHA256(secret, timestamp + '#' + memo + '#' + payload_string))
        - For POST: payload_string is the JSON body string
        - For GET: payload_string is the query string (if any), otherwise empty
        Headers required: X-BM-KEY, X-BM-TIMESTAMP, X-BM-SIGN
        """
        method: str = args[0]
        url: URL = args[1]
        headers: CIMultiDict = kwargs["headers"]

        session = kwargs["session"]
        try:
            api_name = pybotters.auth.Hosts.items[url.host].name
        except (KeyError, AttributeError):
            api_name = url.host

        creds = session.__dict__.get("_apis", {}).get(api_name)
        if not creds or len(creds) < 3:
            raise RuntimeError("Bitmart API credentials (access_key, secret, memo) are required")

        access_key = creds[0]
        secret = creds[1]
        memo = creds[2]
        if isinstance(secret, str):
            secret_bytes = secret.encode("utf-8")
        else:
            secret_bytes = secret
        if isinstance(memo, bytes):
            memo = memo.decode("utf-8")

        timestamp = str(int(time.time() * 1000))
        method_upper = method.upper()

        # Build query string
        params = kwargs.get("params")
        if isinstance(params, dict) and params:
            query_items = [f"{k}={v}" for k, v in params.items() if v is not None]
            query_string = "&".join(query_items)
        else:
            query_string = url.query_string

        # Build body string for signing and ensure sending matches signature
        body = None
        body_str = ""
        if method_upper == "GET":
            body_str = query_string or ""
        else:
            # Prefer original JSON object if present for deterministic signing
            if kwargs.get("json") is not None:
                body = kwargs.get("json")
            else:
                body = kwargs.get("data")

            # If upstream already turned JSON into JsonPayload, extract its value
            if isinstance(body, JsonPayload):
                body_value = getattr(body, "_value", None)
            else:
                body_value = body

            if isinstance(body_value, (dict, list)):
                # Compact JSON to avoid whitespace discrepancies and sign exact bytes we send
                body_str = pyjson.dumps(body_value, separators=(",", ":"), ensure_ascii=False)
                kwargs["data"] = body_str
                kwargs.pop("json", None)
            elif isinstance(body_value, (str, bytes)):
                # Sign and send exactly this string/bytes
                body_str = body_value.decode("utf-8") if isinstance(body_value, bytes) else body_value
                kwargs["data"] = body_str
                kwargs.pop("json", None)
            elif body_value is None:
                body_str = ""
            else:
                # Fallback: string conversion (should still be JSON-like)
                body_str = str(body_value)
                kwargs["data"] = body_str
                kwargs.pop("json", None)

        # Prehash format: timestamp#memo#payload
        message = f"{timestamp}#{memo}#{body_str}"
        signature_hex = hmac.new(secret_bytes, message.encode("utf-8"), hashlib.sha256).hexdigest()

        headers.update(
            {
                "X-BM-KEY": access_key,
                "X-BM-TIMESTAMP": timestamp,
                "X-BM-SIGN": signature_hex,
                "Content-Type": "application/json; charset=UTF-8",
            }
        )

        return args

    @staticmethod
    def coinw(args: tuple[str, URL], kwargs: dict[str, Any]) -> tuple[str, URL]:
        method: str = args[0]
        url: URL = args[1]
        headers: CIMultiDict = kwargs["headers"]

        session = kwargs["session"]
        try:
            api_key, secret, _ = session.__dict__["_apis"][pybotters.auth.Hosts.items[url.host].name]
        except (KeyError, ValueError):
            raise RuntimeError("CoinW credentials (api_key, secret) are required")

        timestamp = str(int(time.time() * 1000))
        method_upper = method.upper()

        params = kwargs.get("params")
        query_string = ""
        if isinstance(params, dict) and params:
            query_items = [
                f"{key}={value}"
                for key, value in params.items()
                if value is not None
            ]
            query_string = "&".join(query_items)
        elif url.query_string:
            query_string = url.query_string

        body_str = ""

        if method_upper == "GET":
            body = None
            data = None
        else:
            body = kwargs.get("json")
            data = kwargs.get("data")
            payload = body if body is not None else data
            if isinstance(payload, (dict, list)):
                body_str = pyjson.dumps(payload, separators=(",", ":"), ensure_ascii=False)
                kwargs["data"] = body_str
                kwargs.pop("json", None)
            elif payload is not None:
                body_str = str(payload)
                kwargs["data"] = body_str
                kwargs.pop("json", None)

        if query_string:
            path = f"{url.raw_path}?{query_string}"
        else:
            path = url.raw_path

        message = f"{timestamp}{method_upper}{path}{body_str}"
        signature = hmac.new(
            secret, message.encode("utf-8"), hashlib.sha256
        ).digest()
        signature_b64 = base64.b64encode(signature).decode("ascii")

        headers.update(
            {
                "sign": signature_b64,
                "api_key": api_key,
                "timestamp": timestamp,
            }
        )

        if method_upper in {"POST", "PUT", "PATCH", "DELETE"} and "data" in kwargs:
            headers.setdefault("Content-Type", "application/json")

        return args

pybotters.auth.Hosts.items["futures.ourbit.com"] = pybotters.auth.Item(
    "ourbit", Auth.ourbit
)
pybotters.auth.Hosts.items["www.ourbit.com"] = pybotters.auth.Item(
    "ourbit", Auth.ourbit_spot
)

pybotters.auth.Hosts.items["www.ourbit.com"] = pybotters.auth.Item(
    "ourbit", Auth.ourbit_spot
)

pybotters.auth.Hosts.items["pro.edgex.exchange"] = pybotters.auth.Item(
    "edgex", Auth.edgex
)


pybotters.auth.Hosts.items["quote.edgex.exchange"] = pybotters.auth.Item(
    "edgex", Auth.edgex
)

pybotters.auth.Hosts.items["uuapi.rerrkvifj.com"] = pybotters.auth.Item(
    "lbank", Auth.lbank
)

pybotters.auth.Hosts.items["api.coinw.com"] = pybotters.auth.Item(
    "coinw", Auth.coinw
)

pybotters.auth.Hosts.items["derivatives.bitmart.com"] = pybotters.auth.Item(
    "bitmart", Auth.bitmart
)

pybotters.auth.Hosts.items["api-cloud-v2.bitmart.com"] = pybotters.auth.Item(
    "bitmart_api", Auth.bitmart_api
)

pybotters.auth.Hosts.items["api.deepcoin.com"] = pybotters.auth.Item(
    "deepcoin", Auth.deepcoin
)
pybotters.auth.Hosts.items["www.deepcoin.com"] = pybotters.auth.Item(
    "deepcoin", Auth.deepcoin
)

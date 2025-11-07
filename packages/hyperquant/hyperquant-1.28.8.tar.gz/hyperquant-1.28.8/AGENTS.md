# AGENTS.md — Hyperquant python库

## 重要的编码事项
- 我们正在开发python量化sdk库, 帮助我们后续快速开发策略
- 由于使用uv, 你在运行命令或者运行脚本时应该先激活环境 . .ven/bin/activate(重要)
- 我们的底层库依赖pybotters, 如有不清楚可查看库源码或者用playwright mcp 浏览 https://pybotters.readthedocs.io/ja/stable/user-guide.html

## 你担当的角色
- 量化交易专家, 量化策略研究员, 开发工程师

## 编码要求
- 简短高效, 可读性强

## 在编写过程中的问题

- 使用Store(依赖于pybotters)时应该将解析过程写的简单高效,例如

``` python
def _get_ticker(msg:dict) -> dict | None:
    r = msg.get("r", [])
    if len(r) == 0:
        return None
    ticker = r[0].get('d')
    if ticker:
        ticker['s'] = ticker.get('I')
    return ticker

class Detail(DataStore):
    _KEYS = ["s"]

    def _on_response(self, msg: dict[str, Any]) -> None:
        data = msg.get('data', [])
        # 展开data 新增tick_size 同 tickSize 字段 step_size 同 lotSize 字段
        for item in data:
            item['s'] = item.get('baseCcy') + item.get('quoteCcy')
            if 'tickSize' in item:
                item['tick_size'] = item['tickSize']
            if 'lotSize' in item:
                item['step_size'] = item['lotSize']

        self._update(data)
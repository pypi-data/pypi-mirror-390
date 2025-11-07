def to_contracts(base_qty: float, ct_val: float) -> float:
    """把币数量转换为合约张数"""
    if ct_val <= 0:
        ct_val = 1
    return base_qty / ct_val

def to_base_qty(contracts: float, ct_val: float) -> float:
    """把合约张数转换为币数量"""
    if ct_val <= 0:
        ct_val = 1
    return contracts * ct_val

def to_quote_notional(contracts: float, ct_val: float, price: float) -> float:
    """计算名义价值（USDT）"""
    return contracts * ct_val * price

ct_val = 1
price = 0.095

contracts = to_contracts(1000, ct_val)
print(contracts)
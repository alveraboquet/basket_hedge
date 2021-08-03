import pandas as pd
from util import key, mdd

def calc_pos(data, coin, alloc, is_long=True):
    df = data[coin]
    if is_long:
        df['norm_return'] = df['close']/df.iloc[0]['close']
    else:
        df['norm_return'] = 2 - df['close']/df.iloc[0]['close']
    df['position'] = df['norm_return'] * alloc
    return df['position']
    
def parse_alloc(coins, alloc, alloc_list):
    return [alloc/len(coins)] * len(coins) if not alloc_list else [float(a) for a in alloc_list.split(",")]


def backtest(data, long_coins, short_coins, plot=False, allocate=0.5, 
        alloc_long=None, alloc_short=None):
    all_pos = {}
    index = data[long_coins[0]].opentime # time
    # money allocated to each symbol at first
    alloc1 = parse_alloc(long_coins, allocate, alloc_long)
    alloc2 = parse_alloc(short_coins, allocate, alloc_short)
    assert len(alloc1) == len(long_coins)
    assert len(alloc2) == len(short_coins)
    not_used_money = 1 - 2*allocate
    for coin, alloc in zip(long_coins, alloc1):
        all_pos[coin] = calc_pos(data, coin, alloc, True)
    for coin, alloc in zip(short_coins, alloc2):
        all_pos[coin] = calc_pos(data, coin, alloc, False)
    value = pd.DataFrame(all_pos)
    value.index = index
    value['total'] = value.sum(axis=1) + not_used_money
    value['daily_return'] = value['total'].pct_change(1)
    sharp = (365**0.5)*value['daily_return'].mean() / value['daily_return'].std()
    maxdd = mdd(value.total)
    k = f"long:[{key(long_coins)}],short:[{key(short_coins)}]"
    title = f"{k}, sharp: {sharp}, mdd:{maxdd}"
    if plot:
        import matplotlib.pyplot as plt
        plt.style.use('fivethirtyeight')
        value['total'].plot(figsize=(12,8), title=title)
        plt.show()
    return k, maxdd, sharp
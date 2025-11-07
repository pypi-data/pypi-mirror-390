import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mk') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
from mns_common.constant.price_enum import PriceEnum
import mk_common.component.qmt.qmt_real_time_api as qmt_real_time_api
import pandas as pd


# 委比=(委买手数－委卖手数)/(委买手数+委卖手数)×100%

def init_trade_price(symbol):
    stock_bid_ask_df = qmt_real_time_api.get_qmt_real_time_quotes([symbol])

    # 价格从大到小
    stock_bid_ask_df[['sell_1', 'sell_2', 'sell_3', 'sell_4', 'sell_5']] = (
        stock_bid_ask_df['askPrice']
        .apply(lambda x: sorted(x, reverse=False))
        .apply(pd.Series)  # 拆分
    )
    # 价格从大到小
    stock_bid_ask_df[['buy_1', 'buy_2', 'buy_3', 'buy_4', 'buy_5']] = (
        stock_bid_ask_df['bidPrice']
        .apply(lambda x: sorted(x, reverse=True))
        .apply(pd.Series)  # 拆分
    )

    stock_bid_ask_df[['sell_1_vol', 'sell_2_vol', 'sell_3_vol', 'sell_4_vol', 'sell_5_vol']] = (
        stock_bid_ask_df['askVol']
        .apply(pd.Series)  # 拆分
    )

    stock_bid_ask_df[['buy_1_vol', 'buy_2_vol', 'buy_3_vol', 'buy_4_vol', 'buy_5_vol']] = (
        stock_bid_ask_df['bidVol']
        .apply(pd.Series)  # 拆分
    )

    stock_bid_ask_df["wei_bi"] = round(100 * (
            (stock_bid_ask_df["buy_1_vol"] + stock_bid_ask_df["buy_2_vol"] + stock_bid_ask_df["buy_3_vol"] +
             stock_bid_ask_df[
                 "buy_4_vol"] + stock_bid_ask_df["buy_5_vol"]) - (
                    stock_bid_ask_df["sell_1_vol"] + stock_bid_ask_df["sell_2_vol"] + stock_bid_ask_df["sell_3_vol"] +
                    stock_bid_ask_df[
                        "sell_4_vol"] + stock_bid_ask_df["sell_5_vol"])) / (
                                               (stock_bid_ask_df["buy_1_vol"] + stock_bid_ask_df["buy_2_vol"] +
                                                stock_bid_ask_df["buy_3_vol"] +
                                                stock_bid_ask_df[
                                                    "buy_4_vol"] + stock_bid_ask_df["buy_5_vol"]) + (
                                                       stock_bid_ask_df["sell_1_vol"] + stock_bid_ask_df["sell_2_vol"] +
                                                       stock_bid_ask_df["sell_3_vol"] +
                                                       stock_bid_ask_df[
                                                           "sell_4_vol"] + stock_bid_ask_df["sell_5_vol"])), 0)

    return stock_bid_ask_df


def get_qmt_trade_price(symbol, price_code, limit_chg):
    stock_bid_ask_df = init_trade_price(symbol)
    wei_bi = list(stock_bid_ask_df['wei_bi'])[0]
    now_price = list(stock_bid_ask_df['lastPrice'])[0]
    if wei_bi == PriceEnum.ZT_WEI_BI.price_name:
        trade_price = list(stock_bid_ask_df['buy_1'])[0]
    elif wei_bi == PriceEnum.DT_WEI_BI.price_name:
        trade_price = list(stock_bid_ask_df['sell_1'])[0]
    elif price_code == PriceEnum.BUY_1.price_code:
        trade_price = list(stock_bid_ask_df['buy_1'])[0]
    elif price_code == PriceEnum.BUY_2.price_code:
        trade_price = list(stock_bid_ask_df['buy_2'])[0]
    elif price_code == PriceEnum.BUY_3.price_code:
        trade_price = list(stock_bid_ask_df['buy_3'])[0]
    elif price_code == PriceEnum.BUY_4.price_code:
        trade_price = list(stock_bid_ask_df['buy_4'])[0]
    elif price_code == PriceEnum.BUY_5.price_code:
        trade_price = list(stock_bid_ask_df['buy_5'])[0]

    elif price_code == PriceEnum.SELL_1.price_code:
        trade_price = list(stock_bid_ask_df['sell_1'])[0]
    elif price_code == PriceEnum.SELL_2.price_code:
        trade_price = list(stock_bid_ask_df['sell_2'])[0]
    elif price_code == PriceEnum.SELL_3.price_code:
        trade_price = list(stock_bid_ask_df['sell_3'])[0]
    elif price_code == PriceEnum.SELL_4.price_code:
        trade_price = list(stock_bid_ask_df['sell_4'])[0]
    elif price_code == PriceEnum.SELL_5.price_code:
        trade_price = list(stock_bid_ask_df['sell_5'])[0]

    elif price_code == PriceEnum.BUY_PRICE_LIMIT.price_code:
        trade_price = round(now_price * (1 + limit_chg), 2)
    elif price_code == PriceEnum.SEll_PRICE_LIMIT.price_code:
        trade_price = round(now_price * (1 - limit_chg), 2)

    elif price_code == PriceEnum.ZT_PRICE.price_code:
        trade_price = list(stock_bid_ask_df['buy_1'])[0]

    elif price_code == PriceEnum.DT_PRICE.price_code:
        trade_price = list(stock_bid_ask_df['sell_1'])[0]
    else:
        trade_price = list(stock_bid_ask_df['lastPrice'])[0]

    trade_price = round(trade_price, 2)
    return trade_price


if __name__ == '__main__':
    while True:
        price = get_qmt_trade_price('300085.SZ', PriceEnum.BUY_5.price_code, 0.02)
        print(price)

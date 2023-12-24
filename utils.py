import asyncio
import sqlite3 as sql
import yfinance as yf
import uuid
import pandas as pd


def addtransaction(filepath, connection):
    cur = connection.cursor()
    df = pd.read_csv(filepath)
    df.to_sql('trades', connection, if_exists='append')
    # cur.execute("CREATE TABLE IF NOT EXISTS stocks (symbol TEXT, price FLOAT, quantity INTEGER, date TEXT)")
    # with open("trades.csv", "w") as f:
    #     pass
    connection.commit()


def calc_positions(connection):
    long = 'LONG'
    short = 'SHORT'
    buy = 'BUY'
    sell = 'SELL'
    positions_df = pd.DataFrame(columns=['Ticker', 'Quantity_Held', 'Average_Price', 'Position_Type'])
    df = pd.read_sql("SELECT * FROM trades", connection)

    for i in list(df['Ticker'].unique()):
        if '/' in i:
            continue
        quantity = 0
        price_of_position = 0
        avreage_price = 0
        position_type = ''
        tickerdf = df[df['Ticker'] == i].sort_values(by='Date')
        for index, row in tickerdf.iterrows():
            if row['Type'] == long:
                if row['Action'] == buy:
                    position_type = long
                    quantity += row['Quantity']
                    price_of_position += row['Price'] * row['Quantity']
                    avreage_price = price_of_position / quantity
                elif row['Action'] == sell:
                    quantity -= row['Quantity']
                    price_of_position -= avreage_price * row['Quantity']
            elif row['Type'] == short:
                if row['Action'] == buy:
                    position_type = short
                    quantity -= row['Quantity']
                    price_of_position -= avreage_price * row['Quantity']
                elif row['Action'] == sell:
                    quantity += row['Quantity']
                    price_of_position += row['Price'] * row['Quantity']
                    avreage_price = price_of_position / quantity
        if quantity != 0:
            positions_df = positions_df._append({'Ticker': i, 'Quantity_Held': quantity, 'Average_Price': avreage_price,
                                                'Position_Type': position_type}, ignore_index=True)
        print(f"{i}: {quantity} @ {avreage_price} ({position_type})")
    return positions_df


def get_unrealized_pnl(ticker, quantity, avg_price):
    ticker = yf.Ticker(ticker)
    current_price = ticker.basic_info['last_price']
    return round((current_price - avg_price) * quantity, 2)


def startasyncloop(asyncfunc):
    asyncio.run(asyncfunc)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import asyncio
import os
import sqlite3 as sql
import yfinance as yf
import uuid
import pandas as pd
from datetime import datetime


# def addtransaction(filepath, connection):
#     cur = connection.cursor()
#     df = pd.read_csv(filepath)
#     df.to_sql('trades', connection, if_exists='append')
#     # cur.execute("CREATE TABLE IF NOT EXISTS stocks (symbol TEXT, price FLOAT, quantity INTEGER, date TEXT)")
#     # with open("trades.csv", "w") as f:
#     #     pass
#     connection.commit()


def get_and_save_ticker_history(ticker, start_date, avg_price, connection):
    # Check if the ticker history already exists in the database
    cursor = connection.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{ticker}';")
    result = cursor.fetchone()

    if result is not None:
        # The ticker history exists in the database
        # Find the most recent date in the database for this ticker
        df = pd.read_sql(f"SELECT * FROM {ticker} ORDER BY Date", connection)
        most_recent_date = df['Date']
        df = df.set_index('Date')
        # df.index = df.index.str.split(" ", expand=True)[0]
        ticker_history = yf.download(ticker, start=most_recent_date, end=datetime.today().strftime('%Y-%m-%d'), interval='1d')
        ticker_history.index = pd.to_datetime(ticker_history.index)
        ticker_history = ticker_history.set_index(ticker_history.index.strftime('%Y-%m-%d'))
        if ticker_history.empty:
            # No new data was downloaded
            return df
        elif ticker_history.index[0] == most_recent_date:
            # The most recent date in the database is the same as the first date in the new data
            # This means that the data is already up to date
            return df
        df_ticker_history = pd.concat([ticker_history, df])
    else:
        # The ticker history does not exist in the database
        # Download the ticker history from yfinance from the start date until today
        ticker_history = yf.download(ticker, start=start_date, end=datetime.today().strftime('%Y-%m-%d'), interval='1d')
        ticker_history = ticker_history.set_index(ticker_history.index.strftime('%Y-%m-%d'))
        df_ticker_history = ticker_history

    # Subtract the average price from the closing price
    ticker_history['Close'] = ticker_history['Close'] - avg_price

    # Save the resulting DataFrame to the database
    ticker_history.to_sql(ticker, connection, if_exists='append')

    return df_ticker_history


def check_table_exists(db_con, table_name):
    cursor = db_con.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    result = cursor.fetchone()
    return result is not None


def positiondb(connection, mode='R'):
    if mode not in ['R', 'W']:
        print("mode must be 'R' or 'W'")
        return
    mode = mode.upper()

    match mode:
        case 'R':
            df = pd.read_sql("SELECT * FROM positions", connection)
            return df
        case 'W':
            from colorama import Fore
            df = asyncio.run(calc_positions(connection))
            df.to_sql('positions', connection, if_exists='replace')
            print(Fore.GREEN + "positions table updated")


def get_transaction(connection):
    df = pd.read_sql("SELECT * FROM trades", connection)
    return df


def add_transaction(connection, ticker, price, quantity, date, action, type):
    df = pd.read_sql("SELECT * FROM trades", connection)
    df = df._append(
        {'Ticker': ticker, 'Price': price, 'Quantity': quantity, 'Date': date, 'Action': action, 'Type': type})
    df.to_sql('trades', connection, if_exists='replace')


async def calc_positions(connection):
    long = 'LONG'
    short = 'SHORT'
    buy = 'BUY'
    sell = 'SELL'
    positions_df = pd.DataFrame(columns=['Ticker', 'Quantity_Held', 'Average_Price', 'Position_Type', 'Start_Date'])
    df = pd.read_sql("SELECT * FROM trades", connection)

    for i in list(df['Ticker'].unique()):
        if '/' in i:
            continue
        quantity = 0
        price_of_position = 0
        avreage_price = 0
        position_type = ''
        startdate = None
        tickerdf = df[df['Ticker'] == i].sort_values(by='Date')
        for index, row in tickerdf.iterrows():
            if quantity == 0:
                startdate = row['Date'].split(' ')[0]

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

            if quantity == 0:
                startdate = None

        positions_df = positions_df._append(
            {
                'Ticker': i, 'Quantity_Held': quantity, 'Average_Price': avreage_price, 'Position_Type': position_type,
                'Start_Date': startdate
            },
            ignore_index=True
        )

        print(f"{i}: {quantity} @ {avreage_price} ({position_type})")
    positions_df.to_sql('positions', connection, if_exists='replace')
    return positions_df


async def get_current_prices(tickers):
    start = time.time()
    if '_' in tickers:
        raise ValueError("please remove the example trade from the trades table")
    tickers_yfstring = ' '.join(tickers)

    loop = asyncio.get_event_loop()
    yfdata = await loop.run_in_executor(None, yf.Tickers, tickers_yfstring)
    yftickers = yfdata.tickers
    current_prices_dict = {key: value.basic_info.last_price for key, value in yftickers.items()}
    end = time.time()
    print(f"get_current_prices took {end - start} seconds")
    return current_prices_dict


def create_example_trades():
    df = pd.DataFrame(columns=['Ticker', 'Price', 'Quantity', 'Date', 'Action', 'Type'])
    tablename = 'trades.xlsx'
    df = df._append({
        'Ticker': 'example_only',
        'Price': 100,
        'Quantity': 10,
        'Date': '2021-12-31',
        'Action': 'example("BUY"/"SELL")',
        'Type': 'example("LONG"/"SHORT")'
    }, ignore_index=True)
    df.to_excel(tablename, index=False)


def open_file_andwaitforsave(filepath):
    os.startfile(filepath)
    wait_for_file_save(filepath)
    return filepath


def edit_and_open_file(filepath):
    # os.startfile(filepath)
    from tkinter.filedialog import askopenfilename
    filename = askopenfilename(initialdir=os.getcwd())
    return filename


def startasyncloop(asyncfunc):
    asyncio.run(asyncfunc)


class MyFileHandler(FileSystemEventHandler):
    def __init__(self, filename):
        self.filename = filename
        self.file_saved = False
        self.file_closed = False

    def on_modified(self, event):
        if event.src_path == self.filename:
            self.file_saved = True
            print("File saved:", event.src_path)


def wait_for_file_save(file_path):
    observer = Observer()
    event_handler = MyFileHandler(file_path)
    observer.schedule(event_handler, path=file_path[:-12], recursive=False)
    observer.start()
    try:
        while not event_handler.file_saved and not event_handler.file_closed:
            time.sleep(1)
        observer.stop()
    except KeyboardInterrupt:
        observer.stop()
    except Exception as e:
        print(e)

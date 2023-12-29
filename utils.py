from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import asyncio
import os
import sqlite3 as sql
import yfinance as yf
import uuid
import pandas as pd


# def addtransaction(filepath, connection):
#     cur = connection.cursor()
#     df = pd.read_csv(filepath)
#     df.to_sql('trades', connection, if_exists='append')
#     # cur.execute("CREATE TABLE IF NOT EXISTS stocks (symbol TEXT, price FLOAT, quantity INTEGER, date TEXT)")
#     # with open("trades.csv", "w") as f:
#     #     pass
#     connection.commit()

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
    df = df._append({'Ticker': ticker, 'Price': price, 'Quantity': quantity, 'Date': date, 'Action': action, 'Type': type})
    df.to_sql('trades', connection, if_exists='replace')


async def calc_positions(connection):
    long = 'LONG'
    short = 'SHORT'
    buy = 'BUY'
    sell = 'SELL'
    positions_df = pd.DataFrame(columns=['Ticker', 'Quantity_Held', 'Average_Price', 'Position_Type'])
    df = pd.read_sql("SELECT * FROM trades", connection)
    #  add start date to each position in positions table

    for i in list(df['Ticker'].unique()):
        if '/' in i:
            continue
        quantity = 0
        price_of_position = 0
        avreage_price = 0
        position_type = ''
        tickerdf = df[df['Ticker'] == i].sort_values(by='Date')
        for index, row in tickerdf.iterrows():
            if index == 0:
                startdate = row['Date']

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
    positions_df.to_sql('positions', connection, if_exists='replace')
    return positions_df


def get_unrealized_pnl(ticker, quantity, avg_price):
    # todo: change this to call moltipule tickers at once format:"aapl msft tsla"
    if '_' in ticker:
        return avg_price * quantity
    ticker = yf.Ticker(ticker)
    current_price = ticker.basic_info['last_price']
    return round((current_price - avg_price) * quantity, 2)


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
    df.to_excel(tablename)


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

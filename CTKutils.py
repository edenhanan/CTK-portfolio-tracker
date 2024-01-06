import random
import asyncio
import threading
import numpy as np
import customtkinter as ctk
import pandas
import utils as ut
from pt_config import PtConfig as Tabs
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter, DayLocator


def addtransaction(
        # conection,
        entrydict: dict
):
    for key, i in entrydict.items():
        print(i.get())


def open_toplevel(self):
    self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed


class ToplevelWindow(ctk.CTkToplevel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.label = ctk.CTkLabel(self, text="ToplevelWindow")
        self.label.pack(padx=20, pady=20)


class Positionframe(ctk.CTkFrame):
    milisecond = 1000
    swidth = 60
    update_time = 10 * milisecond  # 10 seconds

    def __init__(self,
                 master,
                 positionsdata: pandas.DataFrame,
                 padx: int = 10,
                 # pady: int = 5,
                 connection=None,
                 border_width: int = 1):

        # self.pady = pady
        self.ax = None
        global index
        super().__init__(master, border_width=border_width)
        self.padx = padx
        self.positionsdata = positionsdata
        headers = list(self.positionsdata.columns)
        self.position_frames = {}
        self.position_history = {}
        ticker_labels = []
        quantity_labels = []
        avg_price_labels = []
        position_type_labels = []
        self.pnl_labels = []
        self.pnl_percentage_labels = []
        self.tickers_check_boxes = []
        date_labels = []
        self.first_time = True
        self.tickers = list(self.positionsdata.Ticker)
        self.current_prices = asyncio.run(ut.get_current_prices(self.tickers))
        self.quantity = list(self.positionsdata.Quantity_Held)
        self.avg_price = list(self.positionsdata.Average_Price)
        self.position_type = list(self.positionsdata.Position_Type)
        self.position_cost = np.array(self.quantity) * np.array(self.avg_price)
        self.start_date = list(self.positionsdata.Start_Date)
        extra_column = 2
        # Create a new frame for the graph

        # empty_label = ctk.CTkLabel(self, text="")
        # empty_label.grid(row=0, column=0, sticky="nsew", padx=self.padx, pady=5)
        for n, i in enumerate(Tabs.positions['headers']):
            label = ctk.CTkLabel(self, text=i)
            if "Date" in i:
                label.configure(width=15, font=("Arial", 6))
            else:
                label.configure(width=self.swidth)
            label.grid(row=0, column=(n + 1), sticky="nsew", padx=self.padx, pady=5)

        for index, row in self.positionsdata.iterrows():
            ticker_column = 0
            if row.Quantity_Held == 0:
                continue
            self.position_frames[row.Ticker] = ctk.CTkFrame(self)
            self.position_frames[row.Ticker].grid(row=index + 1, columnspan=(len(headers) + extra_column),
                                                  sticky="nsew")
            pnl = (self.current_prices[row.Ticker] - row.Average_Price) * row.Quantity_Held
            pnl_percentage = pnl / self.position_cost[index] * 100
            self.tickers_check_boxes.append(ctk.CTkCheckBox(self.position_frames[row.Ticker], text=row.Ticker,
                                                            width=self.swidth, onvalue=row.Ticker,
                                                            offvalue=None))
            self.tickers_check_boxes[index].grid(row=0, column=ticker_column, padx=(self.padx, 0), pady=5)
            ticker_column += 1
            # ticker_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=row.Ticker,
            #                                   width=self.swidth))
            # ticker_labels[index].grid(row=0, column=ticker_column, sticky="nsew", padx=self.padx, pady=5)
            # ticker_column += 1
            quantity_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=round(row.Quantity_Held, 2),
                                                width=self.swidth))
            quantity_labels[index].grid(row=0, column=ticker_column, sticky="nsew", padx=self.padx, pady=5)
            ticker_column += 1
            avg_price_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=row.Average_Price,
                                                 width=self.swidth))
            avg_price_labels[index].grid(row=0, column=ticker_column, sticky="nsew", padx=self.padx, pady=5)
            ticker_column += 1
            position_type_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=row.Position_Type,
                                                     width=self.swidth))
            position_type_labels[index].grid(row=0, column=ticker_column, sticky="nsew", padx=self.padx, pady=5)
            ticker_column += 1
            self.pnl_labels.append(
                ctk.CTkLabel(self.position_frames[row.Ticker], text=round(pnl, 2), width=self.swidth))
            self.pnl_labels[index].grid(row=0, column=ticker_column, sticky="nsew", padx=self.padx, pady=5)
            ticker_column += 1
            self.pnl_percentage_labels.append(
                ctk.CTkLabel(self.position_frames[row.Ticker], text=f"{round(pnl_percentage, 2)}%",
                             width=self.swidth))
            self.pnl_percentage_labels[index].grid(row=0, column=ticker_column, sticky="nsew", padx=self.padx, pady=5)
            ticker_column += 1
            date_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=row.Start_Date,
                                            width=self.swidth))
            date_labels[index].grid(row=0, column=ticker_column, sticky="nsew", padx=(self.padx + 10), pady=5)
            self.position_history[row.Ticker] = ut.get_and_save_ticker_history(row.Ticker, row.Start_Date,
                                                                               row.Average_Price, connection)
        history_frame = PositionHistoryFrame(self, self.position_history)
        history_frame.grid(row=(self.position_frames.__len__() + 2), column=0, columnspan=(len(headers) + extra_column),
                           sticky="nsew")
        asyncio.run(self.update_pos_frame())

    async def update_pos_frame(self):
        start = time.time()
        if self.first_time:
            self.first_time = False
            pass
        else:
            self.current_prices = await ut.get_current_prices(self.tickers)  # real code
        for index, row in self.positionsdata.iterrows():
            if row.Quantity_Held == 0:
                continue
            pnl = (self.current_prices[row.Ticker] - row.Average_Price) * row.Quantity_Held
            pnl = pnl * random.randint(-10, 10)  # test code
            pnl_percentage = pnl / self.position_cost[index] * 100
            self.pnl_labels[index].configure(text=round(pnl, 2))
            self.pnl_percentage_labels[index].configure(text=f"{round(pnl_percentage, 2)}%")
            if pnl > 0:
                self.pnl_labels[index].configure(text_color="green")
                self.pnl_percentage_labels[index].configure(text_color="green")
            elif pnl < 0:
                self.pnl_labels[index].configure(text_color="red")
                self.pnl_percentage_labels[index].configure(text_color="red")
            else:
                self.pnl_labels[index].configure(text_color="white")
                self.pnl_percentage_labels[index].configure(text_color="white")
        self.update_idletasks()
        end = time.time()
        print(f"update_pos_frame took {end - start} seconds")
        self.after(self.update_time,
                   lambda: threading.Thread(target=ut.startasyncloop, args=(self.update_pos_frame(),)).start())


class PositionHistoryFrame(ctk.CTkFrame):
    def __init__(self, master, position_history, **kwargs):
        super().__init__(master, **kwargs)

        if type(position_history) is not dict:
            raise TypeError("position_history must be a dictionary")
        else:
            for key, df in position_history.items():
                if type(df) is not pandas.DataFrame:
                    raise TypeError(f"position_history['{key}'] must be a pandas.DataFrame")
                elif df.empty:
                    raise ValueError(f"position_history['{key}'] must not be empty")
                elif 'Close' not in df.columns:
                    raise ValueError(f"position_history['{key}'] must have a 'Close' column")
        self.position_history = position_history

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

        self.plot_position_history()

    def plot_position_history(self):
        self.ax.clear()
        self.ax.grid(True)

        for key, value in self.position_history.items():
            self.ax.plot(self.position_history[key].index, value['Close'])
        self.ax.legend(self.position_history.keys())
        self.ax.set_title('Position History Close')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Close')

        # Add a zero dotted red line
        self.ax.axhline(0, color='red', linestyle='dotted')

        # Format the x-axis to display dates nicely
        self.ax.xaxis.set_major_locator(DayLocator(interval=7))  # set major ticks every 7 days
        self.ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))  # format dates as 'YYYY-MM-DD'
        self.fig.autofmt_xdate()  # auto-format the x-axis labels to fit nicely

        self.canvas.draw()

    def update_plot(self, new_position_history):
        self.position_history = new_position_history
        self.plot_position_history()


class Transactionframe(ctk.CTkFrame):
    milisecond = 1000
    swidth = 80
    update_time = 1 * milisecond  # 10 seconds

    def __init__(self,
                 master,
                 transactiondata: pandas.DataFrame,
                 con,
                 load_file_path: str = None,
                 # padx: int = 10,
                 # pady: int = 5,
                 border_width: int = 1):

        transactions_info = Tabs.Transactions
        super().__init__(master, border_width=border_width)
        headers = list(transactiondata.columns)
        tran_frame = ctk.CTkFrame(self)
        tran_frame.grid(row=0, column=0, sticky="nsew")
        addtrans_frame = ctk.CTkFrame(self)
        addtrans_frame.grid(row=1, columnspan=len(headers), sticky="nsew")
        for n, i in enumerate(headers):
            transactions_info['transactions labels'].append(
                ctk.CTkLabel(tran_frame, text=i, width=transactions_info['width']))
            transactions_info['transactions labels'][n].grid(row=0, column=n, sticky="nsew", padx=10, pady=5)
            if i != 'index':
                transactions_info['add_transaction'][i] = ctk.CTkEntry(addtrans_frame, placeholder_text=i,
                                                                       width=transactions_info['width'])
                transactions_info['add_transaction'][i].grid(row=0, column=n + 2, sticky="nsew", padx=10, pady=5)
        for index, row in transactiondata.iterrows():
            transactions_info['transactions frames'][row['Ticker']] = ctk.CTkFrame(tran_frame)
            transactions_info['transactions frames'][row['Ticker']].grid(row=index + 1,
                                                                         columnspan=len(list(transactiondata.columns)),
                                                                         sticky="nsew")
            for n, i in enumerate(row):
                label = ctk.CTkLabel(transactions_info['transactions frames'][row['Ticker']], text=i,
                                     width=transactions_info['width'])
                label.grid(row=0, column=n, sticky="nsew", padx=10, pady=5)
        addtans_button = ctk.CTkButton(addtrans_frame, width=20, text="Add",
                                       command=lambda: addtransaction(transactions_info['add_transaction']))
        addtans_button.grid(row=0, column=1, padx=5, pady=5)
        load_button = ctk.CTkButton(addtrans_frame, width=20, text="Load",
                                    command=lambda: ut.edit_and_open_file(load_file_path))
        load_button.grid(row=0, column=0, padx=5, pady=5)

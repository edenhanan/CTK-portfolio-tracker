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

        #     create a new frame under the ticker frame to show the pnl over time in a graph
        # self.graph_frame = ctk.CTkFrame(self)
        # self.graph_frame.grid(row=index + 2, columnspan=(len(headers) + 1), sticky="nsew")
        #
        # # Create a Figure for the graph
        # self.fig = plt.Figure(figsize=(5, 5), dpi=100)
        #
        # # Create an Axes for the graph
        # self.ax = self.fig.add_subplot(111)
        #
        # # Plot the PnL over time on the Axes
        # self.ax.plot(self.pnl_labels)
        #
        # # Create a FigureCanvasTkAgg for the Figure
        # self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        #
        # # Display the FigureCanvasTkAgg on the graph frame
        # self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

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

import random
import asyncio
import threading
import numpy as np
import customtkinter as ctk
import pandas
import utils as ut
from pt_config import PtConfig as Tabs


def addtransaction(conection, entrydict: dict):
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
    swidth = 80
    update_time = 60 * milisecond  # 10 seconds

    # for n, i in enumerate(Tabs.positions['headers']):
    #     label = customtkinter.CTkLabel(pos_frame, text=i)
    #     label.grid(row=0, column=n, sticky="nsew", padx=10, pady=5)
    # for index, row in dfpos.iterrows():
    #     positionlist[row.Ticker] = Ctku.Positionframe(pos_frame, row, index + 1)
    #     # positionlist.append(Ctku.Positionframe(pos_frame, row, index+1))
    #     positionlist[row.Ticker].grid(row=index + 1, columnspan=h_len, sticky="nsew")

    def __init__(self,
                 master,
                 positionsdata: pandas.DataFrame,
                 # positiondata: pandas.Series,
                 # row: int,
                 padx: int = 10,
                 pady: int = 5,
                 border_width: int = 1):

        super().__init__(master, border_width=border_width)
        headers = list(positionsdata.columns)
        # self.tickers = positionsdata.
        self.position_frames = {}
        ticker_labels = []
        quantity_labels = []
        avg_price_labels = []
        position_type_labels = []
        pnl_labels = []
        pnl_percentage_labels = []
        date_labels = []

        self.tickers = list(positionsdata.Ticker)
        self.current_prices = ut.get_current_prices(self.tickers)
        self.quantity = list(positionsdata.Quantity_Held)
        self.avg_price = list(positionsdata.Average_Price)
        self.position_type = list(positionsdata.Position_Type)
        self.position_cost = np.array(self.quantity) * np.array(self.avg_price)

        # self.quantity = positiondata.Quantity_Held
        # self.avg_price = positiondata.Average_Price
        # self.position_type = positiondata.Position_Type
        # self.position_cost = self.quantity * self.avg_price
        for n, i in enumerate(Tabs.positions['headers']):
            label = ctk.CTkLabel(self, text=i)
            label.grid(row=0, column=n, sticky="nsew", padx=10, pady=5)
        for index, row in positionsdata.iterrows():
            self.position_frames[row.Ticker] = ctk.CTkFrame(self)
            self.position_frames[row.Ticker].grid(row=index + 1, columnspan=len(headers), sticky="nsew")
            pnl = (self.current_prices[row.Ticker] - row.Average_Price) * row.Quantity_Held
            pnl_percentage = pnl / self.position_cost[index] * 100
            ticker_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=row.Ticker,
                                              width=self.swidth))
            ticker_labels[index].grid(row=index, column=0, sticky="nsew", padx=10, pady=5)
            quantity_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=round(row.Quantity_Held, 2),
                                                width=self.swidth))
            quantity_labels[index].grid(row=index, column=1, sticky="nsew", padx=10, pady=5)
            avg_price_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=row.Average_Price,
                                                 width=self.swidth))
            avg_price_labels[index].grid(row=index, column=2, sticky="nsew", padx=10, pady=5)
            position_type_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=row.Position_Type,
                                                     width=self.swidth))
            position_type_labels[index].grid(row=index, column=3, sticky="nsew", padx=10, pady=5)
            pnl_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=round(pnl, 2), width=self.swidth))
            pnl_labels[index].grid(row=index, column=4, sticky="nsew", padx=10, pady=5)
            pnl_percentage_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text=round(pnl_percentage, 2),
                                                      width=self.swidth))
            pnl_percentage_labels[index].grid(row=index, column=5, sticky="nsew", padx=10, pady=5)
            date_labels.append(ctk.CTkLabel(self.position_frames[row.Ticker], text="dd/mm/yyyy",
                                            width=self.swidth))
            date_labels[index].grid(row=index, column=6, sticky="nsew", padx=10, pady=5)
            # for n, i in enumerate(row):
            #     label = ctk.CTkLabel(self.position_frames[row.Ticker], text=i, width=self.swidth)
            #     label.grid(row=0, column=n, sticky="nsew", padx=10, pady=5)

        # asyncio.run(self.update_pos_frame())
        # self.ticker_label = ctk.CTkLabel(self, text=self.tickers, width=self.swidth)
        # self.ticker_label.grid(row=row, column=0, sticky="nsew", padx=padx, pady=pady)
        # self.quantity_label = ctk.CTkLabel(self, text=self.quantity, width=self.swidth)
        # self.quantity_label.grid(row=row, column=1, sticky="nsew", padx=padx, pady=pady)
        # self.avg_price_label = ctk.CTkLabel(self, text=round(self.avg_price, 2), width=self.swidth)
        # self.avg_price_label.grid(row=row, column=2, sticky="nsew", padx=padx, pady=pady)
        # self.position_type_label = ctk.CTkLabel(self, text=self.position_type, width=self.swidth)
        # self.position_type_label.grid(row=row, column=3, sticky="nsew", padx=padx, pady=pady)
        # self.pnl_label = ctk.CTkLabel(self, text=ut.get_unrealized_pnl(self.tickers, self.quantity, self.avg_price),
        #                               width=self.swidth)
        # self.pnl_label.grid(row=row, column=4, sticky="nsew", padx=padx, pady=pady)
        # self.pnl_percentage_label = ctk.CTkLabel(self, text="0.00%", width=self.swidth)
        # self.pnl_percentage_label.grid(row=row, column=5, sticky="nsew", padx=padx, pady=pady)
        # self.date_label = ctk.CTkLabel(self, text="dd/mm/yyyy", width=self.swidth)
        # self.date_label.grid(row=row, column=6, sticky="nsew", padx=padx, pady=pady)

    async def update_pos_frame(self):
        # test code 2 lines below
        # r_random = random.randint(-10, 10)
        # un_pnl = ut.get_unrealized_pnl(self.ticker, self.quantity, self.avg_price) * r_random
        # real code
        un_pnl = ut.get_current_prices(self.tickers, self.quantity, self.avg_price)  # real code
        self.pnl_percentage_label.configure(text=f'{round(un_pnl / self.position_cost * 100, 2)}%')
        self.pnl_label.configure(text=f'$ {round(un_pnl, 2)}')
        if un_pnl > 0:
            self.pnl_label.configure(text_color="green")
            self.pnl_percentage_label.configure(text_color="green")
        elif un_pnl < 0:
            self.pnl_label.configure(text_color="red")
            self.pnl_percentage_label.configure(text_color="red")
        else:
            self.pnl_label.configure(text_color="white")
            self.pnl_percentage_label.configure(text_color="white")
        self.update_idletasks()
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
                 padx: int = 10,
                 pady: int = 5,
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
                                       command=lambda: addtransaction(con, transactions_info[
                                           'add_transaction']))
        addtans_button.grid(row=0, column=1, padx=5, pady=5)
        load_button = ctk.CTkButton(addtrans_frame, width=20, text="Load",
                                    command=lambda: ut.edit_and_open_file(load_file_path))
        load_button.grid(row=0, column=0, padx=5, pady=5)

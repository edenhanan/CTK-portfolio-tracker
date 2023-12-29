import random
import asyncio
import threading

import customtkinter as ctk
import pandas
import utils as ut


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

    def __init__(self,
                 master,
                 positiondata: pandas.Series,
                 row: int,
                 padx: int = 10,
                 pady: int = 5,
                 border_width: int = 1):

        super().__init__(master, border_width=border_width)
        self.ticker = positiondata.Ticker
        self.quantity = positiondata.Quantity_Held
        self.avg_price = positiondata.Average_Price
        self.position_type = positiondata.Position_Type
        self.position_cost = self.quantity * self.avg_price

        self.ticker_label = ctk.CTkLabel(self, text=self.ticker, width=self.swidth)
        self.ticker_label.grid(row=row, column=0, sticky="nsew", padx=padx, pady=pady)
        self.quantity_label = ctk.CTkLabel(self, text=self.quantity, width=self.swidth)
        self.quantity_label.grid(row=row, column=1, sticky="nsew", padx=padx, pady=pady)
        self.avg_price_label = ctk.CTkLabel(self, text=round(self.avg_price, 2), width=self.swidth)
        self.avg_price_label.grid(row=row, column=2, sticky="nsew", padx=padx, pady=pady)
        self.position_type_label = ctk.CTkLabel(self, text=self.position_type, width=self.swidth)
        self.position_type_label.grid(row=row, column=3, sticky="nsew", padx=padx, pady=pady)
        self.pnl_label = ctk.CTkLabel(self, text=ut.get_unrealized_pnl(self.ticker, self.quantity, self.avg_price),
                                      width=self.swidth)
        self.pnl_label.grid(row=row, column=4, sticky="nsew", padx=padx, pady=pady)
        self.pnl_percentage_label = ctk.CTkLabel(self, text="0.00%", width=self.swidth)
        self.pnl_percentage_label.grid(row=row, column=5, sticky="nsew", padx=padx, pady=pady)
        self.date_label = ctk.CTkLabel(self, text="dd/mm/yyyy", width=self.swidth)
        self.date_label.grid(row=row, column=6, sticky="nsew", padx=padx, pady=pady)
        asyncio.run(self.update_pos_frame())

    async def update_pos_frame(self):
        # test code 2 lines below
        # r_random = random.randint(-10, 10)
        # un_pnl = ut.get_unrealized_pnl(self.ticker, self.quantity, self.avg_price) * r_random
        # real code
        un_pnl = ut.get_unrealized_pnl(self.ticker, self.quantity, self.avg_price) # real code
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

        from main import tabs

        transactions_info = tabs['Transactions']
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
        load_button = ctk.CTkButton(addtrans_frame, width=20, text="Load", command=lambda: ut.edit_and_open_file(load_file_path))
        load_button.grid(row=0, column=0, padx=5, pady=5)

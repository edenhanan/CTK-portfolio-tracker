import random
import asyncio
import threading

import customtkinter as ctk
import pandas
import utils as ut


class Positionframe(ctk.CTkFrame):
    milisecond = 1000
    swidth = 80
    update_time = 1 * milisecond  # 10 seconds

    def __init__(
            self, master,
            positiondata: pandas.Series, row: int,
            padx: int = 10, pady: int = 5,
            border_width: int = 1):

        super().__init__(master, border_width=border_width)
        self.ticker = positiondata.Ticker
        self.quantity = positiondata.Quantity_Held
        self.avg_price = positiondata.Average_Price
        self.position_type = positiondata.Position_Type
        self.position_cost = self.quantity * self.avg_price

        self.ticker_label = ctk.CTkLabel(self, text=self.ticker, width=self.swidth)
        self.ticker_label.grid(row=row,  column=0, sticky="nsew", padx=padx, pady=pady)
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
        r_random = random.randint(-10, 10)
        un_pnl = ut.get_unrealized_pnl(self.ticker, self.quantity, self.avg_price) * r_random
        # real code
        # un_pnl = ut.get_unrealized_pnl(self.ticker, self.quantity, self.avg_price) # real code
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
        self.after(self.update_time, lambda: threading.Thread(target=ut.startasyncloop, args=(self.update_pos_frame(),)).start())





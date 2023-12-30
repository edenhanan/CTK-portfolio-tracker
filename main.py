import os
import sqlite3 as sql

import pandas as pd

import utils as ut
import customtkinter
import CTKutils as Ctku
import asyncio
from pt_config import PtConfig as Tabs

con = sql.connect(r"C:\Users\edenh\PycharmProjects\CTK-portfolio-tracker\test.db")
root = customtkinter.CTk()
tablelist = ['trades', 'positions']
for i in tablelist:
    if ut.check_table_exists(con, i):
        print(f"{i} table exists")
    else:
        match i:
            case 'positions':
                asyncio.run(ut.calc_positions(con))
            case 'trades':
                # todo: add the trades to the database
                excel_path = os.getcwd()+'\\trades.xlsx'
                ut.create_example_trades()
                ut.open_file_andwaitforsave(excel_path)
                df = pd.read_excel(excel_path)
                if df.empty:
                    print("no trades added")
                    break
                else:
                    df.to_sql('trades', con, if_exists='replace')
df_trans = ut.get_transaction(con)
dfpos = ut.positiondb(con)

root.title("Portfolio Tracker")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
tabview = customtkinter.CTkTabview(root)
tabview.grid(row=1, column=0, sticky="nsew")
tabview.add(Tabs.Transactions['name'])
tabview.add(Tabs.positions['name'])
# pos_frame = customtkinter.CTkFrame(tabview.tab("positions"))
# pos_frame.grid(row=0, column=0, sticky="nsew")
tran_frame = Ctku.Transactionframe(tabview.tab("Transactions"), df_trans, con)
tran_frame.grid(row=0, column=0, sticky="nsew")

positionlist = Tabs.positions['positionlist']
h_len = len(Tabs.positions['headers'])
pos_frame = Ctku.Positionframe(tabview.tab('positions'), dfpos)
pos_frame.grid(row=0, column=0, sticky="nsew")
# for n, i in enumerate(Tabs.positions['headers']):
#     label = customtkinter.CTkLabel(pos_frame, text=i)
#     label.grid(row=0, column=n, sticky="nsew", padx=10, pady=5)
# for index, row in dfpos.iterrows():
#     positionlist[row.Ticker] = Ctku.Positionframe(pos_frame, row, index + 1)
#     # positionlist.append(Ctku.Positionframe(pos_frame, row, index+1))
#     positionlist[row.Ticker].grid(row=index+1, columnspan=h_len, sticky="nsew")
root.mainloop()

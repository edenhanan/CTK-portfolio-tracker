import os
import sqlite3 as sql
import pandas as pd
import time
import utils as ut
import customtkinter
import CTKutils as Ctku
import asyncio
from pt_config import PtConfig as Tabs
start = time.time()
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
                excel_path = os.getcwd()+'\\trades.xlsx'
                ut.create_example_trades()
                ut.open_file_andwaitforsave(excel_path)
                df = pd.read_excel(excel_path)
                if df.empty:
                    print("no trades added")
                    break
                else:
                    df['Ticker'] = df['Ticker'].str.upper()
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
tran_frame = Ctku.Transactionframe(tabview.tab("Transactions"), df_trans, con)
tran_frame.grid(row=0, column=0, sticky="nsew")

positionlist = Tabs.positions['positionlist']
h_len = len(Tabs.positions['headers'])
pos_frame = Ctku.Positionframe(tabview.tab('positions'), dfpos, connection=con)
pos_frame.grid(row=0, column=0, sticky="nsew")
end = time.time()
print(f"main took {end - start} seconds")
root.mainloop()

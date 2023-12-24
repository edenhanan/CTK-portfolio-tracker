import sqlite3 as sql
import pandas as pd
import utils as ut
import customtkinter
import CTKutils as Ctku


con = sql.connect(r"C:\Users\edenh\PycharmProjects\CTK-portfolio-tracker\test.db")
# ut.addtransaction("trades.csv", con)
dfpos = ut.calc_positions(con)

root = customtkinter.CTk()
root.title("Portfolio Tracker")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
frame = customtkinter.CTkFrame(root)
frame.grid(row=0, column=0, sticky="nsew")
positionlist = []
headers = ['Ticker', 'Qt', 'Avg Price', 'Pos Type', 'PnL', 'PnL %', 'date']
for n, i in enumerate(headers):
    label = customtkinter.CTkLabel(frame, text=i)
    label.grid(row=0, column=n, sticky="nsew", padx=10, pady=5)
for index, row in dfpos.iterrows():
    positionlist.append(Ctku.Positionframe(frame, row, index+1))
    positionlist[index].grid(row=index+1, columnspan=len(headers), sticky="nsew")
root.mainloop()

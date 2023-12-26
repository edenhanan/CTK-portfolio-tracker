import sqlite3 as sql
import utils as ut
import customtkinter
import CTKutils as Ctku
import asyncio


con = sql.connect(r"C:\Users\edenh\PycharmProjects\CTK-portfolio-tracker\test.db")
# ut.addtransaction("trades.csv", con)
dfpos = asyncio.run(ut.calc_positions(con))
df_trans = ut.get_transaction(con)
tabs = {
    "positions": {
        'headers': ['Ticker', 'Qt', 'Avg Price', 'Pos Type', 'PnL', 'PnL %', 'date'],
        'name': 'positions',
        'positionlist': {}
    },
    "Transactions": {
        'name': 'Transactions',
        'transactions frames': {},
        'width': 50,
        'transactions labels': [],
        'add_transaction': {}

    }
}

root = customtkinter.CTk()
root.title("Portfolio Tracker")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
tabview = customtkinter.CTkTabview(root)
tabview.grid(row=1, column=0, sticky="nsew")
tabview.add(tabs['positions']['name'])
tabview.add(tabs['Transactions']['name'])
pos_frame = customtkinter.CTkFrame(tabview.tab("positions"))
pos_frame.grid(row=0, column=0, sticky="nsew")
tran_frame = Ctku.Transactionframe(tabview.tab("Transactions"), df_trans, con)
tran_frame.grid(row=0, column=0, sticky="nsew")

positionlist = tabs['positions']['positionlist']
h_len = len(tabs['positions']['headers'])
for n, i in enumerate(tabs['positions']['headers']):
    label = customtkinter.CTkLabel(pos_frame, text=i)
    label.grid(row=0, column=n, sticky="nsew", padx=10, pady=5)
for index, row in dfpos.iterrows():
    positionlist[row.Ticker] = Ctku.Positionframe(pos_frame, row, index + 1)
    # positionlist.append(Ctku.Positionframe(pos_frame, row, index+1))
    positionlist[row.Ticker].grid(row=index+1, columnspan=h_len, sticky="nsew")
root.mainloop()

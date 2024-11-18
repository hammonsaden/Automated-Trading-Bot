import sqlite3
import requests
import customtkinter as ctk
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import bcrypt
from datetime import datetime
import finnhub
import threading

class TraderBot:
    def __init__(self):
        self.trade_allowed = True
        self.API_KEY = 'co7coipr01qgik2h3bt0co7coipr01qgik2h3btg'
        self.finnhub = finnhub.Client(api_key=self.API_KEY)

    # UNTESTED FOR ACTIVE VALUES!!!
    def update_portval(self, conn, finnhub):
        print("Updating Portfolio Value!")
        cur = conn.cursor()
        cur.execute("SELECT ticker, amount FROM portfolio_stocks")
        rows = cur.fetchall()
        stock_vals = []
        for val in rows:
            if val[0] == "MONEY":
                stock_val = 1.00 * val[1]
                stock_vals.append(stock_val)

            else:
                data = finnhub.quote(str(val[0]))
                data_list = list(data.values())
            
                stock_val = float(data_list[1]) * val[1]

                stock_vals.append(float(stock_val))
        
            total = sum(stock_vals)

            # Updating the Table with New Portfolio Value
            cur_datetime = datetime.now()
            form_dt = cur_datetime.strftime('%H:%M:%S')
            cur.execute("INSERT INTO portfolio (datetime, value) VALUES (?, ?)", (form_dt, total))

            conn.commit()
            # Setting Timer for the Next Call of This Function
            threading.Timer(600, lambda: self.update_portval(conn, finnhub)).start()


    def update_watchlist(self, conn, finnhub, watchlist_bool):
        print("Timer Up! Updating Watchlist Values!")
        cur = conn.cursor()
        cur.execute("SELECT ticker, last_price, amount_owned, approx_value FROM watchlist")
        rows = cur.fetchall()
        num = 0
        for val in rows:
            if val[0] == "MONEY":
                pass
            else:
                data = finnhub.quote(str(val[0]))
                data_list = list(data.values())
            
                # Selecting Amount Owned from Portfolio_stocks table
                cur.execute("SELECT amount FROM portfolio_stocks WHERE ticker = ?", (val[0],))
                amount_owned = cur.fetchone()
                cur_datetime = datetime.now()
                form_dt = cur_datetime.strftime('%H:%M:%S')

                # Putting some Data into the price history
                cur.execute("INSERT INTO price_history (datetime, ticker, price) VALUES (?, ?, ?)", (form_dt, val[0], data_list[0]))
                print("UPDATING PRICE HISTORY AND UPLOADING TO DATABASE!")
                conn.commit()
                if amount_owned:
                    approx_val = amount_owned * float(data_list[0])
                    # Updating Watchlist
                    cur.execute("UPDATE watchlist SET last_price = ?, amount_owned = ?, approx_value = ? WHERE ticker = ?", (data_list[0], amount_owned, approx_val, val[0]))
                    conn.commit()
                else:
                    cur.execute("UPDATE watchlist SET last_price = ?, amount_owned = ?, approx_value = ? WHERE ticker = ?", (data_list[0], 0, 0, val[0]))
                    conn.commit()
                num +=1
                print(f"Watchlist Entry {num} Updated Successfully!")

        # Setting Watchlist Old Bool to True
        watchlist_bool[0] = True  
        # Start Timer Function
        threading.Timer(120, lambda: self.update_watchlist(conn, finnhub, watchlist_bool)).start()
        print("Timer set for 2 minutes!")

    def make_buy(self, conn, ticker, avg_buy_price, amount_to_buy):
        cur = conn.cursor()
    
        # Check available money
        cur.execute("SELECT amount FROM portfolio_stocks WHERE ticker = 'MONEY'")
        money_row = cur.fetchone()
        available_money = money_row[0] if money_row else 0

        # Calculate total cost
        total_cost = avg_buy_price * amount_to_buy

        if available_money >= total_cost:
            # Update portfolio stocks table with new stock or add to existing amount
            cur.execute("SELECT amount FROM portfolio_stocks WHERE ticker = ?", (ticker,))
            stock_row = cur.fetchone()
        
            if stock_row:
                new_amount = stock_row[0] + amount_to_buy
                cur.execute("UPDATE portfolio_stocks SET amount = ? WHERE ticker = ?", (new_amount, ticker))
            else:
                cur.execute("INSERT INTO portfolio_stocks (ticker, amount) VALUES (?, ?)", (ticker, amount_to_buy))

            # Deduct from MONEY in portfolio
            new_money_balance = available_money - total_cost
            cur.execute("UPDATE portfolio_stocks SET amount = ? WHERE ticker = 'MONEY'", (new_money_balance,))

            # Add transaction to trades table
            cur.execute(
                "INSERT INTO trades (datetime, ticker, price, amount, value) VALUES (datetime('now'), ?, ?, ?, ?)",
                (ticker, avg_buy_price, amount_to_buy, total_cost)
            )
        
            conn.commit()
            print(f"Bought {amount_to_buy} of {ticker} at {avg_buy_price} per unit. Total cost: {total_cost}")
        else:
            print("Insufficient funds for purchase.")

    def make_sale(self, conn, ticker, avg_sell_price, amount_to_sell):
        cur = conn.cursor()
    
        # Check if user has enough of the stock to sell
        cur.execute("SELECT amount FROM portfolio_stocks WHERE ticker = ?", (ticker,))
        stock_row = cur.fetchone()
        available_amount = stock_row[0] if stock_row else 0

        if available_amount >= amount_to_sell:
            # Calculate sale value
            sale_value = avg_sell_price * amount_to_sell

            # Deduct from stock amount in portfolio
            new_amount = available_amount - amount_to_sell
            if new_amount > 0:
                cur.execute("UPDATE portfolio_stocks SET amount = ? WHERE ticker = ?", (new_amount, ticker))
            else:
                cur.execute("DELETE FROM portfolio_stocks WHERE ticker = ?", (ticker,))

            # Add sale proceeds to MONEY
            cur.execute("SELECT amount FROM portfolio_stocks WHERE ticker = 'MONEY'")
            money_row = cur.fetchone()
            current_money = money_row[0] if money_row else 0
            new_money_balance = current_money + sale_value
            cur.execute("UPDATE portfolio_stocks SET amount = ? WHERE ticker = 'MONEY'", (new_money_balance,))

            # Add transaction to trades table
            cur.execute(
                "INSERT INTO trades (datetime, ticker, price, amount, value) VALUES (datetime('now'), ?, ?, ?, ?)",
                (ticker, avg_sell_price, -amount_to_sell, sale_value)  # Negative amount for sale
            )

            conn.commit()
            print(f"Sold {amount_to_sell} of {ticker} at {avg_sell_price} per unit. Total proceeds: {sale_value}")
        else:
            print("Insufficient stock to sell.")

    def eval_stock(self, conn):
        '''Here is the most important method of the whole program imo, here the bot will evaluate all of the prices and the data that it is being given
        and make the decision for the bot to buy or sell 
        '''
        if self.trade_allowed == True:
            # 3 dicts to compare eachother against
            average_prices = {}
            avg_trade_prices = {}
            cur_prices = {}

            cur = conn.cursor()

            # Start of the average price history section
            cur.execute("SELECT ticker FROM watchlist")
            watchlist = [row[0] for row in cur.fetchall()]

            if watchlist:
                cur.execute("SELECT * FROM price_history WHERE ticker IN ({})".format(','.join(["?"] * len(watchlist))), watchlist)
                price_history = cur.fetchall()

                ticker_data = {ticker: [] for ticker in watchlist}

                for val in price_history:
                    ticker = val[1]
                    price = val[2]

                    if ticker == "MONEY":
                        continue
                    if ticker in ticker_data:
                        ticker_data[ticker].append(price)

                for ticker, prices in ticker_data.items():
                    if prices:
                        average_prices[ticker] = sum(prices) / len(prices)

            else:
                print("No Values in Watchlist!")
 
            # Start of the average trade history price section
            
            cur.execute("SELECT ticker FROM trades")
            trades_list = [row[0] for row in cur.fetchall()]

            if trades_list:
                cur.execute("SELECT ticker FROM trades WHERE ticker IN ({})".format(','.join(["?"] * len(watchlist))), watchlist)
                trade_history = cur.fetchall()

                trade_data = {ticker: [] for ticker in trades_list}

                for val in trade_history:
                    ticker = val[1]
                    price = val[2]

                    if ticker in trade_data:
                        trade_data[ticker].append(price)

                for ticker, price in trade_data.items():
                    if price:
                        avg_trade_prices[ticker] = sum(price) / len(price)

            else:
                print("No Trade History!")
            
            # Getting Current Prices to compare against

            for ticker in watchlist:
                data = self.finnhub.quote(str(ticker))
                self.data_list = list(data.values())
                cur_price = self.data_list[0]

                cur_prices.update({ticker : float(cur_price)})
            
            # MAIN STOCK EVALUATION CODE

            for stock in watchlist:

                if stock in average_prices and stock in avg_trade_prices and stock in cur_prices:
                    current_price = cur_prices[stock]
                    historical_avg = average_prices[stock]
                    trade_avg = avg_trade_prices[stock]

                    # Decision Making for Buying:
                    if current_price < historical_avg and current_price < trade_avg:
                        print(f"Time to buy {stock} at price {current_price}")
                        self.make_buy(stock, current_price)  # Call make_buy method

                    # Decision Making for Selling (User owns stock)
                    cur.execute("SELECT amount_owned FROM portfolio_stocks WHERE ticker = ?", (stock,))
                    amount_owned = cur.fetchone()

                    if amount_owned and amount_owned[0] > 0:  # User owns stock
                        if current_price > historical_avg and current_price > trade_avg:
                            print(f"Time to sell {stock} at price {current_price}")
                            self.make_sale(stock, current_price)  # Call make_sale method




            print("Starting Timer for 10 minutes on Trade Evaluation!")
            threading.Timer(600, lambda: self.eval_stock(conn)).start()
        else:
            print("Not Ready to Trade Yet!")

class TraderApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.loginconn = sqlite3.connect('users.db')
        self.portfolioconn = sqlite3.connect('portfolio.db', check_same_thread=False)
        self.loginFrame = None
        self.bot = TraderBot()
        self.watchlist = []
        self.watchlist_bool = [False]
        # Finnhub
        self.API_KEY = 'co7coipr01qgik2h3bt0co7coipr01qgik2h3btg'
        self.finnhub = finnhub.Client(api_key=self.API_KEY)
    def window(self):
        ctk.set_appearance_mode("light")
        self.app.title("Automated Trading Bot")
        self.app.geometry("1600x700")
        self.Login_GUI()

    def Login_GUI(self):
        self.loginFrame = ctk.CTkFrame(self.app)
        self.loginFrame.pack(fill="both", expand=True, padx=20, pady=20)

        # Spacers to Center Content
        self.loginFrame.grid_rowconfigure(0, weight=1)  
        self.loginFrame.grid_rowconfigure(1, weight=1)  
        self.loginFrame.grid_rowconfigure(4, weight=1)  

        self.loginFrame.grid_columnconfigure(0, weight=1)  
        self.loginFrame.grid_columnconfigure(1, weight=1)  
        self.loginFrame.grid_columnconfigure(2, weight=1)  

        # Add login header and entry widgets
        loginHeader = ctk.CTkLabel(self.loginFrame, text='LOGIN')
        loginHeader.grid(row=0, column=1, pady=(0, 10))

        # Username
        usrtext = ctk.CTkLabel(self.loginFrame, text="Username: ")
        usrtext.grid(row=1, column=0, sticky="e", padx=10)
        self.userinput = ctk.CTkEntry(self.loginFrame, placeholder_text='Username')
        self.userinput.grid(row=1, column=1, sticky="we", padx=10)  

        # Password
        pswdtext = ctk.CTkLabel(self.loginFrame, text="Password: ")
        pswdtext.grid(row=2, column=0, sticky="e", padx=10)
        self.pswdinput = ctk.CTkEntry(self.loginFrame, placeholder_text="Password")
        self.pswdinput.grid(row=2, column=1, sticky="we", padx=10, pady=20)

        # Enter Button
        etrButton = ctk.CTkButton(self.loginFrame, text="Enter", command=self.Login_Info_Handler)
        etrButton.grid(row=3, column=1, sticky="we", padx=10)
        
    def Login_Info_Handler(self):
        cur = self.loginconn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
            )
    ''')
        
        self.entered_user = self.userinput.get()
        entered_pswd = self.pswdinput.get()

        # Verify Password        
        cur.execute("SELECT password_hash FROM users WHERE username = ?", (self.entered_user,))
        r = cur.fetchone()
        if r:
            stored_password_hash = r[0]
            # Hash Password
            if bcrypt.checkpw(entered_pswd.encode(), stored_password_hash):
                print("User Logged in!")
                self.main_GUI()
        else:
            print("User not found!")
    
    def main_GUI(self):
        if self.loginFrame is not None:
            self.loginFrame.destroy()

        mainFrame = ctk.CTkFrame(self.app)
        mainFrame.pack(fill="both", expand=True, padx=20, pady=20)

        # Display user label
        activity_text = ctk.CTkLabel(mainFrame, text="User: " + self.entered_user, font=("Helvetica", 18))
        activity_text.grid(row=0, column=0, sticky="w", padx=10)

        # Fetch last known portfolio value
        cur = self.portfolioconn.cursor()
        cur.execute("SELECT value FROM portfolio ORDER BY datetime DESC LIMIT 1")
        last_val = cur.fetchone()

        if last_val:
            portfolio_val = last_val[0]
        else:
            portfolio_val = 1000  # Default value if no data

        # Display portfolio value label
        value_text = ctk.CTkLabel(mainFrame, text="Portfolio Value $ " + str(portfolio_val), font=("Helvetica", 18))
        value_text.grid(row=0, column=1, sticky="e", padx=10)


        cur.execute("SELECT amount FROM portfolio_stocks WHERE ticker = ?", ("MONEY",))
        money_val = cur.fetchone()

        # Display Money Available
        money_text = ctk.CTkLabel(mainFrame, text="Money $ " + str(money_val[0]), font=("Helvetica", 18))
        money_text.grid(row=0, column=1, sticky="w", padx=10)

        # Portfolio Frame
        self.portfolio_frame = ctk.CTkScrollableFrame(mainFrame, width=760, height=625)
        self.portfolio_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")  
        portfolioheader = ctk.CTkLabel(self.portfolio_frame, text="PORTFOLIO", font=("Helvetica", 18))
        portfolioheader.grid(row=0, column=0)

        cur.execute("SELECT datetime, value FROM portfolio ORDER BY datetime")
        rows = cur.fetchall()

        x = [row[0] for row in rows]
        y = [row[1] for row in rows]

        # Making the Portfolio Graph
        fig, ax = plt.subplots(figsize=(7,3.2))
        if len(x) == len(y) and len(x) > 0:
            ax.plot(x, y, marker='o', color='green')
            ax.set_title("Portfolio Value")
            ax.set_xlabel("Value Timestamp")
            ax.set_ylabel("Value in Dollars")
            ax.legend()

        port_canvas = FigureCanvasTkAgg(fig, master=self.portfolio_frame)
        port_canvas.get_tk_widget().grid(row=1, column=0)


        self.bot.update_portval(self.portfolioconn, self.finnhub)
        # Redraw Tables with New Value
        self.redraw_graph()

        # Stock Frame
        self.stock_frame = ctk.CTkScrollableFrame(mainFrame, width=460, height=625)
        self.stock_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")  
        stockheader = ctk.CTkLabel(self.stock_frame, text="STOCK SEARCH", font=("Helvetica", 18))
        stockheader.grid(row=0, column=0, columnspan=2)
        
        # Stock Input
        self.stock_input = ctk.CTkEntry(self.stock_frame, placeholder_text="Enter Stock Ticker Here!", width=420)
        self.stock_input.grid(row=1, column=0, sticky='ew', padx=(0, 10))
        stock_button = ctk.CTkButton(self.stock_frame, text="Search Stock!", command=self.stock_search)
        stock_button.grid(row=1, column=1, sticky="ew")

        # Search Frame Inside of Stock Frame
        self.search_frame = ctk.CTkFrame(self.stock_frame, width=475, height=223)
        self.search_frame.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=(10, 0))


        # Watch List Header + Frame inside of Stock Frame
        watchlist_header = ctk.CTkLabel(self.stock_frame, text="WATCHLIST", font=("Helvetica", 18))
        watchlist_header.grid(row=3, column=0, columnspan=2)

        self.watch_frame = ctk.CTkScrollableFrame(self.stock_frame, width=475, height=250)
        self.watch_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(10, 0))

        # Trigger initial watchlist display
        self.redraw_watchlist()

        self.watchlist_bool = [False]  # Use a mutable type like a list to make flag accessible across methods

        self.check_watchlist_update()

        # Update Watchlist
        self.bot.update_watchlist(self.portfolioconn, self.finnhub, self.watchlist_bool)


    
        # Configure grid for the main frame
        mainFrame.grid_columnconfigure(0, weight=1)  
        mainFrame.grid_columnconfigure(1, weight=1)  
        mainFrame.grid_rowconfigure(0, weight=0)   
        mainFrame.grid_rowconfigure(1, weight=1)  

        # Intial Bot Call (This should start the bot working it's magic!)
        self.bot.eval_stock(self.portfolioconn)

    def check_watchlist_update(self):
        if self.watchlist_bool[0]:  # Check if the update flag is set
            self.redraw_watchlist()  # Call your redraw logic here
            self.watchlist_bool[0] = False  # Reset the flag
        self.app.after(1000, self.check_watchlist_update)  # Repeat every second
    
    def redraw_watchlist(self):
          # Clear existing widgets in the watch_frame
        for widget in self.watch_frame.winfo_children():
            widget.destroy()

        # Set up headers
        ticker_header = ctk.CTkLabel(self.watch_frame, text='Ticker', font=("Helvetica", 12))
        ticker_header.grid(row=0, column=0, sticky='w', padx=30)
        lp_header = ctk.CTkLabel(self.watch_frame, text='Last Price', font=("Helvetica", 12))
        lp_header.grid(row=0, column=1, sticky='w', padx=30)
        owned_header = ctk.CTkLabel(self.watch_frame, text='Amount Owned', font=("Helvetica", 12))
        owned_header.grid(row=0, column=2, sticky='w', padx=30)
        value_header = ctk.CTkLabel(self.watch_frame, text='Approximate Value ($)', font=("Helvetica", 12))
        value_header.grid(row=0, column=3, sticky='w', padx=30)

        # Fetch updated watchlist data
        cur = self.portfolioconn.cursor()
        cur.execute("SELECT ticker, last_price, amount_owned, approx_value FROM watchlist")
        watchlist = cur.fetchall()

        # Populate the watchlist rows
        for i, item in enumerate(watchlist):
            ticker, last_price, amount_owned, approx_value = item
            ticker_label = ctk.CTkLabel(self.watch_frame, text=f"{ticker}", font=("Helvetica", 12))
            ticker_label.grid(row=i+1, column=0)

            last_price_label = ctk.CTkLabel(self.watch_frame, text=f"${last_price}", font=("Helvetica", 12))
            last_price_label.grid(row=i+1, column=1)

            amount_owned_label = ctk.CTkLabel(self.watch_frame, text=f"{amount_owned}", font=("Helvetica", 12))
            amount_owned_label.grid(row=i+1, column=2)

            approx_value_label = ctk.CTkLabel(self.watch_frame, text=f"${approx_value}", font=("Helvetica", 12))
            approx_value_label.grid(row=i+1, column=3)

        # Reset the flag after redrawing
        self.watchlist_bool[0] = False

    def redraw_graph(self):
        for widget in self.portfolio_frame.winfo_children():
            widget.destroy()
        
        cur = self.portfolioconn.cursor()
        cur.execute("SELECT datetime, value FROM portfolio ORDER BY datetime")
        rows = cur.fetchall()

        x = [row[0] for row in rows]
        y = [row[1] for row in rows]

        # Making the Portfolio Graph
        fig, ax = plt.subplots(figsize=(7,3.2))
        if len(x) == len(y) and len(x) > 0:
            ax.plot(x, y, marker='o', color='green')
            ax.set_title("Portfolio Value")
            ax.set_xlabel("Value Timestamp")
            ax.set_ylabel("Value in Dollars")
            ax.legend()
     
        port_canvas = FigureCanvasTkAgg(fig, master=self.portfolio_frame)
        port_canvas.get_tk_widget().grid(row=1, column=0)

        # Call this function again in 301 seconds (1 second after the portfolio value refreshes)
        threading.Timer(301, self.redraw_graph).start()

    def stock_search(self):
        # Clear Frame for new results
        for w in self.search_frame.winfo_children():
            w.destroy()
        search_tick = self.stock_input.get()

        data = self.finnhub.quote(str(search_tick))
        self.data_list = list(data.values())
        data_tags = ["Current Price","Change","Percent Change","High Price","Low Price","Open Price","Previous Close Price"]
        i = 0
        for i in range(len(data_tags)):
            info_label = ctk.CTkLabel(self.search_frame, text=data_tags[i] + " : " + str(self.data_list[i]), font=("Helvetica", 12))
            info_label.grid(row=2+i, column=0, sticky='w')
            buffer_label = ctk.CTkLabel(self.search_frame, text="")
            buffer_label.grid(row=2+i, column=1)
            i+=1

        watchlist_button = ctk.CTkButton(self.search_frame, text="Add to Watchlist", command=self.add_watchlist)
        watchlist_button.grid(row=10, column=0, sticky='w')

    def add_watchlist(self):
        ticker = self.stock_input.get().upper()
        cur = self.portfolioconn.cursor()
        cur.execute("SELECT amount FROM portfolio_stocks WHERE ticker = ?", (ticker,))
        amount_owned = cur.fetchone()

        if amount_owned:
            approx_val = amount_owned * float(self.data_list[0])
            cur.execute("INSERT INTO watchlist (ticker, last_price, amount_owned, approx_value) VALUES (?, ?, ?, ?)", (self.stock_input.get().upper(), self.data_list[0], amount_owned, approx_val))
            self.portfolioconn.commit()
        else:
            cur.execute("INSERT INTO watchlist (ticker, last_price, amount_owned, approx_value) VALUES (?, ?, ?, ?)", (self.stock_input.get().upper(), self.data_list[0], 0, 0))
            self.portfolioconn.commit()
        
        for w in self.watch_frame.winfo_children():
            w.destroy()

        self.ticker_header = ctk.CTkLabel(self.watch_frame, text='Ticker', font=("Helvetica", 12))
        self.ticker_header.grid(row=0, column=0, sticky='w', padx=30)
        self.lp_header = ctk.CTkLabel(self.watch_frame, text='Last Price', font=("Helvetica", 12))
        self.lp_header.grid(row=0, column=1, sticky='w', padx=30)
        self.owned_header = ctk.CTkLabel(self.watch_frame, text='Amount Owned', font=("Helvetica", 12))
        self.owned_header.grid(row=0, column=2, sticky='w', padx=30)
        self.value_header = ctk.CTkLabel(self.watch_frame, text='Approximate Value ($)', font=("Helvetica", 12))
        self.value_header.grid(row=0, column=3, sticky='w', padx=30)

        cur.execute("SELECT ticker, last_price, amount_owned, approx_value FROM watchlist")
        self.watchlist = cur.fetchall()

        for i, item in enumerate(self.watchlist):
            ticker, last_price, amount_owned, approx_value = item  # Unpack the values
            ticker_label = ctk.CTkLabel(self.watch_frame, text=f"{ticker}", font=("Helvetica", 12))
            ticker_label.grid(row=i+1, column=0)
    
            last_price_label = ctk.CTkLabel(self.watch_frame, text=f"${last_price}", font=("Helvetica", 12))
            last_price_label.grid(row=i+1, column=1)
    
            amount_owned_label = ctk.CTkLabel(self.watch_frame, text=f"{amount_owned}", font=("Helvetica", 12))
            amount_owned_label.grid(row=i+1, column=2)
    
            approx_value_label = ctk.CTkLabel(self.watch_frame, text=f"${approx_value}", font=("Helvetica", 12))
            approx_value_label.grid(row=i+1, column=3)

    def run(self):
        self.window()
        self.app.mainloop()




app = TraderApp()
app.run()






import sqlite3
import requests
import customtkinter as ctk
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import bcrypt
from datetime import datetime
import finnhub


class TraderBot:
    def __init__(self):
        pass

class TraderApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.loginconn = sqlite3.connect('users.db')
        self.portfolioconn = sqlite3.connect('portfolio.db')
        self.loginFrame = None
        self.bot = TraderBot()
        self.watchlist = []
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
            if bcrypt.checkpw(entered_pswd.encode(), stored_password_hash):
                print("User Logged in!")
                # Transfer us to the main screen in the program
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

        # Portfolio Frame
        portfolio_frame = ctk.CTkScrollableFrame(mainFrame, width=760, height=625)
        portfolio_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")  
        portfolioheader = ctk.CTkLabel(portfolio_frame, text="PORTFOLIO", font=("Helvetica", 18))
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

        # Display Value Above Point
        for i in range(len(x)):
            ax.annotate(f"${y[i]:,.2f}",  
                    (x[i], y[i]),     
                    textcoords="offset points",  
                    xytext=(0, 5),    
                    ha='center')
            
        port_canvas = FigureCanvasTkAgg(fig, master=portfolio_frame)
        port_canvas.draw()
        port_canvas.get_tk_widget().grid(row=1, column=0)

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

        # Configure grid for the main frame
        mainFrame.grid_columnconfigure(0, weight=1)  
        mainFrame.grid_columnconfigure(1, weight=1)  
        mainFrame.grid_rowconfigure(0, weight=0)   
        mainFrame.grid_rowconfigure(1, weight=1)    

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
        else:
            cur.execute("INSERT INTO watchlist (ticker, last_price, amount_owned, approx_value) VALUES (?, ?, ?, ?)", (self.stock_input.get().upper(), self.data_list[0], 0, 0))
        
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






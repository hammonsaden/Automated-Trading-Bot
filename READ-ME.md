# Automated-Trading-Bot


This is my second program I've built for my resume, its a "Automated" Trading Bot built using Python, SQL, and a API called "Finnhub" for all stock data.

The bot will make auto trades for you throughout the day as long as the program is running in the background using live price data, this program was built assuming 0% trade fees.

~ Features ~
You can log in to the program via the home login page (default account login is, username = "user1", password = "pswd")
You can view the amount of money your investing portfolio is currently worth (Fake Money, of course!).
You can view data for any stock using the search bar at the top of the screen (current stock price, high price of the day, low price of the day, previous close price.)
You can add stocks to your watch list for quick searching.
You can view previous trades made by the bot automatically.


 ~ 11/6/2024 ~
I had to do some extra research on some of the functions of this program, because I wasn't exactly sure the route I wanted to go with it. As far as how I will program the trading and 
whether or not to utilize a AI neural network or not. I figured out I will hard code the functions in this and let it make decisions based off of that. I do want to limit the amount of trades per hour to 6,
so it wont just trade every time there is a little change in the program. I also had trouble figuring out how I wanted to display graphs, due to the fact that I found out that I couldn't use finnhubs graphs to put directly into my program, so I decided I will utilize a python module called Mathplotlib (I have never utilized this before, so I am excited) to form my graphs and put them into my customtkinter GUI.

I am planning to have a order in which I want to do things to hopefully make it as smooth as possible in creating this program.

I would like to get as much of the front end done first, but I know that my login page will probably be the first thing that needs to be completed in whole.

I ended up doing the login page with Custom Tkinter and a hasher module named bcrypt for encrypting the passwords in my users sql file, happy with how it turned out. I added 2 different accounts with 1 having user and password "test1" and the other having the user and password "test2". Both of these accounts are going to mirror eachother and have no data difference, but it will show that I can make a functioning login page that can encrypt.

Moving onto the main_GUI of the program. I have a couple key points of data I want it to display when the user first opens up the program. first, I want it to display the current users name in the top left corner, and I want it to display the current value of the portfolio next to that.

As far as how I want my data structure is going to be, here is an idea of how I want it organized:

SQLite3

~ users.db ~ 
    - users table
        - username (TEXT)
        - password_hash (TEXT)

~ portfolio.db ~
    - portfolio table
        - datetime (TEXT)
        - value (REAL)
    - trades table
        - datetime (TEXT)
        - ticker (TEXT)
        - price (REAL)
        - amount (REAL)
        - value (REAL)
    - portfolio_stocks table
        - ticker (TEXT)
        - amount (REAL)
    - watchlist table
        - ticker (TEXT)
        - last_price (REAL)
        - amount_owned (REAL)
        - approx_value (REAL)
    - price_history table
        - datetime (TEXT)
        - ticker (TEXT)
        - price (REAL)
        - average (REAL)

This is just how I think I want my data to be organized, I might end up changing it down the line. My users.db will stay the same, it functions as needed with my program already and will only be used for the logging in portion of the program. As far as my portfolio.db code goes. I will work on that now as well as getting my basic GUI elements organized before I hook the program upto the finnhubb API.

6:07pm
I was able to get the portfolio page setup like I want it. I made a scrollable frame with a graph displaying the portfolio value. I also just implemented my finnhub API and made my stock search bar operational with any stock or ETF on the US Stock Market, which was pretty cool to be able to utilize all of that data.
I am implementing a watch list for the user currently, that they can add and take stocks from as they please. ANY stocks on the users watchlist will be watched and traded by the bot. At this point, I have hit most points in the original idea of my program, but I know most of the work is going to go into storing data per stock and having the bot analyze it and make trades based off of that data. I am going to utilize my portfolio_stocks table to track the price of the stocks on the user's watchlist, to form a price history to be able to make more informed decisions.

6:44pm
I just finished polishing off the stock search and making sure the grid lined up perfectly, and I added a button for when you search a stock, it will ask you if you want to add it to the watch list. I am going to take part of the bottom section of the stock search and turn it into the area where you can see what is on your watch list and edit your watch list.

7:02pm
Finished the watchlist section, and now when you press the watch button under the stock when it pulls up, it was automatically append the stock ticker to your watchlist. At this moment, I am going to also recogfigure my SQL table settings to add another table under portfolio.db that is the watchlist table, which will hold the data "ticker, last_price, amount_owned, approx_value".

7:59pm
I am done for tonight, should be able to configure the rest of the bot tomorrow so that it can hopefully do it's first day of trading tomorrow on the market with the $1,000.00 I have given it. I just ending up getting the watchlist done completely how I wanted it. I had to redo the backend on it, because I did it the simple way earlier that I knew I was going to have to override. I had to go back and hook it up to the watchlist SQL table and have it read the values from there and put it onto a table on the screen, rather than basically hard coding in the values through a jumbled mess of references to different spots. This way should make it much more efficient to handle the watchlist later on. I still haven't added the feature to delete stuff from the watchlist yet, but I will do so tomorrow. I also want to make a function to redraw the plot each time the portfolio value changes (I am thinking I want it to update every 5 minutes or so, so it can update and base the value off of the "somewhat" current market prices (meaning upto 5 minutes old.)). The bot will have to trade based off of a quicker time than that I am thinking. The limit for the bot will be 1 trade every 10 minutes, but I want it to have access to more current prices than that so it can make it's decision.

~ 11/7/2024 ~

4:02pm
Getting time to work on my resume program again. I was able to work on it just a little last night, all I did was outline all of the functions I think I will need for my traderbot class, just so I could get my gears turning for today. First thing I want to do is figure out how I am going to do my timer for my program. I found a library that comes with the python standard library called "threading" that will be able to run multiple threads at once, one for my main program, and one for keeping time on my timer. This is the first time I am using this library, or have even heard of it. I am excited to see what kind of timer I make with it, and I hope I can fit it into my program somewhere to keep time. First thing I am going to focus on, is to get my values on my watchlist to update every 2 minutes to keep us updated with current (or somewhat current) stock prices.

I also just added a new table to my data schema for the program. I added the price_history table which has the values datetime, ticker, and price, average. This will probably update every 15 minutes or so just to givethe bot a little bit of price history to go on per stock. I just went and added the value "average" onto the end of the table schema, and I will have the bot calculate the average of the stock every time new data is entered, so it can have somewhat updated averages.

4:49pm
Just wrapping up my update watchlist, I had to use a lambda function for the threading.Timer function because it made an infinite loop, because it was immediately starting calling my function because I had args in it, so I used a lambda function so it would wait to be called until the timer was used. I just tested my update_watchlist function, and it works as intended. I will have to try it out tomorrow during market hours to see if it will actually want to update the data on the screen. I am going to try to get all of my bot functions done tonight so that they can be tested during open market hours tomorrow.

4:57pm
Going to tackle the next bot function of update_portval, which will update my portfolio value when it is called, every 5 minutes.

5:37pm
Got the update_portval method done for my bot, it was pretty easy. I got distracted by coding, and forgot to write in my devlog.. I went ahead and had to make a redraw_graph method for the graph to redraw every 301 seconds (1 second after the update_portval timer is done). That was pretty easy too. I went ahead and used threading for that too. So, the only methods that I have left to complete are the core "automated" methods, which is the make_buy, make_sale, and eval_stock methods. The bot will first evaluate the stock (It only is interested in evaluating stocks, buy stocks, and sell stocks on your watchlist.). I am going to have the bot base it's evaluation off of the average price history of the stock (collected while the program is running.), and it will make buys based off of that. So that has the eval and buy figured out, but I am not too sure yet on how I want to do my make_sale method. I am not too sure if I want it to look for any sort of small gain (such as a day trader would.), or if i should set it at a margin of like 0.5% or something. I might for the sake of actually testing my bot, and making sure all of the data analysis it does is correct and it can make good buys and make money, I am going to set it to see any sort of small gain, but the bot can only make 1 trade every 10 minutes so that way it will have time to analyze and figure out a buy or a sell. I don't want it to be making like 400 buys a second, which is why I am having to set a limit on it. I am also trying to put notes into functions that I haven't written logic for yet, so that way when I do go into it to write logic this weekend I will be able to know exactly what it needs to do, exactly what I need to write.

6:08pm
So I had to add another table because I did realize a design flaw in my program. I need to enable the bot to differentiate between cash and stocks, it needs to have cash to be able to make trades. so I made the cash table that will track the amount of cash the user has.


~ 11/11/2024 ~

5:54pm 
Been a couple days since I have touched my program, going to possibly wrap it up tonight (If I don't run into too many problems.). I decided against the cash table, at the first entry in the watchlist table, I put a entry, "CASH" ticker, and approximate value is 1.00 and they will own however many dollar they have. In the beginning of the program, the base value is 1,000 so they will have 1,000 of the CASH stock. This is the easier work around that I found for myself, and still be able to make it functional. (This will also show the user how much cash the have in the watchlist.). I also want to put a stat at the top that will show how much cash, right next to the portfolio value. Well, I went ahead and am going to have to change the ticker from CASH haha there is a stock with that ticker. going to change it to "MONEY"

6:36pm
Got my money implementation figured out I think. I also added a function so the watchlist will pop up automatically on program login, and the amount of money the user has will pop up on login as well right next to the portfolio value. Going to work on the eval_stock, make_buy, and make_sale methods of the TraderBot Class now. I went ahead and added outlines to all of my methods the other night when I worked on it, so that way that I can get on and know exactly what the program has to do, makes it a lot easier for me to program and just get it done, also provides better organization as well.

7:01pm
I was going to work on the eval_stock function, but I forgot. The bot can't even do evaluations without some price history and comparing it against the average price of the stock and what it bought it at, so right now I am setting it up to be able to collect price history every time the watchlist prices update (2 minutes). I have a concern about this being too much data for the bot to have to handle, but we will see! 

7:36pm
Okay, I got the bot to be able to evaluate the average of a ticker based off of the price history of each ticker in the watchlist. I am going to continue with the eval_stock method, and get it to compare the current price of the stock with the average stock, and compare it to the past trades it has done as well. I am going to need it to average the past trades of that ticker as well, so it can have an average price it was bought for to compare against. If there is no trade history on the stock, I will have it default to using the price history data.

7:45pm
While working on the trade history section of the eval_stock method. I needed to add the price column to the trades table, so that way the bot could directly pull the past trade prices in a query. Got the trade history figured out, now going to have it check the trade average to the price history average, and make a decision based off of that. I also updated the portfolio value to update on the graph every 10 minutes, because it gets messy pretty quick. I am going to remove the value headers off of the tops of the points, it was making it very messy. I also need to fix the "MONEY" section of the watchlist. it keeps defaulting to 0 owned, when there is 1,000 owned in the beginning (to represent $1,000).

~11/12/24~

7:08pm
Think I am finally done with my whole program, I finished eval_stock, and it wasn't too hard to kind of make the other 2 methods I had left to fall in behind after that. I am going to test it tomorrow to make sure everything runs smoothly. I still need to fix the 1 bug that I noticed yesterday, where MONEY keeps defaulting to 0 owned. I will fix that tomorrow during the testing phase of my program.

~11/13/24~

11:45am
Testing day! starting up my program now to collect some data.

Diagnostic Data
- Little Rough on Startup, will need to limit the number of functions running on start up (such as bot trying to initiate a trade on start up, no need)
- Need to fix watchlist defaulting MONEY stock owned to 0 and approx value to $0
- Watchlist isnt updating every 2 minutes with prices, but values are being put into the price_history db


1:23pm
Got it working how I need for it to atleast start collecting data for the time being, so that way it can make some trade decisions in the future.



~11/14/24~

11:00am 
Going to start it up again to collect some data and test to see if the bot will do any form of trading.

~ 11/17/2024~

2:52pm
Got a lot of stuff figured out, I fixed the portfolio value not wanting to update and the money value not wanting to update. I also got the bot to start buying stocks and it makes trades successfully.
It will just take time to test to see how it actually does. I currently had to put a $100 limit on each trade, which obviously isn't working since some stocks are above $100.


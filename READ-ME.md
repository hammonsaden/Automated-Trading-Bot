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
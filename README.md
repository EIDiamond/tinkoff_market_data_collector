## Description
Main goal is download and keep market data for internal purposes, such as manual analyze, 
historical backtesting [trade_backtesting](https://github.com/EIDiamond/trade_backtesting) project),
ML purposes etc.

The tool is using [Tinkoff Invest Python gRPC client](https://github.com/Tinkoff/invest-python) api and collecting data from MOEX Exchange.

Please note:
1. The tool is downloading market data via market stream in **real-time**. 
Note: You have to keep it running to have whole trade day information.  

2. The tool workflow is "run and forgot". The tool reads trade schedule:
   1. runs and stops data collection by schedule without manual handle it
   2. handles holiday, weekends, also sleep between trade days etc.

## Features
- Downloading the following information from MOEX Exchange:
  - Candle
  - Trades (executed orders)
  - Last price (price in time) 
- Saving this data in csv files
- Working as service. Just run it and forget. 

## Before Start
### Dependencies

- [Tinkoff Invest Python gRPC client](https://github.com/Tinkoff/invest-python)
<!-- termynal -->
```
$ pip install tinkoff-investments
```

### Brokerage account
Open brokerage account [Тинькофф Инвестиции](https://www.tinkoff.ru/invest/).

Do not forget to take TOKEN for API trading.

### Required configuration (minimal)
1. Open `settings.ini` file
2. Specify token for trade API in `TOKEN` (section `INVEST_API`)

### Run
Recommendation is to use python 3.10. 

Run main.py

## Configuration
Configuration can be specified via [settings.ini](settings.ini) file.
### Section WATCHER
Specify `MAX_SEC_API_SILENCE` max delay between check for api hung.  
Specify `DELAY_BETWEEN_API_ERRORS_SEC` max delay between retry runs if api has been failed.  
### Section INVEST_API
Specify `TOKEN` and `APP_NAME` for [Тинькофф Инвестиции](https://www.tinkoff.ru/invest/) api.
### Section DATA_COLLECTION
Specify what kind of data the tool will collect:
- 1 - True
- 0 - False

### Section STOCK_FIGI
Specify stocks via figi.

Syntax:
ticker_name=figi

### Section STORAGE
Specify name of storage (class with storage logic).

`TYPE=FILES_CSV` by default, but you are able to add your own. (see below)

### Section STORAGE_SETTINGS
Section for storage settings. 
You will have to add your own, if you add your own storage class.

## How to add a new storage 
- Write a new class with storage logic
- The new class must have IStorage as super class 
- Give a name for the new class
- Extend StorageFactory class by the name and return the new class by the name
- Specify new settings in settings.ini file. 
  - Put the new class name in `STORAGE` section and `TYPE` field
  - Put new settings into `STORAGE_SETTINGS` section

## CSV files (default storage)
### Structure on file system
By default, root path is specified in `STORAGE_SETTINGS` section and `ROOT_PATH` field. 

Folders structure: `ROOT_PATH`/{figi}/{data_type_folder}/{year}/{month}/{day}/market_data.csv

{data_type_folder} can be:
- "candle" (for candles)
- "trade" (for executed orders)
- "last_price" (for last price information)

### CSV files structure
#### Candles
Headers in candles csv file: **open**, **close**, **high**, **low**, **volume**, **time**

#### Trades
Headers in trades csv file: **direction**, **price**, **quantity**, **time**

Direction: 1 - Buy, 2 - sell

#### Last Prices
Headers in last_prices csv file: **price**, **time**

## Use case
1. Download market data using [tinkoff_market_data_collector](https://github.com/EIDiamond/tinkoff_market_data_collector) project
2. Research data and find an idea for trade strategy using [analyze_market_data](https://github.com/EIDiamond/analyze_market_data) project
3. Test and tune your trade strategy using [trade_backtesting](https://github.com/EIDiamond/trade_backtesting) project
4. Trade by [invest-bot](https://github.com/EIDiamond/invest-bot) and your own strategy.
5. Profit!

### Example
Your can find example in code:
- Let's imagine your have great idea to invent your own idicator. Rsi idicator was selected for example.
- RSI Calculation alghoritm has been written for [research tool](https://github.com/EIDiamond/analyze_market_data/blob/main/analyze/rsi_calculation/rsi_calculation_analyze.py)
- It has been tested by [backtesting](https://github.com/EIDiamond/trade_backtesting/blob/main/trade_system/strategies/rsi_example/rsi_strategy.py)
- And now you are able to make your desicion.

## Logging
All logs are written in logs/collector.log.
Any kind of settings can be changed in main.py code

## Disclaimer
The author is not responsible for any errors or omissions, or for the trade results obtained from the use of this tool. 

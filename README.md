# Portfolio-Management-Project
A basic porfolio management system written in Python using the GUI application Tkinter.

# Table of Contents
- [Introduction](#Introduction)
- [Installation](#Installation)
  * [Getting Started](#Getting-Started)
- [Features](#Features)
  * [Sub-heading](#sub-heading)

# Introduction
This Project (PRMS) utilises the REST API's of Alpha Vantage to create charts with/without technical indicators and Oanda to execute trades to the market. PRMS also uses sqlite3 to store information from the Oanda platform into a database for reconciliation purposes.

# Installation
If you do not have Python 3.7+, you can download it here.

In the terminal navigate to the project directory and type pip install -r requirements.txt. This will install all the required modules to run this application.

API-Keys

This project requires 3 API keys:
* News API - Gets the latest news headlines. Get your key here.
* Oanda API - Various functions pertaining to the portfolio. Get your key here.
* Alpha Vantage API - extract FX data for charting purpose. Get your key here.

*** Note with Oanda you will also need to set up a dummy trading account with them to get your key.
Once you have your API keys and Oanda Account ID. populate them as strings in the config file.

When these processes have been completde you can then run the main application.

# Features
PRMS comes packed with the following features:
* View the latest news headlines
* Oanda Account details
* A list of all tradable securities as well as the live bid/ask prices
* Intraday FX Algorithm trading based on two strategies (Golden Cross, RSI)
* Intraday, Daily, Weekly FX Charting with Technical Indicators
* Buy/Sell Market Executions from the Oanda Platform. (with Trade confirmations)
* Transaction history and manual entry from the applications Database
* Position and Price reconciliation between Oanda and PRMS

# Screenshots

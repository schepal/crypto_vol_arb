# Bitcoin Deribit/FTX Volatility Arbitrage
A tool used to analyze arbitrage opportunities between Deribit and FTX cryptocurrency option markets. 

#### Disclaimer: This tool is only for demonstration purposes and is not financial advice. This script has not undergone extensive testing and may have hidden bugs. Use this tool at your own risk. 

## Overview
Option contracts are powerful financial instruments used to execute a variety of different trading strategies. Notably, the popular long straddle trade is a combination of buying a call and put with the same strike and maturity. A trader would purchase a straddle if they expect their forecasted future volatility to be greater than the current implied volatility. In this case, the trader doesn’t care whether the price of an asset goes up or down. Rather the trader cares about ***how fast*** the price moves as they wish to profit from an increase in volatility (either direction). 

Deribit Exchange offers the greatest option market liquidity relative to the other players in this space. Using the calls and puts trading on Deribit, we can create our own straddle by going long the respective at the money calls and puts. 

FTX is another prominent exchange which offers a product called MOVE contracts. These MOVE contracts are quite similar to straddles in the sense their value is derived from the “[absolute value of the amount a product moves in a period of time](https://help.ftx.com/hc/en-us/articles/360033136331-MOVE-contracts#:~:text=What%20are%20MOVE%20contracts%3F,BTC%20went%20up%20or%20down).” 

In theory an FTX MOVE contract with a similar maturity should be priced closely in line to the respective Deribit at-the-money straddle. After some observation it became quite surprising that the price differences between these two venues were too large to overlook.

## Quick Guide On Usage
There are two primary classes in this script which need to be used.

1. `FTX`: This will be used to retrieve all of the relevant FTX MOVE contract data. You will need to instantiate this class first seperately to get a list of the various MOVE contracts which you would like to analyze. 

2. `VolArb`: This is the primary class which inherits the `FTX` class and its respective methods. This class allows direct comparison between the Deribit and FTX prices accordingly. 

## Example
In the example below, the script is setup to show how to analyze arbitrage opportunites for the chosen FTX MOVE contract.
``` python
>>> import crypto_vol as cv

# List out all MOVE contracts trading on FTX
>>> move_contracts = cv.FTX().get_move_contracts()
>>> move_contracts
['BTC-MOVE-0815',
 'BTC-MOVE-0816',
 'BTC-MOVE-WK-0821',
 'BTC-MOVE-WK-0828',
 'BTC-MOVE-WK-0904',
 'BTC-MOVE-WK-0911',
 'BTC-MOVE-2020Q3',
 'BTC-MOVE-2020Q4',
 'BTC-MOVE-2021Q1']

# Choose whichever FTX MOVE contract you would like to analyze
# Here we will take a look at 'BTC-MOVE-WK-0828'
# You will need to adjust the `strike_threshold` and `days_threshold` accordingly
>>> vol = cv.VolArb('BTC-MOVE-WK-0828', strike_threshold=200, days_threshold=2)

# Retrieve all comparable Deribit Options to form an equivalent straddle
>>> data = vol.get_comparable_deribit()
>>> data
# Returns a dataframe with all the respective options
"""
option_type	strike	  instrument_name	     ftx_expiry_days  deribit_expiry_days option_price
put	       12000.0	  BTC-28AUG20-12000-P	 13.132293	       12.46561	         549.799060
call	     12000.0	  BTC-28AUG20-12000-C	 13.132293	       12.46561          482.544639
"""

# Compare the FTX MOVE and Deribit Straddle 
>>> vol.compare(data)
# Returns a dataframe with printout of the price difference between the two contracts
# Please see attached notebook for a more comprehensive example with a full dataframe output

"""-33.695 % price differential between FTX MOVE and similar Deribit straddle"""
```
When instantiating the `VolArb` class, you may have to tweak the `strike_threshold` and `days_threshold` parameters to 
widen the scope for which Deribit options to trade. Please refer to the detailed documentation in the `crypto_vol.py` file 
to better understand the parameters for each individual component. 

Below we can manually see how to assess the trading opportunity. 

### Deribit Options Chain 
![](/screenshots/deribit_screenshot.png)

### FTX MOVE Contract Price
![](/screenshots/ftx_screenshot.png)


***Calculations:*** 

Deribit Call Mid-Price: (496.19 + 514.12) / 2 = 505.155

Deribit Put Mid-Price: (478.33 + 508.23) / 2 = 493.28

Total Deribit Straddle Price = 505.155 + 493.28 = 998.435

FTX MOVE Mid-Price = (674 + 695) / 2 = 684.50

Difference = 998.435 - 684.50 = 313.94

Note these numbers aren’t exactly the same as the figures below because the screenshots were captured at an earlier time before the script was run. 

### Arbitrage Output Analysis
![](/screenshots/example_table_output.png)

## Risks and Limitations
Below are some of the many risks associated with this trading opportunity.

- **Counterparty Risk**: In the case either Deribit or FTX goes down, one leg of the trade is now exposed to price moves and would need to be closed immediately to avoid further delta exposure.
- **Margin Requirement**: This trade is not capital efficient as it requires margin to be posted on two separate exchanges. As a result, portfolio margin for this trade cannot be effectivey utilized. 
- **Liquidity Risk**: If liquidity is low on either exchange the arbitrage relationship may not hold as markets could become even more inefficient. Furthermore, a lack of liquidity in these derivative markets can be difficult for traders wanting to close their positions. 
- **Assume trades are placed at mid-price**: Relative to traditional financial option markets, the spreads for Deribit straddles and FTX MOVE contracts are quite large. As a result, poor execution will erode away any arbitrage profits. Using [Paradigm's](https://www.paradigm.co/) RFQ service can help reduce slippage on the Deribit leg of this trade.

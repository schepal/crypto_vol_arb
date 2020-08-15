# Bitcoin Volatility Arbitrage Trading 
A tool used to analyze volatility arbitrage opportunities in cryptocurrency derivative markets. 

#### Disclaimer: This tool is only for demonstration purposes and is not financial advice. This script has not undergone extensive testing and is prone to errors and bugs. Use this tool at your own risk. 

## Overview
Option contracts are powerful financial instruments to execute a variety of different trading strategies. Notably, the popular long straddle trade is a combination of buying a call and put with the same strike and maturity. A trader would purchase a straddle if they expect future volatility to be higher based on their forecast. In this case, the trader doesn’t care whether the price of an asset goes up or down. Rather the trader cares about ***how*** fast the price moves as they wish to profit from an increase in volatility (either direction). 

Deribit Exchange offers the greatest option market liquidity relative to the other players in this space. Using the calls and puts trading on Deribit, we can create our own straddle by going long the respective calls and puts. 

FTX is another prominent exchange which offers a product called MOVE contracts. These MOVE contracts are quite similar to straddles in the sense their value is derived from the “[absolute value of the amount a product moves in a period of time](https://help.ftx.com/hc/en-us/articles/360033136331-MOVE-contracts#:~:text=What%20are%20MOVE%20contracts%3F,BTC%20went%20up%20or%20down).” 

In theory an FTX MOVE contract with a similar maturity should be priced closely in line to the respective Deribit at-the-money straddle. After some observation it became quite surprising that the price differences between these two venues were too large to overlook.

## Key Parameters
- Discuss thresholds and how to use the script

## Examples 
- Show screenshot of Deribit and FTX MOVE contracts
- Show how an arb trade can be made
- Include Jupyter Notebook with Examples  

## Risks and Assumptions Involved
- Not a truly risk-free trade
- Counterparty Risk
- Assumption that trades placed at mid-price
- Margin Called on Trades
- Liquidity Risk 

## Installation of dependencies
- Include txt file

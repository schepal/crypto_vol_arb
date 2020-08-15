import pandas as pd
import requests
import numpy as np
import time
import calendar
import sys

class FTX:
     """
     The `FTX` class object is used to retrieve relevant MOVE contract data which is then 
     inherited into the primary `VolArb` class.
     
     """
     def __init__(self):
        self.ftx_api_endpoint = 'https://ftx.com/api/futures'

     def get_move_contracts(self):
        """
        Retrieves the expiry dates of all BTC MOVE contracts trading on FTX.
        
        Returns
        -------------
        dataframe:
            All expiry dates of the BTC MOVE contracts 
            
        """
        df = pd.DataFrame(requests.get(self.ftx_api_endpoint).json()['result'])
        ftx_expiries = list(df[df.name.apply(lambda x: any(pd.Series(x).str.contains('BTC-MOVE')))].name)
        return ftx_expiries

     def get_move_maturity(self, ftx_contract_name):
        """
        Calculates the days remaining until the FTX MOVE contract expiry. 

        Parameters
        -------------
        ftx_contract_name: str
            The name of the FTX move contract can be retrieved from the `get_move_contracts` method
            
        Returns
        -------------
        float:
            Returns the days left until maturity of the FTX MOVE contract

        """
        r = requests.get(self.ftx_api_endpoint + "/" +str(ftx_contract_name)).json()['result']
        expiry_date = pd.to_datetime(r['expiry']).date()
        days_left = (calendar.timegm(expiry_date.timetuple()) - time.time())/(60*60*24)
        return days_left

     def get_move_price(self, ftx_contract_name):
        """
        Calculates the mid-price of the FTX MOVE contract. The mid-price is calculated by
        taking average of the current bid and ask price.

        Parameters
        -------------
        ftx_contract_name: str
            The name of the FTX move contract can be retrieved from the `get_move_contracts` method
            
        Returns
        -------------
        float:
            Returns the mid-price of the FTX MOVE contract
            
        """
        r = requests.get(self.ftx_api_endpoint + "/" + str(ftx_contract_name)).json()['result']
        mid_price = np.mean([r[i] for i in ['bid', 'ask']])
        return mid_price

     def get_move_strike(self, ftx_contract_name):
        """
        Retrieves the strike price of the FTX MOVE Contract. In the case there is no strike listed,
        the default strike price will be the current price of the FTX MOVE Contract's respective index price.

        Parameters
        -------------
        ftx_contract_name: str
            The name of the FTX move contract can be retrieved from the `get_move_contracts` method
            
        Returns
        -------------
        float:
            Returns the strike price of the FTX MOVE contract or the current index price if no strike exists

        """
        index = requests.get(self.ftx_api_endpoint + "/" + str(ftx_contract_name)).json()['result']
        strike = requests.get(self.ftx_api_endpoint + "/" + str(ftx_contract_name) + "/stats").json()['result']
        if 'strikePrice' in strike.keys():
            return round(strike['strikePrice'], -2)
        else:
            return round(index['index'], -2)


class VolArb(FTX): 
     """
     The `VolArb` class object inherits the `FTX` class methods to compare 
     price differential between FTX and Deribit.
     """
     def __init__(self, ftx_comparable_contract, strike_threshold=100, days_threshold=1):
        super().__init__()
        """
        Initializes the `VolArb` class and uses super() to inherit the `FTX` methods.
        
        Parameters
        -------------
        ftx_comparable_contract: str
            The FTX move contract we wish to compare to its closest pair of Deribit contracts
        strike_threshold: int 
            The FTX MOVE contract may not have a strike price exactly equivalent to the 
            respective Deribit straddle strike. This parameter is the maximum dollar amount by 
            which the FTX MOVE Strike can differ by from the Deribit straddle strike. Default value
            is $100.
        days_threshold: int 
            The FTX MOVE contract may not have a maturity exactly equivalent to the 
            respective Deribit straddle maturity. This parameter is the maximum number of days by 
            which the FTX MOVE maturity can differ by from the Deribit straddle maturity. Default value
            is 1 day.
    
         """
        self.deribit_api_endpoint='https://www.deribit.com/api/v2/public/'
        self.ftx_comparable_contract = ftx_comparable_contract
        self.strike_threshold=strike_threshold
        self.days_threshold=days_threshold
        # Test to ensure the FTX contract name exists
        if self.ftx_comparable_contract not in self.get_move_contracts():
            print("Incorrect FTX contract name - please use the `get_move_contracts` method to get the proper names")
            sys.exit()
        
     def get_deribit_price(self, option):
        """
        Retrieves the USD mark price of a Deribit option. This is calculated by taking the 
        underlying mark price in BTC and multiplying by the option's underlying price in USD.

        Parameters
        -------------
        option: str
            The name of the Deribit option contract
            
        Returns
        -------------
        float:
            Returns the USD mark price of the option

        """
        data = requests.get(self.deribit_api_endpoint + "get_order_book?instrument_name="+ str(option)).json()['result']
        return data['mark_price']*data['underlying_price']

     def get_comparable_deribit(self):
        """
        Retrieves the most similar Deribit options with respect to the selected FTX MOVE Contract.
        This method will search through all options on Deribit and filter out all that do not fall
        within the appropriate strike and maturity days thresholds.
            
        Returns
        -------------
        dataframe:
            Returns a dataframe of comparable FTX MOVE contract and Deribit Straddle Data.
            In the case of an empty dataframe, please increase the `strike_threshold` and
            `days_threshold` parameters as the current values are likely too narrow. 
            
        """
        ftx_strike = self.get_move_strike(self.ftx_comparable_contract)
        ftx_mat_date = self.get_move_maturity(self.ftx_comparable_contract)
    
        # Download BTC options list from Deribit
        data = {'currency': 'btc', 'kind': 'option'}
        df = pd.DataFrame(requests.get(self.deribit_api_endpoint + "get_instruments", data).json()['result'])
        # Calculate the days to expiry for the Deribit options
        df['deribit_expiry_days'] = (df.expiration_timestamp/1000 - time.time())/(60*60*24)
        df['ftx_expiry_days'] = ftx_mat_date
        
        # First Criteria: Maturity Period Must Be Within +/- `days_threshold`
        rule1 = ((df.deribit_expiry_days > (ftx_mat_date - self.days_threshold)) & \
                 (df.deribit_expiry_days < (ftx_mat_date + self.days_threshold)))
        # Second Citeria: Strike Amount Must Be Within +/- `strike_threshold`
        rule2 = ((df.strike > (ftx_strike - self.strike_threshold)) & \
                (df.strike < (ftx_strike + self.strike_threshold)))
        df = df[rule1 & rule2].reset_index()[['option_type', 'strike', 'instrument_name', 'ftx_expiry_days', 'deribit_expiry_days']]
        # Retrieve price of selected options
        df['option_price'] = [self.get_deribit_price(option) for option in df.instrument_name]
        df = df.sort_values("strike")
        return df

     def compare(self, data):
        """
        This is the final step in our analysis where a user must manually input the dataframe
        produced by the `get_comparable_deribit` method which produces a detailed summary 
        of the potential arbitrage opportunity. 
            
         Parameters
        -------------
        data: dataframe
            The output of the `get_comparable_deribit` method must be manually inputted here.
            In the case of multiple options in the dataframe, please ensure to subset only
            ONE call and ONE put (straddle). 
                        
        Returns
        -------------
        dataframe:
            Returns a detailed summary of the various positions and potential arbitrage 
            opportunity between the FTX and Deribit straddle.
            
        """        
        # Ensures the dataframe is properly inputted by the user
        if len(data)==0:
            print("The threshold values are too low to detect any similar options." \
            " Please increase the `strike_threshold` and `days_threshold` parameters.")
            sys.exit()
        if len(data)!=2:
            print("There are", len(data), " options are being analyzed." \
            " Please subset the dataframe to only include ONE call and ONE put.")
            sys.exit()

        # Deribit Straddle Information
        straddle_price = data.option_price.sum()
        straddle_position = data.instrument_name.values
        straddle_time = data.deribit_expiry_days[0]
        
        # FTX MOVE Contract Information
        ftx_price = self.get_move_price(self.ftx_comparable_contract)
        ftx_time = data.ftx_expiry_days[0]
        
        # Combine Into DataFrame
        data = { 'deribit_straddle': [straddle_position, straddle_price, straddle_time],
                 'ftx_move': [self.ftx_comparable_contract, ftx_price, ftx_time],
                 'difference': ['NA', straddle_price - ftx_price, straddle_time - ftx_time]}
        df = pd.DataFrame(data, index=['Position', 'Price', 'Days Left'])
        print(round((ftx_price/straddle_price-1)*100, 3), "% price differential between FTX MOVE and similar Deribit straddle")
        return df

v = VolArb("BTC-MOVE-WK-0828", 300, 2)
data = v.get_comparable_deribit()
print(v.compare(data))        
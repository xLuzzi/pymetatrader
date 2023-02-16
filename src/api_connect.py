# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 23:09:05 2022

@author: Pedro Luzzi pedroluzzisc@gmail.com
"""
import json
import time
from datetime import datetime as dt

import pandas as pd
import requests


class ApiConnection:
    """Holds a MyFXBook API connection"""

    def __init__(self, username: str, password: str):
        """
        Parameters
        ----------
        username : str
            MyFXBook username.
        password : str
            MyFXBook password.

        Raises
        ------
        Exception
            Loggin error.
        """
        self.api_base_url = "https://www.myfxbook.com/api/"
        api_login_url = f"{self.api_base_url}login.json?email={username}&password={password}"
        print(f"Loggin {username}")
        session_request = requests.get(api_login_url)
        print(session_request)
        session_request = json.loads(session_request.content)
        time.sleep(1.2)
        if session_request["error"]:
            raise Exception(session_request)
        print("Successes")
        self.session = session_request['session']
        print(f"Session: {self.session}")

    def __del__(self):
        print("Logout...")
        api_logout_url = f"{self.api_base_url}logout.json?session={self.session}"
        self.logout_message = requests.get(api_logout_url).content
        if json.loads(self.logout_message)['error'] == 'false':
            print("Successes Logout")
        else:
            print(self.logout_message)

    def get_accounts(self):
        """
        Get all registered accounts.
        """
        api_get_accounts_url = f"{self.api_base_url}get-my-accounts.json?session={self.session}"
        print("Searching acconts...")
        self.accounts = json.loads(requests.get(
            api_get_accounts_url).content)['accounts']
        print(f"{len(self.accounts)} acconts found")
        time.sleep(1.2)
        self.accounts_df = pd.DataFrame(self.accounts)
        self.exness_accounts = [
            acc for acc in self.accounts if acc['server']['name'] == 'EXNESS']
        return self.exness_accounts

    def get_all_accounts_daily_gain(self):
        """
        Get daily_gain from all accounts.

        Returns
        -------
        dict
            {accounts_daily_gain, empty_accounts}.

        """
        if not self.accounts:
            self.get_accounts()
        self.accounts_daily_gain = []
        self.empty_accounts = []
        i = len(self.exness_accounts)
        for account in self.exness_accounts:
            if 'firstTradeDate' in account:
                start_date = dt.strptime(
                    account['firstTradeDate'], '%m/%d/%Y %M:%S').strftime('%Y-%m-%d')
                end_date = dt.strptime(
                    account['lastUpdateDate'], '%m/%d/%Y %M:%S').strftime('%Y-%m-%d')
                print(
                    f"Retrieving data from account {account['accountId']}. period: {start_date} to {end_date}")
                url_get_data_daily = f"{self.api_base_url}get-data-daily.json?session={self.session}&id={account['id']}&start={start_date}&end={end_date}"
                data_request = requests.get(url_get_data_daily).content
                time.sleep(1.2)
                daily_data = json.loads(data_request)

                account_data = []
                for data in daily_data['dataDaily']:
                    account_data.append(data[0])

                account_data = pd.DataFrame(account_data)
                account_data['account_id'] = account['accountId']
                self.accounts_daily_gain.append(account_data)
            else:
                self.empty_accounts.append(account)
                print(
                    f"Account {account['accountId']} without trading records.")
            i -= 1
            print(f"{i} remaning accounts")
        return {'accounts_daily_gain': self.accounts_daily_gain,
                'empty_accounts': self.empty_accounts}

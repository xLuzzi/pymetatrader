# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 23:14:05 2022

@author: Pedro Luzzi pedroluzzisc@gmail.com
"""
import gspread
import gspread_dataframe as gd
import pandas as pd

from api_connect import ApiConnection


def update_sheets(username, password, gsheet_code, path_key):
    """
    Update Google Sheets with MyFXBook data.

    Parameters
    ----------
    username : str
        MyFXBook username.
    password : str
        MyFXBook password.
    gsheet_code : str
        Google sheet code.
    path_key : str | pathlib.Path
       key file path google sheets.
    """
    gkey = gspread.service_account(filename=path_key)
    sheets = gkey.open_by_key(gsheet_code)

    # sheets
    ws_daily = sheets.worksheet('Fechamento Diário por Conta')
    ws_acc = sheets.worksheet('Contas MyFxBook')
    ws_empty = sheets.worksheet('Contas vazias')

    # Get data
    api = ApiConnection(username, password)
    accounts = api.get_accounts()
    accounts = pd.DataFrame(accounts)
    data_daily = api.get_all_accounts_daily_gain()

    data_daily_df = pd.concat(data_daily['accounts_daily_gain'])

    # Format date
    data_daily_df['date'] = pd.to_datetime(data_daily_df['date'])
    empty_accounts = pd.DataFrame(data_daily['empty_accounts'])

    accounts = accounts[['accountId', 'name', 'balance', 'withdrawals',
                         'deposits', 'id', 'gain',
                         'absGain', 'daily', 'monthly', 'interest',
                         'profit', 'demo', 'lastUpdateDate',
                         'drawdown', 'equity', 'equityPercent',
                         'creationDate', 'firstTradeDate', 'tracking', 'views',
                         'commission', 'currency', 'profitFactor', 'pips',
                         'invitationUrl', 'server']]

    empty_accounts = empty_accounts[['accountId', 'name', 'balance',
                                     'withdrawals', 'deposits', 'id',
                                     'gain', 'absGain', 'daily',
                                     'monthly', 'interest',
                                     'profit', 'demo', 'lastUpdateDate',
                                     'drawdown', 'equityPercent',
                                     'creationDate', 'tracking', 'views',
                                     'commission', 'profitFactor', 'pips',
                                     'invitationUrl', 'server']]

    # Copy column 'name' from acc to data_daily_df
    data_daily_df = data_daily_df.merge(accounts[['accountId', 'name']],
                                        left_on='account_id',
                                        right_on='accountId',
                                        right_index=False,
                                        ).drop(columns='accountId')
    data_daily_df.sort_values('date', inplace=True)
    data_daily_df.reset_index(drop=True, inplace=True)
    data_daily_df['date'] = data_daily_df['date'].astype(str)

    # Rewrite sheets
    gd.set_with_dataframe(worksheet=ws_daily, dataframe=data_daily_df)
    gd.set_with_dataframe(worksheet=ws_acc, dataframe=accounts)
    gd.set_with_dataframe(worksheet=ws_empty, dataframe=empty_accounts)

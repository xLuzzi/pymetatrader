# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 19:16:15 2022

@author: Pedro Luzzi pedroluzzisc@gmail.com
"""
from datetime import datetime as dt

from airflow.decorators import dag, task
from airflow.models import Variable


@dag(schedule='@hourly',
     start_date=dt(2022, 12, 29),
     catchup=False,
     tags=['MyFXBook API ETL'])
def update_google_sheets():

    @task
    def update():
        from update_sheet import update_sheets
        user = Variable.get('myfx_user1')
        passw = Variable.get('myfx_pass1')
        gs_code = Variable.get('codigo_sheets1')
        path = Variable.get('path_key')
        update_sheets(user, passw, gs_code, path)

    update()


dag = update_google_sheets()

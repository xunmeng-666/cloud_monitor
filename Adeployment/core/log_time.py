# -*- coding:utf-8-*-

from datetime import datetime
from datetime import timedelta
def logtime(date_count):
    funcDate = 0
    if date_count != 1:
        funcDate = date_count
    now_date = datetime.now().date()
    end_date = now_date - timedelta(funcDate)
    return end_date

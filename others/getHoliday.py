import datetime
import time
from chinese_calendar import is_holiday
def getHoliday():
    now_year = int(time.strftime('%Y', time.localtime(time.time())))
    now_month = int(time.strftime('%m', time.localtime(time.time())))
    now_day = int(time.strftime('%d', time.localtime(time.time())))
    holiday = datetime.date(now_year, now_month, now_day)
    print(holiday)
    print(is_holiday(holiday))
    return is_holiday(holiday)


if __name__=='__main__':
    getHoliday()
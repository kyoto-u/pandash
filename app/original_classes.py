# 独自に作成したclass

from math import *
import time

class TimeLeft():
    time_ms:int
    language:str

    def __init__(self, time_ms, language = 'ja'):
        self.time_ms = time_ms
        self.language = language
    
    def add_ato(self, msg):
        if self.language == 'ja':
            msg = f'あと{msg}'
        else:
            msg = f'{msg} left'
        return msg

    def add_ijyou(self, msg):
        if self.language == 'ja':
            msg = f'{msg}以上'
        else:
            msg = f'more than {msg}'
        return msg
    
    def add_miman(self, msg):
        if self.language == 'ja':
            msg = f'{msg}未満'
        else:
            msg = f'less than {msg}'
        return msg

    def time_left_to_str(self):
        to = {'ja':'と','en':' and '}
        unit_minute_single = {'ja':'分', 'en':' minute'}
        unit_minute = {'ja':'分', 'en':' minutes'}
        unit_hour_single = {'ja':'時間', 'en':' hour'}
        unit_hour = {'ja':'時間', 'en':' hours'}
        unit_day_single = {'ja':'日', 'en':' day'}
        unit_day = {'ja':'日', 'en':' days'}
        unit_week_single = {'ja':'週間', 'en':' week'}
        unit_week = {'ja':'週間', 'en':' weeks'}
        now = floor(time.time())
        seconds = self.time_ms/1000 - now
        minutes = seconds/60
        hours = minutes/60
        days = hours/24
        weeks = days/7
        months = weeks/4
        judge_style = 'one_sec'
        msg =''

        if seconds < 0:
            return {'msg':'','judge':judge_style}
        elif minutes < 1:
            # 一分未満
            msg = self.add_miman('1'+ unit_minute_single[self.language])
            judge_style = 'one_min'
        elif hours < 1:
            # 一時間未満
            judge_style = 'one_hour'
            if floor(minutes) == 1:
                msg = str(floor(minutes)) + unit_minute_single[self.language]
            else:
                msg = str(floor(minutes)) + unit_minute[self.language]
        elif days < 1:
            # 一日未満
            judge_style = 'one_day'
            if floor(minutes) == 1:
                msg = str(floor(hours)) + unit_hour_single[self.language]
            else:
                msg = str(floor(hours)) + unit_hour[self.language]
        elif weeks < 1:
            # 一週間未満
            judge_style = 'one_week'
            if floor(days) == 1:
                msg = str(floor(days)) + unit_day_single[self.language]
            else:
                msg = str(floor(days)) + unit_day[self.language]
        elif months < 1:
            # 一か月(4週間)未満
            judge_style = 'one_month'
            if floor(weeks) == 1:
                msg = str(floor(weeks)) + unit_week_single[self.language]
            else:
                msg = str(floor(weeks)) + unit_week[self.language]

            remain_days = floor(days) - floor(weeks)*7

            if remain_days != 0:
                if remain_days ==1:
                    msg += to[self.language] + str(remain_days) + unit_day_single[self.language]
                else:
                    msg += to[self.language] + str(remain_days) + unit_day[self.language]
        else:
            # 一か月以上
            judge_style = 'one_year'
            msg = self.add_ijyou('4' + unit_week[self.language])
        
        return {'msg':self.add_ato(msg),'judge':judge_style}

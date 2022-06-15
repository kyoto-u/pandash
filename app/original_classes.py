# 独自に作成したclass

from math import *
import time
import enum
from typing import Dict


class Status(enum.Enum):
    """
        課題の取り組み状況・状態を表すclass
    """
    NotYet="未"
    Done="済"
    AlreadyDue="期限切れ"
    def order(self) -> int:
        if self==self.NotYet:
            return 0
        if self==self.Done:
            return 1
        if self==self.AlreadyDue:
            return 2
        return 3

class TimeLeft():
    time_ms:int
    language:str

    def __init__(self, time_ms, language = 'ja'):
        self.time_ms = time_ms
        self.language = language
    
    def add_ato(self, msg) -> str:
        if self.language == 'ja':
            msg = f'あと{msg}'
        else:
            msg = f'{msg} left'
        return msg

    def add_ijyou(self, msg) -> str:
        if self.language == 'ja':
            msg = f'{msg}以上'
        else:
            msg = f'more than {msg}'
        return msg
    
    def add_miman(self, msg) -> str:
        if self.language == 'ja':
            msg = f'{msg}未満'
        else:
            msg = f'less than {msg}'
        return msg

    def time_left_to_str(self) -> Dict[str,str]:
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
        seconds = self.time_ms//1000 - now
        minutes = seconds//60
        hours = minutes//60
        days = hours//24
        weeks = days//7
        months = weeks//4
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
            if days==1:
                judge_style = 'two days'
            elif days==2:
                judge_style = 'three days'
            elif days==3:
                judge_style = 'four days'
            elif days==4:
                judge_style = 'five days'
            elif days==5:
                judge_style = 'six days'
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

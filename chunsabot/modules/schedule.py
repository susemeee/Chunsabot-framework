# -*- coding: utf-8 -*-
from chunsabot.database import Database

from datetime import datetime, timedelta
import time
from multiprocessing.pool import ThreadPool
from multiprocessing import Lock

class TimeNoti:
    @staticmethod
    def print_time(room_id):
        hour = datetime.now().hour()
        amorpm = u"오후" if hour > 12 else u"오전"
        Sockets.Write(room_id, u"현재 시각 {0} {1}시입니다.".format(amorpm, hour%12))

    # @classmethod
    # def on(cls, room_id):
    #     Scheduler.schedule(room_id, print_time)
    #     return "Success"


class SharedScheduler:
    __filepath__ = ".\\data\\schedule_saved"

    def __init__(self, _sockets, rooms=None):
        self.Sockets = _sockets
        self.pool = ThreadPool(processes=1)
        # self.process_list = Database.load_object(SharedScheduler.__filepath__, 'schedules') or []
        # self.l = Lock()

        #merging 'RoomLog' procedure and schedule objects
        from lib.logger import Logger
        self.pool.apply_async(self.process_main, (rooms, Logger.altLogger()))

    def save_object(self):
        Database.save_object(SharedScheduler.__filepath__, self.process_list)

    def schedule(self, room_id, function, start=None, interval=None):
        assert(type(start) is 'datetime' or 'NoneType')
        assert(type(interval) is 'timedelta' or 'NoneType')

        s = Schedule(room_id, function, start)
        self.process_list.append(s)

    def unschedule(self, schedule_id):
        self.l.acquire()
        self.process_list = [p for p in self.process_list if schedule_id != p.id]
        self.l.release()

    def unschedule_all(self, room_id):
        self.l.acquire()
        self.process_list = [p for p in self.process_list if room_id != p.room_id]
        self.l.release()

    def count(self):
        return len(self.process_list)

    def process_main(self, rooms, logger):
        while not self.Sockets.shutdown:
            logger.info(len(rooms))
            time.sleep(60)
            # now = datetime.now().replace(second=0, microsecond=0)
            # for p in self.process_list:
            #     if p.time == now:
            #         p.func(p.room_id)
            #         if p.interval:
            #             p.time = p.time + p.interval

class Schedule():
    gid = 0

    #start == datetime, interval == timedelta
    #we do not compare seconds.
    def __init__(self, room_id, func, start, interval=None):
        self.room_id = room_id
        self.func = func
        self.id = Schedule.gid
        self.time = start.replace(second=0, microsecond=0)
        self.interval = interval if interval else None

        Schedule.gid += 1

    def __repr__(self):
        return str(self.id)

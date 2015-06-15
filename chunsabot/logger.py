import os
import logging

class Logger:
    inited = False

    @staticmethod
    def mainLogger():
        assert(Logger.inited)
        return logging.getLogger('bot')

    @staticmethod
    def altLogger():
        assert(Logger.inited)
        return logging.getLogger('bot_alt')

    @staticmethod
    def init(start_time, store_file=False, store_alt_file=False, real_path=None):
        formatter = logging.Formatter('%(asctime)s|%(levelname)-7s|%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

        if not real_path:
            real_path = os.getcwd()

        path = os.path.join(real_path, "data/logs")
        room_path = os.path.join(real_path, "data/room_logs")
        
        if store_file:
            if not os.path.isdir(path):
                os.makedirs(path)
            
            fh_main = logging.FileHandler(filename=os.path.join(path, u'chat-{0}.log').format(start_time), mode='w')
            fh_main.setFormatter(formatter)
        
        if store_alt_file:
            if not os.path.isdir(room_path):
                os.makedirs(path)

            fh_alt = logging.FileHandler(filename=os.path.join(room_path, 'rooms.log'), mode='a')
            fh_alt.setFormatter(formatter)

        #handlers for console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        
        #assigning handlers for logger
        main = logging.getLogger('bot')
        alt = logging.getLogger('bot_alt')
        main.addHandler(console)
        
        if store_file:
            main.addHandler(fh_main)

        if store_alt_file:           
            alt.addHandler(fh_alt)

        main.setLevel(logging.DEBUG)
        alt.setLevel(logging.DEBUG)

        Logger.inited = True

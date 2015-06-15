import logging

class Logger:
    init = False

    @staticmethod
    def mainLogger():
        assert(Logger.init)
        return logging.getLogger('bot')

    @staticmethod
    def altLogger():
        assert(Logger.init)
        return logging.getLogger('bot_alt')

    @staticmethod
    def init(start_time, store_file):
        # logging.basicConfig(format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.WARNING)
        
        if store_file:
            formatter = logging.Formatter('%(asctime)s|%(levelname)-7s|%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
            fh_main = logging.FileHandler(filename=u'data/logs/chat-{0}.log'.format(start_time), mode='w')
            fh_alt = logging.FileHandler(filename=u'data/room_logs/rooms.log', mode='a')
            fh_main.setFormatter(formatter)
            fh_alt.setFormatter(formatter)

        #handlers for console
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        
        #assigning handlers for logger
        main = logging.getLogger('bot')
        alt = logging.getLogger('bot_alt')
        logging.getLogger('').addHandler(console)
        
        if store_file:
            main.addHandler(fh_main)
            alt.addHandler(fh_alt)

        main.setLevel(logging.DEBUG)
        alt.setLevel(logging.DEBUG)

        Logger.init = True

# -*- coding: utf-8 -*-
import time
from datetime import datetime

from chunsabot.messages import Message, ResultMessage, ContentType
from chunsabot.logger import Logger
from chunsabot.database import Database
from chunsabot.botlogic import Botlogic

#async_status
from threading import Thread
#th_process_msg
from multiprocessing import Queue
from multiprocessing import Process

def default_func(msg=None):
    print("Function not assigned. Please call set_func before async running.")

class Chunsa:
    __leave__ = Database.load_config("leave")

    def set_func(self, write, write_image, leave):
        self.write = write
        self.write_image = write_image
        self.leave = leave


    def __init__(self, real_path=None, profiling=False, check_warning=True, sync=False):
        self.logger = Logger.mainLogger()

        #logger used to log currently connected all rooms
        #serves for research purposes.
        self.room_logger = Logger.altLogger()

        self.debug_users = Database.load_config("debug_users")
        self.debug_mode = Database.load_config("debug_mode")
        self.debug_allowed_room = Database.load_config("debug_allowed_room")

        #'Shutdown' and 'Shutdown_socket' should be separated since some thread inside botlogic refers Chunsa.shutdown
        self.shutdown = False
        self.shutdown_socket = False
        self.profiling = profiling
        self.check_warning = check_warning
        self.sync = sync

        self.th_profile = None    
        self.th_process_pool = None

        self.msg_queue = Queue()
        self.msg_result_queue = Queue()
        self.msg_queue_Shutdown = 'Shutdown'
        self.lock = False

        # used in async_status
        self.p_count = 0
        self.m_count = 0
        self.warning_recv = 0
        self.warning_trans = 0

        self.profiler = profile_logic(self.profiling)
        self.brain = None
        self.init_time = None

        # functions
        self.write = default_func
        self.leave = default_func
        self.write_image = default_func
        self.on_close = default_func

        if not Database.connected and not self.brain:
            Database.init_connection(real_path)
            self.init_time = datetime.now()
            try:
                #passing class references to prevent confusion
                self.brain = Botlogic(self, starttime(), debug=self.debug_mode, real_path=real_path)
            except Exception as e:
                import traceback
                traceback.print_exc()


    def image_ready(self, room_id, user_id):
        return self.brain.image_ready(room_id, user_id)

    def add_msg(self, msg):
        self.msg_queue.put(msg)

    def queue_size(self):
        try:
            size = self.msg_queue.qsize()
        except NotImplementedError:
            size = "Unknown"
        return size

    def async_status(self):
        while not self.shutdown and not self.profiling and not self.shutdown_socket:
          #selfheal logic
            if not self.debug_mode and self.check_warning:
                if self.p_count == 0:
                    self.warning_trans += 1
                if self.m_count == 0:
                    self.warning_recv += 1
                elif self.m_count != 0 and self.warning_recv > 0:
                    self.warning_recv = 0
                if self.warning_recv > 40:
                    self.logger.warning("Socket recieve failed.")
                    self.shutdown_socket = True
                    self.warning_recv = -100
                    # self.close_all()

            print("Reciving messages at {0}/sec".format(self.m_count))
            print("Processing messages at {0}/sec".format(self.p_count))
            self.p_count = 0
            self.m_count = 0
            time.sleep(1)

    def init_process(self, ensure_outgoing, real_path, profiling=False):
        if not self.th_profile and not profiling and not self.debug_mode:
            # self.th_profile = Thread(target=self.async_status)  
            # self.th_profile.start()
            pass
        if not self.th_process_pool:
            self.th_process_pool = Process(target=self.process_msg_async, args=(ensure_outgoing, real_path, ))

    def start_async(self, real_path=None, ensure_outgoing=False, self_reconn=False):
        if self.debug_mode or not self.check_warning:
            timeout = False
        else:
            timeout = True

        if not self_reconn:      
            #count thread start
            self.init_process(ensure_outgoing, real_path, profiling)
            #msg process start
            self.th_process_pool.start()

    def self_reconnect(self):
        self.shutdown_socket = True
        self.start(self_reconn=True)

    def close_sync_process(self):
        self.logger.info("Closing process thread")
        self.brain.save_rooms()
        self.on_close()

    def close_async_process(self):
        self.msg_queue.put(self.msg_queue_Shutdown)
        self.shutdown = True
        self.shutdown_socket = True
        self.on_close()

    def process_msg(self, msg):
        assert(self.sync == True)
        assert(Database.connected and self.brain is not None)
        return self.inner_process(msg)

    def process_msg_async(self):
        assert(self.sync == False)
        assert(Database.connected and self.brain is not None)

        # Message instance
        for msg in iter(self.msg_queue.get, self.msg_queue_Shutdown):
            try:
                self.inner_process(msg)
            except Exception as e:
                self.logger.exception("Process : Something awful happened!")

        self.logger.info("Closing process thread")
        brain.save_rooms()


    def inner_process(self, msg):
        brain = self.brain
        room_id = msg.room_id

        if msg.datetime < self.init_time:
            self.logger.warning("Ignoring outdated messages")

        if msg.attachment:
            attachment = True
        else:
            attachment = False

            if not self.profiling and self.debug_mode:
                try:
                    room = u"@"+room_map[str(room_id)]
                except KeyError:
                    room = u"@"+unicode(room_id)
                #log if debug mode
                try:
                    p = u"{0}{1}: {2}".format(msg.user_name, room, msg.text)
                    self.logger.info(p)
                except UnicodeEncodeError:
                    pass

        self.profiler.start()

        if not self.debug_mode or room_id in self.debug_allowed_room or self.profiling:
            if attachment:
                resp = brain.translate_attachment(msg)
            #not processing messages if is too long               
            elif msg.text.startswith(".") and len(msg.text) < 1000:
                resp = brain.translate(msg.text, msg)
            else:
                resp = brain.translate_not_command(msg)

            assert(type(resp) is str or resp is None or isinstance(resp, ResultMessage))

            if resp:
                if type(resp) is str:
                    if resp == self.__leave__:
                        resp = ResultMessage(resp, content_type=ContentType.Leave)
                    else:                        
                        resp = ResultMessage(resp, content_type=ContentType.Text)

                #[NAME] keyword conversion
                if resp.content_type == ContentType.Text:
                    resp.content = resp.content.replace(u"[NAME]", msg.user_name)

                # exit before sync process returning
                if resp.content_type == ContentType.Exit:
                    if self.sync:
                        self.close_sync_process()
                    else:
                        self.close_async_process()

                if self.sync:
                    return resp
                else:
                    self.write(resp)

                if resp.content_type == ContentType.Leave:
                    self.leave(room_id)

        elif self.debug_mode and room_id not in self.debug_allowed_room:
            self.logger.info("Ignoring non-debug room : {0}".format(room_id))
            self.leave(msg.room_id)

        self.profiler.end()
        self.p_count += 1


def starttime(date_only=False):
    if not date_only:
        return datetime.strftime(datetime.now(), "%m월 %d일 %H시 %M분 %S초")
    else:
        return datetime.strftime(datetime.now(), "%m월 %d일")

class profile_logic:
    """
        Profile logic
    """
    def __init__(self, p):
        self.t = -1
        self.profiling = p

    def start(self):
        if self.profiling:
            self.t = time.time()

    def end(self):
        if self.profiling:
            rt = (time.time() - self.t)*1000                            
            print(str(rt) + "ms")
            if rt > 10:
                # print "Request : "+msg
                # print "Response : "+resp
                if rt > 100:
                    import pdb
                    pdb.set_trace()




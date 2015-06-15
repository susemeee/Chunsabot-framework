# -*- coding: utf-8 -*-
import re
#module load
import os
import imp
import traceback

# botlogic singleton object
brain = None
initialized_once = False

from chunsabot.messages import Message, ResultMessage, ContentType
from chunsabot.logger import Logger
from chunsabot.database import Database
# from chunsabot.modules.schedule import *
from chunsabot.modules.learn import Learnlogic
from chunsabot.modules.verify_url import VerifyUrl

__regex__ = type(re.compile(''))

class Room:
    def __repr__(self):
        return "<Room>\r\nMembers : {3}\r\nMafiagame : {0}\r\nUpanddown : {1}\r\nSilence : {2}".\
        format(self.mafia, self.upanddown, self.silence, self.members)

    def __init__(self):
        self.mafia = None
        self.monster = None
        self.silence = None
        self.upanddown = { 'num' : -1, 'start' : False }
        self.god_list = []
        self.members = []

    def is_personal(self):
        if len(self.members) < 2:
            return True
        else:
            return False

class Botlogic:
    __version__ = "20150614"
    __intversion__ = "1.0.0"
    __roompath__ = "data/room_saved"
    __temppath__ = "data/temp/"
    __leave__ = Database.load_config("leave")

    @staticmethod
    def hello():
        return u"안녕하세요(미소)\r\n** 수호천사의 계정이 변경되었습니다! (chunsabot) \r\n이전 계정은 더 이상 동작하지 않습니다.\r\n.계정을 입력해 보세요.\r\n메시지가 씹힐 때 왜 그런지 알고 싶으면 .더보기 를 입력해 보세요.\r\n.도움말 을 통해서 명령어를 확인할 수 있습니다."

    def __init__(self, _sockets, start_time, debug=False, real_path=None):
        global brain, initialized_once
        assert(not initialized_once)

        brain = self
        self.cache = {}
        self.sockets = _sockets
        self.debug = debug
        self.logger = Logger.mainLogger()

        self.learn = Learnlogic(_sockets)
        self.modules = []
        
        #used at self.status()
        self.start_time = start_time

        self.update_ready = False

        if real_path:
            Botlogic.__roompath__ = os.path.join(real_path, Botlogic.__roompath__)
            Botlogic.__temppath__ = os.path.join(real_path, Botlogic.__temppath__)
        else:
            Botlogic.__roompath__ = os.path.join(os.getcwd(), Botlogic.__roompath__)
            Botlogic.__temppath__ = os.path.join(os.getcwd(), Botlogic.__temppath__)

        if not os.path.isdir(Botlogic.__temppath__):
            self.logger.info("Created Temp directory")
            os.makedirs(Botlogic.__temppath__)

        self.rooms = Database.load_object(Botlogic.__roompath__, 'rooms') or {}

        self.load_all_modules(real_path=real_path)
        initialized_once = True

    def save_rooms(self):
        # self.sch.save_object()
        Database.save_object(Botlogic.__roompath__, self.rooms)
        
    def new_room(self, room_id):
        self.logger.info("joined from {0}".format(str(room_id)))
        self.rooms[room_id] = Room()
        
        if not self.debug:
            return Botlogic.hello()

    def image_ready(self, room_id, user_id):
        return self.learn.is_image_waiting(room_id, user_id)

    def leave(self, room_id):
        self.logger.info("left from {0}".format(str(room_id)))
        del self.rooms[room_id]
        return Botlogic.__leave__


    def startswith(self, target_msg, **kwargs):
        return self.route(target_msg, startswith=True, **kwargs)

    # route(['나가', '꺼져'])(leave)
    # route("안녕")(hello)
    def route(self, target_msg, startswith=False, no_params=False, disable_when_silence=False, **kwargs):
        assert(isinstance(target_msg, (list, str, __regex__)))

        #registering functions into logic 
        def get_func(functions):
            for module in self.modules:
                if module['target'] == target_msg:
                    raise AssertionError("Duplicated message routing : {0}".format(module['func'].__name__))    
            try:
                order = kwargs['order']
            except KeyError:
                order = 0

            args = kwargs.copy()
            args.update({'disable_when_silence' : disable_when_silence, 'startswith' : startswith, 'params' : not no_params})
            self.modules.append({'target' : target_msg, 'func' : functions, 'extras' : args, 'order' : order})

        return get_func

    def load_all_modules(self, real_path=None):
        """
            loads all module in lib/modules.
            from ssut/choco (https://github.com/ssut/choco)
        """
        global initialized_once
        assert(not initialized_once)

        excluded_modules = Database.load_config('excluded_modules', ignore_when_noexist=True)
        home = real_path if real_path else os.getcwd()

        for fn in os.listdir(os.path.join(home, 'chunsabot/modules')):
            name = os.path.basename(fn)[:-3]
            if excluded_modules and name in excluded_modules: 
                continue
            if fn.endswith('.py') and not fn.startswith('_'):
                fn = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modules', fn)
                try: 
                    imp.load_source(name, fn)
                except Exception as e:
                    print("Error loading {0}: {1}".format(name, e))
                    traceback.print_exc()
                    exit(1)

        # ordering list
        self.modules = sorted(self.modules, key=lambda order: order['order'])
    
    def private_status(self):
        # import resource
        # memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024/1024.0
        memory = "???"
        mafia_count = 0
        u_count = 0
        rm_count = 0
        for r in self.rooms.values():
            if r.mafia:
                mafia_count+=1
            if r.upanddown and r.upanddown['start']:
                u_count+=1
            if not r.is_personal():
                rm_count+=1
        
        return u"[수호천사봇의 현재 상태]\r\n활동중인 방의 개수 : {0}\r\n활동중인 방의 개수(개인 대화 제외) : {1}\r\n업앤다운이 진행중인 방의 개수 : {2}\r\n마피아가 진행중인 방의 개수 : {3}\r\n총 배운 단어 : {4}\r\n켜진 시간 : {5}\r\n메모리 사용량 : {6}MB\r\n실패한 처리 시도 횟수 : {7}".\
        format(len(self.rooms), rm_count, u_count, mafia_count, self.learn.msg_map.count(), self.start_time, memory, self.sockets.warning_trans)



    def translate_debug(self, msg, extras):
        """
            Processing debug messages, only the administrator can trigger debug command.
            Debug messages must be started with 'at' sign (@).
            You can register an administrator via editing 'debug_users' in config.yaml.
        """

        if msg in [u"@ㅅㅌ", u"@상태"]:
            return self.private_status()
        elif msg == u"@EnableDebug":
            self.sockets.profiling = True
            import pdb
            pdb.set_trace()
        elif msg.startswith(u"@Setcurse"):
            msg = msg.split(' ', 1)[1]
            if not msg:
                return "No curse given."
            self.learn.add_curse(msg)
            return u"Curse registered."
        elif msg.startswith(u"@DeleteImg"):
            msg = msg.split(' ', 1)[1]
            self.learn.delete_image(msg)    
            return u"{0} image deleted from Database.".format(msg)         
        elif msg.startswith(u"@Delete"):
            self.learn.delete_msg(extra_msg)
            return u"{0} deleted from Database.".format(msg)
        elif msg.startswith(u"@Updateready"):
            self.update_ready = False if self.update_ready else True
            return u"update_ready : {0}".format(str(self.update_ready))
        elif msg == u"@Clean":
            import gc
            return u"{0} object(s) collected.".format(gc.collect())
        elif msg == u"@QSize":
            return u"{0}".format(self.sockets.queue_size())
        elif msg == u"@Exitexit":
            return ResultMessage("", content_type=ContentType.Exit)
        elif msg == u"@CurrentRoom":
            return u"{0}".format(extras["room_id"])
        elif msg == u"@PI":
            from chunsabot.pi import PI
            t = time.time()
            result = PI.calculate()
            return unicode(result)+u"\r\nTook {0} ms".format((time.time() - t)*1000)
        elif msg == u"@Asynctest":
            import time

            def process():
                time.sleep(3)
                self.sockets.write(ResultMessage("asdf", peer=extras['peer']))
                # self.sockets.add_result_msg(ResultMessage("asdf", peer=extras['peer']))

            from threading import Thread
            p = Thread(target=process)
            p.start()

        #Image upload debugging function   
        # elif msg.startswith(u"@IUT") or msg.startswith(u"@IUT_r"):
        #     try:
        #         # send it to different room
        #         if msg.startswith(u"@IUT_r"):
        #             ma = msg.split(' ', 2)
        #             room = int(ma[2])
        #         else:
        #             ma = msg.split(' ', 1)
        #             room = extras['room_id']
        #         msg = ma[1]
        #     except IndexError:
        #         return "please specify full path."

        #     r = self.sockets.kakao.upload_image(msg.encode('utf-8'))
        #     if not r:
        #         return "path error."
        #     else:
        #         if self.debug:
        #             self.logger.debug("IMAGEPATH : msg | IMAGEURL : "+r)
        #         self.sockets.kakao.write_image(room, r, check_result=False)
        # elif msg.startswith(u"@leave"):
        #     self.sockets.kakao.leave(extras['room_id'])
                    

    def translate_not_command(self, msg):
        """
            Processing messages without dot if applicable.
            Currently used for Verify_url class.
        """
        room_id = msg.room_id
        user_id = msg.user_id

        if room_id not in self.rooms:
            r = self.new_room(room_id)
            if r:
                return r

        # pretty rough ideas to distinguish between private chat and group chat.
        # It seems to be quite a not bad idea since it is a comparison between 'one' and 'not-one'.
        room = self.rooms[room_id]
        if user_id not in room.members:
            room.members.append(user_id)

        # toUpperCase required
        if VerifyUrl.url_only_re.match(msg.text.upper()):
            VerifyUrl.async_verify_url(self.sockets, msg.text, room_id)

  
    def translate_attachment(self, msg):
        """
            Processing attachments, in this case, images.
        """
        image_url = msg.attachment
        return self.learn.save_image(image_url, msg)



    def translate(self, msg, extras):
        """
            Getting messages from sockets and processes it
            Everything goes into extras
            (room_id, user_id, user_name)
        """
        # truncating initial dot (.)
        assert(msg.startswith("."))
        msg = msg[1:]

        room_id = extras.room_id
        user_id = extras.user_id
        if room_id not in self.rooms:
            self.new_room(room_id)

        extras = {
            "room" : self.rooms[room_id], 
            "user_id" : user_id,
            "room_id" : room_id,
            "user_name" : extras.user_name,
            "peer" : extras.peer
        }
        
        if msg.startswith(u"@") and user_id in self.sockets.debug_users:
            return self.translate_debug(msg, extras)

        if u"수호천사" in msg:
            return u"ㅎ(부끄)"
        elif msg.startswith(u"안녕"):
            return "안녕하세요~(부끄)"  

        splited_msg = msg.split(" ", 1)
        command = splited_msg[0]
        if len(splited_msg) == 2:
            extra_cmd = splited_msg[1]
        else:
            extra_cmd = None

        if command == u"URL검증":
            return VerifyUrl.info()

        match = False
        #routing to modules
        for module in self.modules:
            target_cmd = module['target']
            if module['extras']['disable_when_silence'] and self.rooms[room_id].silence:
                pass
            else:
                if isinstance(target_cmd, str):
                    if module['extras']['startswith']:
                        if command.startswith(target_cmd):
                            match = True                
                    else:
                        if command == target_cmd:
                            match = True
                elif isinstance(target_cmd, list):
                    if command in target_cmd:
                        match = True
                elif isinstance(target_cmd, __regex__):
                    if target_cmd.match(command):
                        match = True

                if match:
                    if self.debug:
                        self.sockets.logger.debug(module['func'].__name__)
                    
                    if not module['extras']['params']:
                        return module['func']()  
                    # when routed from list or regex, original command will be passed
                    elif isinstance(target_cmd, (list, __regex__)):
                        return module['func'](command, extra_cmd, extras)  
                    else:
                        return module['func'](extra_cmd, extras)


        if not self.rooms[room_id].silence:
            try:
                #image_map
                if msg[0] == u'.':
                    msg = msg[1:]
                    url = self.learn.get_image(msg, room_id)

                    if not url:
                        return None
                    elif url == Learnlogic.__overload__:
                        return url
                    else:
                        return ResultMessage(url, content_type=ContentType.Image)
                else:
                    #msg_map
                    return self.learn.get_msg(msg, room_id)
            except KeyError:
                pass

        return None



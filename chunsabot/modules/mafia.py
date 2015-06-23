# -*- coding: utf-8 -*-

from chunsabot.database import enum
import random
import time
from threading import Timer
from multiprocessing import Process

Gamestate = enum(WAIT=0, NOON=1, NIGHT=2, VOTING=3, END=4)    
        #WAIT NOON NIGHT VOTING END
Job = enum(MAFIA=0, POL=1, DOC=2, SIMIN=3)

class Mafiagame:
    __mafia__ = "마피아의 방@{0}"
    __police__ = "경찰의 방@{0}"
    __doctor__ = "의사의 방@{0}"
    # i = 0
    d = [u'0', u'첫', u'두', u'세', u'네', u'다섯', u'여섯', u'일곱', u'여덟', u'아홉', u'열']
    
    j = [u'마피아', u'경찰', u'의사', u'시민']
    ab = [u'살인', u'수사', u'치료', u'투표']

    c = [u'투표', u'살인', u'수사', u'치료', u'준비', u'준비취소', u'시작', u'게임종료', u'내정보', u'예', u'플레이어']
    l = [None, [1,0,0], None,
    #기본 직업 분배, 나머지는 시민
    #마피아, 경찰, 의사
     [1,  1,  0],
     [1,  1,  1],
     [1,  1,  1],
     [1,  1,  1],
     [2,  1,  1],
     [2,  1,  1],
     [2,  2,  1],
     [3,  2,  1],
     [3,  2,  1],
     [3,  2,  2],
     [4,  2,  2],
     [4,  3,  2],
     [4,  4,  2],
     [4,  4,  2],
     [5,  4,  2],
     [5,  4,  3],
     [6,  4,  3],
     [6,  4,  3]
    ]

    # in seconds
    t_day_time = 360
    t_vote_a_time = 120
    t_vote_time = 120

    m_mafia_first = u"마피아 게임이 시작되었습니다!"
    m_night = u"[DAY]번째 날 밤이 되었습니다. \r\n직업이 있는 분들은 능력을 사용해 주세요. 모든 능력이 사용될 경우 다음으로 넘어갑니다."
    m_day_normal = u"[DAY]번째 날 낮이 되었습니다. \r\n이번 밤에는 아무도 죽지 않았습니다."
    m_day_who_killed_l = [u"[DAY]번째 날 낮이 되었습니다. \r\n[NAME]님이 현장에서 주검으로 발견되었습니다."]
    
    m_vote_timeleft = u"[DAY]번째 날 낮 투표 진행 전까지 [TIME]분 남았습니다."
    m_vote = u"시간이 다 지났습니다. [DAY]번째 날 낮 투표를 진행해 주세요.\r\n투표는 .투표 [이름]으로 할 수 있습니다."
    m_vote_result = u"[투표 결과]\r\n[NAME]님이 [VOTENUM]표를 받아 처형 대상으로 선정되었습니다.\r\n[NAME]님은 최후의 변론을 해 주세요."
    m_ayeornay = u"[찬반 투표 진행]\r\n[NAME]님을 정말 처형하시겠습니까? \r\n.찬성 또는 .반대로 투표해주세요."
    m_vote_killed_l = [u"[NAME]님이 형장의 이슬로 사라졌습니다."]   
    m_vote_not_killed = u"[NAME]님은 처형되지 않았습니다."
    
    m_pol_result = u"[수사 결과]\r\n{0}님은 마피아가 {1}."
    m_ab_confirm = u"[능력 사용]\r\n[NAME]님은 {0}님을 {1}하였습니다."
    m_ab_cancel = u"[능력 사용 취소]\r\n[NAME]님은 {0}을(를) 취소하였습니다."

    m_mafia_init = u"[마피아의 방]\r\n이곳은 직업이 마피아로 결정된 분들이 초대되는 방입니다.\r\n 마피아가 사용하는 능력 (.살인) 은 밤일 경우, 이 방 내에서만 작동합니다.\r\n마피아가 한명이 아닐 경우, 마피아들끼리 대화를 할 수 있습니다."
    m_pol_init = u"[경찰의 방]\r\n이곳은 직업이 경찰로 결정된 분들이 초대되는 방입니다.\r\n 경찰이 사용하는 능력 (.수사) 은 밤일 경우, 이 방 내에서만 작동합니다.\r\n경찰이 한명이 아닐 경우, 경찰들끼리 대화를 할 수 있습니다."
    m_doc_init = u"[의사의 방]\r\n이곳은 직업이 의사로 결정된 분들이 초대되는 방입니다.\r\n 의사가 사용하는 능력 (.치료) 은 밤일 경우, 이 방 내에서만 작동합니다.\r\n의사가 한명이 아닐 경우, 의사들끼리 대화를 할 수 있습니다."

    m_mafia_close_ask = u"[마피아]\r\n현재 진행중인 마피아 게임이 있습니다. 정말 종료하시겠습니까? \r\n(.예 .아니오)"
    m_mafia_close = u"[마피아]\r\n마피아 게임이 종료되었습니다! \r\n[GAMERESULT]"

    m_dup_name_warn = u"마피아 : 중복되는 닉네임 [NAME]님이 있습니다. \r\n카카오톡 프로필에서 닉네임이 겹치지 않도록 변경해 주어야 게임을 진행할 수 있습니다."

    def __init__(self, chatNum, write, cwrite, leave):
        self.write = write
        self.cwrite = cwrite
        self.leave = leave
        self.registered = True

        self.finished = False
        self.cycle_thread = None
        self.total_tick = 0
        self.current_tick = 0

        self.day = 1
        self.is_closing = False
        self.room_id = chatNum
        self.room_mafia = None
        self.room_pol = None
        self.room_doc = None
        self.whodead = 0
        # player_id : playerObj
        self.players = {}
        self.target_player = {u'마피아' : [], u'경찰' : [], u'의사' : [], u'시민' : [] }
        self.state = Gamestate.WAIT

        self.started = False

    # write, cwrite and leave don't support pickling so exclude it
    def __getstate__(self):
        d = dict((k, v) for (k, v) in self.__dict__.items() 
            if k != "write" and k != "cwrite" and k != "leave")
        d["registered"] = False

        return d

    def register_func(self, write, cwrite, leave):
        self.write = write
        self.cwrite = cwrite
        self.leave = leave

    @classmethod
    def mafia_match(cls, room_name):
        if Mafiagame.__mafia__.format("") in room_name or \
            Mafiagame.__doctor__.format("") in room_name or \
            Mafiagame.__police__.format("") in room_name:
            return True
        else:
            return False

    @classmethod
    def info(cls):
        return u"마피아 : 카카오톡으로 하는 마피아 게임!\r\n.준비 명령어로 게임 참여자를 결정하고, .시작 명령어로 게임을 시작할 수 있습니다. \r\n\
(일정 인원을 넘어야 게임을 시작할 수 있습니다)\r\n명령어 : {0}".format(" ".join(cls.c))

    @classmethod
    def print_suitable_numder(cls):
        pass

    @staticmethod
    def filter(msg):
        if u'[DAY]' in msg:
            if self.day > 10:
                pass
            else:
                day = Mafiagame.d[self.day] if self.day != 1 else Mafiagame.d[0]
            msg = msg.replace(u'[DAY]', day)

        if u'[TIME]' in msg:
            pass

        if u'[GAMERESULT]' in msg:
            pass

        if u'[ABILITYNAME]' in msg:    
            pass

        return msg

    def get_player_list(self, job_name, id=False):
        l = []
        if job_name not in Mafiagame.j:
            raise ValueError('Invalid jobInfo')
        for p in self.players.values():
            if p.job == job_name:
                if id:
                    # telegram requires p.peer to create a chat
                    l.append(p.peer)
                else:
                    l.append(p)
        return l

    def translate(self, msg, e):
        peer = e["peer"]
        by = e["by"]
        room_id = e['room_id']
        player_id = e['user_id']
        player_name = e['user_name']
        
        if msg not in Mafiagame.c:
            return u"마피아 : 올바르지 않은 명령어입니다."
        
        res = None
        if msg == u"준비":
            res = self.player_ready(True, player_id, peer=by, player_name=player_name)
        elif msg == u"준비취소":
            res = self.player_ready(False, player_id)
        elif msg == u"시작":
            res = self.start()
        elif msg == u"플레이어":
            res = self.player_info()
    
        if msg == u"게임종료":
            if not self.is_closing:
                self.is_closing = True
                return Mafiagame.m_mafia_close_ask
            else:
                res = self.stop()
        elif msg == u"예":
            if self.is_closing:
                res = self.stop()

        mine = self.players[player_id]

        if len(res) > 1:
            if msg.startswith(u"투표"):
                res = self.vote(mine, res[1], cancel)
            elif msg.startswith(u"살인"):
                if room_id == self.roomid_mafia:
                    res = self.vote(mine, res[1], Job.MAFIA, cancel)
                else:
                    res = u"이곳은 마피아의 방이 아닙니다!"
            elif msg.startswith(u"수사"):
                if room_id == self.roomid_pol:
                    res = self.vote(mine, res[1], Job.POL, cancel)
                else:
                    res = u"이곳은 경찰의 방이 아닙니다!"
            elif msg.startswith(u"치료"):
                if room_id == self.roomid_doc:
                    res = self.vote(mine, res[1], Job.DOC, cancel)
                else:
                    res = u"이곳은 의사의 방이 아닙니다!"
        else:
            res = Mafiagame.info_ability()

        if not res:
            return u"마피아 : 올바르지 않은 명령어입니다."
        else:
            return Mafiagame.filter(res)

    #target_player could be Name or UID
    def vote(self, mine, target_player, vote_by=Job.SIMIN, cancel=False):
        if vote_by == Job.SIMIN and self.state == Gamestate.NIGHT:
            return u"지금은 투표를 할 수 있는 시간이 아닙니다!"
        elif vote_by != Job.SIMIN and self.state != Gamestate.NIGHT:
            return u"지금은 능력을 사용할 수 있는 시간이 아닙니다!"
        
        tp = None
        for p in self.players:
            if p.name == target_player:
                tp = p
                break
        if not tp:
            return u"{0}는 존재하지 않는 플레이어입니다. 투표하지 않았습니다.".format(target_player)
        else:
            if not cancel:
                #vote or use ab
                self.target_player[vote_name].append(tp)
                mine.voted = True
                return Mafiagame.m_ab_confirm.format(target_player, Mafiagame.ab[vote_by])
            else:
                #cancelling
                self.target_player[vote_name].remove(tp)
                mine.voted = False
                return Mafiagame.m_ab_cancel.format(Mafiagame.ab[vote_by])
            

    def player_ready(self, ready, player_id, peer=None, player_name=None):
        assert(type(ready) is bool)
        if ready:
            for p in self.players.values():
                if p.name == player_name:
                    return Mafiagame.m_dup_name_warn

            self.players[player_id] = Player(player_id, player_name, peer)
            return u"마피아 : [NAME]님이 준비하였습니다. \r\n현재 준비한 인원 수 : {0}".format(len(self.players))
        else:
            try:
                del self.players[player_id]
                return u"마피아 : [NAME]님이 준비 취소하였습니다. \r\n현재 준비한 인원 수 : {0}".format(len(self.players))
            except KeyError:
                return None

    def player_info(self):
        l = []
        for v in self.players.values():
            l.append(v.name)

        return u"[현재 플레이어 목록]\r\n{0}".format(" ".join(l))

    """
    one cycle:
        Gamestate.NIGHT
        wait t_night_time seconds
        Gamestate.DAY
        Notify who is dead
        wait t_day_time seconds
        Gamestate.VOTING
        wait t_vote_time seconds
        Gamestate.VOTINGA
        wait t_vote_a_time seconds
        Notify who is dead by vote or not
    """
    def cycle(self):
        while not self.finished:
            print("tick : {0}".format(self.current_tick))
            if self.state == Gamestate.NIGHT:
                pass
            elif self.state == Gamestate.VOTING:
                pass
            elif self.state == Gamestate.NOON:
                pass

            if self.current_tick > 10:
                self.write("asdf", self.room_mafia.peer)
                self.finished = True

            self.total_tick += 1
            self.current_tick += 1
            time.sleep(1)
            

    def start(self):
        if self.started:
            return "[마피아]\r\n게임이 이미 시작되었습니다!"

        #마피아에 맞는 인원수인지 확인
        try:
            app_jobs = Mafiagame.l[len(self.players)]
            if not app_jobs:
                raise IndexError
        except IndexError:
            return u"마피아 : 적정 인원수가 아닙니다.\r\n(적정 인원수 : 4~20명)"
        #직업 분배
        keys = list(self.players.keys())
        random.shuffle(keys)

        for j in range(0, len(self.players)):
            if j < app_jobs[0]:
                self.players[keys[j]].job = Mafiagame.j[0]
            elif j < app_jobs[1]:
                self.players[keys[j]].job = Mafiagame.j[1]
            elif j < app_jobs[2]:
                self.players[keys[j]].job = Mafiagame.j[2]
            else:
                self.players[keys[j]].job = Mafiagame.j[3]
                
        # Debug code
        for p in self.players.values():
            l = p.__repr__()
            print(l)

        self.finished = False
        self.started = True
        # Inviting jobs
        # Inviting method of peers is subject to change.
        self.roomid_mafia = self.cwrite(self.get_player_list('마피아', id=True), Mafiagame.__mafia__.format(self.room_id), messages=Mafiagame.m_mafia_init)
        self.roomid_doc = self.cwrite(self.get_player_list('경찰', id=True), Mafiagame.__police__.format(self.room_id), messages=Mafiagame.m_pol_init)
        self.roomid_pol = self.cwrite(self.get_player_list('의사', id=True), Mafiagame.__doctor__.format(self.room_id), messages=Mafiagame.m_doc_init)

        self.state = Gamestate.NIGHT
        self.cycle_thread = Process(target=self.cycle)
        self.cycle_thread.start()

        return Mafiagame.m_mafia_first

    def stop(self):
        self.finished = True
        self.started = False

        self.leave(self.roomid_mafia)
        self.leave(self.roomid_pol)
        self.leave(self.roomid_doc)

        self.roomid_mafia = None
        self.roomid_pol = None
        self.roomid_doc = None
        return Mafiagame.m_mafia_close

class MafiaRoom:
    def __init__(self, room_id, peer):
        self.room_id = room_id
        self.peer = peer

class Player:
    def __init__(self, player_id, player_name, peer):
        self.id = player_id
        self.name = player_name
        self.job = None
        self.alive = True
        self.voted = False
        self.peer = peer
    
    def __repr__(self):
        return u"Name : {0}, Job : {1}, Alive : {2}, Voted : {3}".format(self.name, self.job, self.alive, self.voted)
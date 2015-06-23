# -*- coding: utf-8 -*-
import random
import re
from chunsabot.botlogic import brain
from chunsabot.chunsa import starttime

# if msg.startswith(u"나가") 
@brain.route([u"나가", u"꺼져"])
def leave(cmd, msg, extras):
    room_id = extras['room_id']
    user_id = extras['user_id']
    
    if brain.debug:
        return u"The administrator has set the bot to not leave the room. This account is created for debugging and testing a new feature. :D"
    if brain.rooms[room_id].silence and brain.rooms[room_id].silence['id'] != user_id:
        if len(brain.rooms[room_id].silence['override']) >= 3:
            return brain.leave(room_id)
        else:
            brain.rooms[room_id].silence['override'].add(user_id)
            return u"조용히 모드를 설정한 사람 ({0})만 .나가 명령어를 쓸 수 있습니다!\r\n(3명 이상 .나가 명령어를 사용할 경우 무시됩니다.)".format(brain.rooms[room_id].silence['name'])
    else:
        return brain.leave(room_id)


@brain.route(u"오늘", no_params=True)
def today():
    return u"오늘은 {0}입니다.".format(starttime(date_only=True))#\r\n혹시 아직도 진짜 정보가 유출되었다고 생각하세요? \r\n그러면 카카오톡을 Internet Explorer로 실행한 후, 보안 프로그램과 키보드 보안 프로그램을 깔아주세요!\r\n여러분의 정보는 nProtect가 책임집니다!".format(brain.Sockets.starttime(date_only=True))

@brain.route(u"통계", no_params=True)
def status():
    return u"[통계]\r\n2월 25일부터 총 {0} 단어를 배웠습니다.\r\n현재 {1}개의 방에서 활동 중입니다.".format(brain.learn.msg_map.count(), len(brain.rooms))

@brain.route([u"조용히", u"조용히해"])
def silence(cmd, msg, extras=None, override=False):
    room_id = extras['room_id']
    user_id = extras['user_id']
    user_name = extras['user_name']

    sobj = brain.rooms[room_id].silence

    if cmd == u"조용히해" and msg == None:
        if sobj:
            return u"조용히 모드가 이미 설정되어 있습니다!"
        else:
            #set contains only one unique value
            sobj = {'id' : None, 'name' : None, 'override' : set() }
            sobj['id'] = user_id
            sobj['name'] = user_name

            #is it a good code?
            brain.rooms[room_id].silence = sobj
            return u"[NAME] 님이 조용히 모드를 활성화하였습니다! (아픔)"
    
    elif msg == u"취소":
        if sobj:
            if sobj['id'] != user_id and not override:
                return u"[NAME] 님은 조용히 모드를 설정하지 않았습니다!\r\n.조용히해 취소는 .조용히를 활성화한 사용자만 사용할 수 있습니다."
            else:
                brain.rooms[room_id].silence = None
                return u"조용히 모드가 해제되었습니다!"
        else:
            return u"현재 조용히 모드가 설정되어있지 않습니다."
    else:
        return u"봇이 단톡방을 터트리는 걸 원하지 않을 때 .조용히해 명령어를 입력하세요!\r\n\
.배우기와 배운 단어가 동작하지 않고, 기타 기능은 작동합니다.\r\n.조용히해 취소 명령어로 해제할 수 있습니다.\r\n\
*주의: .조용히해 취소는 .조용히를 활성화한 사용자만 사용할 수 있습니다."


@brain.route(u"무작위")
def dorandom(msg, extras):
    if msg == None:
        return u"무작위 : 주어진 단어 속에서 무작위로 하나를 골라줍니다.\r\n예) .무작위 사과 딸기 포도"
    else:
        msg = msg.split(' ')
        rand = int(random.random()*1000)%len(msg)
        return u"[무작위]\r\n{0}".format(msg[rand])

# 4면체
@brain.startswith(u"주사위")
def dice(msg, extras):

    def intfromstr(s):
        try:
            return int("".join(re.findall(r'\d', s)))
        except Exception:        
            return None

    n = 6
    if msg and msg.endswith(u"면체"):
        n = intfromstr(msg)

    if not n:
        return u"[주사위]\r\n올바른 숫자가 아닙니다. (.주사위 20면체)"
    elif n < 4:
        return u"[주사위]\r\n{0}면체 도형이 세상에 어디 있어!".format(str(n))

    dice = int(random.random()*10*n)%n+1
    return u"[주사위 (1~{1})]\r\n[NAME]님이 굴린 주사위의 결과는 [{0}] 입니다!".format(str(dice), str(n))


@brain.startswith(u"갓")
def p_god(msg, extras):
    room_id = extras['room_id']

    if not msg:
        return u"갓 목록을 관리하여 줍니다. \n.갓 리스트, .갓 추가, .갓 삭제"
    else:
        msg = msg.split(" ", 1)
        print(msg[0])
        if msg[0] == u"리스트":
            return u"****현재 갓 목록****\n" + " ".join(brain.rooms[room_id].god_list)
        elif msg[0] == u"추가":
            try:
                brain.rooms[room_id].god_list.append(msg[1])
                return u"{0} 님이 갓으로 추가되었습니다.".format(msg[1])
            except:
                return u"올바르지 않은 사용법입니다."
        elif msg[0] == u"삭제":
            try:
                if msg[1] == "@All":
                    brain.rooms[room_id].god_list = []
                    return u"모두 지워졌습니다."
                    
                brain.rooms[room_id].god_list.remove(msg[1])
                return u"{0} 님이 삭제되었습니다.".format(msg[1])
            except:
                return u"올바르지 않은 사용법입니다."
        else:
            return u"{0}은(는) 올바르지 않은 명령어입니다.".format(msg[0])



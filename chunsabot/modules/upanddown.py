# -*- coding: utf-8 -*-
import re
import random
from chunsabot.botlogic import brain
#start of up-and-down logic

number_only = re.compile('^\d+$')

@brain.route(u"업앤다운")
def upanddown_start(msg, extras):
    uobj = brain.rooms[extras['room_id']].upanddown
    if not uobj['start']:
        uobj['start'] = True
        uobj['num'] = int(random.random()*99)
        return u"업 앤 다운 : 게임을 시작합니다. 범위는 0부터 99까지입니다. \r\n숫자는 앞에 .을 붙여야 인식할 수 있습니다."
    else:
        return u"업 앤 다운 : 이미 게임이 진행되고 있습니다."


@brain.route(number_only)
def upanddown(cmd, msg, extras):

    def upanddown_finish(uobj):
        end_str = u"업앤다운 : 축하합니다! [NAME]님이 숫자 {0}을 맞추셨습니다. \r\n게임을 종료합니다.".format(uobj['num'])
        uobj['num'] = -1
        uobj['start'] = False
        return end_str
    
    uobj = brain.rooms[extras['room_id']].upanddown
    d_num = int(cmd)
    try:
        if uobj['num'] == -1 or uobj['start'] == False:
            return u"업 앤 다운 : 시작하시려면 \".업앤다운\" 이라고 보내주세요."

        if d_num not in range(0,100):
            return u"업 앤 다운 : 범위가 정확하지 않습니다."

        if d_num < uobj['num']:
            return u"업"
        elif d_num > uobj['num']:
            return u"다운"
        else:
            return upanddown_finish(uobj)
    except ValueError:
        return u"업 앤 다운 : 잘못된 값입니다."


#end

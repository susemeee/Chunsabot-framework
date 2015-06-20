# -*- coding: utf-8 -*-
from chunsabot.botlogic import brain
from chunsabot.modules.mafia import Mafiagame

@brain.startswith(u"마피아")
def route_mafia(msg, extras):
    #mafia logic (pass to mafia module)
    if not msg:
        return Mafiagame.info()
    else:
        #initialize
        room_id = extras['room_id']
        room = brain.rooms[room_id]

        if not room.mafia:
            if not brain.update_ready:
                room.mafia = Mafiagame(room_id, **brain.sockets.writewrapper())
                return room.mafia.translate(msg, extras)
            else:
                return u"현재 업데이트 준비 중입니다! 새로운 마피아 게임을 시작할 수 없습니다."
        else:
            if not room.mafia.registered:
                room.mafia.register_func(**brain.sockets.writewrapper())
                    
            return room.mafia.translate(msg, extras)

@brain.route(Mafiagame.c)
def route_direct_mafia(cmd, msg, extras):
    room_id = extras['room_id']

#direct command passing (without '마피아')
    if brain.rooms[room_id].mafia:
        return brain.rooms[room_id].mafia.translate(cmd, extras)
    else:
        return u"[마피아]\r\n지금은 마피아 게임 중이 아닙니다! \r\n시작하려면 .마피아 준비 명령어를 입력해주세요."
#end


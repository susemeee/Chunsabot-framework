# -*- coding: utf-8 -*-
import os
import random
import time
import yaml
import sqlite3
try:
    import cPickle as pickle
except:
    import pickle

DB_Create_query = u"CREATE TABLE IF NOT EXISTS {0}(\
    k VARCHAR(100) NOT NULL,\
    v VARCHAR(100) NOT NULL);"

DB_Create_query_room = u"CREATE TABLE IF NOT EXISTS {0}(\
    k VARCHAR(100) NOT NULL,\
    v VARCHAR(100) NOT NULL,\
    room_id VARCHAR(100) NOT NULL);"

DB_Insert_query_room = u"INSERT INTO {0} VALUES('{1}', '{2}', '{3}')"
DB_Insert_query = u"INSERT INTO {0} VALUES('{1}', '{2}')"
DB_Update_query = u"UPDATE {0} SET v='{2}' WHERE k='{1}'"
DB_Select_query = u"SELECT v FROM {0} WHERE k='{1}'"
DB_Select_query_room = u"SELECT v FROM {0} WHERE k='{1}' AND room_id='{2}'"
DB_Delete_query = u"DELETE FROM {0} WHERE k='{1}'"
DB_Delete_query_room = u"DELETE FROM {0} WHERE k='{1}' AND room_id='{2}'"

# Cache_Select_query = u"SELECT v, saved_at FROM {0} WHERE k='{1}'"
# Cache_Update_query = u"UPDATE {0} SET v='{2}', saved_at={3} WHERE k='{1}'"
# Cache_Insert_query = u"INSERT INTO {0} VALUES('{1}', '{2}', {3})"

class Database(dict):
    conn = None
    c = None

    connected = False

    #load config
    try:
        cfg_path = os.path.join(os.getcwd(), "data/config.yaml")
        if not os.path.isfile(cfg_path):
            _file = os.path.realpath(__file__)
            _file = _file[:_file.rfind("/")]
            cfg_path = os.path.join(_file, "..", "data/config.yaml")

        cfg_object = yaml.load(open(cfg_path, "r").read())
        print("Config load succeeded.")
    except IOError:
        cfg_object = {}
        print(u"/data/config.yaml 파일이 존재하지 않습니다. \nbot.py --make-initial-config로 설정 파일을 만들어 주세요.")

    @staticmethod
    def mkdir():        
        cfg_dir = Database.cfg_path[:Database.cfg_path.rfind('/')]
        if not os.path.isdir(cfg_dir):
            os.makedirs(cfg_dir)


    @staticmethod
    def config_exists():
        if os.path.isfile(Database.cfg_path):
            return True
        else:
            return False


    @staticmethod
    def init_connection(real_path):
        #load database
        if real_path:
            file_path = os.path.join(real_path, "data/database.yangpa")
        else:
            file_path = os.path.join(os.getcwd(), "data/database.yangpa")
            Database.cfg_path = os.path.join(os.getcwd(), "data/config.yaml")

        Database.conn = sqlite3.connect(file_path)
        Database.c = Database.conn.cursor()
        Database.connected = True

    def __init__(self, name, room_specific=False):
        self.name = name
        if Database.c:
            if room_specific:
                Database.c.execute(DB_Create_query_room.format(name))                
            else:
                Database.c.execute(DB_Create_query.format(name))
        else:
            raise Exception('Database not connected')

    def __getitem__(self, key):
        return self.load(key)

    def __setitem__(self, key, value):
        return self.save(key, value)

    def count(self):
        Database.c.execute("SELECT COUNT(*) FROM msg_map")
        return Database.c.fetchone()[0]

    def save(self, key, value, room=None):
        key = key.replace("'", "''")
        value = value.replace("'", "''")
        # try:
        #     self.load(key)
        #     Database.c.execute(DB_Update_query.format(self.name, key, value))
        # except KeyError:
        
        #accepts duplicate value
        if room:
            Database.c.execute(DB_Insert_query_room.format(self.name, key, value, room))
        else:
            Database.c.execute(DB_Insert_query.format(self.name, key, value))

        Database.conn.commit()


    def load(self, key, room=None, strict=False):  
        key = key.replace("'", "''")

        if not room:
            Database.c.execute(DB_Select_query.format(self.name, key))
        else:
            Database.c.execute(DB_Select_query_room.format(self.name, key, room))

        row_array = Database.c.fetchall()
        
        if len(row_array) < 1:
            if not room or strict:
                raise KeyError
            else:
                return self.load(key, None)
        elif len(row_array) > 1:
            #randomly select value
            rand = int(random.random()*len(row_array))
            #tuple (<value>, )
            return row_array[rand][0]
        else:
            return row_array[0][0]
        
    def delete(self, what, room_id=None):
        if not room_id:
            Database.c.execute(DB_Delete_query.format(self.name, what))
        else:
            Database.c.execute(DB_Delete_query_room.format(self.name, what, room_id))

        return Database.c.rowcount
        
    @staticmethod
    def load_config(d, ignore_when_noexist=False):
        try:
            return Database.cfg_object[d]
        except KeyError as e:
            if ignore_when_noexist:
                pass
            else:
                print(u"config.yaml에 누락된 값이 있습니다. {0}".format(e))
                raise KeyError(e)

    @staticmethod
    def check_config(d):
        try:
            return Database.cfg_object[d]
        except KeyError:
            return False

    @staticmethod
    def save_config(d, v):
        Database.cfg_object[d] = v
        with open(Database.cfg_path, 'wb') as outfile:
            outfile.write(yaml.dump(Database.cfg_object, default_flow_style=False, encoding='utf-8', allow_unicode=True))
    
    @staticmethod
    def load_object(path, name=''):
        try:
            cp = open(path, 'rb').read()
            cp = pickle.loads(cp)
            print("{0} loaded from saved file".format(name))
            return cp
        except Exception:
            print(u"방 저장된 정보 불러오기 실패 - 처음 실행하나요?")
            return None

    @staticmethod
    def save_object(path, object):
        with open(path, 'wb') as cp:
            cp.write(pickle.dumps(object))
            cp.flush()
            cp.close()

class Cache:
    c = {}
    VAL = "value"
    TIME = "time"

    @staticmethod
    def create(v):
        return {Cache.VAL : v, Cache.TIME : time.time()}

    @staticmethod
    def load(k, time_limit=3600):
        now = time.time()
        # Database.c.execute(Cache_Select_query.format("cache", k))
        # row = Database.c.fetchone()
        try:
            row = Cache.c[k]
        except KeyError:
            return None

        # if not row:
            # return None
        if now - int(row[Cache.TIME]) > time_limit:
            #1 hour is 3600 sec
            #expired!
            return None
        else:
            return row[Cache.VAL]

    @staticmethod
    def save(k, v):
        Cache.c[k] = Cache.create(v)
        # Database.c.execute(Cache_Update_query.format("cache", k, v, int(time.time())))
        # #checking update query
        # if Database.c.rowcount == 0:
        #     Database.c.execute(Cache_Insert_query.format("cache", k, v, int(time.time())))
        # Database.conn.commit()

    #overrided method for Pickle
    @staticmethod
    def write(v):
        Cache.save('rooms', v)


def enum(**enums):
    return type('Enum', (), enums)


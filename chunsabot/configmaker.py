# -*- coding: utf-8 -*-

from chunsabot.database import Database

def make_initial_config():
    Database.mkdir()

    if Database.config_exists():
        print("There exists account info. \r\nReally overwrite config file? (Y / N)")
        if input().lower() == "y":
            result = True
        else:
            result = False
    else:
        print("There isn't default config file (data/config.yaml). Do you want to generate default config file? (Y / N)")
        if input().lower() == "y":
            result = True
        else:
            result = False

    if result:
        Database.save_config('leave', u"안녕히 계세요!")
        Database.save_config('debug_users', [])
        Database.save_config('curse_map', [])
        Database.save_config('sensitive_map', [])
        Database.save_config('debug_allowed_room', [])
        Database.save_config('debug_users', [])
        Database.save_config('debug_mode', False)    
        Database.save_config('google_api_key', '')    
        Database.save_config('weather_url_all', 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp')

        print("Config sucessfully saved.")
    else:
        print("Configmaker work cancelled.")
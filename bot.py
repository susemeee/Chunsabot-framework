#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 susemine*.

Author: Suho Lee (susemeee@gmail.com)

Chunsabot is following MIT License. (check LICENSE)

"""

import telepot

from chunsabot.database import Database
API_KEY = Database.load_config('telegram_api_key')

bot = telepot.Bot(API_KEY)
print(bot.getMe())

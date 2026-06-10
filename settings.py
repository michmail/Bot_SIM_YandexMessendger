# -*- coding: utf-8 -*-
import re
from os import getenv

from Utilities import (
    MySQL)

from Utilities.Telegram import dp

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

dp, Bot = dp(Token := getenv('Token', '1154697542:AAHlWsqzdBFqULOLyNvB8bGCwMDh40MYbws'))
ID, DB, Company = int(re.match(r'\d+', Token).group()), MySQL.mysql(database='ES_Driver_Bot'), getenv('Company', 'URent')
scheduler, loop = AsyncIOScheduler(), asyncio.get_event_loop().run_until_complete


Monitors = [region['Monitor_Chat_ID'] for region in loop(MySQL.select({'Bot': Company}, '- Monitor_Message_ID', 'regions', DB))]

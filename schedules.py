# -*- coding: utf-8 -*-
import keyboards as kb

from settings import (
    Bot, DB, scheduler,
    Company)
from Utilities import (
    Logger, MySQL)


async def monitor_daily():
    for region in await MySQL.select({'Bot': Company}, '- Monitor_Message_ID', 'regions', DB):
        # monitor_pin(region['Name'], context)
        
        await MySQL.insert({'Monitor_Message_ID': (
            message := await Bot.send_message(
                region['Monitor_Chat_ID'],
                "#Монитор", reply_markup=
                kb.monitor_pin,
                disable_notification=True)
        ).message_id}, {'Monitor_Chat_ID': region['Monitor_Chat_ID']}, '1', 'regions', DB)
        await Bot.pin_chat_message(region['Monitor_Chat_ID'], message.message_id, disable_notification=True)
        await Bot.delete_message(region['Monitor_Chat_ID'], message.message_id + 1)
        await Bot.unpin_chat_message(region['Monitor_Chat_ID'], message_id=region['Monitor_Message_ID'])
scheduler.add_job(monitor_daily, 'cron', hour=5)


async def push_to_gateway():
    scheduler.pause_job('push_to_gateway')
    Logger.metrics.push()
    scheduler.resume_job('push_to_gateway')
scheduler.add_job(push_to_gateway, 'interval', seconds=30, id='push_to_gateway')

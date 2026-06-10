# -*- coding: utf-8 -*-
import datetime as dt

import keyboards as kb

from settings import (
    Bot, DB)
from Utilities import (
    MySQL)
from requests_ import (
    SQL)

from Utilities.Telegram import (
    html_user)


async def monitor_shift(data: str, shift: dict, user: dict) -> str:
    now = dt.datetime.now()
    
    text = f"{html_user(user, '', 'Emoji', 'Name', 'Surname')}\n" \
           f"🕰️ {(now if data == 'START' else shift['Start']).strftime('%H:%M')}-" + \
           (f"{(now if data == 'FINISH' else shift['Finish']).strftime('%H:%M')} ✅🆔{shift['ID']}"
            if data == 'FINISH' or shift['Status'] == "⏹" else "") + "\n"
    if data in ('SHIFT', 'FINISH'):
        text += "".join(
            f"{parking['Icon']}{parking['Count']} "
            for parking in await SQL.monitor_shift(shift))
    return text


async def monitor_pin(region):
    date = dt.datetime.combine(((now := dt.datetime.now()) - dt.timedelta(days=1 if now.hour < 5 else 0)).date(), dt.time(5))
    region = await MySQL.select({'Name': region}, '1', 'regions', DB)
    
    text = f"📅{now.strftime('%d.%m')} #Монитор на {now.strftime('%H:%M')}\n\n" + " ".join(
        f"{a['Icon']}{a['Count']}"
        for a in await SQL.monitor_total(region, date))
    text += "\n"
    for shift in await SQL.monitor_shifts(region, date):
        activities = f"\n{shift['Status']}" + "".join(
            f"{a['Icon']}{a['Count']} "
            for a in await SQL.monitor_count(shift))
        text += f"{html_user(shift, activities, 'Name', 'Surname')}"
    
    await Bot.edit_message_text(
        chat_id=region['Monitor_Chat_ID'], message_id=region['Monitor_Message_ID'], text=
        text, reply_markup=
        kb.monitor_pin)

# -*- coding: utf-8 -*-
import re
import datetime as dt

import texts
import keyboards as kb

from settings import (
    dp, Bot, DB,
    Monitors)
from Utilities import (
    Logger, MySQL)
from requests_ import (
    SQL)

from Utilities.Telegram import (
    interface_)


@dp.message_handler(content_types=('text', 'venue', 'photo'), chat_id=Monitors)
@dp.callback_query_handler(regexp='MONITOR', chat_id=Monitors)
async def monitor(up):
    if not (interface := await interface_(up, 'MONITOR')):
        return False
    if not (user := await MySQL.select({'ID': up.from_user.id}, '1', 'users', DB)):
        return Logger.message("User ❌", up)
    now = dt.datetime.now()
    
    if interface == 'Keyboard':
        data = up.data.replace('MONITOR_', '', 1)
        if 'MONITOR' in data:
            data = data.replace('MONITOR_', '', 1)
            if data == 'PHOTO':
                await up.message.delete()
                
                return Logger.keyboard("Photo ✅", up)
            shift = await MySQL.select({'ID': (await SQL.shift_id(up.message))[0]['ID']}, '1', 'drivers', DB)
            
            if data in ('SHOW', 'HIDE'):
                await up.message.edit_reply_markup(
                    await kb.monitor_show(shift['ID']) if data == 'SHOW' else kb.monitor_hide)
                
                return Logger.keyboard(f"{data.capitalize()} ✅", up)
            elif 'PARKINGS' in data:
                await up.message.edit_text(
                    await texts.monitor_shift('SHIFT', shift, await MySQL.select({'ID': shift['User_ID']}, '1', 'users', DB)), reply_markup=
                    await kb.monitor_show(shift['ID']))
                
                if 'PARKINGS_' in data:
                    await Bot.delete_message(up.message.chat.id, data.replace('PARKINGS_', '', 1))
                
                return Logger.keyboard("Parkings ✅", up)
            elif 'PARKING' in data:
                parking = (await SQL.parkings())[(parking_ := await SQL.monitor_parking(data.replace('PARKING_', '', 1)))[0]['ID']]
                await up.message.edit_text(
                    f"{parking_[0]['Activity']}{len(parking_)} {parking['Type']}{parking['Name']}\n" + "\n".join(
                        f"🛴{b['Bike_ID']}" for b in parking_), reply_markup=
                    await kb.monitor_parking(parking_[0]['Photo'], up))
                
                return Logger.keyboard("Parkings ✅", up)
        elif up.message.reply_to_message and user['ID'] == up.message.reply_to_message.from_user.id and 'ACTIVITY' in data:
            shift = await MySQL.select({'Status': ["⏩", "⏸"], 'User_ID': user['ID']}, '1', 'drivers', DB)
            
            if parking := await MySQL.select({'Parking_ID': 0, 'Driver_ID': shift['ID']}, '1', 'parkings', DB):
                await MySQL.insert({'Activity': "⚠️", 'Parking_ID': -1, 'Photo': "ABANDON SHIP"},
                                   {'ID': parking['ID']}, '1', 'parkings', DB)
            elif parking := await MySQL.select({'Photo': "", 'Driver_ID': shift['ID']}, '1', 'parkings', DB):
                await MySQL.insert({'Photo': "ABANDON SHIP"}, {'ID': parking['ID']}, '1', 'parkings', DB)
            
            parking = await MySQL.create({
                'Activity': (activity := data.replace('ACTIVITY_', '', 1)),
                'Parking_ID': 0, 'Time': now, 'Photo': "" if activity == "✅" else "Photo",
                'Driver_ID': shift['ID']}, 'parkings', DB)
            for bike in re.findall(r'\d{8}|\d{6}|\d{4}', up.message.reply_to_message.text):
                await MySQL.create({
                    'Parking_ID': parking, 'Bike_ID': bike
                }, 'bikes', DB)
            
            await MySQL.insert({'Message_ID': up.message.message_id}, {'ID': shift['ID']}, '1', 'drivers', DB)
            await up.message.edit_text(
                f"{activity} {up.message.text[1:]}", reply_markup=
                kb.monitor_parkings)
            await up.message.reply_to_message.delete()
            await Bot.delete_message(up.message.chat.id, shift['Message_ID'])
            
            await texts.monitor_pin(user['Region'])
            
            return Logger.keyboard("Activity ✅", up)
    elif interface == 'Message':
        if up.venue and up.venue.address == "":
            await up.delete()
        
        elif shift := await MySQL.select({'Status': ["⏩", "⏸"], 'User_ID': user['ID']}, '1', 'drivers', DB):
            if (text := up.text) and re.fullmatch(r"((S.|)(\d{8}|\d{6}|\d{4})((\r\n|\r|\n)| |))+(Итого: \d{1,3}|)", text):
                await up.reply(
                    "🛴" + str(len(re.findall(r'\d{8}|\d{6}|\d{4}', text))), reply_markup=
                    await kb.monitor_activities(user['Region']))
                
                return Logger.message("Bikes ✅", up)
            elif photo := up.photo:
                if parking := await MySQL.select({'Photo': "", 'Driver_ID': shift['ID']}, '1', 'parkings', DB):
                    await MySQL.insert({'Photo': photo.pop().file_id}, {'ID': parking['ID']}, '1', 'parkings', DB)
                    await up.delete()
                    
                    await Bot.edit_message_text(
                        chat_id=up.chat.id, message_id=shift['Message_ID'], text=
                        await texts.monitor_shift('SHIFT', shift, user), reply_markup=
                        kb.monitor_hide)
                    
                    return Logger.message("Photo ✅", up)
                else:
                    await up.reply(
                        "🅿️ Сначала выбери парковку! ⚠️")
                    
                    return Logger.message("Photo ❌", up)
        elif text := up.text:
            if 'Monitor' in text:
                await up.delete()
                
                pin_message_id = await MySQL.retrieve('Monitor_Message_ID', {'Monitor_Chat_ID': up.chat.id}, 'regions', DB)
                await MySQL.insert({'Monitor_Message_ID': (
                    message := await up.reply(
                        "#Монитор",
                        allow_sending_without_reply=True)
                ).message_id}, {'Monitor_Chat_ID': up.chat.id}, '1', 'regions', DB)
                await Bot.pin_chat_message(up.chat.id, message.message_id)
                await Bot.delete_message(up.chat.id, message.message_id + 1)
                await Bot.unpin_chat_message(up.chat.id, message_id=pin_message_id)
                
                return Logger.message("Monitor ✅", up)
            elif '/region' in text:
                if user['Region'] != (region := await MySQL.retrieve('Name', {'Monitor_Chat_ID': up.chat.id}, 'regions', DB)):
                    await MySQL.insert({'Region': region}, {'ID': user['ID']}, '1', 'users', DB)
                    await up.reply(
                        f"Новый регион: {region}")
                    
                    return Logger.message("Region ✅", up)

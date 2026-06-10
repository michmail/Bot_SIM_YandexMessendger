# -*- coding: utf-8 -*-
import re
import datetime as dt

import texts
import keyboards as kb

from settings import (
    dp, Bot, DB)
from Utilities import (
    Logger, MySQL)
from requests_ import (
    SQL)
from Utilities.Utilities import (
    Vincenty)

from Utilities.Telegram import (
    types,
    inline_answer)


async def monitor_shift(user, now, up, geo):
    await inline_answer(up, {
        'ID': 'SHIFT_START',
        'Title':
            f"🚚 Выйти на смену"
    } if not await MySQL.select({'Status': ["⏩", "⏸"], 'User_ID': user['ID']}, '1', 'drivers', DB) else {
        'ID': 'SHIFT_FINISH',
        'Title':
            f"🛌 Завершить смену"})
    
    return Logger.iQuery("Shift ✅", up)


async def monitor_parks(user, now, up, geo):
    if not (driver := await MySQL.select({'Status': ['⏩', '⏸'], 'User_ID': user['ID']}, '1', 'drivers', DB)):
        await inline_answer(up, {
            'Title':
                "🚚 Сначала выйди на смену!"})
        
        return Logger.iQuery("Parks ❌", up)
    if not (parking := await MySQL.select({'Parking_ID': 0, 'Driver_ID': driver['ID']}, '1', 'parkings', DB)):
        await inline_answer(up, {
            'Title':
                "🛴Сначала отправь самокаты!"})
        
        return Logger.iQuery("Parks ❌", up)
    parkings = await SQL.parkings()
    await inline_answer(
        up,
        *[{'ID': f'PARKING_{key}', 'Geo': (point['Latitude'], point['Longitude']),
           'Title':
               f"{point['Type']} {point['Name']}"}
          for key, point in parkings.items() if (point['Type'] == "🚛" if parking['Activity'] != "✅" else 1) and
          Vincenty(geo.latitude, geo.longitude, point['Latitude'], point['Longitude']) < (1000 if point['Type'] == "🚛" else 100)] or
         [{'Title':
               "🗺️ Подойди ближе к парковке!"}])
    
    return Logger.iQuery("Parks ✅", up)


async def foundling(user, now, up, geo):
    parkings = await SQL.parkings()
    await inline_answer(
        up,
        {'ID': 'NONE', 'Geo': (geo.latitude, geo.longitude),
         'Title':
             f"🛴{up.query} ⚠️",
         'Description':
             "Прошу забрать"},
        *[{'ID': bike['ID'], 'Geo': ((parking := parkings[bike['Parking_ID']])['Latitude'], parking['Longitude']),
           'Title':
               f"🛴{up.query} {bike['Activity']}{bike['Time']}",
           'Description':
               f"{parking['Type']}{parking['Name']}"}
          for bike in await SQL.foundling(up.query)], answer='Venue')
    
    return Logger.iQuery("Foundling ✅", up)


queries = {
    re.compile("(?i)Смена"): monitor_shift,
    re.compile(r"\A\Z"): monitor_parks,
    re.compile(r"\d{8}|\d{6}|\d{4}"): foundling,
}


@dp.inline_handler()
async def query_(up: types.InlineQuery):
    if not (geo := up.location):
        await inline_answer(up, {
            'Title':
                "🗺️ Сначала включи геолокацию!",
            'Description':
                "❗Необходимо дать Telegram\n"
                "постоянный доступ в настройках"})
        
        return Logger.iQuery("Geo ❌", up)
    if not (user := await MySQL.select({'ID': up.from_user.id}, '1', 'users', DB)):
        result = {
            'Title':
                "🚛 Подойди на 1 км к Складу!"}
        for region in await MySQL.select('', '', 'warehouses', DB):
            if Vincenty(geo.latitude, geo.longitude, region['Latitude'], region['Longitude']) < 1000:  # 1 km
                await MySQL.create({
                    'Date': dt.datetime.now(), 'Region': region['Parking_ID'][:-2],
                    'Name': up.from_user.first_name, 'Surname': up.from_user.last_name or "",
                    'ID': up.from_user.id}, 'users', DB)
                
                result = {
                    'Title':
                        "✅ Регистрация пройдена!"}
                break
        await inline_answer(up, result)
        
        return Logger.iQuery("Registration ✅", up)
    Logger.iQuery(up.query, up)
    
    for query, function in queries.items():
        if query.fullmatch(up.query):
            return await function(user, dt.datetime.now(), up, geo)
    await inline_answer(up, {
        'Title':
            "❌ Неправильный запрос!"})
    
    return Logger.iQuery("❌", up)


@dp.chosen_inline_handler()
async def result_(up: types.ChosenInlineResult):
    Logger.iResult(data := up.result_id, up)
    
    if data == 'NONE':
        return True
    now = dt.datetime.now()
    user = await MySQL.select({'ID': up.from_user.id}, '1', 'users', DB)
    region = await MySQL.select({'Name': user['Region']}, '1', 'regions', DB)
    shift = await MySQL.select({'Status': ["⏩", "⏸"], 'User_ID': user['ID']}, '1', 'drivers', DB)
    
    if 'SHIFT' in data:
        data = data.replace('SHIFT_', '', 1)
        if data == 'START':
            shift = {
                'Status': "⏩", 'Start': now, 'Finish': now + dt.timedelta(days=1),
                'User_ID': user['ID']}
            shift['ID'] = await MySQL.create(shift, 'drivers', DB)
        elif data == 'FINISH':
            await MySQL.insert({'Status': "⏹", 'Finish': now}, {'ID': shift['ID']}, '1', 'drivers', DB)
            await Bot.delete_message(region['Monitor_Chat_ID'], shift['Message_ID'])
        
        await MySQL.insert({'Message_ID': (
            await Bot.send_message(
                region['Monitor_Chat_ID'],
                await texts.monitor_shift(data, shift, user), reply_markup=
                kb.monitor_hide if data == 'FINISH' else None)
        ).message_id}, {'ID': shift['ID']}, '1', 'drivers', DB)
        
        return Logger.iResult("Shift ✅", up)
    elif 'PARKING' in data:
        await MySQL.insert({'Parking_ID': data.replace('PARKING_', '', 1)},
                           {'ID': await MySQL.retrieve('ID', {'Parking_ID': 0, 'Driver_ID': shift['ID']}, 'parkings', DB)}, '1', 'parkings', DB)
        
        await Bot.edit_message_text(
            chat_id=region['Monitor_Chat_ID'], message_id=shift['Message_ID'], text=
            await texts.monitor_shift('SHIFT', shift, user), reply_markup=
            await kb.monitor_show(shift['ID']))
        
        return Logger.iResult("Parking ✅", up)

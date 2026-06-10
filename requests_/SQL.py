# -*- coding: utf-8 -*-
import datetime as dt

from ES_Driver_Bot.settings import (
    DB)
from Utilities import (
    MySQL, MongoDB)


async def parkings() -> dict: return {
    '0': {'Name': "Ожидание...", 'Type': "🔄", 'Latitude': 0, 'Longitude': 0},
    '-1': {'Name': "ОШИБКА", 'Type': "📛", 'Latitude': 0, 'Longitude': 0},
    **{parking['ID']: parking for parking in await MySQL.select('', '', 'parkings', MongoDB.DB)},
    **{warehouse['ID']: warehouse for warehouse in await MySQL.execute('''SELECT
    Parking_ID AS ID, CONCAT_WS(" ", "Склад", Name) AS Name, "🚛" AS Type, Latitude, Longitude
    FROM warehouses
    ''', DB)}}


async def monitor_shift(shift: dict) -> list: return await MySQL.execute(f'''SELECT
Icon, COUNT(*) AS Count
FROM bikes
JOIN parkings ON bikes.Parking_ID = parkings.ID
JOIN activities ON Activity = Icon
WHERE Driver_ID = {shift['ID']}
GROUP BY Activity
ORDER BY activities.ID
''', DB)


async def monitor_total(region: dict, date: dt.datetime) -> list: return await MySQL.execute(f'''SELECT
Icon, COUNT(*) AS Count
FROM bikes
JOIN parkings ON bikes.Parking_ID = parkings.ID
JOIN activities ON Activity = Icon
JOIN drivers ON Driver_ID = drivers.ID
JOIN users ON User_ID = users.ID
WHERE Start > "{date}" AND Region = "{region['Name']}"
GROUP BY Activity
ORDER BY activities.ID
''', DB)


async def monitor_shifts(region: dict, date: dt.datetime) -> list: return await MySQL.execute(f'''SELECT
Status, drivers.ID AS Driver_ID, users.ID, Surname, CONCAT(LEFT(Name, 1), ".") AS Name
FROM drivers
JOIN users ON User_ID = users.ID
WHERE Start > "{date}" AND Region = "{region['Name']}"
''', DB)


async def monitor_count(shift: dict) -> list: return await MySQL.execute(f'''SELECT
Icon, COUNT(*) AS Count
FROM bikes
JOIN parkings ON bikes.Parking_ID = parkings.ID
JOIN activities ON Activity = Icon
WHERE Driver_ID = {shift['Driver_ID']}
GROUP BY Activity
ORDER BY activities.ID
''', DB)


async def driver_parkings(driver_id) -> list: return await MySQL.execute(f'''SELECT
parkings.ID, DATE_FORMAT(Time, "%H:%i") AS Time, Activity, COUNT(*) AS Count, parkings.Parking_ID, Photo
FROM bikes
JOIN parkings ON bikes.Parking_ID = parkings.ID
WHERE Driver_ID = {driver_id}
GROUP BY parkings.ID
ORDER BY parkings.Time
''', DB)


async def shift_id(up) -> list: return await MySQL.execute(f'''SELECT
drivers.ID
FROM drivers
JOIN users ON User_ID = users.ID
JOIN regions ON Region = regions.Name
WHERE Message_ID = {up.message_id} AND Monitor_Chat_ID = {up.chat.id}
''', DB)


async def monitor_parking(parking_id: str) -> list: return await MySQL.execute(f'''SELECT
Photo, parkings.Parking_ID AS ID, Activity, Bike_ID
FROM bikes
JOIN parkings ON bikes.Parking_ID = parkings.ID
WHERE parkings.ID = {parking_id}
''', DB)


async def foundling(bike_id: str): return await MySQL.execute(f'''SELECT
bikes.ID, Activity, DATE_FORMAT(Time, "%d.%m %H:%i") AS Time, parkings.Parking_ID
FROM bikes
JOIN parkings ON bikes.Parking_ID = parkings.ID
WHERE Bike_ID = {bike_id}
ORDER BY parkings.Time DESC
LIMIT 5
''', DB)

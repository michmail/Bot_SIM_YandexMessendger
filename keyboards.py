# -*- coding: utf-8 -*-
from settings import (
	DB)
from Utilities import (
	MySQL)
from requests_ import (
	SQL)


async def monitor_activities(region: str) -> dict: return {'inline_keyboard': [
	[
		{'callback_data': f"MONITOR_ACTIVITY_{activity['Icon']}",
		 'text': activity['Icon']}
		for activity in await MySQL.select({region: 1}, '- ID', 'activities', DB)
	]
]}


async def monitor_show(driver_id) -> dict:
	parkings = await SQL.parkings()
	return {
		'inline_keyboard':
			[
				[
					{'callback_data': f"MONITOR_MONITOR_PARKING_{parking['ID']}",
					 'text': f"{'🏞️ ' if not parking['Photo'] else ''}{parking['Time']} {parking['Activity']}{parking['Count']} "
							 f"{parkings[parking['Parking_ID']]['Type']}{parkings[parking['Parking_ID']]['Name']}"}
				]
				for parking in await SQL.driver_parkings(driver_id)
			] +
			[
				[
					{'callback_data': 'MONITOR_MONITOR_HIDE',
					 'text': "➖"}
				]
			]
	}


async def monitor_parking(photo: str, up): return {'inline_keyboard': [
	[
		{'callback_data': 'MONITOR_MONITOR_PARKINGS' + (
			f"_{(await up.message.reply_photo(photo, reply_markup=monitor_photo)).message_id}"
			if photo not in ('Photo', 'ABANDON SHIP', '') else ''),
		 'text': "⏪⏪⏪"}
	]
]}


monitor_parkings = {'inline_keyboard': [
	[
		{'switch_inline_query_current_chat': "",
		 'text': "🅿️"}
	]
]}
monitor_hide = {'inline_keyboard': [
	[
		{'callback_data': 'MONITOR_MONITOR_SHOW',
		 'text': "➖"}
	]
]}
monitor_photo = {'inline_keyboard': [
	[
		{'callback_data': 'MONITOR_MONITOR_PHOTO',
		 'text': "➖"}
	]
]}
monitor_pin = {'inline_keyboard': [
	[
		{'switch_inline_query_current_chat': "Смена",
		 'text': "▶️⏹️"}
	]
]}

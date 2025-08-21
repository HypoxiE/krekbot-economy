
import disnake
from disnake.ext import commands
from disnake.ext import tasks
import requests
import numpy as np
import aiohttp
import asyncio
import sys
import os
import copy
import datetime
import math
import random
import json
import re
import shutil
from constants.global_constants import *
from libs.tokens_formatter import TOKENS

import CoreFun


async def main():
	stop_event = asyncio.Event()
	sup_bot = None
	DataBase = None
	all_bots = []

	try:
		DataBase = await CoreFun.init_db()
		#await CoreFun.db_migration(DataBase)

		'''
		async with DataBase.session() as session:
			async with session.begin():
				stmt = DataBase.select(DataBase.model_classes['users']).where(
					DataBase.model_classes['users'].id == 479210801891115009
				).options(
					DataBase.selectinload(DataBase.model_classes['users'].custom_roles)
					.selectinload(DataBase.model_classes['roles_custom'].creator)
				)
				user = (await session.execute(stmt)).scalars().first()
				for role in user.custom_roles:
					print("role: " + str(role.to_dict()), "creator: " + str(role.creator.to_dict()), sep = "\n")

		'''
		
		sup_bot = CoreFun.AdminBot(DataBase, stop_event, task_start = False)
		all_bots = [sup_bot]

		# Загрузка когов
		sup_bot.load_extension("cogs.resetsupcommands")
		#sup_bot.load_extension("cogs.economy")
		#sup_bot.load_extension("cogs.designer")
		#sup_bot.load_extension("cogs.roles")
		sup_bot.load_extension("cogs.admin")
		#sup_bot.load_extension("cogs.rimagochi")

		# Запуск монитора остановки и ботов
		monitor_task = asyncio.create_task(CoreFun.monitor_stop(stop_event, all_bots))
		bot_tasks = [
			asyncio.create_task(CoreFun.run_bot(sup_bot, TOKENS["KrekSupBot"], stop_event)),
		]

		await asyncio.gather(*bot_tasks, monitor_task)

	except KeyboardInterrupt:
		print(f"{datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}:: Боты остановлены по запросу пользователя")
	except Exception as e:
		print(f"{datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}:: Произошла критическая ошибка: {e}")
	finally:

		# Остановка всех ботов
		stop_event.set()
		for bot in all_bots:
			if not bot.is_closed():
				await bot.close()

		if DataBase is not None:
			await DataBase.close()

if __name__ == "__main__":
	asyncio.run(main())

import logging
import typing
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
import inspect
import json
import shutil
import re

from constants.rimagochi_constants import *
from constants.global_constants import *
from libs.tokens_formatter import TOKENS
from database.db_classes import all_data as DataBaseClasses
from managers.DataBaseManager import DatabaseManager
from database.settings import config

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable

import gspread
from google.oauth2.service_account import Credentials

logging.basicConfig(level=logging.INFO)

class AnyBots(commands.Bot):
	logging = logging
	'''
	
	
	Any bot class


	'''
	def __init__(self, DataBaseManager):
		super().__init__(
			command_prefix="=",
			intents=disnake.Intents.all()
		)
		self.DataBaseManager = DataBaseManager
		self.costrolecreate = constants['costrolecreate']
		self.costrolerenewal = constants['costrolerenewal']
		self.dailycrumbs = constants['dailycrumbs']
		self.casinospinslimit = constants['casinospinslimit']

	async def on_ready(self, inherited = False):
		self.krekchat = await self.fetch_guild(constants["krekchat"])
		logging.info(self.krekchat.name)
		self.sponsors = [disnake.utils.get(self.krekchat.roles, id=i) for i in constants["sponsors"]]
		self.mutes = [disnake.utils.get(self.krekchat.roles, id=i) for i in constants["mutes"]]
		self.ban_role = disnake.utils.get(self.krekchat.roles, id=constants["ban_role"])
		self.me = disnake.utils.get(self.krekchat.roles, id=constants["me"])
		self.moder = disnake.utils.get(self.krekchat.roles, id=constants["moder"])
		self.curator = disnake.utils.get(self.krekchat.roles, id=constants["curator"])
		self.everyone = disnake.utils.get(self.krekchat.roles, id=constants["everyone"])
		self.staff = disnake.utils.get(self.krekchat.roles, id=constants["staff"])
		self.level_roles = [disnake.utils.get(self.krekchat.roles, id=i) for i in constants["level_roles"]]
		# lists
		self.moderators = [disnake.utils.get(self.krekchat.roles, id=i) for i in constants["moderators"]]
		# /lists
		self.bots_talk_protocol_channel_id = constants["bots_talk_protocol_channel"]
		self.databases_backups_channel_id = constants["databases_backups_channel"]
		await self.change_presence(status=disnake.Status.online, activity=disnake.Game("Работаю"))

		if not inherited:
			logging.info(f"{datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}::  KrekFunBot activated")

	async def RimagochiUserUpdate(self, member, session = None):
		if session is None:
			raise Exception("Реализация RimagochiUserUpdate без session ещё не сделана")

		else:
			await self.UserUpdate(member, session = session)
			async with session.begin():
				async with self.DataBaseManager.models['rimagochi_users'] as rimagochi_users_models:
					stmt = self.DataBaseManager.select(rimagochi_users_models).where(rimagochi_users_models.id == member.id)
					rimagochi_user = (await session.execute(stmt)).scalars().first()

					if rimagochi_user is None:
						rimagochi_user = rimagochi_users_models(id = member.id, settings = rimagochi_default_settings)
						session.add(rimagochi_user)

	async def CasinoUserUpdate(self, member, session = None):
		if session is None:
			raise Exception("Реализация CasinoUserUpdate без session ещё не сделана")

		else:
			await self.UserUpdate(member, session = session)
			async with session.begin():
				async with self.DataBaseManager.models['casino_user_account'] as casino_user_account_models:
					stmt = self.DataBaseManager.select(casino_user_account_models).where(casino_user_account_models.id == member.id)
					casino_user = (await session.execute(stmt)).scalars().first()

					if casino_user is None:
						casino_user = casino_user_account_models(id = member.id)
						session.add(casino_user)

	async def UserUpdate(self, member, session = None):

		if session is None:
			async with self.DataBaseManager.session() as session:
				async with session.begin():
					async with self.DataBaseManager.models['users'] as users_model:
						stmt = self.DataBaseManager.select(users_model).where(users_model.id == member.id)
						user = (await session.execute(stmt)).scalars().first()

						if user is None:
							user = users_model(id = member.id)
							session.add(user)

			return 0
		else:
			async with session.begin():
				async with self.DataBaseManager.models['users'] as users_model:
					stmt = self.DataBaseManager.select(users_model).where(users_model.id == member.id)
					user = (await session.execute(stmt)).scalars().first()

					if user is None:
						user = users_model(id = member.id)
						session.add(user)
			return user

	async def DeleteRole(self, role_id: int):
		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['roles_custom'] as roles_custom:
					stmt = self.DataBaseManager.select(roles_custom).where(
						roles_custom.id == role_id
					).with_for_update()
					role = (await session.execute(stmt)).scalars().first()
					if not role is None:
						await session.delete(role)

						krekchat = await self.fetch_guild(constants["krekchat"])
						role = krekchat.get_role(role_id)
						if not role:
							return [True, "Кастомная роль успешно удалена из базы данных, но не найдена на сервере"]
						# deleting from server
						await role.delete()
						return [True, "Кастомная роль успешно удалена"]

			async with session.begin():
				async with self.DataBaseManager.models['roles_prize'] as roles_prize:
					async with self.DataBaseManager.models['roles_static'] as roles_static:
						stmt = self.DataBaseManager.select(roles_prize).where(
							roles_prize.id == role_id
						).with_for_update()
						prize_role = (await session.execute(stmt)).scalars().first()
						if not prize_role is None:
							await session.delete(prize_role)
							stmt = self.DataBaseManager.select(roles_static).where(
								roles_static.id == role_id
							).with_for_update()
							static_role = (await session.execute(stmt)).scalars().first()
							if not static_role is None:
								await session.delete(static_role)
							krekchat = await self.fetch_guild(constants["krekchat"])
							role = krekchat.get_role(role_id)
							if not role:
								return [True, "Призовая роль успешно удалена из базы данных, но не найдена на сервере"]
							await role.delete()
							return [True, "Призовая роль успешно удалена"]

		return [False, "Такой роли не существует в базе данных"]

	def PartitioningEmbeder(self, arr):
		result = []
		for i in range(len(arr)):
			if i % 5 == 0:
				result.append([])
			result[-1].append(arr[i])
		return result

	async def CalculateRimagochiBattleStrength(self, users_animals: list):
		sum_strenght = 0
		for animal in users_animals:
			if not animal.in_battle_slots:
				continue
			animal_model = copy.deepcopy(rimagochi_animals[animal.model_animal_id])
			for gene in animal.genes:
				genedata = rimagochi_genes[gene]
				for effect in genedata['effects'].keys():
					animal_model['params'][effect] += genedata['effects'][effect]
			sum_strenght = sum_strenght + ((animal_model['params']['damage']*animal_model['params']['health'])+(animal_model['params']['damage']*animal_model['params']['health']*animal.level/4))
		return sum_strenght

	async def LevelRolesGiver(self, member, level):
		try:
			c = 0
			if level >= 1: c += 1
			if level >= 5: c += 1
			if level >= 55: c += 1
			if level >= 91: c += 1
			for role in range(1, len(self.level_roles)):
				if role == c:
					await member.add_roles(self.level_roles[role])
					continue
				await member.remove_roles(self.level_roles[role])
		except:
			pass

	def HexToRgb(self, value):
		value = value.lstrip('#')
		lv = len(value)
		return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

	def find_for_arr(self, arr, elem):
		for i in range(len(arr)):
			if arr[i] == elem:
				return i
		return -1

	def AnimalLevelAdder(self, exp, level):
		if(level+1<=max(rimagochi_constants["animals_exp_to_levels"].keys())):
			if exp>=rimagochi_constants["animals_exp_to_levels"][level+1]:
				exp = exp - rimagochi_constants["animals_exp_to_levels"][level+1]
				level += 1
				if (level+1<=max(rimagochi_constants["animals_exp_to_levels"].keys())):
					return exp, level, rimagochi_constants["animals_exp_to_levels"][level+1] - exp
				else:
					return exp, level, float('inf')
			else:
				return exp, level, rimagochi_constants["animals_exp_to_levels"][level+1] - exp
		else:
			return exp, level, float('inf')
			
	def CalculateLevel(self, messages, voiceactivity):
		n = (messages + (voiceactivity / (180))) / 4
		# return math.log((messages+(voiceactivity/(30)))+1, 1.11)
		if n < 40:
			return n / 3
		else:
			return math.log(n, 1.05) - 62

	def TimeFormater(self, time_str: str = "", days: float = 0, hours: float = 0, minutes: float = 0, now_timestamp = None):
		"""
		Форматирует строку времени в timestamp и разложенное время
		Поддерживает форматы: 1d2h30m, 1д2ч30мин, 1.5d, 1 день 2 часа 30 минут и т.п.
		Возвращает объект класса FormatedTime
		"""

		class FormatedTime:
			def __init__(self, time_units):
				self.time_units = time_units

				self.days, self.hours, self.minutes = time_units['d'], time_units['h'], time_units['m']
				delta = datetime.timedelta(days=self.days, hours=self.hours, minutes=self.minutes)
				self.future_time = 0
				if now_timestamp is None:
					self.future_time = datetime.datetime.now() + delta
				else:
					self.future_time = datetime.datetime.fromtimestamp(now_timestamp) + delta
				self.timestamp = self.future_time.timestamp()

			def __float__(self):
				return self.timestamp

			def __int__(self):
				return int(self.timestamp)

			def __repr__(self):
				result = []
				if self.days != 0:
					result.append(f"{self.days} дней")
				if self.hours != 0:
					result.append(f"{self.hours} часов")
				if self.minutes != 0:
					result.append(f"{self.minutes} минут")

				return ", ".join(result) + f" [{self.timestamp}]"

			def to_dict(self):
				return self.time_units

		time_units = {'d': 0, 'h': 0, 'm': 0}
		if any([days, hours, minutes]):
			time_units = {'d': days, 'h': hours, 'm': minutes}
		else:
			time_str = time_str.lower().replace(' ', '').replace(',', '.')

			replacements = {
				r'дней?': 'd',
				r'день': 'd',
				r'д': 'd',
				r'часов?': 'h',
				r'час': 'h',
				r'ч': 'h',
				r'минут?': 'm',
				r'мин': 'm',
				r'м': 'm',
			}

			for pattern, replacement in replacements.items():
				time_str = re.sub(pattern, replacement, time_str, flags=re.IGNORECASE)

			pattern = r'(\d+(\.\d+)?)([dhm])'
			matches = re.findall(pattern, time_str)

			for value, _, unit in matches:
				time_units[unit] += value

		return FormatedTime(time_units)

	class ErrEmbed(disnake.Embed):
		def __init__(self, err_func: typing.Callable[..., typing.Awaitable[None]] | None = None, err_func_kwargs: dict | None = None, **kwargs):
			color = kwargs.pop('color', 0x2F3136)
			super().__init__(color=color, **kwargs)
			self.err_func_kwargs: dict = err_func_kwargs or {}
			self.err_func = err_func

		async def send(self, description: str | None = None):
			if self.err_func is None:
				raise ValueError("err_func не задана")
			
			if description is not None:
				self.description = description

			await self.err_func(embed = self, **self.err_func_kwargs)

	class InfoEmbed(disnake.Embed):
		def __init__(self, **kwargs):
			color = kwargs.pop('color', 0x2F3136)
			super().__init__(color = color, **kwargs)

	class WarnEmbed(disnake.Embed):
		def __init__(self, **kwargs):
			color = kwargs.pop('color', 0xFFFF00)
			super().__init__(color = color, **kwargs)

class AdminBot(AnyBots):
	'''
	

	Admin`s bot class


	'''
	def __init__(self, DataBase, stop_event, *, task_start = True):
		super().__init__(DataBase)
		self.task_start = task_start
		self.stop_event = stop_event

	async def on_ready(self, inherited = True):
		await super().on_ready(inherited = True)

		if self.task_start:
			self.VoiceXpAdder.cancel()
			self.CheckDataBase.cancel()
			self.UpdatingTournamentData.cancel()

			self.VoiceXpAdder.start()
			self.CheckDataBase.start()
			self.UpdatingTournamentData.start()
		else:
			self.UpdatingTournamentData.start() # Удалить обязательно!!!

		logging.info(f"{datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}:: KrekFunLoopsBot activated")

	async def BotOff(self):
		self.VoiceXpAdder.cancel()
		self.CheckDataBase.cancel()
		self.UpdatingTournamentData.cancel()

		self.stop_event.set()

	async def on_disconnect(self):
		if self.stop_event.is_set():
			pass
		else:
			logging.error(f"{datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}:: Соединение с дискордом разорвано")
			await self.BotOff()

	async def check_bt_channel(self):
		async def moder_dataparser(data: dict):
			if not 'type' in data.keys():
				raise json.JSONDecodeError("Некорректный JSON", '{"type":value}', 0)
			async with self.DataBaseManager.session() as session:
				async with session.begin():
					async with self.DataBaseManager.models['users'] as users_model:
						if data['type'] == "punishment":
							options = data['options']
							ratings = {'textmute': 10, 'voicemute': 10, 'warning': 5, 'ban': 50, 'reprimand': 15, 'newnick': 0}
							user = await session.get(users_model, options['member'], with_for_update = True)
							if user is None:
								user = users_model(id = options['member'], carma = -ratings[options['severity']])
								session.add(user)
							else:
								user.carma -= ratings[options['severity']]

						elif data['type'] == "unpunishment":
							options = data['options']
							ratings = {'textmute': 10, 'voicemute': 10, 'warning': 5, 'ban': 50, 'reprimand': 15, 'newnick': 0}
							user = await session.get(users_model, options['member'], with_for_update = True)
							if user is None:
								user = users_model(id = options['member'], carma = ratings[options['severity']])
								session.add(user)
							else:
								user.carma += ratings[options['severity']]

						elif data['type'] == "complaint":
							options = data['options']

							attack_member = await session.get(users_model, options['attack_member'], with_for_update = True)
							if attack_member is None:
								attack_member = users_model(id = options['attack_member'], carma = 10 if options['accepted'] else -1)
								session.add(attack_member)
							else:
								attack_member.carma += 10 if options['accepted'] else -1

							moderator = await session.get(users_model, options['moderator'], with_for_update = True)
							if moderator is None:
								moderator = users_model(id = options['moderator'], carma = 10)
								session.add(moderator)
							else:
								moderator.carma += 10

						else:
							return 1

			return 0


		krekchat = await self.fetch_guild(self.krekchat.id)
		bt_channel = await krekchat.fetch_channel(self.bots_talk_protocol_channel_id)
		last_msg = None

		while True:
			stopflag = False
			if not isinstance(bt_channel, disnake.TextChannel):
				raise ValueError("В bt_channel как-то оказалось не disnake.TextChannel")
			batch = await bt_channel.history(limit=10, before=last_msg).flatten()
			for message in batch:
				msg_stopflag = False
				for reaction in message.reactions:
					if reaction.emoji == "✅" or reaction.emoji == "❎":
						msg_stopflag = True
						break
				else:
					data = json.loads(message.content)
					try:
						result = 0
						if not 'sender' in data:
							raise json.JSONDecodeError("Некорректный JSON", '{"sender":value}', 0)
						if data['sender'] == "ModBot":
							result = await moder_dataparser(data)
						if result:
							raise json.JSONDecodeError("Некорерктный JSON", '', 0)
						await message.add_reaction("✅")
					except json.JSONDecodeError as e:
						await message.add_reaction("❎")
					except Exception as exc:
						logging.error(f"{data} {exc}")
				if msg_stopflag:
					stopflag = True
					break
				last_msg = message
			if stopflag:
				break

	async def give_crumbs_counter(self, incoming_crumbs: float, member, sponsor_roles, carma = 0):
		modifier = (carma / 100) + (bool(set(sponsor_roles) & set(member.roles)) + 1)
		add_crumbs = (incoming_crumbs * modifier) if incoming_crumbs * modifier >= 0 else 0
		return add_crumbs

	async def on_message(self, message):
		if message.author.id == 479210801891115009 and message.content == "botsoff":
			await message.reply(embed=disnake.Embed(description=f'Бот отключён', colour=0xff9900))
			await self.BotOff()
		if message.guild is None:
			return
		if message.channel.id == self.bots_talk_protocol_channel_id:
			await self.check_bt_channel()
		if message.author.bot:
			return
		crumb_per_word = 1 / 2
		text = message.content
		while "  " in text:
			text = text.replace("  ", " ")
		add_crumbs = len(text.split(" ")) * crumb_per_word

		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['users'] as users_model:
					stmt = self.DataBaseManager.select(users_model).where(users_model.id == message.author.id)
					user = (await session.execute(stmt)).scalars().first()

					if user is None:
						user = users_model(id = message.author.id, period_messages = 1, summary_messages = 1, crumbs = (await self.give_crumbs_counter(incoming_crumbs = add_crumbs, sponsor_roles = self.sponsors, member = message.author)))
						session.add(user)
						period_messages, period_voice_activity = 1, 0

					else:
						stmt = self.DataBaseManager.update(users_model).where(users_model.id == message.author.id).values(
							period_messages = users_model.period_messages + 1,
							summary_messages = users_model.summary_messages + 1,
							crumbs = users_model.crumbs + (await self.give_crumbs_counter(incoming_crumbs = add_crumbs, sponsor_roles = self.sponsors, member = message.author, carma = user.carma))
						)
						await session.execute(stmt)
						period_messages, period_voice_activity = user.period_messages + 1, user.period_voice_activity

		await self.LevelRolesGiver(message.author, self.CalculateLevel(period_messages, period_voice_activity))

	_url_cache = {}
	@tasks.loop(seconds=3600)
	async def UpdatingTournamentData(self):
		krekchat = await self.fetch_guild(self.krekchat.id)
		tournament_channel = await krekchat.fetch_channel(1396785366882582538)
		if not isinstance(tournament_channel, disnake.TextChannel):
			raise
		webhooks = await tournament_channel.webhooks()
		webhook = webhooks[0]

		if not hasattr(self, 'tournament_table_client'):
			SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
			creds = Credentials.from_service_account_file("secrets/krekbottable-9a40985c56e2.json", scopes=SCOPES)
			self.tournament_table_client = gspread.authorize(creds)

		async def shorten_url_tinyurl(url: str) -> str:
			if not hasattr(self, '_url_cache'):
				self._url_cache = {}

			if url in self._url_cache:
				return self._url_cache[url]

			async with aiohttp.ClientSession() as session:
				async with session.get("https://tinyurl.com/api-create.php", params={"url": url}) as resp:
					resp.raise_for_status()
					short_url = await resp.text()
					self._url_cache[url] = short_url
					return short_url
		
		spreadsheet = self.tournament_table_client.open_by_key("16t28W1nlexAS-J26Mk18EgtPUX3344XdB18c5glA3Fg")
		sheet = spreadsheet.worksheet("Ответы на форму")
		data = sheet.get_all_values()

		class RowData:
			def __init__(self, row):
				if isinstance(row, RowData):
					row = row.raw_data
				self.points = int(row[-2])
				self.discord_id = int(row[5]) if row[5] else None
				self.nick = row[7]
				self.links = row[8]
				self.verified = row[-4]
				self.cost = int(row[-5]) if row[-5] else 0
				self.raw_data = row

			def __lt__(self, other):
				return (self.points, self.cost) < (other.points, other.cost)

			def __le__(self, other):
				return (self.points, self.cost) <= (other.points, other.cost)

			def __gt__(self, other):
				return (self.points, self.cost) > (other.points, other.cost)

			def __ge__(self, other):
				return (self.points, self.cost) >= (other.points, other.cost)

			async def to_str(self, num: int | None = None):
				try:
					member = await krekchat.fetch_member(int(row.discord_id))
				except:
					member = None

				if num is not None:
					result = f"**{num}) "
				else:
					result = f"**-"
					num = -2

				result += f"[{self.nick}]("
				result += f"https://docs.google.com/spreadsheets/d/1QkaNYezumeb-QJHSZ3x1vIi5ktf0ooDklYkrP6xSMZc/edit?gid=0&range=A{num+2}"
				result += ")"
				if member is None:
					result += "**\n"
				else:
					result += f" ({member.mention})**\n"

				result += f"`{self.points} очков`\n"

				saved_links = [("youtu.be", "YouTube"), ("youtube.com", "YouTube"), ("twitch.tv", "Twitch")]
				result += f"Стримы: "

				links = []
				for link in self.links.split():
					for saved_link in saved_links:
						if saved_link[0] in link:
							links.append(f"[{saved_link[1]}]({await shorten_url_tinyurl(link)})")
							break
					else:
						links.append(f"{link}")

				result += ", ".join(links) + "\n"
				result += f"Проверено модерацией: " + ("✅" if self.verified == "Прошло модерацию" else "❎") 
				return result

		class Stack:
			def __init__(self, name, data):
				self.name = name
				self.data_stack = []

				for row in data:
					if isinstance(row, RowData):
						self.data_stack.append(RowData(row))
					else:
						self.data_stack.append(row)

			def __iter__(self):
				return iter(self.data_stack)

		class Stacks:
			def __init__(self, stack_size, data):
				self.data_parts = []
				for i in range(1, (len(data)+(stack_size-1))//stack_size+1):
					self.data_parts.append(Stack(name = f"Топ {i*stack_size}" , data = data[stack_size*(i-1):stack_size*i]))

			def __iter__(self):
				return iter(self.data_parts)

			def __getitem__(self, key):
				return self.data_parts[key]
			

		data = [RowData(i) for i in data[2:]]

		data = [i for i in sorted(data, reverse = True) if i.points > 0]
		fdata = Stacks(stack_size = 5, data = data)

		color = 0x211125

		embeds = []

		embed = disnake.Embed(description = "[Оригинал таблицы](https://docs.google.com/spreadsheets/d/1QkaNYezumeb-QJHSZ3x1vIi5ktf0ooDklYkrP6xSMZc/edit?usp=sharing)\nᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠ\n# Таблица лидеров", colour=color)
		embeds.append(embed)

		row_num = 1
		for stack in fdata[:5]:
			embed = disnake.Embed(title = f"{stack.name}", description = "ᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠᅠ", colour=color)
			
			for row in stack:
				embed.add_field(name = "", value = f"{await row.to_str(num = row_num)}", inline = False)
				row_num += 1
			embeds.append(embed)

		embed = disnake.Embed(description = "**Эта таблица обновляется каждый час и может содержать только топ-20 участников.\n\nБолее детальную и актуальную информацию можете найти в [оригинальной таблице](https://docs.google.com/spreadsheets/d/1QkaNYezumeb-QJHSZ3x1vIi5ktf0ooDklYkrP6xSMZc/edit?usp=sharing).**", colour=color)
		embeds.append(embed)

		await webhook.edit_message(1405594708016889909, content = "", embeds = embeds)

	@tasks.loop(seconds=60)
	async def VoiceXpAdder(self):
		try:
			channels = await self.krekchat.fetch_channels()
			async with self.DataBaseManager.session() as session:
				for channel in channels:

					channel = self.get_channel(channel.id)

					if (not isinstance(channel, disnake.VoiceChannel)) or channel.id == 1250314784914669598:
						continue

					for member in channel.members:
						if member.bot:
							continue
						add_crumbs = 5
						async with session.begin():
							async with self.DataBaseManager.models['users'] as users_model:
								stmt = self.DataBaseManager.select(users_model).where(users_model.id == member.id)
								user = (await session.execute(stmt)).scalars().first()

								if user is None:
									user = users_model(
										id = member.id, 
										period_voice_activity = 60, 
										summary_voice_activity = 60, 
										crumbs = (await self.give_crumbs_counter(incoming_crumbs = add_crumbs, sponsor_roles = self.sponsors, member = member))
									)
									session.add(user)
									period_messages, period_voice_activity = 0, 60

								else:
									stmt = self.DataBaseManager.update(users_model).where(users_model.id == member.id).values(
										period_voice_activity = users_model.period_voice_activity + 60,
										summary_voice_activity = users_model.summary_voice_activity + 60,
										crumbs = users_model.crumbs + (await self.give_crumbs_counter(incoming_crumbs = add_crumbs, sponsor_roles = self.sponsors, member = member, carma = user.carma))
									)
									await session.execute(stmt)
									period_messages, period_voice_activity = user.period_messages, user.period_voice_activity + 60
						await self.LevelRolesGiver(member, self.CalculateLevel(period_messages, period_voice_activity))
				
		except Exception as e:
			logging.error(f"{datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}:: err VoiceXpAdder: {e}")

	@tasks.loop(seconds=3600)
	async def CheckDataBase(self):
		try:
			roles_for_delete = []
			async with self.DataBaseManager.session() as session:
				async with session.begin():
					async with self.DataBaseManager.models['roles_custom'] as roles_custom:

						stmt = self.DataBaseManager.select(roles_custom).join(roles_custom.creator).options(
							self.DataBaseManager.contains_eager(roles_custom.creator)
						).where(roles_custom.renewal_date <= datetime.datetime.now().timestamp()).with_for_update()
						roles = (await session.execute(stmt)).scalars().all()

						for role in roles:
							if role.renewal_enabled:
								if role.creator.crumbs >= self.costrolerenewal:
									async with self.DataBaseManager.models['transaction_history_crumbs'] as transaction_history_crumbs:
										transaction = transaction_history_crumbs(sender_id = role.creator.id, amount = self.costrolerenewal, description = f"Содержание роли {role.id}")
										session.add(transaction)
									role.creator.crumbs -= self.costrolerenewal
									await role.renewal_date_update(self.TimeFormater)
									continue
								else:
									roles_for_delete.append(role.id)
				async with session.begin():
					async with self.DataBaseManager.models['users'] as users_model:
						stmt = self.DataBaseManager.update(users_model).where(users_model.staff_salary > 0).values(
							crumbs = users_model.crumbs+users_model.staff_salary
						)
						await session.execute(stmt)
			for role_id in roles_for_delete:
				await self.DeleteRole(role_id)
			# создание бэкапов
			backup_file = await self.DataBaseManager.pg_dump()
			krekchat = await self.fetch_guild(self.krekchat.id)
			backups_channel = await krekchat.fetch_channel(self.databases_backups_channel_id)
			if not isinstance(backups_channel, disnake.TextChannel):
				raise ValueError("backups_channel is not disnake.TextChannel")
			
			if "Backup failed" in backup_file:
				await backups_channel.send(content=backup_file)
			else:
				await backups_channel.send(content=f"Бэкап бд за {datetime.datetime.now()}:", file=disnake.File(backup_file))

		except Exception as e:
			logging.error(f"err CheckDataBase: {e}")

async def init_db():
	DataBaseEngine = create_async_engine(
		config.Settings().DB_URL,
		pool_size=20,
		max_overflow=10,
		pool_recycle=300,
		pool_pre_ping=True,
		#echo=True,
	)
	async with DataBaseEngine.begin() as conn:
		await conn.run_sync(DataBaseClasses['base'].metadata.create_all)
	
	return DatabaseManager(DataBaseEngine, DataBaseClasses)

async def run_bot(bot, token, stop_event):
	try:
		await bot.start(token)
	except Exception as e:
		logging.info(f"Бот {bot.user.name if hasattr(bot, 'user') else 'Unknown'} упал с ошибкой: {e}")
		stop_event.set()  # Сигнализируем об остановке

async def monitor_stop(stop_event, bots):
	await stop_event.wait()
	logging.info(f"{datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')}:: Получен сигнал остановки, завершаю всех ботов...")

	for bot in bots:
		if not bot.is_closed():
			try:
				await bot.close()
			except Exception as e:
				logging.error(f"Ошибка при закрытии бота: {e}")

	await asyncio.sleep(0.1)

async def main():
	stop_event = asyncio.Event()
	DataBase = None
	all_bots = []
	admin_bot = None

	try:
		DataBase = await init_db()

		# Инициализация ботов
		admin_bot = AdminBot(DataBase, stop_event)
		economy_bot = AnyBots(DataBase)
		rimagochi_bot = AnyBots(DataBase)
		all_bots = [economy_bot, admin_bot, rimagochi_bot]

		# Загрузка когов
		economy_bot.load_extension("cogs.economy")
		economy_bot.load_extension("cogs.roles")
		economy_bot.load_extension("cogs.designer")
		admin_bot.load_extension("cogs.admin")
		rimagochi_bot.load_extension("cogs.rimagochi")

		# Запуск монитора остановки и ботов
		monitor_task = asyncio.create_task(monitor_stop(stop_event, all_bots))
		bot_tasks = [
			asyncio.create_task(run_bot(economy_bot, TOKENS["KrekFunBot"], stop_event)),
			asyncio.create_task(run_bot(admin_bot, TOKENS["KrekAdminBot"], stop_event)),
			asyncio.create_task(run_bot(rimagochi_bot, TOKENS["KrekRimagochiBot"], stop_event))
		]

		await asyncio.gather(*bot_tasks, monitor_task)

	except KeyboardInterrupt:
		logging.info("Боты остановлены по запросу пользователя")
	except Exception as e:
		logging.error(f"Произошла критическая ошибка: {e}", exc_info=e)
	finally:
		if admin_bot is not None:
			await admin_bot.BotOff()

		for bot in all_bots:
			if not bot.is_closed():
				await bot.close()

		if DataBase is not None:
			await DataBase.close()

		current_task = asyncio.current_task()
		pending = [t for t in asyncio.all_tasks() if t is not current_task and not t.done()]
		for task in pending:
			task.cancel()
		await asyncio.gather(*pending, return_exceptions=True)

		await asyncio.sleep(0.1)


if __name__ == "__main__":
	asyncio.run(main())
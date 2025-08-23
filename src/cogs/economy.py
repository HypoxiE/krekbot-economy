import disnake
from disnake.ext import commands
from disnake.ext import tasks
import requests
import numpy as np
import asyncio
import sys
import os
import copy
import datetime
import math
import random
import json
import shutil
from constants.global_constants import *


def setup(bot):
	bot.add_cog(MainEconomyModule(bot))

class MainEconomyModule(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.DataBaseManager = client.DataBaseManager
		
	@commands.Cog.listener()
	async def on_ready(self):
		self.krekchat = await self.client.fetch_guild(constants["krekchat"])
		self.sponsors = [disnake.utils.get(self.krekchat.roles, id=i) for i in constants["sponsors"]]
		self.me = disnake.utils.get(self.krekchat.roles, id=constants["me"])
		self.client.logger.info(f'KrekFunBot economy module activated')

	@commands.slash_command(name = "статистика", description="Статистика отображает все данные о пользователе")
	async def UserStatistic(self, ctx: disnake.AppCmdInter,
					  member: disnake.Member = commands.Param(description="Чью статистику хотите посмотреть?", name="участник", default=None)):
		if not member:
			member = ctx.author

		if ctx.guild is None:
			embed = self.client.InfoEmbed(title=f"Статистика **{member.name}**", description=f'')
		elif member.nick != None:
			embed = self.client.InfoEmbed(title=f"Статистика **{member.nick}**", description=f'')
		else:
			embed = self.client.InfoEmbed(title=f"Статистика **{member.name}**", description=f'')

		embed.set_thumbnail(url=member.avatar)

		await ctx.response.defer()

		users_model = self.DataBaseManager.models['users'].m
		rimagochi_users_model = self.DataBaseManager.models['rimagochi_users'].m

		async with self.DataBaseManager.session() as session:
			async with session.begin():
				user = await session.get(users_model, member.id)
				if user is None:
					embed = self.client.ErrEmbed(title="Ошибка статистики", description="Такого пользователя нет в базе данных")
					await ctx.edit_original_message(embed=embed)
					return

				stmt = self.DataBaseManager.select(users_model).options(
					self.DataBaseManager.selectinload(users_model.custom_roles),
					self.DataBaseManager.joinedload(users_model.creation_role),
					self.DataBaseManager.selectinload(users_model.prize_roles),
					self.DataBaseManager.selectinload(users_model.sender_in_crumbs_transactions),
					self.DataBaseManager.selectinload(users_model.recipient_in_crumbs_transactions),
					self.DataBaseManager.joinedload(users_model.casino_account),
				).where(
					users_model.id == member.id
				)
				user = (await session.execute(stmt)).scalars().first()

				stmt = self.DataBaseManager.select(rimagochi_users_model).options(
					self.DataBaseManager.selectinload(rimagochi_users_model.animals),
					self.DataBaseManager.selectinload(rimagochi_users_model.battle_slots_animals)
				).where(
					rimagochi_users_model.id == member.id
				)
				rimagochi_user = (await session.execute(stmt)).scalars().first()

				embed.add_field(name=f"Модуль экономики", value=f"", inline=False)
				embed.add_field(name=f"крошки", value=f"{user.crumbs}", inline=False)
				embed.add_field(name=f"сообщения (в общем)", value=f"{user.summary_messages}", inline=False)
				embed.add_field(name=f"минут в голосовом канале (в общем)", value=f"{user.summary_voice_activity/60}", inline=False)
				embed.add_field(name=f"сообщения (после сброса)", value=f"{user.period_messages}", inline=False)
				embed.add_field(name=f"минут в голосовом канале (после сброса)", value=f"{user.period_voice_activity/60}", inline=False)
				embed.add_field(name=f"репутация", value=f"{user.carma}", inline=False)
				embed.add_field(name=f"зарплата", value=f"{user.staff_salary}", inline=False)
				embed.add_field(name=f"время получения последней ежедневной награды", value=f"<t:{int(user.last_daily_crumbs_date)}:F>", inline=False)
				embed.add_field(name=f"время последней активности", value=f"<t:{int(user.last_activity_date)}:F>", inline=False)
				embed.add_field(name=f"количество записей в истории об отправлениях (общая сумма)", value=f"{len(user.sender_in_crumbs_transactions)} ({sum([write.amount for write in user.sender_in_crumbs_transactions]+[0])})", inline=False)
				embed.add_field(name=f"количество записей в истории о получениях (общая сумма)", value=f"{len(user.recipient_in_crumbs_transactions)} ({sum([write.amount for write in user.recipient_in_crumbs_transactions]+[0])})", inline=False)
				embed.add_field(name=f"наличие записей в казино", value=f"{not user.casino_account is None}", inline=False)
				if not user.casino_account is None:
					embed.add_field(name=f"количество круток сегодня (может быть не актуальным)", value=f"{user.casino_account.spins_today_count}", inline=False)
					embed.add_field(name=f"время последнего сброса лимитов", value=f"<t:{int(user.casino_account.last_reset_time)}:F>", inline=False)

				embed.add_field(name=f"Ролевой модуль", value=f"", inline=False)
				embed.add_field(name=f"количество кастомных ролей (общая стоимость)", value=f"{len(user.custom_roles)} ({sum([role.cost for role in user.custom_roles]+[0])})", inline=False)
				embed.add_field(name=f"количество призовых ролей", value=f"{len(user.prize_roles)}", inline=False)
				embed.add_field(name=f"созданная кастомная роль", value=(f"<@&{user.creation_role.id}>" if not user.creation_role is None else "None"), inline=False)

				embed.add_field(name=f"Модуль rimagochi", value=f"", inline=False)
				embed.add_field(name=f"наличие аккаунта rimagochi", value=f"{not rimagochi_user is None}", inline=False)
				if not rimagochi_user is None:
					embed.add_field(name=f"количество зверей", value=f"{len(rimagochi_user.animals)}", inline=False)
					embed.add_field(name=f"количество генов", value=f"{sum([int(i) for i in rimagochi_user.genes.values()])}", inline=False)
					embed.add_field(name=f"количество предметов", value=f"{sum([int(i) for i in rimagochi_user.items.values()])}", inline=False)
					embed.add_field(name=f"количество побед", value=f"{rimagochi_user.wins}", inline=False)
				await ctx.edit_original_message(embed=embed)

	@commands.slash_command(description="Показывает топ участников сервера по заданному параметру (по умолчанию - уровень)", name="топ")
	async def TopSlash(self, ctx: disnake.AppCmdInter, parameter: str = commands.Param(description="По какому критерию хотите увидеть топ?",
														name="критерий", default = 'по уровню',
														choices=['по уровню', 'по количеству сообщений', 'по времени в голосовых каналах', 'по количеству крошек'])):
		await ctx.response.defer()
		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['users'] as users_model:
					order_by = None
					match parameter:
						case "по уровню":
							order_by = [self.DataBaseManager.desc(users_model.period_messages + (users_model.period_voice_activity / 180))]
						case "по количеству сообщений":
							order_by = [self.DataBaseManager.desc(users_model.period_messages), self.DataBaseManager.desc(users_model.period_voice_activity)]
						case "по времени в голосовых каналах":
							order_by = [self.DataBaseManager.desc(users_model.period_voice_activity), self.DataBaseManager.desc(users_model.period_messages)]
						case "по количеству крошек":
							order_by = [self.DataBaseManager.desc(users_model.crumbs), self.DataBaseManager.desc(users_model.period_messages), self.DataBaseManager.desc(users_model.period_voice_activity)]
					if order_by is None:
						return
					stmt = self.DataBaseManager.select(users_model).order_by(*order_by).limit(20)
					users = (await session.execute(stmt)).scalars().all()

		embed = self.client.InfoEmbed(title=f"Общий топ {parameter}", description=f'')
		users_counter = 0
		for user in users:
			try:
				member = await self.krekchat.fetch_member(user.id)
			except disnake.NotFound:
				continue
			member_name = None
			if member.nick != None:
				member_name = member.nick
			elif member.display_name != None:
				member_name = member.display_name
			else:
				member_name = member.name
			match parameter:
				case "по уровню":
					embed.add_field(name=f"{users_counter + 1}) {member_name}",
									value=f"{member.mention} - {int(self.client.CalculateLevel(user.period_messages, user.period_voice_activity))} уровень",
									inline=False)
				case "по количеству сообщений":
					embed.add_field(name=f"{users_counter + 1}) {member_name}",
									value=f"{member.mention} - {user.period_messages} сообщений",
									inline=False)
				case "по времени в голосовых каналах":
					embed.add_field(name=f"{users_counter + 1}) {member_name}",
									value=f"{member.mention} - {int(user.period_voice_activity/60)} минут",
									inline=False)
				case "по количеству крошек":
					embed.add_field(name=f"{users_counter + 1}) {member_name}",
									value=f"{member.mention} - {int(user.crumbs)} крошек",
									inline=False)
			users_counter += 1

			if users_counter >= 10:
				break

		await ctx.edit_original_message(embed=embed)


	@commands.slash_command(name="ежедневная")
	async def DailySlash(self, ctx):
		pass
	@DailySlash.sub_command(
		description=f"Получайте награду в крошках каждый день",
		name="награда")
	async def DailyCrumbsSub(self, ctx: disnake.AppCmdInter):
		await ctx.response.defer()
		err_embed = self.client.ErrEmbed(title="Ошибка начисления ежедневной награды")
		if ctx.guild is None:
			err_embed.description = "Эта команда не работает в личных сообщениях!"
			await ctx.edit_original_message(embed=err_embed)
			return
		async with self.DataBaseManager.session() as session:
			await self.client.UserUpdate(member = ctx.author, session = session)
			async with session.begin():
				async with self.DataBaseManager.models['users'] as users_model:
					stmt = self.DataBaseManager.select(users_model).where(users_model.id == ctx.author.id).with_for_update()
					user = (await session.execute(stmt)).scalars().first()

					result = await user.claim_daily_crumbs(daily_constant = constants['dailycrumbs'], member = ctx.author, sponsor_roles = self.sponsors)

					if result['success']:
						history = self.DataBaseManager.models['transaction_history_crumbs'].m(recipient_id = ctx.author.id, amount = result['count'], description = f"Ежедневная награда за {result['date'].strftime('%d.%m.%Y')}")
						session.add(history)
						await ctx.edit_original_message(embed=self.client.InfoEmbed(description=result['output']))
						return
					else:
						err_embed.description = result['output']
						await ctx.edit_original_message(embed=err_embed)
						return


	@commands.slash_command(name="история", description="Показывает историю транзакций")
	async def HistoryCrumbsSlash(self, ctx: disnake.AppCmdInter):
		pass
	@HistoryCrumbsSlash.sub_command(description="Показывает историю транзакций", name="транзакций")
	async def HistoryCrumbsSub(self, ctx: disnake.AppCmdInter, member_inp: disnake.Member = commands.Param(
							  description="Чью историю хотите посмотреть?(только для администраторов)",
							  name="участник", default=None)):
		
		member = ctx.author
		if isinstance(ctx.author, disnake.Member) and (member_inp is not None) and (self.me in ctx.author.roles):
			member = member_inp
		class HistoryButtons(disnake.ui.View):
			def __init__(self, ctx, transactions, member, embed):
				super().__init__(timeout=180)
				self.transactions = transactions
				self.ctx = ctx
				self.embed = embed
				self.member = member
				self.page = 1
				self.maxpage = len(transactions) if len(transactions) > 0 else 1

				self.left.disabled = (self.page == 1)
				self.right.disabled = (self.page == self.maxpage)

			@disnake.ui.button(label="<", custom_id="left", style=disnake.ButtonStyle.secondary)
			async def left(self, button, inter):
				if inter.author != self.ctx.author:
					return
				self.page -= 1
				self.left.disabled = (self.page == 1)
				self.right.disabled = (self.page == self.maxpage)
				self.embed = await EmbedHistoryChanger(self.transactions, self.embed, self.page, self.member)
				await inter.response.edit_message(embed=self.embed, view=self)

			@disnake.ui.button(label=">", custom_id="right", style=disnake.ButtonStyle.secondary)
			async def right(self, button, inter):
				if inter.author != self.ctx.author:
					return
				self.page += 1
				self.left.disabled = (self.page == 1)
				self.right.disabled = (self.page == self.maxpage)
				self.embed = await EmbedHistoryChanger(self.transactions, self.embed, self.page, self.member)
				await inter.response.edit_message(embed=self.embed, view=self)

			async def on_timeout(self):
				for child in self.children:
					if isinstance(child, (disnake.ui.Button, disnake.ui.BaseSelect)):
						child.disabled = True
				await self.ctx.edit_original_message(view=self)
		async def EmbedHistoryChanger(transactions, embed, selfpage, member):
			embed.clear_fields()
			if len(transactions) == 0:
				embed.add_field(name=f"В истории пока ничего нет", value=f"", inline=False)
				return embed
			embed.add_field(name=f"", value=f"", inline=False)
			page = transactions[selfpage - 1]
			maxpage = len(transactions) if len(transactions) > 0 else 1
			c = 1
			for transaction in transactions[selfpage - 1]:
				if transaction.recipient_id == member.id:
					string = (
						f"{c+5*(selfpage-1)}) <:A_g_wplus:606920277443608593> **{int(transaction.amount)} крошек** {f' (комиссия: {int(transaction.commission_fraction * 100)}%)'if transaction.commission_fraction != 0 else ''}\n"
						f"{f'Отправитель: <@{transaction.sender_id}>' if not transaction.sender_id is None else ''}\n"
						f"Время транзакции: <t:{int(transaction.transaction_time)}:f>\n"
						f"> {transaction.description}"
					)
				else:
					string = (
						f"{c+5*(selfpage-1)}) <:A_g_wmins:606920287044239362> **{int(transaction.amount)} крошек** {f' (комиссия: {int(transaction.commission_fraction * 100)}%)'if transaction.commission_fraction != 0 else ''}\n"
						f"{f'Получатель: <@{transaction.recipient_id}>' if not transaction.recipient_id is None else ''}\n"
						f"Время транзакции: <t:{int(transaction.transaction_time)}:f>\n"
						f"> {transaction.description}"
					)
				embed.add_field(name=f"", value=string, inline=False)

				c += 1
			embed.add_field(name=f"", value=f"Страница {selfpage}/{maxpage}", inline=False)
			return embed
		await ctx.response.defer(ephemeral = True)
		embed = self.client.InfoEmbed(title=f'История транзакций {member.name}', description=f"")

		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['transaction_history_crumbs'] as transaction_history_crumbs_model:
					stmt = self.DataBaseManager.select(transaction_history_crumbs_model).where(
						self.DataBaseManager.or_(
							transaction_history_crumbs_model.sender_id == member.id,
							transaction_history_crumbs_model.recipient_id == member.id
						)
					).order_by(self.DataBaseManager.desc(transaction_history_crumbs_model.id))
					transactions = (await session.execute(stmt)).scalars().all()

		readyarray = self.client.PartitioningEmbeder(transactions)
		view = HistoryButtons(ctx, readyarray, member, embed)

		embed = await EmbedHistoryChanger(readyarray, embed, 1, member)
		await ctx.edit_original_message(embed=embed, view=view)


	@commands.slash_command(name="казино",
						  description="Хотите иметь очень много крошек? Тогда, эта команда точно не для вас)")
	async def CasinoSlash(self, ctx: disnake.AppCmdInter,
						  count: commands.Range[int, 1, ...] = commands.Param(description="Сколько крошек хотите поставить на кон?", name="ставка"),
						  possibility_input: commands.Range[int, 1, 99] = commands.Param(
							  description="Шанс на победу. Чем выше, тем меньше крошек вы получите после победы(целое число от 1 до 99)",
							  name="шанс", default=50),
						  quantity: int = commands.Param(
							  description=f"Количество круток(целое число от 1 до {constants['casinospinslimit']}({constants['casinospinslimit']*2} для спонсоров))",
							  name="количество", default=1)):
		possibility = float(possibility_input)
		await ctx.response.defer()

		err_embed = self.client.ErrEmbed(title="Ошибка казино")
		if isinstance(ctx.author, disnake.User) or ctx.guild is None:
			err_embed.description = "Эта команда не работает в личных сообщениях!"
			await ctx.edit_original_message(embed=err_embed)
			return
		def get_dynamic_fee(count: int) -> float:
			if count < 1_000:
				return 0
			elif count < 5_000:
				return 0.1
			elif count < 10_000:
				return 0.2
			elif count < 25_000:
				return 0.3
			elif count < 50_000:
				return 0.4
			elif count < 75_000:
				return 0.5
			elif count < 100_000:
				return 0.6
			elif count < 125_000:
				return 0.7
			elif count < 150_000:
				return 0.8
			else:
				return 0.9
		def calculate_multiplier(possibility: float, count: int) -> float:
			fee = get_dynamic_fee(count)
			multiplier = ((0.909/possibility)-0.918)*(1-fee)
			return multiplier*count

		async with self.DataBaseManager.session() as session:
			await self.client.CasinoUserUpdate(member = ctx.author, session = session)
			async with session.begin():
				users_model = self.DataBaseManager.models['users'].m
				casino_account_model = self.DataBaseManager.models['casino_user_account'].m
				stmt = self.DataBaseManager.select(users_model).where(users_model.id == ctx.author.id).with_for_update()
				user = (await session.execute(stmt)).scalars().first()
				stmt = self.DataBaseManager.select(casino_account_model).where(casino_account_model.id == ctx.author.id).with_for_update()
				casino_user = (await session.execute(stmt)).scalars().first()
				user_is_sponsor = await user.in_role(member = ctx.author, roles = self.sponsors)
				casinospinslimit = constants['casinospinslimit']
				if quantity <= 0:
					err_embed.description = f'Количество круток должно быть > 0'
					await ctx.edit_original_message(embed=err_embed)
					return
				if quantity > casinospinslimit * (user_is_sponsor + 1) and (not self.me in ctx.author.roles):
					err_embed.description = f'Вы не можете крутить казино больше {casinospinslimit * (user_is_sponsor + 1)} раз в день!'
					await ctx.edit_original_message(embed=err_embed)
					return
				if not 0 < possibility < 100:
					err_embed.description = f'Шанс должен быть от 1% до 99%'
					await ctx.edit_original_message(embed=err_embed)
					return
				possibility = possibility / 100
				if count <= 0:
					err_embed.description = f'Ставка должна быть больше 0'
					await ctx.edit_original_message(embed=err_embed)
					return
				if user.crumbs < count * quantity:
					err_embed.description = f'Для такой ставки вам необходимо иметь {quantity*count} крошек'
					await ctx.edit_original_message(embed=err_embed)
					return

				now = datetime.datetime.now().timestamp()

				if now - casino_user.last_reset_time >= 86400:
					casino_user.spins_today_count = 0
					casino_user.last_reset_time = now

				if casino_user.spins_today_count + quantity > casinospinslimit * (user_is_sponsor + 1) and (not self.me in ctx.author.roles):
					if casino_user.spins_today_count >= casinospinslimit * (user_is_sponsor + 1):
						err_embed.description = f'У вас не осталось круток, возобновление лимита будет <t:{casino_user.last_reset_time + 86400}:R>'
						await ctx.edit_original_message(embed=err_embed)
					else:
						err_embed.description = f'У вас осталось только {casinospinslimit * (user_is_sponsor + 1) - (casino_user.spins_today_count)} круток, возобновление лимита будет <t:{casino_user.last_reset_time + 86400}:R>'
						await ctx.edit_original_message(embed=err_embed)
					return

				results = [random.random() < possibility for _ in range(quantity)]
				totalwins = sum(results)
				totalcrumbs = totalwins * calculate_multiplier(possibility, count) - (quantity - totalwins) * count

				casino_user.spins_today_count += quantity

				user.crumbs += totalcrumbs
				if int(totalcrumbs)>0:
					history = self.DataBaseManager.models['transaction_history_crumbs'].m(recipient_id = ctx.author.id, amount = int(totalcrumbs), description = f"Выигрыш в казино с шансом {int(possibility * 100)}% и ставкой {count} крошек ({totalwins} побед, {quantity-totalwins} поражений)")
					session.add(history)
					embed=self.client.InfoEmbed(title=f'Вы в плюсе!', description=f"Ваш выигрыш составил {int(totalcrumbs)}!")
				elif int(totalcrumbs) == 0:
					embed=self.client.InfoEmbed(title=f'Вы вышли в 0',description=f"")
				else:
					history = self.DataBaseManager.models['transaction_history_crumbs'].m(sender_id = ctx.author.id, amount = int(abs(totalcrumbs)), description = f"Проигрыш в казино с шансом {int(possibility * 100)}% и ставкой {count} крошек ({totalwins} побед, {quantity-totalwins} поражений)")
					session.add(history)
					embed=self.client.InfoEmbed(title=f'Вы в минусе(', description=f"Ваш проигрыш составил {int(-totalcrumbs)}")
				
				if embed.description is None:
					raise ValueError("embed.description в казино = None")
				embed.description += (f"\n-# У вас осталось {casinospinslimit * (user_is_sponsor + 1) - (casino_user.spins_today_count)} круток")
				await ctx.edit_original_message(embed = embed)


	@commands.slash_command(name="отдать")
	async def GiveCrumbsSlash(self, ctx):
		pass
	@GiveCrumbsSlash.sub_command(description=f"Передайте свои крошки другому участнику сервера (комиссия {int(constants['givecrumbscommission']*100)}%)", name="крошки")
	async def GiveCrumbsSub(self, ctx: disnake.AppCmdInter,
							member: disnake.Member = commands.Param(description="Кому вы хотите перевести крошки?",
																	name="адресат"),
							count: int = commands.Param(description="Сколько крошек вы хотите перевести?",
														name="количество"),
							comment: str = commands.Param(description="Комментарий к переводу", name="комментарий",
														  default="Перевод"),
							commission: float = commands.Param(description="Доля комиссии(доступно только админам)",
															  name="комиссия", default=None)):
		
		err_embed = self.client.ErrEmbed(err_func = ctx.response.send_message, title="Ошибка перевода")
		if isinstance(ctx.author, disnake.User):
			await err_embed.send("Эта команда не работает в личных сообщениях!")
			return
		if comment != "Перевод":
			comment = "Перевод | " + comment
		if (commission == None) or (not self.me in ctx.author.roles) or (ctx.author.id == 515542927158804480):
			commission = constants['givecrumbscommission']
		if count <= 0:
			await err_embed.send("Количество крошек должно быть больше 0")
			return
		users_model = self.DataBaseManager.models['users'].m
		async with self.DataBaseManager.session() as session:
			async with session.begin():
				author_data = await session.get(users_model, ctx.author.id, with_for_update = True)
				member_data = await session.get(users_model, member.id, with_for_update = True)

				if author_data is None:
					await err_embed.send(f'Вас нет в базе данных')
					return

				if member_data is None:
					await err_embed.send(f'Такого пользователя нет в базе данных')
					return

				if author_data.crumbs - count < 0:
					await err_embed.send(f'У вас не хватает крошек')
					return

				history_write = self.DataBaseManager.models["transaction_history_crumbs"].m(sender_id = ctx.author.id, recipient_id = member.id, commission_fraction = commission, description = comment, amount = count)
				session.add(history_write)
				author_data.crumbs -= count
				member_data.crumbs += count * (1 - commission)

				await ctx.response.send_message(embed=self.client.InfoEmbed(
					description=f'{count} крошек успешно отправлено на счёт {member.mention}, комиссия составила {int(commission * 100)}%({int(count * commission)} крошек)'))
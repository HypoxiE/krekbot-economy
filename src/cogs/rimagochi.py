
import logging
import disnake
from disnake.ext import commands
from disnake.ext import tasks
import requests
import numpy as np
import aiohttp

import asyncio
import sqlite3
import sys
import os
import copy
import datetime
import math
import random
import json
import shutil
from constants.global_constants import *
from constants.rimagochi_constants import *

def now():
	return datetime.datetime.now().timestamp()


def setup(bot):
	bot.add_cog(MainRimagochiModule(bot))


class MainRimagochiModule(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.DataBaseManager = client.DataBaseManager

	@commands.Cog.listener()
	async def on_ready(self):
		logging.info(f'KrekFunBot rimagochi module activated')
		krekchat = await self.client.fetch_guild(constants["krekchat"])
		self.me = disnake.utils.get(krekchat.roles, id=constants["me"])

	'''


	Профили


	'''

	@commands.slash_command(description="Группа команд для реализации профилей", name="профиль")
	async def RimagochiProfileSlash(self, ctx: disnake.AppCmdInter):
		pass

	@RimagochiProfileSlash.sub_command(description="Показывает профиль игрока", name="игрока")
	async def RimagochiPlayerProfileSub(self, ctx: disnake.AppCmdInter,
										member: disnake.Member = commands.Param(description="Чей профиль хотите посмотреть?",
																	name="игрок", default=None)):
		if member is None:
			member = ctx.author
		async with self.DataBaseManager.session() as session:
			if member == ctx.author:
				await self.client.RimagochiUserUpdate(member = member, session = session)
			else:
				user = await session.get(self.DataBaseManager.models['rimagochi_users'].m, member.id)
				if user is None:
					err_embed = self.client.ErrEmbed(title = "Ошибка профиля", thumbnail = member.avatar, description = f"Пользователь не найден")
					await ctx.response.send_message(embed = err_embed)
					return
			async with session.begin():
				async with self.DataBaseManager.models['rimagochi_users'] as rimagochi_users_model:
					stmt = self.DataBaseManager.select(rimagochi_users_model).options(
						self.DataBaseManager.selectinload(rimagochi_users_model.animals),
						self.DataBaseManager.selectinload(rimagochi_users_model.battle_slots_animals)
					).where(
						rimagochi_users_model.id == member.id
					)
					user = (await session.execute(stmt)).scalars().first()

					if not isinstance(ctx.author, disnake.Member):
						if (member != ctx.author and user.settings['hide_the_animals']):
							err_embed = self.client.ErrEmbed(title = "Ошибка профиля", thumbnail = member.avatar, description = f"Этот пользователь скрывает свои данные")
							await ctx.response.send_message(embed = err_embed)
							return
					else:
						if (member != ctx.author and user.settings['hide_the_animals']) and (not self.client.me in ctx.author.roles):
							err_embed = self.client.ErrEmbed(title = "Ошибка профиля", thumbnail = member.avatar, description = f"Этот пользователь скрывает свои данные")
							await ctx.response.send_message(embed = err_embed)
							return
					await ctx.response.defer(ephemeral = user.settings['hide_the_animals'])

					strength = await self.client.CalculateRimagochiBattleStrength(user.battle_slots_animals)
					embed = self.client.InfoEmbed(title=f"", description=f"### Профиль игрока {member.mention}")
					embed.set_thumbnail(url=member.avatar)
					embed.add_field(name=f"Победы в битвах", value=f"{user.wins}", inline=False)
					embed.add_field(name=f"Cила отряда", value=f"{strength}", inline=True)
					embed.add_field(name=f"Животные в отряде", value=", ".join([rimagochi_animals[animal.model_animal_id]['name'] for animal in user.battle_slots_animals]).capitalize(), inline=True)
					embed.add_field(name=f"Всего животных", value=f"{len(user.animals)}", inline=True)

					await ctx.edit_original_message(embed=embed)

	'''


	Настройки


	'''

	@commands.slash_command(description="Тут вы можете поменять некоторые настройки", name="настройки")
	async def SettingsSlash(self, ctx: disnake.AppCmdInter):
		await ctx.response.defer()

		class SettingsEmbedView(disnake.ui.View):
			DataBaseManager = self.DataBaseManager
			client = self.client
			def __init__(self, settings):
				super().__init__(timeout=120)
				self.settings = settings

			@disnake.ui.button(label="1", style=disnake.ButtonStyle.primary)
			async def button1_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if ctx.author != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Вы не можете менять настройки другого пользователя")
					await inter.response.send_message(embed=err_embed, ephemeral=True)
					return
				await inter.response.defer()
				self.settings['hide_the_animals'] = not self.settings['hide_the_animals']
				await self.dump(self.settings)
				await ctx.edit_original_message(embed=SettingsEmbedMaker(self.settings))

			@disnake.ui.button(label="2", style=disnake.ButtonStyle.primary)
			async def button2_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if ctx.author != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Вы не можете менять настройки другого пользователя")
					await inter.response.send_message(embed=err_embed, ephemeral=True)
					return
				await inter.response.defer()
				self.settings['always_use_crumbs_for_feeding'] = not self.settings['always_use_crumbs_for_feeding']
				await self.dump(self.settings)
				await ctx.edit_original_message(embed=SettingsEmbedMaker(self.settings))

			@disnake.ui.button(label="3", style=disnake.ButtonStyle.primary)
			async def button3_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if ctx.author != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Вы не можете менять настройки другого пользователя")
					await inter.response.send_message(embed=err_embed, ephemeral=True)
					return
				await inter.response.defer()
				self.settings['accept_the_challenge'] = not self.settings['accept_the_challenge']
				await self.dump(self.settings)
				await ctx.edit_original_message(embed=SettingsEmbedMaker(self.settings))

			async def dump(self, settings):
				async with self.DataBaseManager.session() as session:
					async with session.begin():
						async with self.DataBaseManager.models["rimagochi_users"] as r_users_model:
							stmt = self.DataBaseManager.update(r_users_model).where(r_users_model.id == ctx.author.id).values(settings = settings)
							await session.execute(stmt)

			async def on_timeout(self):
				await ctx.edit_original_message(view=None)

		def SettingsEmbedMaker(settings):
			embed = self.client.InfoEmbed(title=f"Глобальные настройки", description=f'')
			embed.set_thumbnail(url=ctx.author.avatar)
			embed.add_field(name=f"1) Скрывать свои данные", value="Отключено" if not settings['hide_the_animals'] else "Включено", inline=False)
			embed.add_field(name=f"2) Всегда использовать крошки для кормления животных", value="Отключено" if not settings['always_use_crumbs_for_feeding'] else "Включено", inline=False)
			embed.add_field(name=f"3) Получать вызовы на бой", value="Отключено" if not settings['accept_the_challenge'] else "Включено", inline=False)
			return embed

		async with self.DataBaseManager.session() as session:
			await self.client.RimagochiUserUpdate(member = ctx.author, session = session)
			async with session.begin():
				stmt = self.DataBaseManager.select(self.DataBaseManager.models["rimagochi_users"].m.settings).where(
					self.DataBaseManager.models["rimagochi_users"].m.id == ctx.author.id
				)
				settings = (await session.execute(stmt)).scalars().first()
		await ctx.edit_original_message(embed=SettingsEmbedMaker(settings), view=SettingsEmbedView(settings))

	'''


	Гача


	'''

	@commands.slash_command(name="открыть")
	async def OpenGachaSlash(self, ctx: disnake.AppCmdInter):
		pass

	@OpenGachaSlash.sub_command(description="После открытия капсулы, вы получаете боевого питомца", name="капсулу")
	async def OpenGachaSub(self, ctx: disnake.AppCmdInter,
								capsule_id: int = commands.Param(description="Название капсулы",
																	name="капсула",
																	choices=[disnake.OptionChoice(name=f"{i['name']} - {i['cost']} крошек", value=i['id']) for i in rimagochi_capsules.values()])):
		def get_random_rarity(chances):
			rarity_list = []
			probability_list = []

			for chance_data in chances:
				rarity_list.append(chance_data["rarity"])
				probability_list.append(chance_data["chance"])

			chosen_rarity = random.choices(
				population=rarity_list,
				weights=probability_list,
				k=1
			)[0]

			return chosen_rarity

		async with self.DataBaseManager.session() as session:
			await self.client.RimagochiUserUpdate(member = ctx.author, session = session)
			async with session.begin():
				stmt = self.DataBaseManager.select(self.DataBaseManager.models['users'].m).options(
					self.DataBaseManager.selectinload(self.DataBaseManager.models['users'].m.rimagochi_account)
				).where(self.DataBaseManager.models['users'].m.id == ctx.author.id).with_for_update()
				user = (await session.execute(stmt)).scalars().first()

				await ctx.response.defer(ephemeral = user.rimagochi_account.settings['hide_the_animals'])
				err_embed = self.client.ErrEmbed(err_func = ctx.edit_original_message, title = "Ошибка открытия капсулы")
				capsule = rimagochi_capsules[capsule_id]

				if user.crumbs < capsule['cost']:
					await err_embed.send(f"Для открытия этой капсулы необходимо иметь {capsule['cost']} крошек")
					return

				timed_animals = {}
				for animal in rimagochi_animals.keys():
					timed_animals.setdefault(rimagochi_animals[animal]["params"]["rarity"]["id"], [])
					timed_animals[rimagochi_animals[animal]["params"]["rarity"]["id"]].append(animal)

				rarity = get_random_rarity(capsule['chances'])
				animal = rimagochi_animals[random.choices(timed_animals[rarity['id']])[0]]

				chance = 0
				for chance_data in capsule['chances']:
					if rarity == chance_data["rarity"]:
						chance = chance_data["chance"]
						break

				new_animal = self.DataBaseManager.models['rimagochi_animals'].m(model_animal_id = animal['id'], initial_owner_id = ctx.author.id, owner_id = ctx.author.id)
				history_write = self.DataBaseManager.models['transaction_history_crumbs'].m(sender_id = ctx.author.id, amount = capsule['cost'], description = f"Открыта капсула \"{capsule['name']}\", получен {animal['name']}({(chance*100):.02f}%)")
				user.crumbs -= capsule['cost']
				session.add_all([new_animal, history_write])
				await session.flush()

				new_animal_id = new_animal.id

				embed = self.client.InfoEmbed(title=f"{rarity['emoji']} {animal['name'].capitalize()} ({(chance*100):.02f}%)", description=f"{animal['description']}", colour=0x2F3136)
				embed.set_thumbnail(url = animal['params']['image_url'])

		class SlaughterView(disnake.ui.View):
			client = self.client
			DataBaseManager = self.DataBaseManager
			def __init__(self):
				super().__init__(timeout=30)

			@disnake.ui.button(label="Оставить", style=disnake.ButtonStyle.success, emoji="<:A_risworld_rislove:759009763840622622>")
			async def button1_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if ctx.author != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Вы не можете выбирать за другого игрока")
					await inter.response.send_message(embed=err_embed, ephemeral = True)
					return
				self.stop()
				await self.on_timeout()

			@disnake.ui.button(label="Забить", style=disnake.ButtonStyle.danger, emoji="<:A_risworld_risantilove:760082727356727297>")
			async def button2_callback(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if ctx.author != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Вы не можете выбирать за другого игрока")
					await inter.response.send_message(embed=err_embed, ephemeral = True)
					return
				await ctx.edit_original_message(view=None)
				self.stop()

				async with self.DataBaseManager.session() as session:
					async with session.begin():
						stmt = self.DataBaseManager.select(self.DataBaseManager.models['rimagochi_animals'].m).where(
							self.DataBaseManager.models['rimagochi_animals'].m.id == new_animal_id
						).with_for_update()

						new_animal = (await session.execute(stmt)).scalars().first()

						if new_animal is None:
							err_embed = self.client.ErrEmbed(title = "Ошибка операции", description = f"Животное не найдено")
							await inter.response.send_message(embed=err_embed, ephemeral = True)
							await self.on_timeout()
							return

						stmt = self.DataBaseManager.select(self.DataBaseManager.models['users'].m).options(
							self.DataBaseManager.selectinload(self.DataBaseManager.models['users'].m.rimagochi_account)
						).where(self.DataBaseManager.models['users'].m.id == ctx.author.id).with_for_update()
						user = (await session.execute(stmt)).scalars().first()

						items = copy.deepcopy(user.rimagochi_account.items)
						receiveditems = {}
						for item in animal['params']['after_death']:
							items.setdefault(str(item['item']['id']), 0)
							receive=random.randint(*item['count'])
							receiveditems.setdefault(item['item']['name'], receive)
							items[str(item['item']['id'])] += receive

						await session.delete(new_animal)
						user.rimagochi_account.items = items

				embed = self.client.InfoEmbed(title=f"~~{rarity['emoji']} {animal['name'].capitalize()} ({(chance*100):.02f}%)~~", description=",\n".join(f"{i} - {receiveditems[i]}" for i in receiveditems.keys()), colour=0x2F3136)
				embed.set_thumbnail(url = "https://static.wikia.nocookie.net/rimworld/images/a/ad/Мясо.png/revision/latest?cb=20190130152311&path-prefix=ru")
				await ctx.edit_original_message(embed=embed)


			async def on_timeout(self):
				await ctx.edit_original_message(view=None)

		await ctx.edit_original_message(embed=embed, view=SlaughterView())

	'''


	Продать


	'''

	@commands.slash_command(description="Продать предметы", name="продать")
	async def SellSlash(self, ctx: disnake.AppCmdInter, num: commands.Range[int, 1, ...] = commands.Param(description="Укажите количество", name="количество"),
							item: int = commands.Param(description="Какой предмет хотите продать?", name="предмет", choices=[disnake.OptionChoice(name=f"{i['name']} - {i['sell_cost']} крошек/шт", value=i['id']) for i in rimagochi_items.values()])):
		
		async with self.DataBaseManager.session() as session:
			await self.client.RimagochiUserUpdate(member = ctx.author, session = session)
			async with session.begin():
				stmt = self.DataBaseManager.select(self.DataBaseManager.models['users'].m).options(
					self.DataBaseManager.selectinload(self.DataBaseManager.models['users'].m.rimagochi_account)
				).where(self.DataBaseManager.models['users'].m.id == ctx.author.id).with_for_update()
				user = (await session.execute(stmt)).scalars().first()

				await ctx.response.defer(ephemeral = user.rimagochi_account.settings['hide_the_animals'])
				err_embed = self.client.ErrEmbed(err_func = ctx.edit_original_message, title = "Ошибка продажи")

				if not (str(item) in user.rimagochi_account.items.keys() and user.rimagochi_account.items[str(item)] >= num):
					await err_embed.send(f"У вас недостаточно {rimagochi_items[item]['name']}")
					return
				items = copy.deepcopy(user.rimagochi_account.items)
				items[str(item)] -= num
				user.rimagochi_account.items = items
				user.crumbs += num * rimagochi_items[item]["sell_cost"]
				history_write = self.DataBaseManager.models['transaction_history_crumbs'].m(recipient_id = ctx.author.id, amount = num * rimagochi_items[item]["sell_cost"], description = f"Продажа {rimagochi_items[item]['name']}({num} шт)")
				session.add(history_write)

				embed = self.client.InfoEmbed(title=f"{rimagochi_items[item]['name'].capitalize()}(x{num}) продано! Вы получили {num * rimagochi_items[item]['sell_cost']} крошек", description=f"", colour=0x2F3136)
				embed.set_thumbnail(url=ctx.author.avatar)
				await ctx.edit_original_message(embed=embed)

	'''


	Магазины


	'''

	@commands.slash_command(name="магазин")
	async def ShopSlash(self, ctx: disnake.AppCmdInter):
		pass

	@ShopSlash.sub_command(name="генов", description="Купите гены, чтобы улучшить ваших зверей! Информация о генах: \"/информация гены\"")
	async def GenesShopSub(self, ctx: disnake.AppCmdInter,
							gene_id: int = commands.Param(description="Какой ген желаете приобрести?", name="ген",
														choices=[disnake.OptionChoice(name=f"{i['name']} - {i['cost']} крошек", value=i['id']) for i in rimagochi_genes.values()])):
		gene = rimagochi_genes[gene_id]

		async with self.DataBaseManager.session() as session:
			await self.client.RimagochiUserUpdate(member = ctx.author, session = session)
			async with session.begin():
				stmt = self.DataBaseManager.select(self.DataBaseManager.models['users'].m).options(
					self.DataBaseManager.selectinload(self.DataBaseManager.models['users'].m.rimagochi_account)
				).where(self.DataBaseManager.models['users'].m.id == ctx.author.id).with_for_update()
				user = (await session.execute(stmt)).scalars().first()

				await ctx.response.defer(ephemeral = user.rimagochi_account.settings['hide_the_animals'])

				if user.crumbs < gene['cost']:
					err_embed = self.client.ErrEmbed(title = "Ошибка покупки гена", description = f"Для покупки этого гена необходимо иметь {gene['cost']} крошек")
					await ctx.edit_original_message(err_embed)
					return

				genes = copy.deepcopy(user.rimagochi_account.genes)
				genes.setdefault(str(gene['id']), 0)
				genes[str(gene['id'])] += 1
				user.rimagochi_account.genes = genes

				user.crumbs -= gene['cost']

				history_write = self.DataBaseManager.models['transaction_history_crumbs'].m(sender_id = ctx.author.id, amount = gene['cost'], description = f"Покупка гена \"{gene['name']}\"")
				session.add(history_write)

				embed = self.client.InfoEmbed(title=f"Ген \"{gene['name']}\" успешно приобретён!", description=f"Описание:\n{gene['description']}", colour=0x2F3136)
				embed.set_thumbnail(url = "https://static.wikia.nocookie.net/rimworld/images/f/fc/GeneBackground_Xenogene.png/revision/latest?cb=20221216070153&path-prefix=ru")
				await ctx.edit_original_message(embed=embed)

	
	'''


	Корм


	'''

	@commands.slash_command(name="кормить")
	async def FeedSlash(self, ctx: disnake.AppCmdInter):
		pass

	@FeedSlash.sub_command(description="Покормите всех животных, которых возможно (используются только крошки)", name="всех")
	async def RimagochiFeedAllSub(self, ctx: disnake.AppCmdInter):
		async with self.DataBaseManager.session() as session:
			await self.client.RimagochiUserUpdate(member = ctx.author, session = session)
			async with session.begin():
				user = await session.get(self.DataBaseManager.models['users'].m, ctx.author.id, with_for_update=True)

				async def feed_animal(animal_model, animaldata, food = None):
					food = rimagochi_items[food] if food else None
					animal_model = copy.deepcopy(animal_model)

					if animaldata.feed_today_count >= 4 and (now() - animaldata.first_today_feed_time) < (24*60*60):
						return None

					if (now()-animaldata.last_feeding_time)<(3*60*60):
						return None

					genes = []
					for gene in animaldata.genes:
						genedata = rimagochi_genes[int(gene)]
						genes.append(genedata['name'])
						for effect in genedata['effects'].keys():
							animal_model['params'][effect] += genedata['effects'][effect]

					hunger = (animal_model['params']['hunger'] if animal_model['params']['hunger']>0 else 0)*rimagochi_constants['hanger_multiplayer']/4

					if user.crumbs < hunger:
						return None

					user.crumbs -= hunger

					if (now() - animaldata.first_today_feed_time) >= (24*60*60):
						animaldata.feed_today_count=0
						animaldata.first_today_feed_time=now()
					
					animaldata.feed_today_count+=1
					animaldata.last_feeding_time=now()
					animaldata.experience, animaldata.level, remains = self.client.AnimalLevelAdder(animaldata.experience+100, animaldata.level)

					return hunger

				stmt = self.DataBaseManager.select(self.DataBaseManager.models['rimagochi_animals'].m).where(self.DataBaseManager.models['rimagochi_animals'].m.owner_id == ctx.author.id).with_for_update()
				animals = (await session.execute(stmt)).scalars().all()
				crumbs_amout = 0
				feeded_animals = []
				for animal in animals:
					animal_model = rimagochi_animals[animal.model_animal_id]
					new_feed = await feed_animal(animal_model, animal)
					if new_feed != None:
						crumbs_amout += new_feed
						feeded_animals.append(animal_model['name'])
				
				if crumbs_amout!=0:
					history_write = self.DataBaseManager.models['transaction_history_crumbs'].m(sender_id = ctx.author.id, amount = crumbs_amout, description = f"Корм для " + ", ".join(feeded_animals))
					session.add(history_write)
				embed = self.client.InfoEmbed(title=f"Всего удалось потратить {crumbs_amout:.0f} крошек на {len(feeded_animals)} животных.", description="", colour=0x2F3136)
				stmt = self.DataBaseManager.select(self.DataBaseManager.models['rimagochi_users'].m.settings).where(self.DataBaseManager.models['rimagochi_users'].m.id == ctx.author.id)
				settings = (await session.execute(stmt)).scalars().first()
				if not settings['hide_the_animals']: embed.description = f"Покормлены:\n"+",\n".join(feeded_animals)
				embed.set_thumbnail(url=ctx.author.avatar)
				await ctx.response.send_message(embed=embed)

	'''


	Инвентари


	'''

	@commands.slash_command(name="инвентарь")
	async def InventorySlash(self, ctx: disnake.AppCmdInter):
		pass

	@InventorySlash.sub_command(description="Покажет все ваши предметы", name="предметы")
	async def RimagochiItemsInventorySub(self, ctx: disnake.AppCmdInter, 
											member: disnake.Member = commands.Param(description="Чей инвентарь хотите посмотреть?",
																	name="игрок", default=None)):
		if member == None:
			member = ctx.author

		async with self.DataBaseManager.session() as session:
			await self.client.RimagochiUserUpdate(member = member, session = session)
			async with session.begin():
				user = await session.get(self.DataBaseManager.models['rimagochi_users'].m, member.id)

				err_embed = self.client.ErrEmbed(err_func = ctx.response.send_message, title = "Ошибка инвентаря", description = f"Пользователь {member.mention} скрыл свой инвентарь")
				if isinstance(ctx.author, disnake.Member):
					if user.settings['hide_the_animals'] and member != ctx.author and (not self.client.me in ctx.author.roles):
						await err_embed.send()
						return
				else:
					if user.settings['hide_the_animals'] and member != ctx.author:
						await err_embed.send()
						return
					
				await ctx.response.defer(ephemeral = user.settings['hide_the_animals'])

				embed = self.client.InfoEmbed(title=f"", description=f"### Инвентарь {member.mention}\n", colour=0x2F3136)
				embed.set_thumbnail(url=member.avatar)

				if len([i for i in user.items.keys() if user.items[i]>0]) > 0:
					embed.add_field(name=f"Предметы:", value=f"", inline=False)
					for i in [i for i in user.items.keys() if user.items[i]>0]:
						embed.add_field(name=f"{rimagochi_items[int(i)]['name']} - {int(user.items[i])} штук", value=f"", inline=False)
				if len([i for i in user.genes.keys() if user.genes[i]>0]) > 0:
					embed.add_field(name=f"Гены:", value=f"", inline=False)
					for i in [i for i in user.genes.keys() if user.genes[i]>0]:
						embed.add_field(name=f"{rimagochi_genes[int(i)]['name']} - {int(user.genes[i])} штук", value=f"", inline=False)
				if len(user.items.keys()) == 0 and len(user.genes.keys()) == 0:
					embed.add_field(name=f"Тут пока ничего нет", value=f"", inline=True)
				await ctx.edit_original_message(embed=embed)



	@InventorySlash.sub_command(description="Покажет всех ваших животных, из него их можно покормить или применить генопаки", name="животные")
	async def RimagochiAnimalsInventorySub(self, ctx: disnake.AppCmdInter, 
											member: disnake.Member = commands.Param(description="Чей инвентарь хотите посмотреть?",
																	name="игрок", default=None)):
		if member == None:
			member = ctx.author

		rimagochi_users_model = self.DataBaseManager.models['rimagochi_users'].m
		rimagochi_animals_model = self.DataBaseManager.models['rimagochi_animals'].m
		users_model = self.DataBaseManager.models['users'].m

		async with self.DataBaseManager.session() as session:
			await self.client.RimagochiUserUpdate(member = member, session = session)
			async with session.begin():
				stmt = self.DataBaseManager.select(rimagochi_users_model).options(
					self.DataBaseManager.selectinload(rimagochi_users_model.animals)
				).where(rimagochi_users_model.id == member.id)

				user = (await session.execute(stmt)).scalars().first()
				user.animals.sort(key=lambda animal: animal.creation_time, reverse=True)

				await ctx.response.defer(ephemeral = user.settings['hide_the_animals'])
				err_embed = self.client.ErrEmbed(err_func = ctx.edit_original_message, title = "Ошибка профиля", thumbnail = member.avatar)

				if user.settings['hide_the_animals'] and member != ctx.author and (isinstance(ctx.author, disnake.User) or not self.client.me in ctx.author.roles):
					await err_embed.send(f"Пользователь {member.mention} скрыл свой профиль")
					return

				if len(user.animals) == 0:
					await err_embed.send(f"Кажется, тут зверей пока нет")
					return

		async def AnimalsEmbeder(num: int, review = False):

			animal_data = user.animals[num-1]
			animal = rimagochi_animals[animal_data.model_animal_id]

			embed = self.client.InfoEmbed(title=f"Инвентарь {member.name}", description=f"\n### {animal['params']['rarity']['emoji']} {animal['name'].capitalize()}", colour=0x2F3136)
			embed.set_footer(text = f"id: {animal_data.id}")
			embed.set_thumbnail(url=animal['params']['image_url'])
			animal = copy.deepcopy(animal)
			genes = []
			exp, level, to_next_level = self.client.AnimalLevelAdder(animal_data.experience, animal_data.level)
			for gene in animal_data.genes:
				genedata = rimagochi_genes[int(gene)]
				genes.append(genedata['name'])
				for effect in genedata['effects'].keys():
					animal['params'][effect] += genedata['effects'][effect]


			embed.add_field(name=f"Уровень",
						value=f"`{animal_data.level}`\n|{'█' * int(((exp/(exp+to_next_level)) % 1) * 35) + '░' * (35 - int(((exp/(exp+to_next_level)) % 1) * 35))}|\n",
						inline=False)
			embed.add_field(name=f"Урон:",
							value=f"{animal['params']['damage']*rimagochi_constants['damage_multiplayer']}",
							inline=True)
			embed.add_field(name=f"Здоровье:",
							value=f"{animal['params']['health']*rimagochi_constants['health_multiplayer']}",
							inline=True)
			embed.add_field(name=f"Состоит в отряде?\n(занимает {animal['params']['required_slots']}/{rimagochi_constants['max_battle_slots']} мест)",
							value=f"{'Да' if animal_data.in_battle_slots else 'Нет'}",
							inline=True)
			embed.add_field(name=f"Количество потребляемых крошек(шт/день):",
							value=f"{int((animal['params']['hunger'] if animal['params']['hunger']>0 else 0)*rimagochi_constants['hanger_multiplayer'])}",
							inline=False)

			if (now()-animal_data.first_today_feed_time) >= (24 * 60 * 60):
				animal_data.feed_today_count=0
				animal_data.first_today_feed_time=now()

			if animal_data.feed_today_count >= 4 and (now() - animal_data.first_today_feed_time) < (24 * 60 * 60) and (animal_data.first_today_feed_time+(24 * 60 * 60) > animal_data.last_feeding_time + (3 * 60 * 60)):
				embed.add_field(name=f"Покормлено за сегодня:",
							value=f"{animal_data.feed_today_count} раз (следующий раз <t:{int(animal_data.first_today_feed_time+(24*60*60))}:R>)",
							inline=True)
			elif (now()-animal_data.last_feeding_time)<(3*60*60):
				embed.add_field(name=f"Покормлено за сегодня:",
							value=f"{animal_data.feed_today_count} раз (следующий раз <t:{int(animal_data.last_feeding_time+(3*60*60))}:R>)",
							inline=True)
			else:
				embed.add_field(name=f"Покормлено за сегодня:",
							value=f"{animal_data.feed_today_count} раз (уже доступно)",
							inline=True)

			embed.add_field(name=f"Побед:",
							value=f"{animal_data.wins}",
							inline=True)

			if len(genes) != 0:
				embed.add_field(name=f"Гены", value=f", ".join(genes), inline=False)

			if review:
				await ctx.edit_original_message(embed=embed, view=ButtonsView(animal, animal_data, user.settings, len(user.animals)))
			else:
				await ctx.edit_original_message(embed=embed)

			return animal, animal_data, user.settings

		async def feed_animal(inter, animal, animal_id, food = None):
			err_embed = self.client.ErrEmbed(err_func = inter.response.send_message, err_func_kwargs = {'ephemeral': True}, title = "Ошибка инвентаря")
			async with self.DataBaseManager.session() as session:
				async with session.begin():
					stmt = self.DataBaseManager.select(rimagochi_users_model).options(
						self.DataBaseManager.selectinload(rimagochi_users_model.user)
					).where(rimagochi_users_model.id == member.id).with_for_update()
					rimagochi_user = (await session.execute(stmt)).scalars().first()

					animal_data = await session.get(rimagochi_animals_model, animal_id, with_for_update=True)

					food = rimagochi_items[food] if food else None
					animal = copy.deepcopy(animal)

					if animal_data.feed_today_count >= 4 and (now() - animal_data.first_today_feed_time) < (24 * 60 * 60):
						await err_embed.send(f"Вы уже покормили своего зверя 4 раза за сегодня, обновление лимитов будет <t:{int(animal_data.first_today_feed_time + (24 * 60 * 60))}:R>")
						return

					if (now() - animal_data.last_feeding_time) < (3 * 60 * 60):
						await err_embed.send(f"Следующий раз можно покормить <t:{int(animal_data.last_feeding_time + (3 * 60 * 60))}:R>")
						return

					genes = []
					for gene in animal_data.genes:
						genedata = rimagochi_genes[int(gene)]
						genes.append(genedata['name'])
						for effect in genedata['effects'].keys():
							animal['params'][effect] += genedata['effects'][effect]

					hunger = (animal['params']['hunger'] if animal['params']['hunger']>0 else 0)*rimagochi_constants['hanger_multiplayer']/4


					if food:
						items = copy.deepcopy(rimagochi_user.items)
						if (not str(food['id']) in items.keys()) or items[str(food['id'])] < hunger / 10:
							await err_embed.send(f"У вас недостаточно {food['name']}")
							return

						items[str(food['id'])] = items[str(food['id'])] - hunger / 10
						rimagochi_user.items = items
					else:
						if rimagochi_user.user.crumbs < hunger:
							await err_embed.send(f"У вас недостаточно крошек")
							return

						rimagochi_user.user.crumbs -= hunger
						history_write = self.DataBaseManager.models['transaction_history_crumbs'].m(sender_id = ctx.author.id, amount = hunger, description = f"Корм для {animal['name']}")
						session.add(history_write)

					if (now() - animal_data.first_today_feed_time) >= (24 * 60 * 60):
						animal_data.feed_today_count = 1
						animal_data.first_today_feed_time = now()
					else:
						animal_data.feed_today_count += 1

					animal_data.last_feeding_time = now()
					animal_data.experience, animal_data.level, remains = self.client.AnimalLevelAdder(animal_data.experience+100, animal_data.level)

					embed = self.client.InfoEmbed(description=f"{animal['name'].capitalize()} покормлен, до следующего уровня ему осталось всего {remains} опыта", title=f"", colour=0x2F3136)
					await inter.response.send_message(embed = embed, ephemeral=True)

					nonlocal user

					stmt = self.DataBaseManager.select(rimagochi_users_model).options(
						self.DataBaseManager.selectinload(rimagochi_users_model.animals)
					).where(rimagochi_users_model.id == member.id)

					user = (await session.execute(stmt)).scalars().first()
					user.animals.sort(key=lambda animal: animal.creation_time, reverse=True)


		class FeedModal(disnake.ui.Modal):
			def __init__(self, buttons):
				self.animal = buttons.animal
				can_eate = ['крошки']+[i['item']['name'] for i in self.animal['params']['can_eate']]
				string = []
				for i in range(len(can_eate)):
					string.append(f"{i+1} - {can_eate[i]}")
				components = [disnake.ui.TextInput(label=f"Чем кормить?", custom_id="feed_animal", style=disnake.TextInputStyle.short, placeholder=f"Введите число: {', '.join(string)}", max_length=1)]
				super().__init__(title=f"Выберите, чем хотите покормить", components=components)
				self.buttons = buttons
				self.animal_id = buttons.animal_data.id
				self.done = asyncio.Event()

			async def callback(self, inter: disnake.ModalInteraction):
				feedback = int(inter.text_values["feed_animal"])
				if feedback == 1:
					await feed_animal(inter, self.animal, self.animal_id)
				else:
					item = self.animal['params']['can_eate'][feedback-2]['item']
					await feed_animal(inter, self.animal, self.animal_id, item['id'])
				self.done.set()
			async def wait(self):
				await self.done.wait()


		class ButtonsView(disnake.ui.View):
			DataBaseManager = self.DataBaseManager
			client = self.client
			def __init__(self, animal, animal_data, settings, max_page):
				super().__init__(timeout = 180)
				self.animal = animal
				self.animal_data = animal_data
				self.settings = settings
				self.page = 1
				self.max_page = max_page
				self.update_button_labels()

			@disnake.ui.button(label="Покормить", style=disnake.ButtonStyle.success, row=1)
			async def feed_modal(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if member != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Нельзя кормить чужих животных!!!")
					await inter.response.send_message(embed=err_embed, ephemeral=True)
					return
				if len(self.animal["params"]["can_eate"])==0 or self.settings['always_use_crumbs_for_feeding']:
					await feed_animal(inter, self.animal, self.animal_data.id)
				else:
					modal = FeedModal(self)
					await inter.response.send_modal(modal)
					await modal.wait()

				self.animal, self.animal_data, self.settings = await AnimalsEmbeder(self.page)

			@disnake.ui.button(label="Забить", style=disnake.ButtonStyle.danger, row=1)
			async def kill_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if member != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Нельзя убивать чужих животных!!!")
					await inter.response.send_message(embed=err_embed, ephemeral=True)
					return
				await inter.response.defer()
				self.stop()
				class MixedView(disnake.ui.View):
					client = self.client
					DataBaseManager = self.DataBaseManager
					animal_data = self.animal_data
					animal = self.animal
					def __init__(self):
						super().__init__(timeout = 60)
						self.add_item(disnake.ui.Button(label="Забить!!!", style=disnake.ButtonStyle.danger, custom_id="accept"))
						self.add_item(disnake.ui.Button(label="Нет, отменяй", style=disnake.ButtonStyle.success, custom_id="reject"))
					async def interaction_check(self, interaction):
						if member != interaction.author:
							err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Нельзя убивать чужих животных!!!")
							await interaction.response.send_message(embed=err_embed, ephemeral=True)
							return True
						if interaction.data.custom_id == "accept":
							async with self.DataBaseManager.session() as session:
								async with session.begin():
									animal = await session.get(rimagochi_animals_model, self.animal_data.id, with_for_update = True)
									if animal is None:
										return True
									await session.delete(animal)

									user = await session.get(rimagochi_users_model, member.id, with_for_update = True)

									items = copy.deepcopy(user.items)
									receiveditems = {}
									for item in self.animal['params']['after_death']:
										items.setdefault(str(item['item']['id']), 0)
										receive=random.randint(*item['count'])
										receiveditems.setdefault(item['item']['name'], receive)
										items[str(item['item']['id'])] += receive
									user.items = items

									embed = self.client.InfoEmbed(title=f"~~{self.animal['name'].capitalize()}~~", description=",\n".join(f"{i} - {receiveditems[i]}" for i in receiveditems.keys()), colour=0x2F3136)
									embed.set_thumbnail(url = "https://static.wikia.nocookie.net/rimworld/images/a/ad/Мясо.png/revision/latest?cb=20190130152311&path-prefix=ru")
									await ctx.edit_original_message(embed=embed, view=None)

						if interaction.data.custom_id == "reject":
							await interaction.response.defer()
							embed = self.client.InfoEmbed(title=f"", description=f"В этот раз {self.animal['name']} остался в живых", colour=0x2F3136)
							await ctx.edit_original_message(embed=embed, view=None)
						
						self.stop()
						return False
					async def on_timeout(self):
						embed = self.client.InfoEmbed(title=f"Выбор не сделан", description=f"В этот раз {self.animal['name']} остался в живых", colour=0x2F3136)
						await ctx.edit_original_message(embed=embed, view=None)

				embed = self.client.WarnEmbed(title=f"Вы вменяемы?", description=f"{self.animal['name']} умрёт и вы потеряете все гены и опыт с него!!!", colour=0x2F3136)
				await ctx.edit_original_message(embed=embed, view=MixedView())

			@disnake.ui.button(label = ".", style=disnake.ButtonStyle.primary, row=1)
			async def battle_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if member != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Вы не можете управлять чужим отрядом")
					await inter.response.send_message(embed=err_embed, ephemeral=True)
					return
				async with self.DataBaseManager.session() as session:
					async with session.begin():
						stmt = self.DataBaseManager.select(rimagochi_users_model).options(
							self.DataBaseManager.selectinload(rimagochi_users_model.battle_slots_animals)
						).where(rimagochi_users_model.id == member.id).with_for_update()
						rimagochi_user = (await session.execute(stmt)).scalars().first()
						animal_data = await session.get(rimagochi_animals_model, self.animal_data.id, with_for_update = True)

						busy_battle_slots = sum(
							[
								rimagochi_animals[i.model_animal_id]['params']['required_slots']
								for i in rimagochi_user.battle_slots_animals
							] + [0]
						)
						if animal_data.in_battle_slots:
							animal_data.in_battle_slots = False

						else:
							if busy_battle_slots + self.animal['params']['required_slots'] > rimagochi_constants['max_battle_slots']:
								embed = self.client.InfoEmbed(title=f"у вас нет столько свободного места в отряде!!!", description=f"", colour=0x2F3136)
								await inter.response.send_message(embed=embed, ephemeral=True)
								return
							animal_data.in_battle_slots = True

						nonlocal user

						stmt = self.DataBaseManager.select(rimagochi_users_model).options(
							self.DataBaseManager.selectinload(rimagochi_users_model.animals)
						).where(rimagochi_users_model.id == member.id)

						user = (await session.execute(stmt)).scalars().first()
						user.animals.sort(key=lambda animal: animal.creation_time, reverse=True)

						self.animal, self.animal_data, self.settings = await AnimalsEmbeder(self.page)
						self.update_button_labels()
						await inter.response.defer()
						await inter.edit_original_message(view=self)

			@disnake.ui.button(label="Применить ген", style=disnake.ButtonStyle.primary, row=1)
			async def apply_genes_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if member != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Вы не можете управлять чужим отрядом")
					await inter.response.send_message(embed=err_embed, ephemeral=True)
					return
				class ApplyGenesView(disnake.ui.View):
					client = self.client
					DataBaseManager = self.DataBaseManager
					animal_data = self.animal_data
					animal = self.animal
					def __init__(self, suitable_genes):
						super().__init__(timeout = 60)
						self.add_item(disnake.ui.Select(
							placeholder="Выберите вариант",
							options=[
								disnake.SelectOption(label=rimagochi_genes[int(i)]['name'], value=i) for i in suitable_genes
							]
						))
					async def interaction_check(self, interaction: disnake.MessageInteraction):
						if member != inter.author:
							err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Вы не можете управлять чужим отрядом")
							await inter.response.send_message(embed=err_embed, ephemeral=True)
							return True
						if interaction.data.values is None:
							raise ValueError("rimagochi.py: interaction.data.values None type")
						selected_value = interaction.data.values[0]

						async with self.DataBaseManager.session() as session:
							async with session.begin():
								rimagochi_user = await session.get(rimagochi_users_model, ctx.author.id, with_for_update = True)
								self.animal_data = await session.get(rimagochi_animals_model, self.animal_data.id, with_for_update = True)

								suitable_genes = [i for i in rimagochi_user.genes.keys() if (not int(i) in animal_data.genes) and rimagochi_user.genes[i] > 0]

								if not selected_value in suitable_genes:
									err_embed = self.client.ErrEmbed(title = "Ошибка применения генов", description = "У вас больше нет этого гена или ген уже был применён")
									await inter.response.send_message(embed=err_embed, ephemeral=True)
									return True

								animal_genes = copy.deepcopy(self.animal_data.genes)
								animal_genes.append(int(selected_value))
								self.animal_data.genes = animal_genes

								user_genes = copy.deepcopy(rimagochi_user.genes)
								user_genes[selected_value]-=1
								rimagochi_user.genes = user_genes

								suitable_genes.remove(selected_value)

						embed = self.client.InfoEmbed(title=f"", description=f"В животное `{self.animal['name']}` успешно вставлен ген {rimagochi_genes[int(selected_value)]['name']}", colour=0x2F3136)
						await interaction.response.send_message(embed = embed, ephemeral=True)
						if len(suitable_genes) != 0:
							await ctx.edit_original_message(view=ApplyGenesView(suitable_genes))
						else:
							await ctx.edit_original_message(view=None)
						
						return False

					async def on_timeout(self):
						await ctx.edit_original_message(view=None)

				async with self.DataBaseManager.session() as session:
					async with session.begin():
						rimagochi_user = await session.get(rimagochi_users_model, ctx.author.id)
						animal_data = await session.get(rimagochi_animals_model, self.animal_data.id)

						suitable_genes = [i for i in rimagochi_user.genes.keys() if (not int(i) in animal_data.genes) and rimagochi_user.genes[i] > 0]

						if len(suitable_genes) == 0:
							err_embed = self.client.ErrEmbed(title = "Ошибка применения генов", description = f"У вас пока нет генов, которые можно применить на {self.animal['name']}")
							await inter.response.send_message(embed=err_embed, ephemeral=True)
							return

						self.stop()
						await inter.response.defer()
						embed = self.client.InfoEmbed(title=f"Какие гены хотите применить на животное {self.animal['name']}?", description=f"Будьте внимательны, вернуть использованные генопаки уже не выйдет", colour=0x2F3136)
				await ctx.edit_original_message(embed=embed, view=ApplyGenesView(suitable_genes))

			@disnake.ui.button(label="<", style=disnake.ButtonStyle.secondary, row=2)
			async def backward_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if ctx.author != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Вы не можете управлять чужим инвентарём")
					await inter.response.send_message(embed=err_embed, ephemeral=True)
					return
				await inter.response.defer()
				self.page = max(self.page-1, 1)
				self.animal, self.animal_data, self.settings = await AnimalsEmbeder(self.page)
				self.update_button_labels()
				await inter.edit_original_message(view=self)

			@disnake.ui.button(label=">", style=disnake.ButtonStyle.secondary, row=2)
			async def forward_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if ctx.author != inter.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Вы не можете управлять чужим инвентарём")
					await inter.response.send_message(embed=err_embed, ephemeral=True)
					return
				await inter.response.defer()
				self.page = min(self.page+1, self.max_page)
				self.animal, self.animal_data, self.settings = await AnimalsEmbeder(self.page)
				self.update_button_labels()
				await inter.edit_original_message(view=self)

			async def on_timeout(self):
				await ctx.edit_original_message(view=None)

			def update_button_labels(self):
				for child in self.children:
					if isinstance(child, disnake.ui.Button):
						if child.custom_id == self.battle_button.custom_id:
							child.label = "Взять в бой" if not self.animal_data.in_battle_slots else "Убрать из отряда"
						elif child.label == ">":
							child.disabled = (self.page >= self.max_page)
						elif child.label == "<":
							child.disabled = (self.page <= 1)

		await AnimalsEmbeder(1, review = True)

	'''


	Сражения


	'''

	@commands.slash_command(name="бросить")
	async def ChallengeSlash(self, ctx: disnake.AppCmdInter):
		pass

	@ChallengeSlash.sub_command(description="Можно бросить вызов адресно (заполнив поле 'игрок'), а можно любому, кто захочет его принять", name="вызов")
	async def ChallengeSub(self, ctx: disnake.AppCmdInter, bet: commands.Range[int, 1000, ...] = commands.Param(description="Введите ставку",
																	name="ставка"),
											member: disnake.Member = commands.Param(description="Кому хотите бросить вызов?",
																	name="игрок", default=None)):
		
		err_embed = self.client.ErrEmbed(err_func = ctx.response.send_message, err_func_kwargs = {'ephemeral': True}, title = "Ошибка вызова")
		if ctx.author == member:
			await err_embed.send(f"Нельзя бросить вызов самому себе")
			return

		rimagochi_users_model = self.DataBaseManager.models['rimagochi_users'].m
		async with self.DataBaseManager.session() as session:
			await self.client.RimagochiUserUpdate(member = ctx.author, session = session)
			async with session.begin():
				stmt = self.DataBaseManager.select(rimagochi_users_model).options(
					self.DataBaseManager.joinedload(rimagochi_users_model.user),
					self.DataBaseManager.selectinload(rimagochi_users_model.battle_slots_animals)
				).where(rimagochi_users_model.id == ctx.author.id)
				author_user = (await session.execute(stmt)).scalars().first()

				if author_user.user.crumbs < bet:
					await err_embed.send(f"Вам не хватает крошек на такую ставку")
					return

				if len(author_user.battle_slots_animals)==0:
					await err_embed.send(f"У вас нет экипированных зверей")
					return

				if not author_user.settings['accept_the_challenge']:
					await err_embed.send(f"Чтобы бросить вызов, у вас должна быть включена настройка 'получать вызовы'")
					return

				if not member is None:
					stmt = self.DataBaseManager.select(rimagochi_users_model).options(
						self.DataBaseManager.joinedload(rimagochi_users_model.user),
						self.DataBaseManager.selectinload(rimagochi_users_model.battle_slots_animals)
					).where(rimagochi_users_model.id == member.id)
					member_user = (await session.execute(stmt)).scalars().first()

					if member_user is None:
						await err_embed.send(f"У этого пользователя пока нет профиля")
						return

					if member_user.user.crumbs < bet:
						await err_embed.send(f"Вашему оппоненту не хватает крошек на такую ставку")
						return

					if len(member_user.battle_slots_animals)==0:
						await err_embed.send(f"У вашего оппонента нет экипированных зверей")
						return

					if not member_user.settings['accept_the_challenge']:
						await err_embed.send(f"Этот пользователь не принимает вызовы")
						return

		class ButtonsView(disnake.ui.View):
			client = self.client
			DataBaseManager = self.DataBaseManager
			CalculateRimagochiBattleStrength = self.client.CalculateRimagochiBattleStrength
			def __init__(self, author, member, bet):
				super().__init__(timeout = 180)
				self.member = member
				self.author = author
				self.bet = bet

			@disnake.ui.button(label="Принять вызов", style=disnake.ButtonStyle.success, row=1)
			async def take_challenge(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				
				err_embed = self.client.ErrEmbed(err_func = inter.response.send_message, err_func_kwargs = {'ephemeral': True}, title = "Ошибка вызова")
				if self.member:
					if self.member != inter.author:
						await err_embed.send(f"Этот вызов был брошен не вам, к сожалению, вы не сможете его принять")
						return
				elif inter.author == self.author:
					await err_embed.send(f"Вы не можете принять свой же вызов!!!")
					return
				else:
					self.member = inter.author
				rimagochi_users_model = self.DataBaseManager.models['rimagochi_users'].m
				async with self.DataBaseManager.session() as session:
					async with session.begin():
						stmt = self.DataBaseManager.select(rimagochi_users_model).options(
							self.DataBaseManager.selectinload(rimagochi_users_model.user),
							self.DataBaseManager.selectinload(rimagochi_users_model.animals)
						).where(rimagochi_users_model.id == ctx.author.id).with_for_update()
						author_user = (await session.execute(stmt)).scalars().first()

						stmt = self.DataBaseManager.select(rimagochi_users_model).options(
							self.DataBaseManager.selectinload(rimagochi_users_model.user),
							self.DataBaseManager.selectinload(rimagochi_users_model.animals)
						).where(rimagochi_users_model.id == self.member.id).with_for_update()
						member_user = (await session.execute(stmt)).scalars().first()

						if member_user is None:
							await err_embed.send(f"У вас пока нет профиля, напишите хотя бы одно сообщение")
							return

						if not member_user.settings['accept_the_challenge']:
							await err_embed.send(f"Чтобы принять вызов, у вас должна быть включена настройка 'получать вызовы'")
							return

						if member_user.user.crumbs < self.bet:
							await err_embed.send(f"Вам не хватает крошек, чтобы принять этот вызов")
							return

						if len([animal for animal in member_user.animals if animal.in_battle_slots]) == 0:
							await err_embed.send(f"У вас нет экипированных зверей")
							return

						self.stop()
						await ctx.edit_original_message("", view = None)

						if author_user.user.crumbs < self.bet:
							err_embed = self.client.ErrEmbed(title = err_embed.title, description = f"{self.author.mention} не хватает крошек на ставку, бой отменяется")
							await ctx.edit_original_message(embed=err_embed)
							return

						players_list = [self.author, self.member]
						db_players_list = [author_user, member_user]
						weights_list = [await self.CalculateRimagochiBattleStrength(author_user.animals), await self.CalculateRimagochiBattleStrength(member_user.animals)]

						chosen_player = random.choices(
							population=[0, 1],
							weights=weights_list,
							k=1
						)[0]

						db_players_list[chosen_player].wins += 1
						for animal in db_players_list[chosen_player].animals:
							if animal.in_battle_slots:
								animal.wins += 1

						db_players_list[chosen_player].user.crumbs += self.bet * 0.9
						db_players_list[1-chosen_player].user.crumbs -= self.bet

						history_write = self.DataBaseManager.models['transaction_history_crumbs'].m(sender_id = players_list[1-chosen_player].id, recipient_id = players_list[chosen_player].id, amount = self.bet, commission_fraction = 0.1, description = f"Бой зверей")
						session.add(history_write)

				await inter.response.defer()

				for i in range(10, 0, -1):
					embed = self.client.InfoEmbed(title=f"", description=f"### Вызов принят {self.member.mention}\nИдёт подсчёт сил и рассчёт победителя...\n-# Результат будет через {i} секунд", colour=0x2F3136)
					embed.set_thumbnail(url="https://media.discordapp.net/attachments/887735863734313000/1357768401195634728/confused-cat-confused.gif?ex=67f167dc&is=67f0165c&hm=bebc160fac83107c143b93c825b926cbf83caf9d5eb56535c4c11ada09e57103&=")
					await ctx.edit_original_message(embed=embed)
					await asyncio.sleep(1)
				embed = self.client.InfoEmbed(title=f"", description=f"### Победил {players_list[chosen_player].mention}!\n\nИздалека все могли видеть сражающихся животных:\n"
															 f"На стороне {self.author.mention}: {', '.join(rimagochi_animals[animal.model_animal_id]['name'] for animal in author_user.animals if animal.in_battle_slots)}\n"
															 f"На стороне {self.member.mention}: {', '.join(rimagochi_animals[animal.model_animal_id]['name'] for animal in member_user.animals if animal.in_battle_slots)}", colour=0x2F3136)
				embed.set_thumbnail(url=players_list[chosen_player].avatar)
				await ctx.edit_original_message(embed=embed)

			@disnake.ui.button(label="Отменить вызов", style=disnake.ButtonStyle.danger, row=1)
			async def off_challenge(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
				if inter.author != self.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = f"Отменить этот вызов может только {self.author.mention}")
					await inter.response.send_message(embed=err_embed, ephemeral = True)
					return
				embed = self.client.InfoEmbed(title=f"", description=f"### {self.author.mention} отменил вызов на бой", colour=0x2F3136)
				embed.set_thumbnail(url=self.author.avatar)
				self.stop()
				await ctx.edit_original_message("", embed = embed, view = None)

			async def on_timeout(self):
				embed = self.client.InfoEmbed(title=f"", description=f"\n### Вызов от {ctx.author.mention}(просрочено)\nВы уже не можете принять вызов, нажав на кнопку ниже.\n-# Ставка `{bet}` крошек", colour=0x2F3136)
				embed.set_thumbnail(url=ctx.author.avatar)
				await ctx.edit_original_message(embed=embed, view=None)

		embed = self.client.InfoEmbed(title=f"", description=f"### Вызов от {ctx.author.mention}\nВы можете принять вызов, нажав на кнопку ниже!\n-# Ставка `{bet}` крошек", colour=0x2F3136)
		embed.set_thumbnail(url=ctx.author.avatar)
		await ctx.response.send_message(f"{member.mention}" if member else None, embed=embed, view = ButtonsView(ctx.author, member, bet))

	'''


	Википедия


	'''

	@commands.slash_command(name="информация")
	async def InformationSubGroup(self, ctx: disnake.AppCmdInter):
		pass

	@staticmethod
	async def animal_autocomplete(interaction: disnake.ApplicationCommandInteraction, user_input: str):
		animals = [
			animal["name"]
			for animal in rimagochi_animals.values()
			if user_input.lower() in animal["name"].lower()
		][:25]
		return animals

	@InformationSubGroup.sub_command(description="Показывает информацию о выбранном животном", name="животные")
	async def RimagochiBestiarySub(self, ctx: disnake.AppCmdInter,
								animal_str: str = commands.Param(description="Название животного или его ID", name="животное",
										autocomplete=animal_autocomplete)):
		matches = {}
		animal_formated = animal_str.lower()
		finded_flag = False
		animal = {}
		if animal_formated.isnumeric() and int(animal_formated) in rimagochi_animals.keys():
			animal = rimagochi_animals[int(animal_formated)]
			finded_flag = True
		else:
			for key, value in rimagochi_animals.items():
				if animal_formated in value['name'].lower():
					matches.setdefault(key, value['name'])
				if animal_formated == value['name'].lower():
					animal = rimagochi_animals[key]
					finded_flag = True
					break
			if (not finded_flag) and (not matches):
				for key, value in rimagochi_animals.items():
					if animal_formated in value['description'].lower():
						matches.setdefault(key, value['name'])
		if len(matches)==1 and (not finded_flag):
			animal = rimagochi_animals[list(matches.keys())[0]]
			finded_flag = True

		if not finded_flag and len(matches)==0:
			embed = self.client.InfoEmbed(title=f"", description=f"Мы искали как могли, но не смогли найти такого зверя", colour=0x2F3136)
			await ctx.response.send_message(embed = embed)
			return
		elif not finded_flag:
			embed = self.client.InfoEmbed(title=f"", description=f"Мы нашли много совпадений, но ничего конкретного, уточните запрос\n-# Найдено совпадений: {', '.join([i for i in matches.values()])}", colour=0x2F3136)
			await ctx.response.send_message(embed = embed)
			return

		await ctx.response.defer()
		embed = self.client.InfoEmbed(title=f"{animal['name'].capitalize()}", description=f"{animal['description']}", colour=0x2F3136)
		embed.set_thumbnail(url = animal['params']['image_url'])
		embed.set_footer(text = f"id: {animal['id']}")
		embed.add_field(name=f"Редкость:",
							value=f"{animal['params']['rarity']['emoji']} {animal['params']['rarity']['name']}",
							inline=False)
		embed.add_field(name=f"Основные характеристики".center(40, '-'),value=f"",inline=False)
		embed.add_field(name=f"Количество потребляемых крошек(шт/день):",
							value=f"{int(animal['params']['hunger']*rimagochi_constants['hanger_multiplayer'])}",
							inline=True)
		embed.add_field(name=f"Может питаться:",
							value=f"{', '.join(['крошки']+[i['item']['name'] for i in animal['params']['can_eate']])}",
							inline=True)
		embed.add_field(name=f"Ресурсы при смерти:",
							value=', \n'.join([f"{i['item']['name']} ≈x{int(sum(i['count'])/2)}" for i in animal['params']['after_death']]),
							inline=True)
		embed.add_field(name=f"Боевые характеристики".center(40, '-'),value=f"",inline=False)
		embed.add_field(name=f"Занимает слотов в бою:",
							value=f"{animal['params']['required_slots']}/{rimagochi_constants['max_battle_slots']}",
							inline=True)
		embed.add_field(name=f"Урон:",
							value=f"{animal['params']['damage']*rimagochi_constants['damage_multiplayer']}",
							inline=True)
		embed.add_field(name=f"Здоровье:",
							value=f"{animal['params']['health']*rimagochi_constants['health_multiplayer']}",
							inline=True)

		await ctx.edit_original_message(embed=embed)

	@InformationSubGroup.sub_command(description="Показывает информацию о выбранном предмете", name="предметы")
	async def RimagochiItemsInfoSub(self, ctx: disnake.AppCmdInter,
								item_id: str = commands.Param(description="Название предмета",
																	name="предмет",
																	choices=[disnake.OptionChoice(name=f"{i['name']}", value=str(i['id'])) for i in rimagochi_items.values()])):
		item = rimagochi_items[int(item_id)]
		await ctx.response.defer()
		embed = self.client.InfoEmbed(title=f"{item['name'].capitalize()}", description=f"{item['description']}", colour=0x2F3136)
		embed.set_footer(text = f"id: {item['id']}")
		embed.add_field(name=f"Основные характеристики".center(40, '-'),value=f"",inline=False)
		embed.add_field(name=f"Стоимость при продаже:",
							value=f"{item['sell_cost']}",
							inline=True)
		'''embed.add_field(name=f"Стоимость при покупке на рынке:",
													value=f"{item['buy_cost']}",
													inline=True)
								embed.add_field(name=f"Стоимость при покупке в магазине:",
													value=f"{item['shop_cost']}",
													inline=True)'''

		await ctx.edit_original_message(embed=embed)

	@InformationSubGroup.sub_command(description="Показывает информацию о выбранном генопаке", name="генопаки")
	async def RimagochiGenesInfoSub(self, ctx: disnake.AppCmdInter,
								gene_id: str = commands.Param(description="Название гена",
																	name="ген",
																	choices=[disnake.OptionChoice(name=f"{i['name']}", value=str(i['id'])) for i in rimagochi_genes.values()])):
		gene = rimagochi_genes[int(gene_id)]
		await ctx.response.defer()
		embed = self.client.InfoEmbed(title=f"{gene['name'].capitalize()}", description=f"{gene['description']}", colour=0x2F3136)
		embed.set_footer(text = f"id: {gene['id']}")
		embed.set_thumbnail(url = "https://static.wikia.nocookie.net/rimworld/images/f/fc/GeneBackground_Xenogene.png/revision/latest?cb=20221216070153&path-prefix=ru")

		await ctx.edit_original_message(embed=embed)

	@InformationSubGroup.sub_command(description="Показывает информацию о выбранной капсуле криптосна", name="капсулы")
	async def RimagochiCapsuleInfoSub(self, ctx: disnake.AppCmdInter,
								capsule_id: str = commands.Param(description="Название капсулы",
																	name="капсула",
																	choices=[disnake.OptionChoice(name=f"{i['name']}", value=str(i['id'])) for i in rimagochi_capsules.values()])):
		capsule = rimagochi_capsules[int(capsule_id)]
		await ctx.response.defer()
		embed = self.client.InfoEmbed(title=f"{capsule['name'].capitalize()}", description=f"Цена: {capsule['cost']}", colour=0x2F3136)
		embed.set_footer(text = f"id: {capsule['id']}")
		for i in capsule['chances']:
			embed.add_field(name=f"",value=f"{i['rarity']['emoji']} {i['rarity']['name']} - {i['chance']*100:.02f}%",inline=False)

		await ctx.edit_original_message(embed=embed)
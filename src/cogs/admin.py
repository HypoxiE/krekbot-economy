
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


def setup(bot):
	bot.add_cog(MainAdminModule(bot))

class MainAdminModule(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.DataBaseManager = client.DataBaseManager

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'KrekFunBot admin module activated')
		self.krekchat = await self.client.fetch_guild(constants["krekchat"])
		self.me = disnake.utils.get(self.krekchat.roles, id=constants["me"])
		

	@commands.slash_command(name="bot_fun_off")
	async def BotFunOff(self, ctx: disnake.ApplicationCommandInteraction):
		if isinstance(ctx.author, disnake.User) or ctx.guild is None:
			await ctx.send(embed=self.client.ErrEmbed(description=f'Не допустимо в личных сообщениях'), ephemeral=True)
			return
		
		if self.me in ctx.author.roles:
			await ctx.send(embed=self.client.InfoEmbed(description=f'Бот отключён'), ephemeral=True)
			await self.client.BotOff()
		else:
			await ctx.send(embed=self.client.ErrEmbed(description=f'Не допустимо'), ephemeral=True)


	@commands.slash_command(name="зарегистрировать_призовую_роль")
	async def RegisterAPrizeRoleSlash(self, ctx, role: disnake.Role):
		await ctx.response.defer(ephemeral=True)
		if not self.me in ctx.author.roles:
			await ctx.edit_original_message(
				embed=self.client.ErrEmbed(description=f'Эта команда доступна только администратору'))
			return

		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['roles_prize'] as roles_prize_model:
					stmt = self.DataBaseManager.select(roles_prize_model).where(roles_prize_model.id == role.id)
					role_prize = (await session.execute(stmt)).scalars().first()
					if role_prize is None:
						prize_role = roles_prize_model(id = role.id)
						session.add(prize_role)
						await ctx.edit_original_message(embed=self.client.InfoEmbed(description=f'Теперь роль {role.mention} зарегистрирована!'))
					else:
						await ctx.edit_original_message(embed=self.client.ErrEmbed(description=f'Эта роль уже зарегистрирована!'))
		


	@commands.slash_command(name="выдать_призовую_роль")
	async def GiveAPrizeRoleSlash(self, ctx, role: disnake.Role, member: disnake.Member):
		await ctx.response.defer(ephemeral=True)
		if not self.me in ctx.author.roles:
			await ctx.edit_original_message(embed=self.client.ErrEmbed(description=f'Эта команда доступна только администратору'))
			return

		async with self.DataBaseManager.session() as session:
			await self.client.UserUpdate(member, session = session)
			async with session.begin():
				async with self.DataBaseManager.models['roles_prize'] as roles_prize_model:

					stmt = self.DataBaseManager.select(roles_prize_model).where(roles_prize_model.id == role.id)
					role_prize = (await session.execute(stmt)).scalars().first()
					if role_prize is None:
						await ctx.edit_original_message(embed=self.client.ErrEmbed(description=f'Данная роль не зарегистрирована как призовая'))
						return 1

				async with self.DataBaseManager.models['received_roles_prize'] as received_roles_prize_model:
					stmt = self.DataBaseManager.select(received_roles_prize_model).where(
						received_roles_prize_model.role_id == role.id,
						received_roles_prize_model.user_id == member.id
					)
					received_roles_prize = (await session.execute(stmt)).scalars().first()
					if not received_roles_prize is None:
						await ctx.edit_original_message(embed=self.client.ErrEmbed(description=f'У {member.mention} уже есть роль {role.mention}'))
						return 1

					received_roles_prize = received_roles_prize_model(role_id = role.id, user_id = member.id)
					session.add(received_roles_prize)

		embed = self.client.InfoEmbed(description=f'Роль {role.mention} успешно передана {member.mention}!')
		await member.add_roles(role)
		await ctx.edit_original_message(embed=embed)


	@commands.slash_command(name="забрать_призовую_роль")
	async def TakeAwayAPrizeRoleSlash(self, ctx, role: disnake.Role, member: disnake.Member):
		await ctx.response.defer(ephemeral=True)
		if not self.me in ctx.author.roles:
			await ctx.edit_original_message(embed=self.client.ErrEmbed(description=f'Эта команда доступна только администратору'))
			return

		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['received_roles_prize'] as received_roles_prize_model:
					stmt = self.DataBaseManager.select(received_roles_prize_model).where(
						received_roles_prize_model.user_id == member.id,
						received_roles_prize_model.role_id == role.id
					).with_for_update()
					user_role = (await session.execute(stmt)).scalars().first()
					if user_role is None:
						await ctx.edit_original_message(embed=self.client.ErrEmbed(description=f'Данный пользователь не связан с этой ролью'))
						return

					await session.delete(user_role)
		embed = self.client.InfoEmbed(description=f'Роль {role.mention} удалена из инвентаря {member.mention}!')
		await member.remove_roles(role)
		await ctx.edit_original_message(embed=embed)


	@commands.slash_command(name="удалить_роль")
	async def DeleteRoleSlash(self, ctx: disnake.AppCmdInter, roleid: str):
		if isinstance(ctx.author, disnake.User) or ctx.guild is None:
			await ctx.send(embed=self.client.ErrEmbed(description=f'Не допустимо в личных сообщениях'), ephemeral=True)
			return
		
		if not self.me in ctx.author.roles:
			await ctx.send(embed=self.client.ErrEmbed(description=f'Эта команда доступна только администратору'))
			return
		try:
			res = await self.client.DeleteRole(int(roleid))
			await ctx.send(embed=self.client.InfoEmbed(description=f'{res[1]}'), ephemeral=True)
		except ValueError:
			await ctx.send(embed=self.client.ErrEmbed(description=f'Введён неверный id'), ephemeral=True)


	@commands.slash_command(name="установить_описание_роли")
	async def RoleDescriptoinSetSlash(self, ctx, role: disnake.Role, description: str):
		await ctx.response.defer(ephemeral=True)
		if not self.me in ctx.author.roles:
			await ctx.edit_original_message(embed=self.client.ErrEmbed(description=f'Эта команда доступна только администратору'))
			return

		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['roles_static'] as roles_static_model:
					stmt = self.DataBaseManager.select(roles_static_model).where(
						roles_static_model.id == role.id
					).with_for_update()
					role_static = (await session.execute(stmt)).scalars().first()
					if role_static is None:
						role = roles_static_model(id = role.id, description = description)
						session.add(role)
					else:
						role_static.description = description
		await ctx.edit_original_message(embed=self.client.InfoEmbed(description=f'Для роли {role.mention} успешно установлено описание\n```{description}```'))
		return

	@commands.slash_command(name = "изменить_параметр")
	async def ChangeParamSlash(self, ctx: disnake.AppCmdInter, member: disnake.Member, vector: int, parameter: str = commands.Param(description="Какой параметр хотите изменить?",
																									 name="параметр",
																									 choices=['крошки', 'сообщения', 'секунды в голосовом канале', 'репутация', 'зарплата'])):
		if isinstance(ctx.author, disnake.User) or ctx.guild is None:
			await ctx.send(embed=self.client.ErrEmbed(description=f'Не допустимо в личных сообщениях'), ephemeral=True)
			return
		
		if not self.me in ctx.author.roles:
			await ctx.edit_original_message(embed=self.client.ErrEmbed(description=f'Эта команда доступна только администратору'))
			return

		async with self.DataBaseManager.session() as session:
			await self.client.UserUpdate(member, session = session)
			async with session.begin():
				async with self.DataBaseManager.models['users'] as user_model:
					stmt = self.DataBaseManager.select(user_model).where(
						user_model.id == member.id
					).with_for_update()
					user = (await session.execute(stmt)).scalars().first()
					count = 0
					match parameter:
						case 'крошки':
							user.crumbs += vector
							count = user.crumbs
						case 'сообщения':
							user.period_messages += vector
							user.summary_messages += vector
							count = user.period_messages
						case 'секунды в голосовом канале':
							user.period_voice_activity += vector
							user.summary_voice_activity += vector
							count = user.period_voice_activity
						case 'репутация':
							user.carma += vector
							count = user.carma
						case 'зарплата':
							user.staff_salary += vector
							count = user.staff_salary
					await ctx.send(embed=self.client.InfoEmbed(description=f'Количество {parameter} пользователя {member.mention} успешно изменено до `{count}`'), ephemeral=True)

	@commands.slash_command(name = "дать_зверя")
	async def GiveRimagochiAnimalSlash(self, ctx: disnake.AppCmdInter, member: disnake.Member, animal_id: int):
		if isinstance(ctx.author, disnake.User) or ctx.guild is None:
			await ctx.send(embed=self.client.ErrEmbed(description=f'Не допустимо в личных сообщениях'), ephemeral=True)
			return
		
		if not self.me in ctx.author.roles:
			await ctx.edit_original_message(embed=self.client.ErrEmbed(description=f'Эта команда доступна только администратору'))
			return

		if not animal_id in rimagochi_animals.keys():
			await ctx.send(embed=self.client.ErrEmbed(description=f'Некорректный идентификатор животного'), ephemeral=True)
			return

		async with self.DataBaseManager.session() as session:
			await self.client.RimagochiUserUpdate(member, session = session)
			async with session.begin():
				async with self.DataBaseManager.models['rimagochi_animals'] as rimagochi_animals_model:
					animal = rimagochi_animals_model(model_animal_id = animal_id, initial_owner_id = ctx.author.id, owner_id = member.id)
					session.add(animal)
					await ctx.send(embed=self.client.InfoEmbed(description=f'{member.mention} успешно получил `{rimagochi_animals[animal_id]["name"]}`'), ephemeral=True)

	@commands.slash_command(name = "удалить_зверя")
	async def RemoveRimagochiAnimalSlash(self, ctx: disnake.AppCmdInter, inventory_id: int):
		if isinstance(ctx.author, disnake.User) or ctx.guild is None:
			await ctx.send(embed=self.client.ErrEmbed(description=f'Не допустимо в личных сообщениях'), ephemeral=True)
			return
		
		if not self.me in ctx.author.roles:
			await ctx.edit_original_message(embed=self.client.ErrEmbed(description=f'Эта команда доступна только администратору'))
			return

		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['rimagochi_animals'] as rimagochi_animals_model:
					stmt = self.DataBaseManager.select(rimagochi_animals_model).where(
						rimagochi_animals_model.id == inventory_id
					).with_for_update()
					animal = (await session.execute(stmt)).scalars().first()

					if animal is None:
						await ctx.send(embed=self.client.ErrEmbed(description=f'Животного с таким идентификатором не обнаружено'), ephemeral=True)
						return 1
					else:
						await session.delete(animal)
						await ctx.send(embed=self.client.InfoEmbed(description=f"<@{animal.owner_id}> лишился `{rimagochi_animals[animal.model_animal_id]['name']}` с id `{inventory_id}`"), ephemeral=True)
						return 0


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


def setup(bot):
	bot.add_cog(MainRolesModule(bot))


class MainRolesModule(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.DataBaseManager = client.DataBaseManager
		self.costrolecreate = client.costrolecreate
		self.costrolerenewal = client.costrolerenewal

	@commands.Cog.listener()
	async def on_ready(self):
		self.client.logger.info(f'KrekFunBot roles module activated')
		krekchat = await self.client.fetch_guild(constants["krekchat"])
		self.me = disnake.utils.get(krekchat.roles, id=constants["me"])
		

	@commands.slash_command(name="создать")
	async def CreateSlash(self, ctx):
		pass
	@CreateSlash.sub_command(
		description=f"создайте свою роль за {constants['costrolecreate']} крошек (ежемесячная оплата за роль:{constants['costrolerenewal']})",
		name="роль")
	async def CreateRoleSub(self, ctx: disnake.AppCmdInter,
							name: str = commands.Param(description="Название роли", name="название"),
							cost: int = commands.Param(description="цена роли для других участников в магазине", name="цена"), 
													   colour: disnake.Colour = commands.Param(
																				description="цвет роли (указывается в hex формате, например: #ff9900)",
																				name="цвет", default=0xff9900)):
		await ctx.response.defer()
		err_embed = self.client.ErrEmbed(err_func = ctx.edit_original_message, title = "Ошибка создания роли")
		if ctx.guild is None or not isinstance(ctx.author, disnake.Member):
			await err_embed.send("Эта команда не работает в личных сообщениях!")
			return
		async with self.DataBaseManager.session() as session:
			await self.client.UserUpdate(member = ctx.author, session = session)
			received_roles_custom_model = self.DataBaseManager.model_classes['received_roles_custom']
			roles_custom_model = self.DataBaseManager.model_classes['roles_custom']
			users_model = self.DataBaseManager.model_classes['users']
			transaction_history_crumbs = self.DataBaseManager.model_classes['transaction_history_crumbs']
			async with session.begin():
				stmt = self.DataBaseManager.select(roles_custom_model).where(roles_custom_model.creator_id == ctx.author.id)
				custom_role = (await session.execute(stmt)).scalars().first()

				if not custom_role is None:
					await err_embed.send(f'Вы уже владеете кастомной ролью')
					return

				krekchat = await self.client.fetch_guild(constants["krekchat"])
				bordertop = krekchat.get_role(1221400083736690698)
				borderbottom = krekchat.get_role(1221400071908753480)

				if not (100 < cost < 2147483647):
					await err_embed.send(f"Минимальная стоимость: 100 крошек")
					return

				if disnake.utils.get(ctx.guild.roles, name=name):
					await err_embed.send(f"Роль с таким названием уже есть на сервере")
					return

				stmt = self.DataBaseManager.select(self.DataBaseManager.func.count()).select_from(roles_custom_model)
				count = (await session.execute(stmt)).scalars().first()
				if count >= 50:
					await err_embed.send(f"На сервере сейчас максимальное количество кастомных ролей ({count}), попробуйте позже")
					return

			async with session.begin():
				stmt = self.DataBaseManager.select(users_model).where(users_model.id == ctx.author.id).with_for_update()
				user = (await session.execute(stmt)).scalars().first()
				if user.crumbs < self.costrolecreate:
					await err_embed.send(f"Для создания роли необходимо заплатить {self.costrolecreate} крошек, а у вас есть только {round(user.crumbs)}")
					return

				role = await ctx.guild.create_role(name=name, colour=colour)
				await role.edit(position=bordertop.position - 1)
				await ctx.author.add_roles(role)
				custom_role = roles_custom_model(id = role.id, creator_id = ctx.author.id, cost = cost, renewal_date = 0)
				await custom_role.renewal_date_update(self.client.TimeFormater)
				session.add(custom_role)
				transaction = transaction_history_crumbs(sender_id = ctx.author.id, amount = self.costrolecreate, description = f"Создание кастомной роли {role.mention}")
				session.add(transaction)
				user.crumbs -= self.costrolecreate
				await session.flush()
				received_role_custom = received_roles_custom_model(role_id = role.id, user_id = ctx.author.id)
				session.add(received_role_custom)
				await ctx.edit_original_message(embed=self.client.InfoEmbed(
					title=f"Роль успешно создана! Вы можете проверить её статус или поменять настройки через команду /изменить роль",
					description=f'', colour=0x2F3136))


	@commands.slash_command(name="роль")
	async def RoleInfoSlash(self, ctx):
		pass
	@RoleInfoSlash.sub_command(description="Показывает информацию о ролях", name="инфо")
	async def RoleInfoSub(self, ctx: disnake.AppCmdInter,
						  role: disnake.Role = commands.Param(description="О какой роли хотите получить информацию?",
															  name="роль", default=None)):
		await ctx.response.defer()
		err_embed = self.client.ErrEmbed(err_func = ctx.edit_original_message, title = "Ошибка")

		krekchat = await self.client.fetch_guild(constants["krekchat"])
		roles_custom_model = self.DataBaseManager.model_classes['roles_custom']
		roles_static_model = self.DataBaseManager.model_classes['roles_static']
		custom_role = None
		async with self.DataBaseManager.session() as session:
			async with session.begin():
				if role is None:
					stmt = self.DataBaseManager.select(roles_custom_model).options(self.DataBaseManager.selectinload(roles_custom_model.users)).where(roles_custom_model.creator_id == ctx.author.id)
					custom_role = (await session.execute(stmt)).scalars().first()
					if custom_role is None:
						await err_embed.send(f'Вы не создавали кастомных ролей.\nЧтобы получить информацию о статичной роли, введите целевую роль в поле "роль" при вызове команды "/роль инфо"')
						return
					role = krekchat.get_role(custom_role.id)
					if role is None:
						await err_embed.send(f'Вашей роли нет на сервере, вероятно, произошла ошибка, обратитесь к администратору')
						return
					
				else:
					stmt = self.DataBaseManager.select(roles_static_model).where(roles_static_model.id == role.id)
					static_role = (await session.execute(stmt)).scalars().first()
					if not static_role is None:
						embed = self.client.InfoEmbed(title=f"", description=f'### Информация о статичной роли {role.mention}', colour=0x2F3136)
						embed.add_field(name=f"Описание", value=f"> {static_role.description}", inline=True)
						await ctx.edit_original_message(embed=embed)
						return
					else:
						stmt = self.DataBaseManager.select(roles_custom_model).options(self.DataBaseManager.selectinload(roles_custom_model.users)).where(roles_custom_model.id == role.id)
						custom_role = (await session.execute(stmt)).scalars().first()
						if custom_role is None:
							await err_embed.send(f'Описания этой роли пока не существует.')
							return

			embed = self.client.InfoEmbed(title=f"", description=f'### Информация о кастомной роли {role.mention}', colour=0x2F3136)
			embed.add_field(name=f"Время продления", value=f"> <t:{int(custom_role.renewal_date)}:D>", inline=True)
			embed.add_field(name=f"Цена продления", value=f"> {constants['costrolerenewal']}", inline=True)
			embed.add_field(name=f"", value=f"", inline=False)
			embed.add_field(name=f"Количество покупок", value=f"> {len(custom_role.users)-1}", inline=True)
			embed.add_field(name=f"Цена роли", value=f"> {custom_role.cost}", inline=True)
			embed.add_field(name=f"", value=f"", inline=False)
			try:
				creator = await krekchat.fetch_member(custom_role.creator_id)
			except:
				creator = custom_role.creator_id
			embed.add_field(name=f"Создатель", value=f"> {creator.mention if creator else custom_role.creator_id}", inline=True)
			await ctx.edit_original_message(embed=embed)


	@commands.slash_command(name="изменить")
	async def RoleChangeSlash(self, ctx):
		pass
	@RoleChangeSlash.sub_command(description="Позволяет изменить вашу роль", name="роль")
	async def RoleChangeSub(self, ctx: disnake.AppCmdInter):
		await ctx.response.defer()
		err_embed = self.client.ErrEmbed(err_func = ctx.edit_original_message, title = "Ошибка изменения роли")

		if ctx.guild is None:
			await err_embed.send("Эта команда не работает в личных сообщениях!")
			return

		krekchat = await self.client.fetch_guild(constants["krekchat"])
		client = self.client
		HexToRgb = self.client.HexToRgb

		class ButtonsEditRole(disnake.ui.View):
			client = self.client
			def __init__(self, ctx, role, embed):
				super().__init__(timeout=180)
				self.ctx = ctx
				self.role = role
				self.embed = embed

			@disnake.ui.button(label="Стоимость", custom_id="cost", style=disnake.ButtonStyle.blurple)
			async def cost(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете редактировать эту роль")
					await inter.send(embed=err_embed, ephemeral = True)
					return
				modal = ActionModal(self.role, self.ctx, self.embed, "cost")
				await inter.response.send_modal(modal)

			@disnake.ui.button(label="Цвет", custom_id="color", style=disnake.ButtonStyle.blurple)
			async def color(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете редактировать эту роль")
					await inter.send(embed=err_embed, ephemeral = True)
					return
				modal = ActionModal(self.role, self.ctx, self.embed, "color")
				await inter.response.send_modal(modal)

			@disnake.ui.button(label="Название", custom_id="name", style=disnake.ButtonStyle.blurple)
			async def name(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете редактировать эту роль")
					await inter.send(embed=err_embed, ephemeral = True)
					return
				modal = ActionModal(self.role, self.ctx, self.embed, "name")
				await inter.response.send_modal(modal)

			@disnake.ui.button(label="Иконку", custom_id="icon", style=disnake.ButtonStyle.blurple)
			async def icon(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете редактировать эту роль")
					await inter.send(embed=err_embed, ephemeral = True)
					return
				modal = ActionModal(self.role, self.ctx, self.embed, "icon")
				await inter.response.send_modal(modal)

			async def on_timeout(self):
				for child in self.children:
					if isinstance(child, (disnake.ui.Button, disnake.ui.BaseSelect)):
						child.disabled = True
				await self.ctx.edit_original_message(view=self)

		class ActionModal(disnake.ui.Modal):
			DataBaseManager = self.DataBaseManager
			client = self.client
			def __init__(self, role, ctx, embed, operation):
				self.role = role
				self.ctx = ctx
				self.embed = embed
				self.operation = operation
				components = []
				if operation == "name":
					components = [
						disnake.ui.TextInput(label="Новое название", placeholder="Например: abc", custom_id="name",
											 style=disnake.TextInputStyle.short, max_length=25)
					]
				if operation == "cost":
					components = [
						disnake.ui.TextInput(label="Новая стоимость", placeholder="Например: 123", custom_id="cost",
											 style=disnake.TextInputStyle.short, min_length=3)
					]
				if operation == "color":
					components = [
						disnake.ui.TextInput(label="Новый цвет", placeholder="Например: #ff9900", custom_id="color",
											 style=disnake.TextInputStyle.short)
					]
				if operation == "icon":
					components = [
						disnake.ui.TextInput(label="Введите ссылку на новую иконку", placeholder="Например: https://i.imgur.com/zWsCJun.png", custom_id="icon",
											 style=disnake.TextInputStyle.short)
					]

				super().__init__(title=operation, components=components, timeout=300)

			async def callback(self, interaction: disnake.ModalInteraction):
				ctx = self.ctx
				err_embed = self.client.ErrEmbed(err_func = interaction.send, title = "Ошибка изменения роли")

				async with self.DataBaseManager.session() as session:
					key, value, = list(interaction.text_values.items())[0]
					await interaction.response.defer(ephemeral=True)
					if self.operation == "name":
						await self.role.edit(name=value)
					if self.operation == "color":
						rgb = HexToRgb(value)
						await self.role.edit(color=disnake.Colour.from_rgb(rgb[0], rgb[1], rgb[2]))
					if self.operation == "cost":
						cost = abs(int(value))
						if not 100 < cost < 2147483647:
							await err_embed.send("Нельзя ставить стоимость роли меньше 100")
							return
						async with session.begin():
							async with self.DataBaseManager.models['roles_custom'] as roles_custom_model:
								stmt = self.DataBaseManager.update(roles_custom_model).where(roles_custom_model.creator_id == ctx.author.id).values(cost = cost)
								await session.execute(stmt)
					if self.operation == "icon":
						image_url = value
						TRUSTED_DOMAINS = ["imgur.com", "cdn.discordapp.com", "i.imgur.com"]
						if ctx.guild.premium_tier < 2:
							await err_embed.send("Этот сервер должен быть уровня 2 буста для изменения иконок ролей")
							return
						if not any(domain in image_url for domain in TRUSTED_DOMAINS):
							await err_embed.send("Загрузка изображений разрешена только с ресурса https://imgur.com/")
							return
						if not image_url.lower().endswith((".png", ".jpg", ".jpeg")):
							await err_embed.send("Разрешены только файлы с расширением .png, .jpg или .jpeg")
							return
						async with aiohttp.ClientSession() as http_session:
							try:
								headers = {
									"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
								}
								async with http_session.get(image_url, headers=headers) as resp:
									if resp.status != 200:
										await err_embed.send("Не удалось загрузить изображение")
										return

									content_type = resp.headers.get("Content-Type", "").lower()
									if content_type not in ("image/png", "image/jpeg"):
										await err_embed.send("Файл должен быть изображением в формате PNG или JPEG")
										return

									# Проверка размера файла (не более 5 МБ)
									content_length = int(resp.headers.get("Content-Length", 0))
									if content_length > 5 * 1024 * 1024:  # 5 МБ
										await err_embed.send("Размер файла не должен превышать 5 МБ")
										return

									image_data = await resp.read()  # Получаем изображение в виде bytes

							except aiohttp.ClientError as e:
								await err_embed.send(f"Ошибка при загрузке изображения: {e}")
								return
						try:
							await self.role.edit(icon=image_data, reason=f"Иконка изменена пользователем {ctx.author}")
						except disnake.Forbidden:
							await err_embed.send("У бота недостаточно прав для изменения роли")
							return
						except disnake.HTTPException as e:
							await err_embed.send(f"Ошибка при изменении роли: {e}")
							return

					krekchat = await client.fetch_guild(constants["krekchat"])

					role = krekchat.get_role(self.role.id)

					async with session.begin():
						async with self.DataBaseManager.models['roles_custom'] as roles_custom_model:
							stmt = self.DataBaseManager.select(roles_custom_model).where(roles_custom_model.id == self.role.id)
							custom_role = (await session.execute(stmt)).scalars().first()
							self.embed.description = f"**Укажите, какой параметр вы хотите изменить у роли {role.mention}:**\n\n**1) Стоимость: **```{custom_role.cost} крошек```\n**2) Цвет: **```{role.color}```\n**3) Название: **```{role.name}```"

					await interaction.edit_original_message(embed=self.client.InfoEmbed(title="Роль успешно изменена!", description=f'', colour=0x2F3136))

					await self.ctx.edit_original_message(embed=self.embed)

		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['users'] as users_model:
					stmt = self.DataBaseManager.select(users_model).options(self.DataBaseManager.joinedload(users_model.creation_role)).where(users_model.id == ctx.author.id)
					user = (await session.execute(stmt)).scalars().first()
					if user.creation_role is None:
						await err_embed.send(f"Вы не создавали кастомных ролей")
						return

					role = krekchat.get_role(user.creation_role.id)
					if not role:
						await err_embed.send(f'Вашей роли нет на сервере')
						return

		embed = self.client.InfoEmbed(title=f"Управление ролью",
							  description=f'**Укажите, какой параметр вы хотите изменить у роли {role.mention}:**\n\n**1) Стоимость: **```{user.creation_role.cost} крошек```\n**2) Цвет: **```{role.color}```\n**3) Название: **```{role.name}```',
							  colour=0x2F3136)
		embed.set_thumbnail(ctx.author.avatar)
		EditRole = ButtonsEditRole(ctx, role, embed)
		krekchat = await self.client.fetch_guild(constants["krekchat"])
		await ctx.edit_original_message(embed=embed, view=EditRole)



	@commands.slash_command(name="инвентарь")
	async def RoleInventorySlash(self, ctx):
		pass
	@RoleInventorySlash.sub_command(description="Показывает все роли, которыми вы владеете", name="ролей")
	async def RoleInventorySub(self, ctx: disnake.AppCmdInter):
		await ctx.response.defer()
		err_embed = self.client.ErrEmbed(err_func = ctx.edit_original_message, title = "Ошибка инвентаря")
		if ctx.guild is None:
			await err_embed.send("Эта команда не работает в личных сообщениях!")
			return
		krekchat = await self.client.fetch_guild(constants["krekchat"])

		class RolesInventoryButtons(disnake.ui.View):
			DataBaseManager = self.DataBaseManager
			client = self.client
			def __init__(self, ctx, inventory, embed):
				super().__init__(timeout=180)
				self.inventory = inventory
				self.ctx = ctx
				self.embed = embed
				self.page = 1
				self.maxpage = len(inventory) if len(inventory) > 0 else 1

				self.left.disabled = (self.page == 1)
				self.right.disabled = (self.page == self.maxpage)

			@disnake.ui.button(label="1", custom_id="1", style=disnake.ButtonStyle.blurple)
			async def one(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете управлять ролями другого участника")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				await self.ToggleRoles(inter, button)

			@disnake.ui.button(label="2", custom_id="2", style=disnake.ButtonStyle.blurple)
			async def two(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете управлять ролями другого участника")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				await self.ToggleRoles(inter, button)

			@disnake.ui.button(label="3", custom_id="3", style=disnake.ButtonStyle.blurple)
			async def three(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете управлять ролями другого участника")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				await self.ToggleRoles(inter, button)

			@disnake.ui.button(label="4", custom_id="4", style=disnake.ButtonStyle.blurple)
			async def four(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете управлять ролями другого участника")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				await self.ToggleRoles(inter, button)

			@disnake.ui.button(label="5", custom_id="5", style=disnake.ButtonStyle.blurple)
			async def five(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете управлять ролями другого участника")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				await self.ToggleRoles(inter, button)

			@disnake.ui.button(label="<", custom_id="left", style=disnake.ButtonStyle.secondary)
			async def left(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете управлять ролями другого участника")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				self.page -= 1
				self.left.disabled = (self.page == 1)
				self.right.disabled = (self.page == self.maxpage)
				self.embed = await EmbedRoleInventoryChanger(self.inventory, self.embed, self.page, self.ctx.author)
				await inter.response.edit_message(embed=self.embed, view=self)

			@disnake.ui.button(label=">", custom_id="right", style=disnake.ButtonStyle.secondary)
			async def right(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете управлять ролями другого участника")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				self.page += 1
				self.left.disabled = (self.page == 1)
				self.right.disabled = (self.page == self.maxpage)
				self.embed = await EmbedRoleInventoryChanger(self.inventory, self.embed, self.page, self.ctx.author)
				await inter.response.edit_message(embed=self.embed, view=self)

			async def ToggleRoles(self, inter, button):
				err_embed = self.client.ErrEmbed(err_func = inter.send, err_func_kwargs = {'ephemeral': True}, title = "Ошибка инвентаря")

				if len(self.inventory) < 1:
					await err_embed.send(f'Роли с таким номером нет на странице')
					return
				if len(self.inventory[self.page - 1]) < int(button.custom_id):
					await err_embed.send(f'Роли с таким номером нет на странице')
					return
				role = self.inventory[self.page - 1][int(button.custom_id) - 1]
				role = krekchat.get_role(role)
				if not role:
					return
				if role in self.ctx.author.roles:
					await self.ctx.author.remove_roles(role)
				else:
					roles_inventory_ids = []
					async with self.DataBaseManager.session() as session:
						async with session.begin():
							async with self.DataBaseManager.models['received_roles_custom'] as received_roles_custom_model:
								stmt = self.DataBaseManager.select(received_roles_custom_model).where(
									received_roles_custom_model.user_id == ctx.author.id
								)
								custom_roles = (await session.execute(stmt)).scalars().all()
								roles_inventory_ids += [role.role_id for role in custom_roles if not role.role_id in roles_inventory_ids]

							async with self.DataBaseManager.models['received_roles_prize'] as received_roles_prize_model:
								stmt = self.DataBaseManager.select(received_roles_prize_model).where(
									received_roles_prize_model.user_id == ctx.author.id
								)
								prize_roles = (await session.execute(stmt)).scalars().all()
								roles_inventory_ids += [role.role_id for role in prize_roles if not role.role_id in roles_inventory_ids]
					
					if not role.id in roles_inventory_ids:
						await err_embed.send(f"Эта роль пропала из вашего инвентаря")
						return
					await self.ctx.author.add_roles(role)
				self.embed = await EmbedRoleInventoryChanger(self.inventory, self.embed, self.page, self.ctx.author)
				await inter.response.edit_message(embed=self.embed, view=self)

			async def on_timeout(self):
				for child in self.children:
					if isinstance(child, (disnake.ui.Button, disnake.ui.BaseSelect)):
						child.disabled = True
				await self.ctx.edit_original_message(view=self)

		async def EmbedRoleInventoryChanger(inventory, embed, selfpage, member):
			embed.clear_fields()
			if len(inventory) == 0:
				embed.add_field(name=f"В инвентаре пока ничего нет", value=f"", inline=False)
				return embed
			page = inventory[selfpage - 1]
			c = 1
			for roleid in page:
				role = krekchat.get_role(roleid)

				wearing = role in member.roles
				embed.add_field(name=f"",
								value=f"**{c})** {role.mention if role else roleid} {':green_circle:' if wearing else ':red_circle:'}",
								inline=False)
				c += 1
			return embed

		roles_inventory_sorted_ids = []
		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['roles_custom'] as roles_custom_model:
					stmt = self.DataBaseManager.select(roles_custom_model).where(
						roles_custom_model.creator_id == ctx.author.id
					)
					creation_role = (await session.execute(stmt)).scalars().first()
					if not creation_role is None:
						roles_inventory_sorted_ids.append(creation_role.id)

				async with self.DataBaseManager.models['received_roles_prize'] as received_roles_prize_model:
					stmt = self.DataBaseManager.select(received_roles_prize_model).where(
						received_roles_prize_model.user_id == ctx.author.id
					)
					prize_roles = (await session.execute(stmt)).scalars().all()
					roles_inventory_sorted_ids += [role.role_id for role in prize_roles if not role.role_id in roles_inventory_sorted_ids]

				async with self.DataBaseManager.models['received_roles_custom'] as received_roles_custom_model:
					stmt = self.DataBaseManager.select(received_roles_custom_model).where(
						received_roles_custom_model.user_id == ctx.author.id
					)
					custom_roles = (await session.execute(stmt)).scalars().all()
					roles_inventory_sorted_ids += [role.role_id for role in custom_roles if not role.role_id in roles_inventory_sorted_ids]

		ready_array = self.client.PartitioningEmbeder(roles_inventory_sorted_ids)
		embed = self.client.InfoEmbed(title=f"Инвентарь ролей", description=f'', colour=0x2F3136)
		embed.set_thumbnail(ctx.author.avatar)
		view = RolesInventoryButtons(ctx, ready_array, embed)

		embed = await EmbedRoleInventoryChanger(ready_array, embed, 1, ctx.author)
		await ctx.edit_original_message(embed=embed, view=view)


	@commands.slash_command(name="магазин")
	async def ShopSlash(self, ctx):
		pass
	@ShopSlash.sub_command(description="Тут вы можете купить себе роль", name="ролей")
	async def RolesShopSub(self, ctx: disnake.AppCmdInter):
		'''


		магазин ролей


		'''
		await ctx.response.defer()
		err_embed = self.client.ErrEmbed(err_func = ctx.edit_original_message, title = "Ошибка магазина")
		DataBaseManager = self.DataBaseManager

		if ctx.guild is None:
			await err_embed.send("Эта команда не работает в личных сообщениях!")
			return
		PartitioningEmbeder = self.client.PartitioningEmbeder
		krekchat = await self.client.fetch_guild(constants["krekchat"])

		class ShopView(disnake.ui.View):
			client = self.client
			def __init__(self, ctx, embed):
				super().__init__(timeout=180)
				self.ctx = ctx
				self.embed = embed

			async def initialize(self):
				async with DataBaseManager.session() as session:
					async with session.begin():
						async with DataBaseManager.models['roles_custom'] as roles_custom_model:

							stmt = DataBaseManager.select(roles_custom_model).order_by(DataBaseManager.asc(roles_custom_model.date_of_creation))
							self.sortbydateofcreation = (await session.execute(stmt)).scalars().all()

							stmt = DataBaseManager.select(roles_custom_model).order_by(DataBaseManager.asc(roles_custom_model.cost))
							self.sortbycost = (await session.execute(stmt)).scalars().all()

							stmt = DataBaseManager.select(roles_custom_model).order_by(DataBaseManager.desc(roles_custom_model.cost))
							self.sortbycostreversed = (await session.execute(stmt)).scalars().all()

							stmt = DataBaseManager.select(roles_custom_model).order_by(DataBaseManager.desc(roles_custom_model.date_of_creation))
							self.sortbydateofcreationreversed = (await session.execute(stmt)).scalars().all()

							stmt = DataBaseManager.select(roles_custom_model).outerjoin(roles_custom_model.users).group_by(roles_custom_model.id).order_by(DataBaseManager.func.count(DataBaseManager.models['users'].model.id).desc())
							self.sortbypopularityreversed = (await session.execute(stmt)).scalars().all()

							stmt = DataBaseManager.select(roles_custom_model).outerjoin(roles_custom_model.users).group_by(roles_custom_model.id).order_by(DataBaseManager.func.count(DataBaseManager.models['users'].model.id).asc())
							self.sortbypopularity = (await session.execute(stmt)).scalars().all()

				self.sortvalues = {"sortbydateofcreation": self.sortbydateofcreation, "sortbycost": self.sortbycost,
								   "sortbycostreversed": self.sortbycostreversed,
								   "sortbydateofcreationreversed": self.sortbydateofcreationreversed,
								   "sortbypopularityreversed": self.sortbypopularity,
								   "sortbypopularity": self.sortbypopularityreversed}
				self.maxpage = len(PartitioningEmbeder([i for i in self.sortbydateofcreation]))

				self.page = 1

			@disnake.ui.button(label="<<", custom_id="leftmax")
			async def leftmax(self, button, inter):
				await inter.response.defer()
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				self.page = 1
				self.leftmax.disabled = (self.page == 1)
				self.left.disabled = (self.page == 1)
				self.rightmax.disabled = (self.page == self.maxpage)
				self.right.disabled = (self.page == self.maxpage)

				self.embed = await EmbedShopChanger(self.sort.values, self.embed, self.page, self.sortvalues)

				await inter.message.edit(view=self, embed=self.embed)

			@disnake.ui.button(label="<", custom_id="left")
			async def left(self, button, inter):
				await inter.response.defer()
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				self.page = max(self.page - 1, 1)
				self.leftmax.disabled = (self.page == 1)
				self.left.disabled = (self.page == 1)
				self.rightmax.disabled = (self.page == self.maxpage)
				self.right.disabled = (self.page == self.maxpage)

				self.embed = await EmbedShopChanger(self.sort.values, self.embed, self.page, self.sortvalues)

				await inter.message.edit(view=self, embed=self.embed)

			@disnake.ui.button(label=">", custom_id="right")
			async def right(self, button, inter):
				await inter.response.defer()
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				self.page = min(self.page + 1, self.maxpage)
				self.leftmax.disabled = (self.page == 1)
				self.left.disabled = (self.page == 1)
				self.rightmax.disabled = (self.page == self.maxpage)
				self.right.disabled = (self.page == self.maxpage)

				self.embed = await EmbedShopChanger(self.sort.values, self.embed, self.page, self.sortvalues)

				await inter.message.edit(view=self, embed=self.embed)

			@disnake.ui.button(label=">>", custom_id="rightmax")
			async def rightmax(self, button, inter):
				await inter.response.defer()
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				self.page = self.maxpage
				self.leftmax.disabled = (self.page == 1)
				self.left.disabled = (self.page == 1)
				self.rightmax.disabled = (self.page == self.maxpage)
				self.right.disabled = (self.page == self.maxpage)

				self.embed = await EmbedShopChanger(self.sort.values, self.embed, self.page, self.sortvalues)

				await inter.message.edit(view=self, embed=self.embed)

			@disnake.ui.string_select(
				placeholder="Сначала новые",
				options=[
					disnake.SelectOption(label="Сначала новые", value="sortbydateofcreationreversed", default=True),
					disnake.SelectOption(label="Сначала старые", value="sortbydateofcreation", default=False),
					disnake.SelectOption(label="Сначала дешёвые", value="sortbycost", default=False),
					disnake.SelectOption(label="Сначала дорогие", value="sortbycostreversed", default=False),
					disnake.SelectOption(label="Сначала популярные", value="sortbypopularity", default=False),
					disnake.SelectOption(label="Сначала не популярные", value="sortbypopularityreversed", default=False),
				],
				min_values=1,
				max_values=1,
			)
			async def sort(self, select: disnake.ui.StringSelect, inter: disnake.MessageInteraction):
				await inter.response.defer()
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				self.page = 1
				self.leftmax.disabled = (self.page == 1)
				self.left.disabled = (self.page == 1)
				self.rightmax.disabled = (self.page == self.maxpage)
				self.right.disabled = (self.page == self.maxpage)

				self.embed = await EmbedShopChanger(self.sort.values, self.embed, self.page, self.sortvalues)

				for opt in range(len(self.sort.options)):
					if self.sort.options[opt].value == self.sort.values[0]:
						self.sort.options[opt].default = True
					else:
						self.sort.options[opt].default = False

				await inter.message.edit(view=self, embed=self.embed)

			@disnake.ui.button(label="1", custom_id="1", style=disnake.ButtonStyle.blurple, row=3)
			async def one(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				await self.BuyRoles(inter, button)

			@disnake.ui.button(label="2", custom_id="2", style=disnake.ButtonStyle.blurple, row=3)
			async def two(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				await self.BuyRoles(inter, button)

			@disnake.ui.button(label="3", custom_id="3", style=disnake.ButtonStyle.blurple, row=3)
			async def three(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				await self.BuyRoles(inter, button)

			@disnake.ui.button(label="4", custom_id="4", style=disnake.ButtonStyle.blurple, row=3)
			async def four(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				await self.BuyRoles(inter, button)

			@disnake.ui.button(label="5", custom_id="5", style=disnake.ButtonStyle.blurple, row=3)
			async def five(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				await self.BuyRoles(inter, button)

			async def on_timeout(self):
				for child in self.children:
					if isinstance(child, (disnake.ui.Button, disnake.ui.BaseSelect)):
						child.disabled = True
				await self.ctx.edit_original_message(view=self)

			async def BuyRoles(self, inter, button):
				err_embed = self.client.ErrEmbed(err_func = inter.send, err_func_kwargs = {'ephemeral': True}, title = "Ошибка покупки")
				async with DataBaseManager.session() as session:
					async with session.begin():
						async with DataBaseManager.models['users'] as users_model:
							stmt = DataBaseManager.select(users_model).options(DataBaseManager.selectinload(users_model.custom_roles)).where(users_model.id == inter.author.id)
							user = (await session.execute(stmt)).scalars().first()

							page = (PartitioningEmbeder(
								self.sortvalues[self.sort.values[0] if len(self.sort.values) == 1 else "sortbydateofcreationreversed"]))[
								self.page - 1]

							if len(page) < int(button.custom_id):
								await err_embed.send(f'Роли с таким номером нет на странице')
								return

							custom_role = page[int(button.custom_id) - 1]
							if user.crumbs < custom_role.cost:
								await err_embed.send(f'У вас недостаточно крошек')
								return

							if custom_role.id in [role.id for role in user.custom_roles]:
								await err_embed.send(f'У вас уже есть эта роль')
								return

							role = krekchat.get_role(custom_role.id)
							confirmembed = self.client.InfoEmbed(description=f'Вы уверены, что хотите преобрести роль {role.mention if role else custom_role.id} за {custom_role.cost} крошек?',
								colour=0x2F3136)
							ConfMessage = ConfirmView(self.ctx, role, custom_role)
							await inter.response.edit_message(view=ConfMessage, embed=confirmembed)
		class ConfirmView(disnake.ui.View):
			client = self.client
			def __init__(self, ctx, role, custom_role):
				super().__init__(timeout=180)
				self.ctx = ctx
				self.role = role
				self.custom_role = custom_role

			@disnake.ui.button(label="Да", custom_id="yes", style=disnake.ButtonStyle.green)
			async def yes(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return
				if not self.role:
					err_embed = self.client.ErrEmbed(title = "Ошибка покупки", description = "Такая роль не найдена на сервере. Возможно, это ошибка базы данных")
					await inter.send(embed = err_embed, ephemeral = True)
					return

				ctx = self.ctx
				async with DataBaseManager.session() as session:
					async with session.begin():
						async with DataBaseManager.models['users'] as users_model:
							stmt = DataBaseManager.select(users_model).where(users_model.id == inter.author.id).with_for_update()
							user = (await session.execute(stmt)).scalars().first()
							stmt = DataBaseManager.select(users_model).where(users_model.id == self.custom_role.creator_id).with_for_update()
							creator = (await session.execute(stmt)).scalars().first()
							user.crumbs -= self.custom_role.cost
							creator.crumbs += self.custom_role.cost
							receive = DataBaseManager.models['received_roles_custom'].m(role_id = self.custom_role.id, user_id = user.id)
							session.add(receive)
							history = DataBaseManager.models['transaction_history_crumbs'].m(sender_id = user.id, recipient_id = creator.id, amount = self.custom_role.cost, description = f"Покупка роли {self.role.mention}")
							await self.ctx.author.add_roles(self.role)
							embed = self.client.InfoEmbed(description=f'Роль {self.role.mention} успешно преобретена!', colour=0x2F3136)
							await self.ctx.edit_original_message(embed=embed, view=None)

			@disnake.ui.button(label="Нет", custom_id="no", style=disnake.ButtonStyle.red)
			async def no(self, button, inter):
				if inter.author != self.ctx.author:
					err_embed = self.client.ErrEmbed(title = "Ошибка доступа", description = "Вы не можете покупать роли в магазине другого участника. Используйте команду `/магазин ролей`, чтобы купить роли")
					await inter.send(embed = err_embed, ephemeral = True)
					return

				ctx = self.ctx

				embed = self.client.InfoEmbed(title=f"Магазин ролей", description=f'', colour=0x2F3136)
				ShopMessage = ShopView(ctx, embed)
				await ShopMessage.initialize()
				ShopMessage.leftmax.disabled = (ShopMessage.page == 1)
				ShopMessage.left.disabled = (ShopMessage.page == 1)
				ShopMessage.rightmax.disabled = (ShopMessage.page == ShopMessage.maxpage)
				ShopMessage.right.disabled = (ShopMessage.page == ShopMessage.maxpage)

				embed = await EmbedShopChanger([], embed, 1)

				embed.set_thumbnail(ctx.author.avatar)

				await ctx.edit_original_message(view=ShopMessage, embed=embed)

			async def on_timeout(self):
				for child in self.children:
					if isinstance(child, (disnake.ui.Button, disnake.ui.BaseSelect)):
						child.disabled = True
				await self.ctx.edit_original_message(view=self)
		async def EmbedShopChanger(sortvalues, embed, selfpage, constvalues=None):
			if not constvalues:
				async with DataBaseManager.session() as session:
					async with session.begin():
						async with DataBaseManager.models['roles_custom'] as roles_custom_model:

							stmt = DataBaseManager.select(roles_custom_model).order_by(DataBaseManager.asc(roles_custom_model.date_of_creation))
							sortbydateofcreation = (await session.execute(stmt)).scalars().all()

							stmt = DataBaseManager.select(roles_custom_model).order_by(DataBaseManager.asc(roles_custom_model.cost))
							sortbycost = (await session.execute(stmt)).scalars().all()

							stmt = DataBaseManager.select(roles_custom_model).order_by(DataBaseManager.desc(roles_custom_model.cost))
							sortbycostreversed = (await session.execute(stmt)).scalars().all()

							stmt = DataBaseManager.select(roles_custom_model).order_by(DataBaseManager.desc(roles_custom_model.date_of_creation))
							sortbydateofcreationreversed = (await session.execute(stmt)).scalars().all()

							stmt = DataBaseManager.select(roles_custom_model).outerjoin(roles_custom_model.users).group_by(roles_custom_model.id).order_by(DataBaseManager.func.count(DataBaseManager.models['users'].model.id).desc())
							sortbypopularityreversed = (await session.execute(stmt)).scalars().all()

							stmt = DataBaseManager.select(roles_custom_model).outerjoin(roles_custom_model.users).group_by(roles_custom_model.id).order_by(DataBaseManager.func.count(DataBaseManager.models['users'].model.id).asc())
							sortbypopularity = (await session.execute(stmt)).scalars().all()

				constvalues = {"sortbydateofcreation": sortbydateofcreation, "sortbycost": sortbycost,
							   "sortbycostreversed": sortbycostreversed,
							   "sortbydateofcreationreversed": sortbydateofcreationreversed,
							   "sortbypopularityreversed": sortbypopularity,
							   "sortbypopularity": sortbypopularityreversed}
			embed.clear_fields()
			page = \
			(PartitioningEmbeder(constvalues[sortvalues[0] if len(sortvalues) == 1 else "sortbydateofcreationreversed"]))[
				selfpage - 1]
			c = 1
			for custom_role in page:
				try:
					creator = await krekchat.fetch_member(custom_role.creator_id)
				except:
					creator = custom_role.creator_id
				role = krekchat.get_role(custom_role.id)
				embed.add_field(name=f"",
								value=f"**{c})** {role.mention if role else custom_role.id}\n**Цена: **{custom_role.cost} крошек\n**Создатель: **{creator.mention if type(creator)!=int else creator}",
								inline=False)
				c += 1
			return embed
		embed = self.client.InfoEmbed(title=f"Магазин ролей", description=f'', colour=0x2F3136)
		async with DataBaseManager.session() as session:
			await self.client.UserUpdate(ctx.author, session = session)
			async with session.begin():
				async with DataBaseManager.models['roles_custom'] as roles_custom_model:
					stmt = DataBaseManager.select(roles_custom_model)
					roles = (await session.execute(stmt)).scalars().all()
		if len(roles) == 0:
			embed.description = "В магазине пока нет ни одной роли"
			embed.set_thumbnail(ctx.author.avatar)
			await ctx.edit_original_message(embed=embed)
			return
		ShopMessage = ShopView(ctx, embed)
		await ShopMessage.initialize()
		ShopMessage.leftmax.disabled = (ShopMessage.page == 1)
		ShopMessage.left.disabled = (ShopMessage.page == 1)
		ShopMessage.rightmax.disabled = (ShopMessage.page == ShopMessage.maxpage)
		ShopMessage.right.disabled = (ShopMessage.page == ShopMessage.maxpage)


		embed = await EmbedShopChanger([], embed, 1)
		embed.set_thumbnail(ctx.author.avatar)
		await ctx.edit_original_message(view=ShopMessage, embed=embed)
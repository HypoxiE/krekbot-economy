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
import imageio
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from io import BytesIO
import textwrap
from constants.global_constants import *


def setup(bot):
	bot.add_cog(MainDesignerModule(bot))

class MainDesignerModule(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.DataBaseManager = client.DataBaseManager
		
	@commands.Cog.listener()
	async def on_ready(self):
		self.krekchat = await self.client.fetch_guild(constants["krekchat"])
		self.sponsors = [disnake.utils.get(self.krekchat.roles, id=i) for i in constants["sponsors"]]
		self.me = disnake.utils.get(self.krekchat.roles, id=constants["me"])
		self.client.logging.info(f'KrekFunBot designer module activated')

	@commands.slash_command(name = "профиль", description="Ваш профиль на сервере")
	async def Profile(self, ctx: disnake.AppCmdInter,
					  member: disnake.Member = commands.Param(description="Чей профиль хотите посмотреть?", name="участник", default=None),
					  old_style: bool = commands.Param(description="Если у вас не грузятся картинки, это лучший вариант", name="старый_стиль", default=False)):
		if not member:
			member = ctx.author

		await ctx.response.defer()

		async with self.DataBaseManager.session() as session:
			async with session.begin():
				async with self.DataBaseManager.models['users'] as users_model:
					user = await session.get(users_model, member.id)

					if user is None:
						embed = self.client.ErrEmbed(title="Ошибка профиля", description=f"{'Вас' if member == ctx.author else 'Этого пользователя'} пока нет в базе данных{', напишите хотя бы одно сообщение' if member == ctx.author else ''}")
						await ctx.edit_original_message(embed=embed)
						return

					rating = users_model.period_messages + (users_model.period_voice_activity / 180.0)
					subquery = (
						self.DataBaseManager.select(
							users_model.id,
							self.DataBaseManager.func.row_number().over(order_by=[self.DataBaseManager.desc(rating)]).label('rank')
						)
						.subquery()
					)
					stmt = (
						self.DataBaseManager.select(subquery.c.rank)
						.where(subquery.c.id == member.id)
					)
					user_rank = (await session.execute(stmt)).scalar()

					stmt = self.DataBaseManager.select(self.DataBaseManager.models['profile_design_inventory'].m).where(
						self.DataBaseManager.models['profile_design_inventory'].m.user_id == member.id,
						self.DataBaseManager.models['profile_design_inventory'].m.is_active == True
					)

					design = (await session.execute(stmt)).scalars().first()
					if design is None:
						design = await session.get(self.DataBaseManager.models['profile_design'].m, 1)
					else:
						design = design.design

		if old_style:
			embed = self.client.InfoEmbed(title=f"Профиль **{member.display_name}**", description=f'')

			embed.colour = 0x2F3136
			embed.set_thumbnail(url=member.avatar)
			
			level = self.client.CalculateLevel(user.period_messages, user.period_voice_activity)
			embed.add_field(name=f"Уровень",
							value=f"`{int(level)}`\n|{'█' * int((level % 1) * 35) + '░' * (35 - int((level % 1) * 35))}|\n",
							inline=False)
			if ctx.guild is None:
				embed.add_field(name=f"Баланс ", value=f"`{int(user.crumbs)} крошек`", inline=True)
			else:
				modify = max(0, (bool(await user.in_role(roles = self.sponsors, member = member))+1) + (user.carma / 100))
				embed.add_field(name=f"Баланс " + ("" if modify == 1 else f"(x{float(modify):.02n})"), value=f"`{int(user.crumbs)} крошек`", inline=True)
			embed.add_field(name=f"Текстовая активность", value=f"`{user.period_messages} сообщений`", inline=True)
			embed.add_field(name=f"Голосовая активность", value=f"`{round(user.period_voice_activity / (60))} минут`", inline=True)
			embed.add_field(name=f"Репутация", value=f"`{int(user.carma)}`", inline=True)
			embed.add_field(name=f"Топ", value=f"`{user_rank}`", inline=True)
			if user.staff_salary != 0:
				embed.add_field(name=f"Зарплата", value=f"`{user.staff_salary:.02n} крошек в час`", inline=True)
			await ctx.edit_original_message(embed=embed)
		else:
			data = {}

			if design.render_profile_code is None:
				embed = self.client.ErrEmbed(title="Ошибка профиля", description=f"Для этой темы профиля не определена функция render. Свяжитесь с разработчиком для решения этой проблемы")
				await ctx.edit_original_message(embed=embed)
				return

			avatar_asset = member.avatar or member.default_avatar
			avatar_bytes = await avatar_asset.read()
			avatar_buffer = BytesIO(avatar_bytes)
			avatar_image = Image.open(avatar_buffer).convert("RGBA")
			data['avatar'] = avatar_image
			data['user'] = user
			data['place_in_top'] = user_rank
			data['crumbs_modify'] = max(0, (bool(await user.in_role(roles = self.sponsors, member = member))+1) + (user.carma / 100)) if ctx.guild is not None else 1
			data['nick'] = member.display_name
			data['level'] = self.client.CalculateLevel(user.period_messages, user.period_voice_activity)
			namespace = globals().copy()

			if design.type == "PNG":
				await ctx.edit_original_message(file=disnake.File(fp=design.render_profile(data, namespace), filename="profile.png"))
			elif design.type == "GIF":
				await ctx.edit_original_message(file=disnake.File(fp=design.render_profile(data, namespace), filename="profile.webp"))
from sqlalchemy import Column, Integer, BigInteger, Text, Float, ForeignKey, UniqueConstraint, MetaData, Boolean, JSON, String, ARRAY, CheckConstraint, func, Index
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import text
import datetime
from zoneinfo import ZoneInfo
from typing import Annotated, List
import disnake

class Base(DeclarativeBase):

	def get_table_name(self):
		return self.__tablename__

	def to_dict(self, exclude: list[str] = None):
		"""Конвертирует модель в словарь, исключая указанные поля."""
		if exclude is None:
			exclude = []

		return {
			c.name: getattr(self, c.name)
			for c in self.__table__.columns
			if c.name not in exclude
		}


discord_identificator_pk = Annotated[int, mapped_column(BigInteger, primary_key=True, nullable=False, index = True)]
identificator_pk = Annotated[int, mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True, index = True)]
discord_identificator = Annotated[int, mapped_column(BigInteger, nullable=False, index=True)]

class User(Base):
	__tablename__ = 'users'
	
	id: Mapped[discord_identificator_pk]
	crumbs: Mapped[float] = mapped_column(Float, nullable=False, default=0)
	period_messages: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	summary_messages: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	period_voice_activity: Mapped[float] = mapped_column(Float, nullable=False, default=0)
	summary_voice_activity: Mapped[float] = mapped_column(Float, nullable=False, default=0)
	carma: Mapped[float] = mapped_column(Float, nullable=False, default=0)
	staff_salary: Mapped[float] = mapped_column(Float, nullable=False, default=0)
	last_daily_crumbs_date: Mapped[float] = mapped_column(Float, nullable=False, default=0)
	last_activity_date: Mapped[float] = mapped_column(Float, nullable=False, onupdate=func.extract('epoch', func.now()), server_onupdate=text("EXTRACT(EPOCH FROM NOW())"), server_default=text("EXTRACT(EPOCH FROM NOW())"))

	custom_roles: Mapped[list["CustomRole"]] = relationship(
		secondary="received_roles_custom",
		back_populates="users",
		#lazy="selectin"
	)

	creation_role: Mapped["CustomRole"] = relationship(
		back_populates="creator",
		uselist=False,
		#lazy="joined"
	)

	prize_roles: Mapped[list["PrizeRole"]] = relationship(
		secondary="received_roles_prize",
		back_populates="users",
		#lazy="selectin"
	)

	sender_in_crumbs_transactions: Mapped[list["CrumbsTransactionHistory"]] = relationship(
		back_populates="sender",
		uselist=True,
		foreign_keys="[CrumbsTransactionHistory.sender_id]",
		#lazy="selectin"
	)

	recipient_in_crumbs_transactions: Mapped[list["CrumbsTransactionHistory"]] = relationship(
		back_populates="recipient",
		uselist=True,
		foreign_keys="[CrumbsTransactionHistory.recipient_id]",
		#lazy="selectin"
	)

	casino_account: Mapped["CasinoUser"] = relationship(
		back_populates="user",
		uselist=False,
		#lazy="joined"
	)

	rimagochi_account: Mapped["RimagochiUser"] = relationship(
		back_populates="user",
		uselist=False,
		#lazy="joined"
	)

	async def get_member(self, client = None, guild = None, guild_id = None):

		if not guild is None:
			try:
				member = await guild.fetch_member(self.id)
			except disnake.NotFound:
				member = None
			return member

		if client is None:
			raise TypeError("get_member() не хватает обязательного аргумента: 'client'")

		if guild_id is None:
			raise TypeError("get_member() не хватает обязательного аргумента: 'guild_id'")
		else:
			guild = await client.fetch_guild(guild_id)
			return self.get_member(guild = guild, client = None, guild_id = None)

	async def in_role(self, roles = None, member = None, boolean = True, guild = None, guild_id = None, client = None):
		'''
		Находит пересечение между ролями пользователя и входным списком ролей
		'''
		if member is None:
			await self.get_member(guild = guild, guild_id = guild_id, client = client)

		if roles is None:
			raise TypeError("in_role() не хватает обязательного аргумента: 'roles'")

		member_roles = set(member.roles)
		roles = set(roles)

		if boolean:
			return bool(member_roles & roles)
		else:
			return member_roles & roles

	async def crumbs_adder(self, incoming_crumbs: float, sponsor = None, member = None, sponsor_roles = None):
		if sponsor is None:
			sponsor = await self.in_role(roles = sponsor_roles, member = member)

		modifier = (self.carma / 100) + (sponsor+1)

		add_crumbs = (incoming_crumbs * modifier) if incoming_crumbs * modifier >= 0 else 0
		self.crumbs += add_crumbs
		return add_crumbs

	async def give_salary(self):
		self.crumbs += self.staff_salary

	async def claim_daily_crumbs(self, sponsor = None, member = None, sponsor_roles = None, daily_constant = 300):

		moscow_tz = ZoneInfo("Europe/Moscow")
		last_daily_time = datetime.datetime.fromtimestamp(self.last_daily_crumbs_date, tz=moscow_tz)
		now_time = datetime.datetime.now(tz=moscow_tz)
		if now_time.date() > last_daily_time.date():
			daily = await self.crumbs_adder(incoming_crumbs = daily_constant, sponsor = sponsor, sponsor_roles = sponsor_roles, member = member)
			self.last_daily_crumbs_date = datetime.datetime.now().timestamp()
			return {'success': True, 'output': f"Вы получили ежедневную награду в размере {int(daily)} крошек!", 'count': daily, 'date': now_time.date()}
		else:
			next_day = (now_time + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
			return {'success': False, 'output': f"Вы уже получали ежедневную награду сегодня, следующая будет доступна <t:{int(next_day)}:R>"}

#роли
class CustomRole(Base):
	__tablename__ = 'roles_custom'
	
	id: Mapped[discord_identificator_pk]
	creator_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
	date_of_creation: Mapped[float] = mapped_column(Float, nullable=False, server_default=text("EXTRACT(EPOCH FROM NOW())"))
	cost: Mapped[int] = mapped_column(Integer, nullable=False)
	renewal_date: Mapped[float] = mapped_column(Float, nullable=False)
	renewal_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

	users: Mapped[list["User"]] = relationship(
		secondary="received_roles_custom",
		back_populates="custom_roles",
		#lazy="selectin"
	)

	creator: Mapped["User"] = relationship(
		back_populates="creation_role",
		foreign_keys = [creator_id],
		uselist=False,
		#lazy="joined"
	)

	async def renewal_date_update(self, time_formater_function, days = 30):
		self.renewal_date = float(time_formater_function(days = days))
	
class PrizeRole(Base):
	__tablename__ = 'roles_prize'
	
	id: Mapped[discord_identificator_pk]

	users: Mapped[list["User"]] = relationship(
		secondary="received_roles_prize",
		back_populates="prize_roles",
		#lazy="selectin"
	)

class StaticRole(Base):
	__tablename__ = 'roles_static'
	
	id: Mapped[discord_identificator_pk]
	description: Mapped[str | None] = mapped_column(String, nullable=True)

class ReceivedCustomRoles(Base):
	__tablename__ = 'received_roles_custom'

	role_id: Mapped[int] = mapped_column(ForeignKey('roles_custom.id', ondelete='CASCADE'), primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)

	__table_args__ = (
		UniqueConstraint('user_id', 'role_id', name='received_roles_custom_user_role'),
	)

class ReceivedPrizeRoles(Base):
	__tablename__ = 'received_roles_prize'

	role_id: Mapped[int] = mapped_column(ForeignKey('roles_prize.id', ondelete='CASCADE'), primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)

	__table_args__ = (
		UniqueConstraint('user_id', 'role_id', name='received_roles_prize_user_role'),
	)

#профили
class ProfileDesign(Base):
	__tablename__ = 'profile_design'

	id: Mapped[identificator_pk]
	file_name: Mapped[str] = mapped_column(String, nullable=False)
	type: Mapped[str | None] = mapped_column(String, server_default=text("'PNG'"), nullable=False)
	border_color: Mapped[list[int]] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[0, 0, 0, 255]"), nullable=False)
	border_width: Mapped[int | None] = mapped_column(Integer, server_default=text("3"), nullable=False)
	scale: Mapped[int | None] = mapped_column(Integer, server_default=text("4"), nullable=False)

	blackout_background_size: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[452, 226]"), nullable=False)
	blackout_background_position: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[30, 15]"), nullable=False)
	blackout_background_color: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[0, 0, 0, 100]"), nullable=False)
	blackout_background_radius: Mapped[int | None] = mapped_column(Integer, server_default=text("15"), nullable=False)

	avatar_size: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[100, 100]"), nullable=False)
	avatar_position: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[50, 25]"), nullable=False)

	nick_size: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[145, 65]"), nullable=False)
	nick_position: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[30, 110]"), nullable=False)
	nick_color: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[255, 255, 255, 255]"), nullable=False)
	nick_stroke_width: Mapped[int | None] = mapped_column(Integer, server_default=text("6"), nullable=False)
	nick_stroke_color: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[0, 0, 0, 255]"), nullable=False)

	progress_bar_size: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[400, 40]"), nullable=False)
	progress_bar_position: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[50, 175]"), nullable=False)
	progress_bar_fill_color: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[0, 255, 0, 255]"), nullable=False)
	progress_bar_empty_color: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[50, 50, 50, 255]"), nullable=False)
	progress_bar_radius: Mapped[int | None] = mapped_column(Integer, server_default=text("15"), nullable=False)
	progress_bar_text_position: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[15, 7]"), nullable=False)
	progress_bar_text_color: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[255, 255, 255, 255]"), nullable=False)
	progress_bar_text_stroke_width: Mapped[int | None] = mapped_column(Integer, server_default=text("6"), nullable=False)
	progress_bar_text_stroke_color: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[0, 0, 0, 255]"), nullable=False)

	info_bar_size: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[275, 135]"), nullable=False)
	info_bar_position: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[175, 30]"), nullable=False)
	info_bar_color: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[255, 255, 255, 0]"), nullable=False)
	info_bar_radius: Mapped[int | None] = mapped_column(Integer, server_default=text("15"), nullable=False)
	info_bar_text_color: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[0, 0, 0, 255]"), nullable=False)
	info_bar_text_position: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), server_default=text("ARRAY[15, 10]"), nullable=False)

	render_profile_code: Mapped[str | None] = mapped_column(Text, nullable=True)

	def render_profile(self, data, namespace):
		#{user, place_in_top, avatar, nick, level, crumbs_modify} in data
		exec(self.render_profile_code, namespace)
		render_func = namespace['render']

		return render_func(data, design = self)

	usage: Mapped[list["ProfileDesignInventory"]] = relationship(
		back_populates="design",
		#lazy="selectin"
	)

class ProfileDesignInventory(Base):
	__tablename__ = 'profile_design_inventory'

	user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
	design_id: Mapped[int] = mapped_column(ForeignKey('profile_design.id', ondelete='CASCADE'), primary_key=True)
	is_active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("FALSE"), nullable=False)

	design: Mapped["ProfileDesign"] = relationship(
		back_populates="usage",
		foreign_keys=[design_id],
		lazy="joined"
	)

	__table_args__ = (
		UniqueConstraint('user_id', 'design_id', name='received_profile_design_inventory_user_design'),
		Index(
			'received_profile_design_inventory_user_only_one_active',
			'user_id',
			unique=True,
			postgresql_where=text('is_active')
		),
	)

#экономика
class CrumbsTransactionHistory(Base):
	__tablename__ = 'transaction_history_crumbs'
	
	id: Mapped[identificator_pk]
	sender_id: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=True, default=None)
	recipient_id: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=True, default=None)
	amount: Mapped[int] = mapped_column(Integer, nullable=False)
	commission_fraction: Mapped[float] = mapped_column(Float, default=0, nullable=False)
	description: Mapped[str | None] = mapped_column(String, default=None, nullable=True)
	transaction_time: Mapped[float] = mapped_column(Float, nullable=False, server_default=text("EXTRACT(EPOCH FROM NOW())"))

	sender: Mapped["User | None"] = relationship(
		back_populates="sender_in_crumbs_transactions",
		foreign_keys=[sender_id],
		uselist=False,
		#lazy="joined"
	)

	recipient: Mapped["User | None"] = relationship(
		back_populates="recipient_in_crumbs_transactions",
		foreign_keys=[recipient_id],
		uselist=False,
		#lazy="joined"
	)

	__table_args__ = (
		CheckConstraint('NOT (sender_id IS NULL AND recipient_id IS NULL)'),
	)

class CasinoUser(Base):
	__tablename__ = 'casino_user_account'
	
	id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, nullable=False)
	spins_today_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
	last_reset_time: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

	user: Mapped["User"] = relationship(
		back_populates="casino_account",
		uselist=False,
		#lazy="joined"
	)

#rimagochi
class RimagochiUser(Base):
	__tablename__ = 'rimagochi_users'
	
	id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, nullable=False, index = True)
	items: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)
	genes: Mapped[dict] = mapped_column(JSON, default={}, nullable=False)
	wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
	settings: Mapped[dict] = mapped_column(JSON, nullable=False)

	user: Mapped["User"] = relationship(
		back_populates="rimagochi_account",
		uselist=False,
		#lazy="joined"
	)

	animals: Mapped[list["RimagochiAnimal"]] = relationship(
		back_populates="owner",
		uselist=True,
		#lazy="selectin"
	)

	battle_slots_animals: Mapped[list["RimagochiAnimal"]] = relationship(
		primaryjoin=(
			"and_("
			"RimagochiAnimal.owner_id == RimagochiUser.id, "
			"RimagochiAnimal.in_battle_slots == True"
			")"
		),
		uselist=True,
		viewonly=True,
		#lazy="selectin"
	)

class RimagochiAnimal(Base):
	__tablename__ = 'rimagochi_animals'

	id: Mapped[identificator_pk]
	model_animal_id: Mapped[int] = mapped_column(Integer, nullable=False)
	genes: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=[], nullable=False)
	items: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=[], nullable=False)
	last_feeding_time: Mapped[float] = mapped_column(Float, default=0, nullable=False)
	first_today_feed_time: Mapped[float] = mapped_column(Float, default=0, nullable=False)
	feed_today_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
	experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
	level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
	wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
	initial_owner_id: Mapped[discord_identificator]
	owner_id: Mapped[int] = mapped_column(ForeignKey('rimagochi_users.id', ondelete='CASCADE'), nullable=False, index = True)
	in_battle_slots: Mapped[bool] = mapped_column(Boolean, default = False, nullable = False)
	creation_time: Mapped[float] = mapped_column(Float, nullable=False, server_default=text("EXTRACT(EPOCH FROM NOW())"))

	owner: Mapped["RimagochiUser"] = relationship(
		back_populates="animals",
		foreign_keys = [owner_id],
		uselist=False,
		#lazy="joined"
	)


all_data = {
	'base': Base
}
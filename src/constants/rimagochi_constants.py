rimagochi_default_settings = {
	'hide_the_animals': False,
	'always_use_crumbs_for_feeding':False,
	'accept_the_challenge': True,
}
rimagochi_constants = {
	"health_multiplayer": 1,
	"damage_multiplayer": 1,
	"hanger_multiplayer": 100,
	"max_battle_slots": 8,
	"animals_exp_to_levels": {1: 1000, 2: 1500, 3: 2500, 4: 5000, 5: 10_000, 6: 20_000, 7: 40_000, 8: 80_000, 9: 160_000, 10: 320_000}
}
rimagochi_items = {
	11:{
		"id": 11,
		"name": "мясо",
		"description": "Будет расходоваться вместо крошек для кормления животных, которые его едят (заменяет 10 крошек)",
		"buy_cost": 9, "sell_cost": 5,
		"shop_cost": 15,
	},
	12:{
		"id": 12,
		"name": "кожа",
		"description": "Можно продать, ну или, может быть, использовать на что-нибудь ещё...",
		"buy_cost": 15, "sell_cost": 10,
		"shop_cost": 25,
	},
	13:{
		"id": 13,
		"name": "рог трумбо",
		"description": "Можно продать, ну или, может быть, использовать на что-нибудь ещё...",
		"buy_cost": 20_000, "sell_cost": 10_000,
		"shop_cost": 25_000,
	},
	14:{
		"id": 14,
		"name": "древесина",
		"description": "Будет расходоваться вместо крошек для кормления животных, которые её едят (заменяет 10 крошек)",
		"buy_cost": 9, "sell_cost": 5,
		"shop_cost": 15,
	},
	15:{
		"id": 15,
		"name": "рог носорога",
		"description": "Можно продать, ну или, может быть, использовать на что-нибудь ещё...",
		"buy_cost": 6_000, "sell_cost": 3_000,
		"shop_cost": 8_000,
	},
	16:{
		"id": 16,
		"name": "бивень слона",
		"description": "Можно продать, ну или, может быть, использовать на что-нибудь ещё...",
		"buy_cost": 3_000, "sell_cost": 1_500,
		"shop_cost": 4_000,
	},
	17:{
		"id": 17,
		"name": "химическое топливо",
		"description": "Можно продать, ну или, может быть, использовать на что-нибудь ещё...",
		"buy_cost": 30, "sell_cost": 20,
		"shop_cost": 50,
	},
	18:{
		"id": 18,
		"name": "хитин",
		"description": "Можно продать, ну или, может быть, использовать на что-нибудь ещё...",
		"buy_cost": 30, "sell_cost": 20,
		"shop_cost": 50,
	},
	19:{
		"id": 19,
		"name": "биоферрит",
		"description": "Можно продать, ну или, может быть, использовать на что-нибудь ещё...",
		"buy_cost": 30, "sell_cost": 20,
		"shop_cost": 50,
	},
	110:{
		"id": 110,
		"name": "позвоночник ревенанта",
		"description": "Можно продать, ну или, может быть, использовать на что-нибудь ещё...",
		"buy_cost": 5_000, "sell_cost": 3_000,
		"shop_cost": 8_000,
	},
}
rimagochi_genes = {
	41: {"id": 41, "name": "железная кожа", "description": f"Здоровье носителя увеличивается на {2*rimagochi_constants['health_multiplayer']} единицы", "effects": {"health": 2}, "cost": 10_000},
	42: {"id": 42, "name": "улучшенный метаболизм", "description": f"Потребление пищи носителя снижается на {int(0.5*rimagochi_constants['hanger_multiplayer'])} единиц(не ниже 0)", "effects": {"hunger": -0.5}, "cost": 2250},
	43: {"id": 43, "name": "ядерный желудок", "description": f"Снижает потребление пищи на {int(10*rimagochi_constants['hanger_multiplayer'])} единиц(не ниже 0)", "effects": {"hunger": -10}, "cost": 30_000},
	44: {"id": 44, "name": "сильный урон в ближнем бою", "description": f"Урон носителя увеличивается на {2*rimagochi_constants['damage_multiplayer']} единицы", "effects": {"damage": 2}, "cost": 10_000}
}
rimagochi_rarity = {
	31: {"id": 31, "name": "мифический", "emoji": "🟣", "standart_chance": 0.002},
	32: {"id": 32, "name": "легендарный", "emoji": "🟠", "standart_chance": 0.02},
	33: {"id": 33, "name": "эпический", "emoji": "🔴", "standart_chance": 0.139},
	34: {"id": 34, "name": "редкий", "emoji": "🔵", "standart_chance": 0.239},
	35: {"id": 35, "name": "обычный", "emoji": "🟢", "standart_chance": 0.4},
	36: {"id": 36, "name": "дно", "emoji": "⚫", "standart_chance": 0.2},

	#лимитки
	37: {"id": 37, "name": "аномальный", "emoji": "<:Golden_cube:1368690052435279992>", "standart_chance": 0},
}
rimagochi_capsules = {
	51: {
		'id': 51,
		'name': 'обычный саркофаг криптосна',
		'cost': 2000,
		'chances': [
			{"rarity": rimagochi_rarity[31], "chance": rimagochi_rarity[31]["standart_chance"]},
			{"rarity": rimagochi_rarity[32], "chance": rimagochi_rarity[32]["standart_chance"]},
			{"rarity": rimagochi_rarity[33], "chance": rimagochi_rarity[33]["standart_chance"]},
			{"rarity": rimagochi_rarity[34], "chance": rimagochi_rarity[34]["standart_chance"]},
			{"rarity": rimagochi_rarity[35], "chance": rimagochi_rarity[35]["standart_chance"]},
			{"rarity": rimagochi_rarity[36], "chance": rimagochi_rarity[36]["standart_chance"]},
		],
	},
	# 52: {
	# 	'id': 52,
	# 	'name': 'аномальный саркофаг криптосна',
	# 	'cost': 3000,
	# 	'chances': [
	# 		{"rarity": rimagochi_rarity[31], "chance": 0.001},
	# 		{"rarity": rimagochi_rarity[37], "chance": 0.04},
	# 		{"rarity": rimagochi_rarity[32], "chance": 0.02},
	# 		{"rarity": rimagochi_rarity[33], "chance": 0.2},
	# 		{"rarity": rimagochi_rarity[34], "chance": 0.3},
	# 		{"rarity": rimagochi_rarity[35], "chance": 0.439},
	# 	],
	# },
}
rimagochi_animals = {
	261: {
		"id": 261,
		"name": "ревенант",
		"description": "В фольклоре чужеземцев описывается невидимый призрак, который завладевает разумом грешников, помещая их в настоящий ад. Согласно легенде, жертв можно вернуть к жизни, только выследив существо во время его сна и убив его.",
		"params":{
			"hunger": 0,
			"can_eate": [],
			"damage": 30,
			"health": 35,
			"after_death": [
				{"item": rimagochi_items[19], "count": (50, 85)},
				{"item": rimagochi_items[110], "count": (1, 1)}
			],
			"rarity": rimagochi_rarity[37],
			"required_slots" : 8,
			"image_url": "https://rimworldwiki.com/images/thumb/0/07/Revenant.png/72px-Revenant.png",
		}
	},
	262: {
		"id": 262,
		"name": "золотой куб",
		"description": "Кубик кажется неуязвимым для большинства повреждений.",
		"params":{
			"hunger": 0,
			"can_eate": [],
			"damage": 0.5,
			"health": 70,
			"after_death": [
				{"item": rimagochi_items[19], "count": (0, 0)}
			],
			"rarity": rimagochi_rarity[37],
			"required_slots" : 1,
			"image_url": "https://rimworldwiki.com/images/d/d2/Golden_cube.png",
		}
	},


	#стандарт
	21: {
		"id": 21,
		"name": "трумбо",
		"description": "Медленный гигант с кожей, непробиваемой для большинства снарядов. Его рог дробит скалы, а упрямство сравнимо только с толщиной шкуры. Не ждите от него тактики — Трумбо просто идёт вперёд, пока что-то не рухнет. И это «что-то» обычно не он.",
		"params":{
			"hunger": 4.5,
			"can_eate": [
				{"item": rimagochi_items[14]}
			],
			"damage": 30,
			"health": 30,
			"after_death": [
				{"item": rimagochi_items[11], "count": (250, 260)},
				{"item": rimagochi_items[12], "count": (50, 66)},
				{"item": rimagochi_items[13], "count": (1, 1)}
			],
			"rarity": rimagochi_rarity[31],
			"required_slots" : 5,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/9/90/Трумбо.png/revision/latest?cb=20160716092442&path-prefix=ru",
		}
	},
	22: {
		"id": 22,
		"name": "слон",
		"description": "Исполин прерий, чьи удары сбивают с ног даже бронированных противников. Его бивни — это природные копья, а хобот запросто ломает рёбра. Медлителен, но один точный удар может переломить ход битвы.",
		"params":{
			"hunger": 3.5,
			"can_eate": [],
			"damage": 20,
			"health": 25,
			"after_death": [
				{"item": rimagochi_items[11], "count": (350, 370)},
				{"item": rimagochi_items[12], "count": (75, 85)},
				{"item": rimagochi_items[16], "count": (1, 2)}
			],
			"rarity": rimagochi_rarity[32],
			"required_slots" : 4,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/f/f8/Слон.png/revision/latest/scale-to-width-down/51?cb=20161122173318&path-prefix=ru",
		}
	},
	23: {
		"id": 23,
		"name": "носорог",
		"description": "Живой таран в броне. Его рог пробивает даже пласталевые двери, а разгону позавидует любой механоид. Не ищите тактику — носорог знает лишь один манёвр: «Ломись, круши, добеги».",
		"params":{
			"hunger": 3.3,
			"can_eate": [],
			"damage": 24,
			"health": 21,
			"after_death": [
				{"item": rimagochi_items[11], "count": (260, 280)},
				{"item": rimagochi_items[12], "count": (58, 62)},
				{"item": rimagochi_items[15], "count": (1, 1)}
			],
			"rarity": rimagochi_rarity[32],
			"required_slots" : 4,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/a/ae/Носорог.png/revision/latest/scale-to-width-down/51?cb=20150613162727&path-prefix=ru",
		}
	},
	238: {
		"id": 238,
		"name": "мегапаук",
		"description": "Мегапаук - агрессивное существо, которое обитает в пещерах. Не являясь на самом деле пауком, мегапаук - генно-модифицированное насекомое размером с медведя, созданное для тяжёлой работы и боя. Толстая хитиновая броня хорошо защищает паука, а длинные потрошащие клинки опасны для его врагов.",
		"params": {
			"hunger": 3.4,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 22,
			"health": 22,
			"after_death": [
				{"item": rimagochi_items[11], "count": (120, 140)},
				{"item": rimagochi_items[18], "count": (100, 120)}
			],
			"rarity": rimagochi_rarity[32],
			"required_slots": 4,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/d/d5/Мегапаук.png/revision/latest/scale-to-width-down/51?cb=20180418143103&path-prefix=ru"
		}
	},
	24: {
		"id": 24,
		"name": "гигантский ленивец",
		"description": "Крупный медлительный зверь с толстой шкурой. Наносит слабый урон из-за низкой скорости атак, но благодаря живучести может долго держаться в бою. Опасен в ближнем бою — его мощные когти наносят дробящие повреждения.",
		"params":{
			"hunger": 2.5,
			"can_eate": [],
			"damage": 15.6,
			"health": 17,
			"after_death": [
				{"item": rimagochi_items[11], "count": (350, 370)},
				{"item": rimagochi_items[12], "count": (70, 80)}
			],
			"rarity": rimagochi_rarity[33],
			"required_slots" : 3,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/7/7c/Гигантский_ленивец.png/revision/latest/scale-to-width-down/51?cb=20161215005219&path-prefix=ru",
		}
	},
	211: {
		"id": 211,
		"name": "белый медведь",
		"description": "Король ледяных пустошей. Его лапы бьют с силой айсберга, а шкура не боится ни пуль, ни мороза. Медлителен, но каждый его удар сносит головы — если цель выживет, то лишь потому, что медведь решил пощадить.",
		"params":{
			"hunger": 2.7,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 18,
			"health": 15,
			"after_death": [
				{"item": rimagochi_items[11], "count": (180, 200)},
				{"item": rimagochi_items[12], "count": (40, 46)}
			],
			"rarity": rimagochi_rarity[33],
			"required_slots" : 3,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/f/fe/Белый_медведь.png/revision/latest/scale-to-width-down/51?cb=20170624170811&path-prefix=ru",
		}
	},
	219: {
		"id": 219,
		"name": "гризли",
		"description": "Медвежий ужас лесов. Его когти рвут плоть, как бумагу, а рёв парализует слабонервных. Не ждите тактики — гризли просто идёт напролом, снося всё на своём пути. Единственная стратегия против него — не попадаться на глаза.",
		"params": {
			"hunger": 2.2,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 17,
			"health": 16,
			"after_death": [
				{"item": rimagochi_items[11], "count": (190, 200)},
				{"item": rimagochi_items[12], "count": (40, 46)},
			],
			"rarity": rimagochi_rarity[33],
			"required_slots": 3,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/6/60/Медведь.png/revision/latest/scale-to-width-down/51?cb=20170709181213&path-prefix=ru"
		}
	},
	239: {
		"id": 239,
		"name": "мегаскарабей",
		"description": "Большой генно-модифицированный жук. Когда-то они были рабочей кастой искусственной экосистемы инсектоидов, специально выведенной для борьбы с вторжением механоидов. Теперь их обычно видят без более смертоносных инсектоидных собратьев. Тем не менее, размер и твердый панцирь делают их опасными противниками в бою.",
		"params": {
			"hunger": 0.8,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 11,
			"health": 9,
			"after_death": [
				{"item": rimagochi_items[11], "count": (18, 18)},
				{"item": rimagochi_items[18], "count": (25, 30)}
			],
			"rarity": rimagochi_rarity[33],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/8/83/Мегаскарабей.png/revision/latest/scale-to-width-down/51?cb=20180418142807&path-prefix=ru"
		}
	},
	240: {
		"id": 240,
		"name": "муффало",
		"description": "Мохнатый гигант тундры. Его рога — природные тараны, а шкура не боится даже арктических морозов. В ярости сносит всё на своём пути, но требует огромного количества пищи.",
		"params": {
			"hunger": 2.0,
			"can_eate": [],
			"damage": 16.5,
			"health": 16,
			"after_death": [
				{"item": rimagochi_items[11], "count": (170, 190)},
				{"item": rimagochi_items[12], "count": (39, 41)}
			],
			"rarity": rimagochi_rarity[33],
			"required_slots": 3,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/e/eb/Муффало.png/revision/latest/scale-to-width-down/51?cb=20131103180147&path-prefix=ru"
		}
	},
	260: {
		"id": 260,
		"name": "зубр",
		"description": "Крупное травоядное, которое при атаке превращается в живой таран. Его шкура достаточно толстая, чтобы игнорировать ножи, а рога оставляют рваные раны. Главный недостаток — требует много места и еды.",
		"params": {
			"hunger": 2.8,
			"can_eate": [],
			"damage": 16,
			"health": 17,
			"after_death": [
				{"item": rimagochi_items[11], "count": (180, 200)},
				{"item": rimagochi_items[12], "count": (60, 66)}
			],
			"rarity": rimagochi_rarity[33],
			"required_slots": 3,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/6/64/Зубр.png/revision/latest/scale-to-width-down/51?cb=20200529154650&path-prefix=ru"
		}
	},
	25: {
		"id": 25,
		"name": "пума",
		"description": "Быстрый и смертоносный хищник. Атакует первым благодаря высокой скорости, нанося кровавые рваные раны когтями. Хрупкая, но опасная в первой линии боя — лучше убить её до того, как она совершит фатальный прыжок.",
		"params":{
			"hunger": 1.4,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 19,
			"health": 9,
			"after_death": [
				{"item": rimagochi_items[11], "count": (120, 136)},
				{"item": rimagochi_items[12], "count": (26, 30)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots" : 3,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/9/9f/Пума.png/revision/latest/scale-to-width-down/51?cb=20161121084144&path-prefix=ru",
		}
	},
	215: {
		"id": 215,
		"name": "варг",
		"description": "Когда-то его предков боялись целые планеты. Теперь же он всего лишь дорогая мясорубка: за те же крошки можно нанять двух свиней, но они не выглядят так угрожающе. Уровень повышает только его самомнение.",
		"params":{
			"hunger": 1.4,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 20,
			"health": 9,
			"after_death": [
				{"item": rimagochi_items[11], "count": (89, 91)},
				{"item": rimagochi_items[12], "count": (20, 20)},
			],
			"rarity": rimagochi_rarity[34],
			"required_slots" : 3,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/4/40/Варг.png/revision/latest/scale-to-width-down/51?cb=20160715194624&path-prefix=ru",
		}
	},
	213: {
		"id": 213,
		"name": "бумалопа",
		"description": "Генетический эксперимент с печальными последствиями. Накапливает в жировых отложениях легковоспламеняющееся биохимическое топливо.",
		"params":{
			"hunger": 1.2,
			"can_eate": [],
			"damage": 10,
			"health": 10,
			"after_death": [
				{"item": rimagochi_items[11], "count": (130, 140)},
				{"item": rimagochi_items[12], "count": (28, 32)},
				{"item": rimagochi_items[17], "count": (5, 15)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots" : 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/2/27/Boomalope-0.png/revision/latest/scale-to-width-down/51?cb=20200910181859&path-prefix=ru",
		}
	},
	217: {
		"id": 217,
		"name": "волк",
		"description": "Стайный хищник, привыкший разрывать добычу в координированных атаках. В бою действует хитро: атакует первым, нанося глубокие рваные раны, а затем отступает, чтобы избежать контрудара. Идеален для фланговых манёвров и добивания ослабленных врагов.",
		"params": {
			"hunger": 1.5,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 14,
			"health": 9,
			"after_death": [
				{"item": rimagochi_items[11], "count": (70, 86)},
				{"item": rimagochi_items[12], "count": (20, 26)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/9/99/Волк.png/revision/latest/scale-to-width-down/51?cb=20170126162033&path-prefix=ru"
		}
	},
	227: {
		"id": 227,
		"name": "капибара",
		"description": "Легендарный носитель дзена. Капибара не сражается — она существует. В бою вызывает недоумение у врага и восторг у союзников. Никто не знает, зачем она здесь, но все уверены: она делает это важно. Почти неуязвима к стрессу… и к урону тоже.",
		"params": {
			"hunger": 1,
			"can_eate": [],
			"damage": 2,
			"health": 45,
			"after_death": [
				{"item": rimagochi_items[11], "count": (48, 52)},
				{"item": rimagochi_items[12], "count": (10, 12)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/b/b8/Капибара.png/revision/latest/scale-to-width-down/51?cb=20161125110014&path-prefix=ru"
		}
	},
	230: {
		"id": 230,
		"name": "кобра",
		"description": "Смертоносная рептилия, чей яд парализует жертву за секунды. В бою атакует молниеносно, но крайне уязвима к ответным ударам.",
		"params": {
			"hunger": 0.6,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 15,
			"health": 4,
			"after_death": [
				{"item": rimagochi_items[11], "count": (23, 23)},
				{"item": rimagochi_items[12], "count": (5, 5)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/7/77/Кобра.png/revision/latest/scale-to-width-down/51?cb=20150613162522&path-prefix=ru"
		}
	},
	237: {
		"id": 237,
		"name": "лиса",
		"description": "Хитрый мелкий хищник, предпочитающий атаковать исподтишка. Её укусы не смертельны, но она мастерски отвлекает противников, заставляя их бегать за собой по всему полю боя.",
		"params": {
			"hunger": 1.2,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 9,
			"health": 7,
			"after_death": [
				{"item": rimagochi_items[11], "count": (50, 50)},
				{"item": rimagochi_items[12], "count": (18, 18)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/8/83/Лисица.png/revision/latest/scale-to-width-down/51?cb=20170604232620&path-prefix=ru"
		}
	},
	243: {
		"id": 243,
		"name": "пантера",
		"description": "Идеальный убийца — быстрый, тихий и безжалостный. Её атаки нацелены в горло, а чёрная шкура делает её почти невидимой в темноте. Боится огня и громких звуков.",
		"params": {
			"hunger": 1.5,
			"can_eate": [
			    {"item": rimagochi_items[11]}
			],
			"damage": 15,
			"health": 8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (120, 132)},
				{"item": rimagochi_items[12], "count": (30, 32)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/7/72/Пантера.png/revision/latest/scale-to-width-down/51?cb=20180422111902&path-prefix=ru"
		}
	},
	244: {
		"id": 244,
		"name": "полярный волк",
		"description": "Белоснежный хищник арктических пустошей. Его густая шерсть защищает от лютых морозов, а стайная тактика делает смертельно опасным даже для более крупных противников.",
		"params": {
			"hunger": 1.5,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 14,
			"health": 9,
			"after_death": [
				{"item": rimagochi_items[11], "count": (70, 86)},
				{"item": rimagochi_items[12], "count": (20, 26)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/8/82/Полярный_волк.png/revision/latest/scale-to-width-down/51?cb=20170126163932&path-prefix=ru"
		}
	},
	245: {
		"id": 245,
		"name": "полярная лисица",
		"description": "Мелкий, но невероятно живучий хищник. Меняет окрас шерсти в зависимости от сезона, идеально маскируясь в снегах. Предпочитает атаковать исподтишка.",
		"params": {
			"hunger": 1.2,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 9,
			"health": 7,
			"after_death": [
				{"item": rimagochi_items[11], "count": (50, 50)},
				{"item": rimagochi_items[12], "count": (18, 18)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/8/8f/Песец.png/revision/latest/scale-to-width-down/51?cb=20220206124138&path-prefix=ru"
		}
	},
	246: {
		"id": 246,
		"name": "рысь",
		"description": "Одинокий охотник с молниеносной реакцией. Её кисточки на ушах - не просто украшение, а природный радар. Атакует прыжком, целясь в шею жертвы.",
		"params": {
			"hunger": 1.5,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 14,
			"health": 9,
			"after_death": [
				{"item": rimagochi_items[11], "count": (70, 74)},
				{"item": rimagochi_items[12], "count": (15, 17)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/b/bd/Рысь.png/revision/latest/scale-to-width-down/51?cb=20170624164203&path-prefix=ru"
		}
	},
	257: {
		"id": 257,
		"name": "конь",
		"description": "Галопом — в атаку, копытом — в лицо. Идеален для стремительных прорывов, но в ближнем бою мечется.",
		"params": {
			"hunger": 1.2,
			"can_eate": [],
			"damage": 10,
			"health": 11,
			"after_death": [
				{"item": rimagochi_items[11], "count": (160, 200)},
				{"item": rimagochi_items[12], "count": (50, 70)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/6/65/Лошадь.png/revision/latest/scale-to-width-down/51?cb=20200602055837&path-prefix=ru"
		}
	},
	259: {
		"id": 259,
		"name": "як",
		"description": "Мохнатый гигант с нравом бульдозера. Его рога — природные копья, а выносливость позволяет тащить на себе полбатальона.",
		"params": {
			"hunger": 1.3,
			"can_eate": [],
			"damage": 12,
			"health": 14,
			"after_death": [
				{"item": rimagochi_items[11], "count": (160, 180)},
				{"item": rimagochi_items[12], "count": (55, 60)}
			],
			"rarity": rimagochi_rarity[34],
			"required_slots": 3,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/a/aa/Як.png/revision/latest/scale-to-width-down/51?cb=20200601124520&path-prefix=ru"
		}
	},
	26: {
		"id": 26,
		"name": "свинья",
		"description": "Жирный и агрессивный боец ближнего боя. Наносит слабый урон, но устойчив к кровотечениям. Неплохой 'танк' для отвлечения врагов в первых рядах.",
		"params":{
			"hunger": 1,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 6,
			"health": 10,
			"after_death": [
				{"item": rimagochi_items[11], "count": (68, 76)},
				{"item": rimagochi_items[12], "count": (14, 18)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots" : 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/5/50/Свинья.png/revision/latest/scale-to-width-down/51?cb=20161029112449&path-prefix=ru",
		}
	},
	28: {
		"id": 28,
		"name": "альпака",
		"description": "Мирное на вид существо, способное яростно защищаться. Бьёт врагов копытами и плюётся желудочным соком. Не наносит серьёзного урона, но может долго держаться в бою благодаря выносливости.",
		"params":{
			"hunger": 0.9,
			"can_eate": [],
			"damage": 5,
			"health": 12,
			"after_death": [
				{"item": rimagochi_items[11], "count": (85, 95)},
				{"item": rimagochi_items[12], "count": (18, 22)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots" : 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/7/77/Альпака.png/revision/latest/scale-to-width-down/51?cb=20160419074343&path-prefix=ru",
		}
	},
	218: {
		"id": 218,
		"name": "газель",
		"description": "Стремительный и пугливый бегун, чья тактика сводится к одному — ударил, убежал, повторил. Её рога скорее царапают, чем ранят, но в группе они могут измотать противника. После смерти оставляет нежное мясо и тонкую кожу — идеально для начинающих фермеров-бойцов.",
		"params": {
			"hunger": 0.8,
			"can_eate": [],
			"damage": 7,
			"health": 9,
			"after_death": [
				{"item": rimagochi_items[11], "count": (60, 66)},
				{"item": rimagochi_items[12], "count": (14, 14)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/1/18/Газель.png/revision/latest/scale-to-width-down/51?cb=20170624175956&path-prefix=ru"
		}
	},
	29: {
		"id": 29,
		"name": "альфабобер",
		"description": "Генетически модифицированный бобр-переросток с усиленными резцами. Стремительно грызёт врагов, нанося высокий урон для своего класса, но крайне уязвим к ответным атакам.",
		"params":{
			"hunger": 1,
			"can_eate": [
				{"item": rimagochi_items[14]}
			],
			"damage": 10,
			"health": 7,
			"after_death": [
				{"item": rimagochi_items[11], "count": (52, 56)},
				{"item": rimagochi_items[12], "count": (10, 12)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots" : 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/e/ed/Альфабобёр.png/revision/latest/scale-to-width-down/51?cb=20150613162449&path-prefix=ru",
		}
	},
	214: {
		"id": 214,
		"name": "бумкрыса",
		"description": "Гибрид крысы и бочки с горючим. Постоянно дрожит и нервно озирается — видимо, догадывается о своей... нестабильной природе. Кусается больно, но главная тактика: запустить её в толпу врагов и надеяться, что те запаникуют от одного её вида.",
		"params":{
			"hunger": 0.8,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 6,
			"health": 5,
			"after_death": [
				{"item": rimagochi_items[11], "count": (18, 18)},
				{"item": rimagochi_items[12], "count": (4, 4)},
				{"item": rimagochi_items[17], "count": (2, 6)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots" : 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/0/05/Boomrat.png/revision/latest/scale-to-width-down/51?cb=20200910182241&path-prefix=ru",
		}
	},
	216: {
		"id": 216,
		"name": "верблюд",
		"description": "Выносливый корабль пустыни, который в бою ведёт себя как живая баррикада. Его плевки не наносят серьёзного урона, но способны деморализовать даже самых стойких противников. Медлителен, но терпелив — идеален для изматывания врагов в долгих стычках. После смерти оставляет внушительные запасы мяса и шкуры, словно напоминая, что даже в смерти он полезнее, чем иные существа в жизни.",
		"params":{
			"hunger": 1,
			"can_eate": [],
			"damage": 6,
			"health": 10,
			"after_death": [
				{"item": rimagochi_items[11], "count": (169, 172)},
				{"item": rimagochi_items[12], "count": (37, 41)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots" : 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/1/1b/Верблюд.png/revision/latest/scale-to-width-down/51?cb=20190105160837&path-prefix=ru",
		}
	},
	221: {
		"id": 221,
		"name": "енот",
		"description": "Мелкий хитрый воришка, который в бою полагается на внезапность и грязные приёмы. Не надейтесь на его силу — его козырь это умение ударить в спину и быстро скрыться. После смерти оставляет лишь клочья меха, но зато какой мягкий!",
		"params": {
			"hunger": 0.7,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 6,
			"health": 5,
			"after_death": [
				{"item": rimagochi_items[11], "count": (20, 25)},
				{"item": rimagochi_items[12], "count": (8, 13)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/c/c2/Енот.png/revision/latest/scale-to-width-down/51?cb=20170624165320&path-prefix=ru"
		}
	},
	224: {
		"id": 224,
		"name": "индейка",
		"description": "Птица, которая выглядит как шутка, но может неожиданно клюнуть в самый неожиданный момент. Не отличается силой или выносливостью, но зато потребляет минимум ресурсов. Хорошо подходит тем, кто хочет поднять армию из пернатых за копейки.",
		"params": {
			"hunger": 0.6,
			"can_eate": [],
			"damage": 4,
			"health": 7,
			"after_death": [
				{"item": rimagochi_items[11], "count": (60, 66)},
				{"item": rimagochi_items[12], "count": (20, 22)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/a/a0/Индейка.png/revision/latest/scale-to-width-down/51?cb=20200311182418&path-prefix=ru"
		}
	},
	225: {
		"id": 225,
		"name": "кабан",
		"description": "Упрямый и яростный зверь, который прёт напролом. Кабан не умеет сдаваться — он способен продырявить строй противника своими клыками. Идеален для мясных таранов и врывов с разбега. Лучше дружи с ним, чем злись.",
		"params": {
			"hunger": 0.9,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 10,
			"health": 7,
			"after_death": [
				{"item": rimagochi_items[11], "count": (60, 66)},
				{"item": rimagochi_items[12], "count": (12, 16)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/b/bd/Кабан.png/revision/latest/scale-to-width-down/51?cb=20161122141442&path-prefix=ru"
		}
	},
	226: {
		"id": 226,
		"name": "казуар",
		"description": "Говорят, что это просто птица. Но каждый, кто сталкивался с казуаром, знает: это ураган на двух лапах с клювом и когтями. Мгновенный рывок и серия ударов — пока враг моргает, он уже валяется в пыли. Нестабилен, но страшен.",
		"params": {
			"hunger": 0.8,
			"can_eate": [],
			"damage": 9,
			"health": 7,
			"after_death": [
				{"item": rimagochi_items[11], "count": (80, 82)},
				{"item": rimagochi_items[12], "count": (20, 28)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/b/b0/Казуар.png/revision/latest/scale-to-width-down/51?cb=20170624173810&path-prefix=ru"
		}
	},
	228: {
		"id": 228,
		"name": "карибу",
		"description": "Выносливый кочевник тундры. Его рога — грозное оружие в сезон гона, но в бою он полагается скорее на стойкость, чем на агрессию. После смерти оставляет ценную шкуру и нежное оленину — желанную добычу для любого охотника.",
		"params": {
			"hunger": 1,
			"can_eate": [],
			"damage": 8,
			"health": 8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (165, 180)},
				{"item": rimagochi_items[12], "count": (36, 41)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/0/08/Северный_олень.png/revision/latest/scale-to-width-down/51?cb=20170624174911&path-prefix=ru"
		}
	},
	229: {
		"id": 229,
		"name": "лось",
		"description": "Атакует стремительным наскоком, сметая всё на пути. Не так силён, как медведь, но его удары копыт способны переломать рёбра даже бронированному противнику. После смерти оставляет огромное количество мяса и прочную шкуру.",
		"params": {
			"hunger": 1,
			"can_eate": [],
			"damage": 8,
			"health": 8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (165, 180)},
				{"item": rimagochi_items[12], "count": (36, 41)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/8/80/Лось.png/revision/latest/scale-to-width-down/51?cb=20220523154624&path-prefix=ru"
		}
	},
	231: {
		"id": 231,
		"name": "горный козёл",
		"description": "Проворный скалолаз, способный атаковать с неожиданных углов. Его рога - грозное оружие в горной местности, а цепкие копыта позволяют занимать выгодные позиции. После смерти оставляет крепкую шкуру и нежное мясо.",
		"params": {
			"hunger": 1,
			"can_eate": [],
			"damage": 8,
			"health": 8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (75, 77)},
				{"item": rimagochi_items[12], "count": (23, 23)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/f/f0/Горный_козёл.png/revision/latest/scale-to-width-down/51?cb=20170127064950&path-prefix=ru"
		}
	},
	232: {
		"id": 232,
		"name": "корова",
		"description": "Мирное создание, чья главная боевая тактика — занимать место. Её удары копытами слабы, но неожиданно болезненны для тех, кто недооценивает её массу.",
		"params": {
			"hunger": 0.9,
			"can_eate": [],
			"damage": 7,
			"health": 8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (160, 164)},
				{"item": rimagochi_items[12], "count": (36, 36)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/8/88/Корова.png/revision/latest/scale-to-width-down/51?cb=20160717123309&path-prefix=ru"
		}
	},
	233: {
		"id": 233,
		"name": "кот",
		"description": "Независимый хищник, который сражается только когда сам этого захочет. Его атаки — стремительные царапины, от которых противник истекает кровью. Чаще просто наблюдает за битвой с высокомерием существа, которое знает: люди — временные, а кошки — вечные.",
		"params": {
			"hunger": 0.7,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 7,
			"health": 3.8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (22, 23)},
				{"item": rimagochi_items[12], "count": (5, 5)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/6/62/Кошка.png/revision/latest/scale-to-width-down/51?cb=20161029110411&path-prefix=ru"
		}
	},
	236: {
		"id": 236,
		"name": "лабрадор ретривер",
		"description": "Преданный пёс, который защищает хозяина ценой своей жизни. Не самый сильный боец, но его укусы целенаправленны, а преданность делает его живым щитом. После битвы может притащить брошенное оружие... или хотя бы палку.",
		"params": {
			"hunger": 0.8,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 9,
			"health": 6,
			"after_death": [
				{"item": rimagochi_items[11], "count": (85, 95)},
				{"item": rimagochi_items[12], "count": (20, 22)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/d/d9/Лабрадор-ретривер.png/revision/latest/scale-to-width-down/51?cb=20161121091243&path-prefix=ru"
		}
	},
	242: {
		"id": 242,
		"name": "олень",
		"description": "Грациозный бегун, который предпочитает избегать боя. Его рога — скорее украшение, чем оружие, но в отчаянии он может нанести болезненный удар. Главная ценность — нежное мясо и прочная шкура.",
		"params": {
			"hunger": 1,
			"can_eate": [],
			"damage": 8,
			"health": 8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (79, 82)},
				{"item": rimagochi_items[12], "count": (17, 19)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/e/ec/Олень.png/revision/latest/scale-to-width-down/51?cb=20161122181902&path-prefix=ru"
		}
	},
	247: {
		"id": 247,
		"name": "страус",
		"description": "Нелетающая птица-рекордсмен. Может разогнаться до 70 км/ч, а удар её ноги ломает рёбра. В бою использует тактику 'ударил-убежал'.",
		"params": {
			"hunger": 1,
			"can_eate": [],
			"damage": 8,
			"health": 7,
			"after_death": [
				{"item": rimagochi_items[11], "count": (90, 108)},
				{"item": rimagochi_items[12], "count": (25, 28)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/f/fb/Страус.png/revision/latest/scale-to-width-down/51?cb=20170605224933&path-prefix=ru"
		}
	},
	248: {
		"id": 248,
		"name": "эму",
		"description": "Менее агрессивный, но более выносливый собрат обычного страуса. В бою полагается на свою скорость и долгие ноги, изматывая противника.",
		"params": {
			"hunger": 1,
			"can_eate": [],
			"damage": 7,
			"health": 8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (90, 108)},
				{"item": rimagochi_items[12], "count": (25, 28)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/0/07/Эму.png/revision/latest/scale-to-width-down/51?cb=20170624172722&path-prefix=ru"
		}
	},
	249: {
		"id": 249,
		"name": "фенек",
		"description": "Мелкая пустынная лисица с огромными ушами. Невероятно проворная, но хрупкая. В бою полагается на скорость и внезапные атаки.",
		"params": {
			"hunger": 0.5,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 6,
			"health": 5,
			"after_death": [
				{"item": rimagochi_items[11], "count": (50, 50)},
				{"item": rimagochi_items[12], "count": (18, 18)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/2/22/Фенек.png/revision/latest/scale-to-width-down/51?cb=20170624171740&path-prefix=ru"
		}
	},
	250: {
		"id": 250,
		"name": "хаски",
		"description": "Верный пёс, чья преданность компенсирует отсутствие тактического гения. В бою полагается на стайный инстинкт.",
		"params": {
			"hunger": 0.8,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 9,
			"health": 8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (90, 90)},
				{"item": rimagochi_items[12], "count": (18, 22)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/f/f5/Хаски.png/revision/latest/scale-to-width-down/51?cb=20161122135832&path-prefix=ru"
		}
	},
	251: {
		"id": 251,
		"name": "черепаха",
		"description": "Живой щит с философским отношением к жизни. Её панцирь игнорирует половину урона, но атакует так медленно, что противники успевают заскучать.",
		"params": {
			"hunger": 0.5,
			"can_eate": [],
			"damage": 3,
			"health": 20,
			"after_death": [
				{"item": rimagochi_items[11], "count": (45, 45)},
				{"item": rimagochi_items[12], "count": (8, 12)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/5/5a/Черепаха.png/revision/latest/scale-to-width-down/51?cb=20150613162739&path-prefix=ru"
		}
	},
	253: {
		"id": 253,
		"name": "осёл",
		"description": "Упрямый таскер, который в бою ведёт себя как живая баррикада. Его пинки ломают кости, но главная сила — терпение.",
		"params": {
			"hunger": 1,
			"can_eate": [],
			"damage": 8,
			"health": 8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (130, 140)},
				{"item": rimagochi_items[12], "count": (40, 50)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/6/66/Осел.png/revision/latest/scale-to-width-down/51?cb=20200602064232&path-prefix=ru"
		}
	},
	254: {
		"id": 254,
		"name": "селезень",
		"description": "Агрессивная птица, чьи шипящие атаки снижают боевой дух врагов. Клюв бьёт точнее, чем кажется.",
		"params": {
			"hunger": 0.6,
			"can_eate": [],
			"damage": 6,
			"health": 5,
			"after_death": [
				{"item": rimagochi_items[11], "count": (16, 16)},
				{"item": rimagochi_items[12], "count": (5, 5)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/f/fa/Утка.png/revision/latest?cb=20200601121206&path-prefix=ru"
		}
	},
	255: {
		"id": 255,
		"name": "козёл",
		"description": "Неукротимый горный боец. Бьётся рогами в стиле «танк-ролл», снося противников с ног.",
		"params": {
			"hunger": 0.9,
			"can_eate": [],
			"damage": 8,
			"health": 8,
			"after_death": [
				{"item": rimagochi_items[11], "count": (66, 70)},
				{"item": rimagochi_items[12], "count": (26, 28)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/b/b8/Козел.png/revision/latest/scale-to-width-down/51?cb=20200602061648&path-prefix=ru"
		}
	},
	256: {
		"id": 256,
		"name": "гусь",
		"description": "Пернатый террор. В стае превращает поле боя в хаос: шипение, хлопанье крыльев и укусы в самые неожиданные места.",
		"params": {
			"hunger": 0.7,
			"can_eate": [],
			"damage": 5,
			"health": 6,
			"after_death": [
				{"item": rimagochi_items[11], "count": (36, 38)},
				{"item": rimagochi_items[12], "count": (20, 22)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/c/c6/Гусь.png/revision/latest/scale-to-width-down/51?cb=20200602052723&path-prefix=ru"
		}
    },
    258: {
		"id": 258,
		"name": "баран",
		"description": "Живая таранная установка. Разгоняется медленно, но удар его лба сбивает с ног даже медведей.",
		"params": {
			"hunger": 1,
			"can_eate": [],
			"damage": 9,
			"health": 7,
			"after_death": [
				{"item": rimagochi_items[11], "count": (175, 185)},
				{"item": rimagochi_items[12], "count": (65, 71)}
			],
			"rarity": rimagochi_rarity[35],
			"required_slots": 2,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/2/27/Баран.png/revision/latest/scale-to-width-down/51?cb=20200602054539&path-prefix=ru"
		}
	},
	27: {
		"id": 27,
		"name": "морская свинка",
		"description": "Единственное тактическое преимущество — способность умереть так громко, что противник на секунду задумается: 'А не слишком ли я жесток'?",
		"params":{
			"hunger": 0.5,
			"can_eate": [],
			"damage": 3,
			"health": 4,
			"after_death": [
				{"item": rimagochi_items[11], "count": (28, 30)},
				{"item": rimagochi_items[12], "count": (15, 17)}
			],
			"rarity": rimagochi_rarity[36],
			"required_slots" : 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/d/d2/Морская_свинка.png/revision/latest?cb=20200602065852&path-prefix=ru",
		}
	},
	210: {
		"id": 210,
		"name": "белка",
		"description": "Юркий, но абсолютно бесполезный в бою грызун. Мечется по полю, хаотично царапая врагов, и тут же погибает от любого удара. Единственное применение — сбивает противников с толку своей нелепой анимацией смерти.",
		"params":{
			"hunger": 0.6,
			"can_eate": [],
			"damage": 5,
			"health": 3,
			"after_death": [
				{"item": rimagochi_items[11], "count": (14, 14)},
				{"item": rimagochi_items[12], "count": (3, 3)}
			],
			"rarity": rimagochi_rarity[36],
			"required_slots" : 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/d/da/Белка.png/revision/latest/scale-to-width-down/51?cb=20161121160342&path-prefix=ru",
		}
	},
	212: {
		"id": 212,
		"name": "беляк",
		"description": "Трусливый комок шерсти с единственной тактикой — драпать при первой опасности. Его 'атаки' (робкие тычки лапками) не пугают даже мышей. Чаще всего просто служит живой консервой для хищников.",
		"params":{
			"hunger": 0.5,
			"can_eate": [],
			"damage": 4,
			"health": 3,
			"after_death": [
				{"item": rimagochi_items[11], "count": (18, 18)},
				{"item": rimagochi_items[12], "count": (4, 4)}
			],
			"rarity": rimagochi_rarity[36],
			"required_slots" : 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/e/e1/Заяц-беляк.png/revision/latest/scale-to-width-down/51?cb=20180422112010&path-prefix=ru",
		}
	},
	220: {
		"id": 220,
		"name": "заяц",
		"description": "Трусливый комок шерсти с единственной тактикой — драпать при первой опасности. Его 'атаки' (робкие тычки лапками) не пугают даже мышей. Чаще всего просто служит живой консервой для хищников.",
		"params":{
			"hunger": 0.5,
			"can_eate": [],
			"damage": 4,
			"health": 3,
			"after_death": [
				{"item": rimagochi_items[11], "count": (18, 18)},
				{"item": rimagochi_items[12], "count": (4, 4)}
			],
			"rarity": rimagochi_rarity[36],
			"required_slots" : 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/d/d6/Заяц.png/revision/latest/scale-to-width-down/51?cb=20150613162547&path-prefix=ru",
		}
	},
	222: {
		"id": 222,
		"name": "игуана",
		"description": "Медлительная, но удивительно живучая рептилия. Её укусы слабы, но она может часами изматывать противников, прячась в укрытиях.",
		"params": {
			"hunger": 0.6,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 1,
			"health": 12,
			"after_death": [
				{"item": rimagochi_items[11], "count": (24, 26)},
				{"item": rimagochi_items[12], "count": (6, 6)}
			],
			"rarity": rimagochi_rarity[36],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/c/ca/Игуана.png/revision/latest/scale-to-width-down/51?cb=20150613162556&path-prefix=ru"
		}
	},
	223: {
		"id": 223,
		"name": "йоркширский терьер",
		"description": "Крошечный пёсик с комплексом Наполеона. Его лай страшнее укусов, но зато он отвлекает врагов своей истеричной суетой. Идеальный живой щит — противники теряют время, пытаясь попасть по этой юркой мишени.",
		"params": {
			"hunger": 0.4,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 2,
			"health": 5,
			"after_death": [
				{"item": rimagochi_items[11], "count": (26, 28)},
				{"item": rimagochi_items[12], "count": (6, 6)}
			],
			"rarity": rimagochi_rarity[36],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/a/a3/Йоркширский_терьер.png/revision/latest/scale-to-width-down/51?cb=20161124131207&path-prefix=ru"
		}
	},
	234: {
		"id": 234,
		"name": "крыса",
		"description": "Рой этих тварей способен обглодать врага до костей за минуты. Поодиночке абсолютно беспомощны, но в массовом порядке становятся живой бензопилой. Главный козырь — противник теряет рассудок от их писка и шевелящейся массы.",
		"params": {
			"hunger": 0.4,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 3,
			"health": 4,
			"after_death": [
				{"item": rimagochi_items[11], "count": (20, 20)},
				{"item": rimagochi_items[12], "count": (8, 8)}
			],
			"rarity": rimagochi_rarity[36],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/b/bc/Крыса.png/revision/latest/scale-to-width-down/51?cb=20170812161851&path-prefix=ru"
		}
	},
	235: {
		"id": 235,
		"name": "курица",
		"description": "Беспорядочно мечется по полю боя, создавая хаос. Её клевки почти безвредны, но стая куриц может затоптать противника в прямом смысле.",
		"params": {
			"hunger": 0.2,
			"can_eate": [],
			"damage": 2,
			"health": 4,
			"after_death": [
				{"item": rimagochi_items[11], "count": (23, 23)}
			],
			"rarity": rimagochi_rarity[36],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/3/34/Курица.png/revision/latest/scale-to-width-down/51?cb=20160715183052&path-prefix=ru"
		}
	},
	241: {
		"id": 241,
		"name": "обезьяна",
		"description": "Проворный боец, использующий примитивное оружие и тактику 'бей-беги'. Может швырять в врагов камни и экскременты, снижая их мораль.",
		"params": {
			"hunger": 0.6,
			"can_eate": [
				{"item": rimagochi_items[11]}
			],
			"damage": 5,
			"health": 3,
			"after_death": [
				{"item": rimagochi_items[11], "count": (30, 34)},
				{"item": rimagochi_items[12], "count": (7, 7)}
			],
			"rarity": rimagochi_rarity[36],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/2/26/Обезьяна.png/revision/latest/scale-to-width-down/51?cb=20150613162702&path-prefix=ru"
		}
	},
	252: {
		"id": 252,
		"name": "шиншилла",
		"description": "Пушистый шарик с тактикой «отвлечь милотой». Её укусы безвредны, но противники теряют ход, пытаясь понять: это боец или декоративный аксессуар?",
		"params": {
			"hunger": 0.4,
			"can_eate": [],
			"damage": 3,
			"health": 3,
			"after_death": [
				{"item": rimagochi_items[11], "count": (18, 22)},
				{"item": rimagochi_items[12], "count": (5, 7)}
			],
			"rarity": rimagochi_rarity[36],
			"required_slots": 1,
			"image_url": "https://static.wikia.nocookie.net/rimworld/images/c/cc/Шиншилла.png/revision/latest/scale-to-width-down/51?cb=20200523125620&path-prefix=ru"
		}
	},
}
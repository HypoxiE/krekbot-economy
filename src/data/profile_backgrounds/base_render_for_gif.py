
def render(data, design):
	avatar_image = data['avatar']
	user = data['user']

	border_color = tuple(design.border_color)
	border_width = design.border_width
	scale = design.scale

	pillow_frames = []
	background_gif = Image.open(f"src/data/profile_backgrounds/{design.file_name}")
	frames = [frame.convert("RGBA").copy() for frame in ImageSequence.Iterator(background_gif)]
	#frames = imageio.mimread(f"src/data/profile_backgrounds/{design.file_name}")

	#затемнение фона
	# Параметры
	blackout_background_size = design.blackout_background_size
	blackout_background_position = design.blackout_background_position
	blackout_background_color = tuple(design.blackout_background_color)
	blackout_background_radius = design.blackout_background_radius
	blackout_background_image = Image.new("RGBA", (blackout_background_size[0]*scale, blackout_background_size[1]*scale), (0,0,0,0))
	draw = ImageDraw.Draw(blackout_background_image)
	#фон
	draw.rounded_rectangle((0, 0, blackout_background_size[0]*scale, blackout_background_size[1]*scale), radius=blackout_background_radius*scale, fill=blackout_background_color, outline=border_color, width=border_width*scale)
	#вставляем в профиль
	small_blackout_background_image = blackout_background_image.resize((blackout_background_image.width//scale, blackout_background_image.height//scale), resample=Image.LANCZOS)

	#размещение аватарки
	avatar_size = design.avatar_size
	avatar_position = design.avatar_position
	big_size = (avatar_size[0] * scale, avatar_size[1] * scale)
	big_avatar = avatar_image.resize(big_size, resample=Image.LANCZOS)
	# Маска для большого размера
	mask = Image.new('L', big_size, 0)
	draw = ImageDraw.Draw(mask)
	radius = min(big_size)//2
	border_width_scaled = border_width * scale
	draw.ellipse((border_width_scaled, border_width_scaled, big_size[0] - border_width_scaled, big_size[1] - border_width_scaled), fill=255)
	# Аналогично для border_mask
	border_mask = Image.new('L', big_size, 0)
	border_draw = ImageDraw.Draw(border_mask)
	border_draw.ellipse((0, 0, big_size[0], big_size[1]), fill=255)
	border_draw.ellipse((border_width_scaled, border_width_scaled, big_size[0] - border_width_scaled, big_size[1] - border_width_scaled), fill=0)
	# Пастим и композим
	small_avatar = Image.new('RGBA', big_size)
	small_avatar.paste(big_avatar, (0, 0), mask)
	border = Image.new('RGBA', big_size, border_color)
	border.putalpha(border_mask)
	small_avatar = Image.alpha_composite(border, small_avatar)
	# Теперь уменьшаем
	small_avatar = small_avatar.resize(avatar_size, resample=Image.LANCZOS)

	#Размещение ника
	# Параметры
	nick_size = design.nick_size
	nick_position = design.nick_position
	nick_color = tuple(design.nick_color)
	nick_stroke_width = design.nick_stroke_width
	nick_stroke_color = tuple(design.nick_stroke_color)
	nick_pannel_image = Image.new("RGBA", (nick_size[0]*scale, nick_size[1]*scale), (0,0,0,0))
	draw = ImageDraw.Draw(nick_pannel_image)
	#draw.rectangle([(0, 0), (nick_pannel_image.width, nick_pannel_image.height)], fill=(200, 100, 50), outline=(0, 0, 0), width=5)
	# Текст
	try:
		font = ImageFont.truetype("src/data/fonts/segoeuib.ttf", 24*scale)
		if len(data['nick']) > 12:
			font = ImageFont.truetype("src/data/fonts/segoeuib.ttf", 20*scale)
	except:
		font = ImageFont.load_default()

	text = "\n".join([line.center(12) for line in textwrap.wrap(data['nick'], width=12)])
	bbox = draw.textbbox((0,0), text, font=font)
	text_w = bbox[2] - bbox[0]
	text_h = bbox[3] - bbox[1]
	x = (nick_size[0]*scale - text_w + 1) // 2
	y = (nick_size[1]*scale - text_h + 1) // 2
	draw.text((x, y), text, font=font, fill=nick_color, stroke_width=nick_stroke_width, stroke_fill=nick_stroke_color)
	#вставляем в профиль
	small_nick_pannel_image = nick_pannel_image.resize((nick_pannel_image.width//scale, nick_pannel_image.height//scale), resample=Image.LANCZOS)

	#размещение progressbar
	# Параметры
	progress_bar_size = design.progress_bar_size
	progress_bar_position = design.progress_bar_position
	progress_bar_fill_color = tuple(design.progress_bar_fill_color)
	progress_bar_empty_color = tuple(design.progress_bar_empty_color)
	progress_bar_radius = design.progress_bar_radius
	progress_bar_text_position = design.progress_bar_text_position
	progress_bar_text_color = tuple(design.progress_bar_text_color)
	progress_bar_text_stroke_width = design.progress_bar_text_stroke_width
	progress_bar_text_stroke_color = tuple(design.progress_bar_text_stroke_color)
	level = data['level']
	progress = level % 1
	big_progress_bar_image = Image.new("RGBA", (progress_bar_size[0]*scale, progress_bar_size[1]*scale), (0,0,0,0))
	draw = ImageDraw.Draw(big_progress_bar_image)
	# фон прогрессбара
	draw.rounded_rectangle((0,0,progress_bar_size[0]*scale, progress_bar_size[1]*scale), radius=progress_bar_radius*scale, fill=progress_bar_empty_color, outline=border_color, width=border_width*scale)
	# прогресс
	fill_width = int(progress_bar_size[0] * progress * scale)
	draw.rounded_rectangle((0,0,fill_width, progress_bar_size[1]*scale), radius=progress_bar_radius*scale, fill=progress_bar_fill_color, outline=border_color, width=border_width*scale)
	# Текст
	try:
		font = ImageFont.truetype("src/data/fonts/ComicRelief-Regular.ttf", 19*scale)
	except:
		font = ImageFont.load_default()
	text = f"Уровень {int(level)}"
	bbox = draw.textbbox((0,0), text, font=font)
	text_w = bbox[2] - bbox[0]
	text_h = bbox[3] - bbox[1]
	draw.text((progress_bar_text_position[0]*scale, progress_bar_text_position[1]*scale), text, font=font, fill=progress_bar_text_color, stroke_width=progress_bar_text_stroke_width, stroke_fill=progress_bar_text_stroke_color)
	#вставляем в профиль
	small_progress_bar_image = big_progress_bar_image.resize((big_progress_bar_image.width//scale, big_progress_bar_image.height//scale), resample=Image.LANCZOS)

	#размещение информации
	# Параметры
	info_bar_size = design.info_bar_size
	info_bar_position = design.info_bar_position
	info_bar_color = tuple(design.info_bar_color)
	info_bar_radius = design.info_bar_radius
	info_bar_text_color = tuple(design.info_bar_text_color)
	info_bar_text_position = design.info_bar_text_position
	info_pannel_image = Image.new("RGBA", (info_bar_size[0]*scale, info_bar_size[1]*scale), (0,0,0,0))
	draw = ImageDraw.Draw(info_pannel_image)
	#фон панели
	draw.rounded_rectangle((0, 0, info_bar_size[0]*scale, info_bar_size[1]*scale), radius=info_bar_radius*scale, fill=info_bar_color, outline=border_color, width=border_width*scale)
	# Текст
	try:
		font = ImageFont.truetype("src/data/fonts/ComicRelief-Bold.ttf", 15*scale)
	except:
		font = ImageFont.load_default()

	modify = data['crumbs_modify']
	text = (f"Баланс" + (f"(x{float(modify):.02n})" if modify != 1 else "") + f": {int(user.crumbs)} крошек\n"+
			f"Место в топе: {data['place_in_top']}\n"+
			(f"Репутация: {int(user.carma)}\n" if user.carma != 0 else "")+
			(f"Зарплата: {user.staff_salary:.02n}\n" if user.staff_salary != 0 else ""))
	bbox = draw.textbbox((0,0), text, font=font)
	text_w = bbox[2] - bbox[0]
	text_h = bbox[3] - bbox[1]
	draw.text((info_bar_text_position[0]*scale, info_bar_text_position[1]*scale), text, font=font, fill=info_bar_text_color)
	#вставляем в профиль
	small_info_pannel_image = info_pannel_image.resize((info_pannel_image.width//scale, info_pannel_image.height//scale), resample=Image.LANCZOS)

	for arr in frames:
		#bg_image = Image.fromarray(arr).convert("RGBA")
		bg_image = arr.copy()
		bg_image.paste(small_blackout_background_image, blackout_background_position, small_blackout_background_image)
		small_avatar_final = small_avatar.copy()
		bg_image.paste(small_avatar_final, avatar_position, small_avatar_final)
		bg_image.paste(small_nick_pannel_image, nick_position, small_nick_pannel_image)
		bg_image.paste(small_progress_bar_image, progress_bar_position, small_progress_bar_image)
		bg_image.paste(small_info_pannel_image, info_bar_position, small_info_pannel_image)

		bg_image = bg_image.convert("RGB")
		pillow_frames.append(bg_image)

	buffer = BytesIO()
	pillow_frames[0].save(buffer, save_all=True, append_images=pillow_frames[1:], loop=0, duration=100, format='WEBP')
	buffer.seek(0)

	return buffer
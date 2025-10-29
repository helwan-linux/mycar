import pygame
import random
import json
import os
from objects import Road, Player, Nitro, Tree, Button, \
					Obstacle, Coins, Fuel, Pursuer 

pygame.init()
SCREEN = WIDTH, HEIGHT = 288, 512

info = pygame.display.Info()
width = info.current_w
height = info.current_h

if width >= height:
	win = pygame.display.set_mode(SCREEN, pygame.NOFRAME)
else:
	win = pygame.display.set_mode(SCREEN, pygame.NOFRAME | pygame.SCALED | pygame.FULLSCREEN)

clock = pygame.time.Clock()
FPS = 30

lane_pos = [50, 95, 142, 190]

# COLORS **********************************************************************

WHITE = (255, 255, 255)
BLUE = (30, 144,255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 20)
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0) 

# FONTS ***********************************************************************

font = pygame.font.SysFont('cursive', 32)
score_font = pygame.font.SysFont('cursive', 24)
title_font = pygame.font.SysFont('cursive', 38)
small_font = pygame.font.SysFont('cursive', 16)
store_title_font = pygame.font.SysFont('cursive', 30) 

select_car = font.render('Select Car', True, WHITE)

# HIGH SCORE SYSTEM ***********************************************************

SCORE_FILE = 'high_score.json'

def load_high_score():
	if os.path.exists(SCORE_FILE):
		with open(SCORE_FILE, 'r') as f:
			return json.load(f)
	return 0.0

def save_high_score(score):
	with open(SCORE_FILE, 'w') as f:
		json.dump(score, f)

HIGH_SCORE = load_high_score()

# GAME CONSTANTS AND VARIABLES ************************************************
MIN_GEAR = 1           
MAX_GEAR = 4           
GEAR_SPEED_MULTIPLIER = 1.8 
BASE_SPEED = 2.0       
SPEED_INCREASE_PER_LEVEL = 0.3 

# استخدام قاموس لتخزين الإعدادات القابلة للتعديل
GAME_SETTINGS = {
	'MAX_FUEL': 100, # القيمة الأولية للحد الأقصى للوقود
	'FUEL_UPGRADE_LEVEL': 1 # مستوى الترقية
}

OBSTACLE_SPAWN_INTERVAL = 90
COLLECTIBLE_SPAWN_INTERVAL = 270

# PURSUIT METER CONSTANTS (عداد المطاردة) **************************************
PURSUIT_MAX = 100
BASE_PURSUIT_INCREASE_RATE = 0.3   
BASE_PURSUIT_DECREASE_RATE = 2.5   
REQUIRED_SPEED_TO_ESCAPE = 8.0 
PURSUIT_RATE_INCREASE_PER_LEVEL = 0.1 
GEAR_DOWN_TIME = 30 

# IMAGES **********************************************************************

bg = pygame.image.load('Assets/bg.png')

home_img = pygame.image.load('Assets/home.png')
play_img = pygame.image.load('Assets/buttons/play.png')
end_img = pygame.image.load('Assets/end.jpg')
end_img = pygame.transform.scale(end_img, (WIDTH, HEIGHT))
game_over_img = pygame.image.load('Assets/game_over.png')
game_over_img = pygame.transform.scale(game_over_img, (220, 220))
coin_img = pygame.image.load('Assets/coins/1.png')
dodge_img = pygame.image.load('Assets/car_dodge.png')

try:
	rare_coin_img = pygame.image.load('Assets/rare_coins/1.png')
except:
	rare_coin_img = pygame.image.load('Assets/coins/5.png')
rare_coin_img = pygame.transform.scale(rare_coin_img, (24, 24))

home_btn_img = pygame.image.load('Assets/buttons/home.png')
# نستخدم صورة بديلة للزر فقط لإنشاء كائن الزر
store_img = home_btn_img 

left_arrow = pygame.image.load('Assets/buttons/arrow.png')
right_arrow = pygame.transform.flip(left_arrow, True, False)

replay_img = pygame.image.load('Assets/buttons/replay.png')
sound_off_img = pygame.image.load("Assets/buttons/soundOff.png")
sound_on_img = pygame.image.load("Assets/buttons/soundOn.png")

cars = []
car_type = 0
for i in range(1, 9):
	img = pygame.image.load(f'Assets/cars/{i}.png')
	img = pygame.transform.scale(img, (59, 101))
	cars.append(img)

nitro_frames = []
nitro_counter = 0
for i in range(6):
	img = pygame.image.load(f'Assets/nitro/{i}.gif')
	img = pygame.transform.flip(img, False, True)
	img = pygame.transform.scale(img, (18, 36))
	nitro_frames.append(img)

# FUNCTIONS *******************************************************************
def center(image):
	return (WIDTH // 2) - image.get_width() // 2

# BUTTONS *********************************************************************
play_btn = Button(play_img, (100, 34), center(play_img)+10, HEIGHT-120) 
la_btn = Button(left_arrow, (32, 42), 40, 180)
ra_btn = Button(right_arrow, (32, 42), WIDTH-60, 180)

# إنشاء كائن زر المتجر باستخدام صورة بديلة (لتحمل حالة الضغط فقط)
store_btn = Button(store_img, (36, 36), WIDTH // 2 - 18, HEIGHT - 70) 

home_btn = Button(home_btn_img, (24, 24), WIDTH // 4 - 18, HEIGHT - 80)
replay_btn = Button(replay_img, (36,36), WIDTH // 2  - 18, HEIGHT - 86)
sound_btn = Button(sound_on_img, (24, 24), WIDTH - WIDTH // 4 - 18, HEIGHT - 80)

# SOUNDS **********************************************************************

click_fx = pygame.mixer.Sound('Sounds/click.mp3')
fuel_fx = pygame.mixer.Sound('Sounds/fuel.wav')
start_fx = pygame.mixer.Sound('Sounds/start.mp3')
restart_fx = pygame.mixer.Sound('Sounds/restart.mp3')
coin_fx = pygame.mixer.Sound('Sounds/coin.mp3')

pygame.mixer.music.load('Sounds/mixkit-tech-house-vibes-130.mp3')
pygame.mixer.music.play(loops=-1)
pygame.mixer.music.set_volume(0.6)

# OBJECTS *********************************************************************
road = Road()
nitro = Nitro(WIDTH-80, HEIGHT-80)
p = Player(100, HEIGHT-120, car_type)
pursuer = Pursuer(random.choice(lane_pos) + 10) 

tree_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
fuel_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
pursuer_group = pygame.sprite.Group() 
pursuer_group.add(pursuer)

# VARIABLES *******************************************************************
home_page = True
car_page = False
game_page = False
over_page = False
instructions_page = True 
store_page = False # حالة جديدة: صفحة المتجر

move_left = False
move_right = False
nitro_on = False
sound_on = True

counter = 0 
coins = 0   
counter_inc = 1
speed = BASE_SPEED
dodged = 0
cfuel = GAME_SETTINGS['MAX_FUEL'] # يستخدم القيمة من القاموس
level = 1 
gear = MIN_GEAR 
pursuit_level = 0 
gear_hold_time = GEAR_DOWN_TIME 

endx, enddx = 0, 0.5
gameovery = -50

running = True
while running:
	win.fill(BLACK)
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
				running = False

			if event.key == pygame.K_LEFT:
				move_left = True

			if event.key == pygame.K_RIGHT:
				move_right = True

			# منطق تغيير الغيارات
			if event.key == pygame.K_a:
				gear = 1
				gear_hold_time = GEAR_DOWN_TIME
			
			if event.key == pygame.K_s:
				gear = 2
				gear_hold_time = GEAR_DOWN_TIME
			
			if event.key == pygame.K_d:
				gear = 3
				gear_hold_time = GEAR_DOWN_TIME
			
			if event.key == pygame.K_b:
				gear = 4 
				gear_hold_time = GEAR_DOWN_TIME
				
			# مفتاح النيترو
			if event.key == pygame.K_n:
				nitro_on = True

			if instructions_page and event.key:
				instructions_page = False
				home_page = True


		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT:
				move_left = False

			if event.key == pygame.K_RIGHT:
				move_right = False
				
			if event.key == pygame.K_n:
				nitro_on = False
				
		if event.type == pygame.MOUSEBUTTONDOWN:
			x, y = event.pos

			if nitro.rect.collidepoint((x, y)):
				nitro_on = True
			else:
				if x <= WIDTH // 2:
					move_left = True
				else:
					move_right = True
			
			if instructions_page:
				instructions_page = False
				home_page = True


		if event.type == pygame.MOUSEBUTTONUP:
			move_left = False
			move_right = False
			
			if not pygame.mouse.get_pressed()[0]:
				nitro_on = False

	# *********************************************************************
	# INSTRUCTIONS PAGE
	# *********************************************************************
	if instructions_page:
		win.blit(bg, (0,0))
		
		# Box for instructions
		box_rect = pygame.Rect(30, 80, WIDTH - 60, HEIGHT - 160)
		pygame.draw.rect(win, BLACK, box_rect, border_radius=10)
		pygame.draw.rect(win, WHITE, box_rect, 2, border_radius=10)
		
		title = title_font.render('High-Speed Pursuit', True, GOLD)
		win.blit(title, (center(title), 100))
		
		# Line 1: The Main Goal
		goal_title = score_font.render('Main Goal:', True, WHITE)
		goal_text = small_font.render('Escape the pursuer! Keep your speed high.', True, WHITE)
		win.blit(goal_title, (40, 160))
		win.blit(goal_text, (40, 185))
		
		# Line 2: The Red Meter (Pursuit)
		pursuit_title = score_font.render('Red Meter (Pursuit):', True, RED)
		pursuit_text1 = small_font.render('Fills up if speed < 8.0 (Gears 1/2).', True, WHITE)
		pursuit_text2 = small_font.render('Decreases if speed > 8.0 (Gears 3/4/N).', True, WHITE)
		pursuit_text3 = small_font.render('If it reaches 100%, the pursuer CATCHES you!', True, RED)
		win.blit(pursuit_title, (40, 230))
		win.blit(pursuit_text1, (40, 255))
		win.blit(pursuit_text2, (40, 275))
		win.blit(pursuit_text3, (40, 295))

		# Line 3: The Green Meter (Fuel)
		fuel_title = score_font.render('Green Meter (Fuel):', True, GREEN)
		fuel_text1 = small_font.render('Collect fuel to keep driving. No fuel = stop.', True, WHITE)
		fuel_text2 = small_font.render('Fuel drains faster in high gears (3/4).', True, WHITE)
		win.blit(fuel_title, (40, 340))
		win.blit(fuel_text1, (40, 365))
		win.blit(fuel_text2, (40, 385))

		
		# Controls Hint
		control_hint = score_font.render('Gears: A (1), S (2), D (3), B (4) | Nitro: N', True, YELLOW)
		win.blit(control_hint, (center(control_hint), 420))
		
		continue_hint = small_font.render('Click or Press any key to start...', True, WHITE)
		win.blit(continue_hint, (center(continue_hint), 460))
		
		pygame.display.update()
		continue
	# *********************************************************************

	if home_page:
		win.blit(home_img, (0,0))
		
		high_score_text = score_font.render(f'HIGH SCORE: {HIGH_SCORE:.2f} km', True, GOLD)
		win.blit(high_score_text, (center(high_score_text), HEIGHT - 30))
		
		counter += 1
		if counter % 60 == 0:
			home_page = False
			car_page = True

	if car_page:
		win.blit(select_car, (center(select_car), 80))
		
		current_coins_text = score_font.render(f'Coins: {coins}', True, GOLD)
		win.blit(current_coins_text, (WIDTH - 100, 20))

		win.blit(cars[car_type], (WIDTH//2-30, 150))
		if la_btn.draw(win):
			car_type -= 1
			click_fx.play()
			if car_type < 0:
				car_type = len(cars) - 1

		if ra_btn.draw(win):
			car_type += 1
			click_fx.play()
			if car_type >= len(cars):
				car_type = 0
				
		# زر المتجر (تم تحسين شكله ليصبح عربة تسوق)
		store_x, store_y = WIDTH // 2 - 18, HEIGHT - 70
		store_rect = pygame.Rect(store_x, store_y, 36, 36)
		
		# رسم أيقونة سلة التسوق
		pygame.draw.rect(win, GOLD, store_rect, border_radius=5)
		pygame.draw.rect(win, BLACK, store_rect, 1)
		
		# رسم شكل عربة تسوق بسيط (صندوق وخطين)
		pygame.draw.rect(win, BLACK, (store_x + 10, store_y + 12, 16, 16), 2) 
		pygame.draw.line(win, BLACK, (store_x + 8, store_y + 10), (store_x + 28, store_y + 10), 2) 
		pygame.draw.circle(win, BLACK, (store_x + 12, store_y + 30), 3) 
		pygame.draw.circle(win, BLACK, (store_x + 24, store_y + 30), 3) 

		# التحقق من الضغط يدوياً باستخدام كائن الزر لحمل حالة الضغط
		pos = pygame.mouse.get_pos()
		if store_rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] and not store_btn.clicked:
				store_btn.clicked = True
				car_page = False
				store_page = True
				click_fx.play()
			elif not pygame.mouse.get_pressed()[0]:
				store_btn.clicked = False
		
		# نص فوق زر المتجر
		store_label = small_font.render('STORE', True, WHITE)
		win.blit(store_label, (WIDTH // 2 - 20, HEIGHT - 100))

		if play_btn.draw(win):
			car_page = False
			game_page = True

			start_fx.play()

			p = Player(100, HEIGHT-120, car_type)
			counter = 0
			level = 1
			gear = MIN_GEAR 
			
	# *********************************************************************
	# NEW: Store Page 
	# *********************************************************************
	if store_page:
		# التصحيح الأكيد: هذه يجب أن تكون أول الأوامر التنفيذية
		global GAME_SETTINGS
		global cfuel
		global coins
		
		# الآن يمكن استخدام المتغيرات العامة بأمان
		current_upgrade_level = GAME_SETTINGS['FUEL_UPGRADE_LEVEL']
		
		# تحديد قيم الترقية حسب المستوى الحالي
		if current_upgrade_level == 1:
			MAX_FUEL_COST = 50
			MAX_FUEL_NEXT = 150
			MAX_FUEL_CAP = 100
		else:
			MAX_FUEL_COST = 0 
			MAX_FUEL_NEXT = 150 
			MAX_FUEL_CAP = 150 
			
		
		win.blit(bg, (0,0))
		
		store_title = store_title_font.render('Store & Upgrades', True, GOLD)
		win.blit(store_title, (center(store_title), 50))
		
		coins_display = font.render(f'Your Coins: {coins}', True, YELLOW)
		win.blit(coins_display, (center(coins_display), 100))
		
		# -----------------------------------------------------
		# Upgrade: Fuel Tank ⛽ (ترقية فعالة)
		# -----------------------------------------------------
		upgrade_rect = pygame.Rect(30, 160, WIDTH - 60, 60)
		pygame.draw.rect(win, BLACK, upgrade_rect, border_radius=5)
		pygame.draw.rect(win, WHITE, upgrade_rect, 2, border_radius=5)
		
		# النص
		fuel_upgrade_text = score_font.render(f'Upgrade Fuel Tank (Current Max: {MAX_FUEL_CAP})', True, WHITE)
		
		win.blit(fuel_upgrade_text, (40, 170))
		
		buy_btn = Button(play_img, (36, 36), WIDTH - 60, 172)
		
		if current_upgrade_level == 1:
			# حالة عدم الشراء بعد
			cost_text = score_font.render(f'Cost: {MAX_FUEL_COST} Coins', True, GOLD)
			win.blit(cost_text, (40, 195))
			
			if buy_btn.draw(win):
				if coins >= MAX_FUEL_COST:
					coins -= MAX_FUEL_COST
					# تعديل المتغيرات العامة
					GAME_SETTINGS['MAX_FUEL'] = MAX_FUEL_NEXT 
					GAME_SETTINGS['FUEL_UPGRADE_LEVEL'] = 2 
					cfuel = GAME_SETTINGS['MAX_FUEL'] # يتم تعبئة الوقود بالكامل
					click_fx.play()
				else:
					# رسالة خطأ مؤقتة لعدم كفاية العملات
					error_msg = small_font.render('Not enough coins!', True, RED)
					win.blit(error_msg, (WIDTH - 150, 185))
		else:
			# حالة تم الشراء بالفعل
			purchased_text = score_font.render('PURCHASED (Max Level)', True, GREEN)
			win.blit(purchased_text, (WIDTH - 150, 185))


		# -----------------------------------------------------
		# زر العودة
		# -----------------------------------------------------
		if home_btn.draw(win): 
			store_page = False
			car_page = True
			click_fx.play()
		
		# نص فوق زر العودة
		back_label = small_font.render('BACK', True, WHITE)
		win.blit(back_label, (WIDTH // 4 - 18, HEIGHT - 100))

	# *********************************************************************
	
	if over_page:
		win.blit(end_img, (endx, 0))
		endx += enddx
		if endx >= 10 or endx<=-10:
			enddx *= -1
			
		current_distance = counter / 1000
		if current_distance > HIGH_SCORE:
			HIGH_SCORE = current_distance
			save_high_score(HIGH_SCORE)
			
			
		win.blit(game_over_img, (center(game_over_img), gameovery))
		if gameovery < 16:
			gameovery += 1

		num_coin_img = font.render(f'{coins}', True, WHITE)
		num_dodge_img = font.render(f'{dodged}', True, WHITE)
		distance_img = font.render(f'Distance : {current_distance:.2f} km', True, WHITE)
		high_score_img = font.render(f'HIGH : {HIGH_SCORE:.2f} km', True, GOLD)

		win.blit(coin_img, (80, 240))
		win.blit(dodge_img, (50, 280))
		
		win.blit(num_coin_img, (180, 250))
		win.blit(num_dodge_img, (180, 300))
		
		win.blit(distance_img, (center(distance_img), (350)))
		win.blit(high_score_img, (center(high_score_img), (390)))


		if home_btn.draw(win):
			over_page = False
			instructions_page = True

			coins = 0
			dodged = 0
			counter = 0
			nitro.gas = 0
			cfuel = GAME_SETTINGS['MAX_FUEL'] # العودة للحد الأقصى المتاح
			level = 1
			gear = MIN_GEAR
			pursuit_level = 0
			gear_hold_time = GEAR_DOWN_TIME
			pursuer.rect.y = HEIGHT * 2 

			endx, enddx = 0, 0.5
			gameovery = -50

		if replay_btn.draw(win):
			over_page = False
			game_page = True

			coins = 0
			dodged = 0
			counter = 0
			nitro.gas = 0
			cfuel = GAME_SETTINGS['MAX_FUEL'] # العودة للحد الأقصى المتاح
			level = 1
			gear = MIN_GEAR
			pursuit_level = 0
			gear_hold_time = GEAR_DOWN_TIME
			pursuer.rect.y = HEIGHT * 2 


			endx, enddx = 0, 0.5
			gameovery = -50

			restart_fx.play()

		if sound_btn.draw(win):
			sound_on = not sound_on

			if sound_on:
				sound_btn.update_image(sound_on_img)
				pygame.mixer.music.play(loops=-1)
			else:
				sound_btn.update_image(sound_off_img)
				pygame.mixer.music.stop()

	if game_page:
		
		# Gear Auto-Downshift Logic
		if gear > MIN_GEAR and not nitro_on:
			gear_hold_time -= 1
			if gear_hold_time <= 0:
				gear = MIN_GEAR 
				gear_hold_time = GEAR_DOWN_TIME

		# 1. Level Speed 
		level_base_speed = BASE_SPEED + (level - 1) * SPEED_INCREASE_PER_LEVEL
		
		# 2. Final Speed Calculation 
		max_fuel_value = GAME_SETTINGS['MAX_FUEL'] # قراءة القيمة من القاموس

		if nitro_on and cfuel > 0:
			speed = 15.0 
			counter_inc = 7
		else:
			speed = level_base_speed * (gear * GEAR_SPEED_MULTIPLIER)
			
			counter_inc = int(speed / 2) if speed > 2 else 1
			if speed < 2.0:
				speed = 2.0

		# 3. PURSUIT METER LOGIC
		pursuit_increase_rate = BASE_PURSUIT_INCREASE_RATE + (level - 1) * PURSUIT_RATE_INCREASE_PER_LEVEL
		
		if speed < REQUIRED_SPEED_TO_ESCAPE:
			pursuit_level += pursuit_increase_rate
		else:
			pursuit_level -= BASE_PURSUIT_DECREASE_RATE

		pursuit_level = max(0, min(PURSUIT_MAX, pursuit_level))

		# PURSUIT METER GAME OVER (العدو يلحق بك)
		if pursuit_level >= PURSUIT_MAX:
			speed = 0.0
			game_page = False
			over_page = True
			
			tree_group.empty()
			coin_group.empty()
			fuel_group.empty()
			obstacle_group.empty()
			pursuer.rect.y = HEIGHT * 2 
			continue

		# Game Over if Fuel Runs Out 
		if cfuel <= 0 and not nitro_on:
			speed = 0.0
			game_page = False
			over_page = True
			
			tree_group.empty()
			coin_group.empty()
			fuel_group.empty()
			obstacle_group.empty()
			pursuer.rect.y = HEIGHT * 2 
			continue

		win.blit(bg, (0,0))
		road.update(speed)
		road.draw(win)

		# LEVEL UP LOGIC: 
		current_level = int(counter / 1000) + 1
		if current_level > level:
			level = current_level
			
			OBSTACLE_SPAWN_INTERVAL = max(30, 90 - (level * 8))
			COLLECTIBLE_SPAWN_INTERVAL = max(90, 270 - (level * 15))


		counter += counter_inc
		if counter % 60 == 0:
			tree = Tree(random.choice([-5, WIDTH-35]), -20)
			tree_group.add(tree)

		# Spawn Collectibles and Obstacles based on dynamic intervals
		if counter % COLLECTIBLE_SPAWN_INTERVAL == 0:
			# وزن لظهور العملة النادرة (3) مقابل العملة العادية (5) والوقود (3)
			spawn_type = random.choices([1, 2, 3], weights=[5, 3, 2], k=1)[0]
			x = random.choice(lane_pos)+10
			
			if spawn_type == 1:
				count = random.randint(1, 3)
				for i in range(count):
					coin = Coins(x,-100 - (25 * i), coin_type=1) 
					coin_group.add(coin)
			elif spawn_type == 2:
				fuel = Fuel(x, -100)
				fuel_group.add(fuel)
			elif spawn_type == 3:
				coin = Coins(x,-100, coin_type=2) # عملة نادرة
				coin_group.add(coin)
				
		elif counter % OBSTACLE_SPAWN_INTERVAL == 0:
			obs = random.choices([1, 2, 3], weights=[6,2,2], k=1)[0]
			obstacle = Obstacle(obs)
			obstacle_group.add(obstacle)

		# NITRO LOGIC (Consumption)
		if nitro_on and cfuel > 0:
			x, y = p.rect.centerx - 8, p.rect.bottom - 10
			win.blit(nitro_frames[nitro_counter], (x, y))
			nitro_counter = (nitro_counter + 1) % len(nitro_frames)
				
			cfuel -= 1.5 
			if cfuel < 0:
				cfuel = 0
				nitro_on = False
		
		elif nitro_on and cfuel <= 0:
			nitro_on = False

		nitro.update(nitro_on)
		nitro.draw(win)
		obstacle_group.update(speed)
		obstacle_group.draw(win)
		tree_group.update(speed)
		tree_group.draw(win)
		coin_group.update(speed)
		coin_group.draw(win)
		fuel_group.update(speed)
		fuel_group.draw(win)

		p.update(move_left, move_right)
		p.draw(win)
		
		# تحديث ورسم المطارد
		if pursuit_level >= 10:
			pursuer.update(speed, pursuit_level)
			pursuer.draw(win)
		else:
			pursuer.rect.y = HEIGHT * 2 # إخفاؤه

		# DRAWING METERS ******************************************************
		
		FUEL_X, FUEL_Y = 20, 20
		PURSUIT_Y_OFFSET = 35 
		
		# 1. FUEL BAR (Top Left)
		fuel_level = cfuel
		max_bar_width = 100
		
		# العنوان فوق عداد الوقود
		fuel_label = score_font.render('Fuel', True, WHITE)
		win.blit(fuel_label, (FUEL_X, FUEL_Y - 20))
		
		# Background line/frame (White line)
		pygame.draw.line(win, WHITE, (FUEL_X, FUEL_Y), (FUEL_X + max_bar_width, FUEL_Y), 2)
		pygame.draw.line(win, WHITE, (FUEL_X + max_bar_width, FUEL_Y), (FUEL_X + max_bar_width, FUEL_Y + 15), 2)
		pygame.draw.line(win, WHITE, (FUEL_X + max_bar_width, FUEL_Y + 15), (FUEL_X, FUEL_Y + 15), 2)
		pygame.draw.line(win, WHITE, (FUEL_X, FUEL_Y + 15), (FUEL_X, FUEL_Y), 2)
		
		# Fuel fill (Green) - يستخدم القيمة المحدثة من القاموس لحساب النسبة المئوية
		if fuel_level > 0:
			fuel_bar_width = int(fuel_level * max_bar_width / max_fuel_value)
			pygame.draw.rect(win, GREEN, (FUEL_X + 1, FUEL_Y + 1, fuel_bar_width - 1, 13))
			
		# Low fuel indicator
		if cfuel <= max_fuel_value * 0.25: # استخدام نسبة مئوية
			pygame.draw.circle(win, RED, (FUEL_X + max_bar_width + 5, FUEL_Y + 7), 5) 
			
		# Fuel consumption based on gear
		fuel_consumption = 0.05 + (gear * 0.015) 
		cfuel -= fuel_consumption


		# 2. PURSUIT METER (تحت عداد الوقود مباشرةً)
		PURSUIT_X, PURSUIT_Y = FUEL_X, FUEL_Y + PURSUIT_Y_OFFSET
		PURSUIT_W, PURSUIT_H = max_bar_width, 15
		
		# العنوان فوق عداد المطاردة (موضح الهدف)
		pursuit_label_text = 'Escape (Speed > 8.0)'
		pursuit_label_color = RED if pursuit_level > 0 else WHITE
		pursuit_label = score_font.render(pursuit_label_text, True, pursuit_label_color)
		win.blit(pursuit_label, (PURSUIT_X, PURSUIT_Y - 20)) 
			
		# Background line/frame (White line)
		pygame.draw.rect(win, WHITE, (PURSUIT_X, PURSUIT_Y, PURSUIT_W, PURSUIT_H), 2)

		# Pursuit fill (Red)
		current_pursuit_width = int(pursuit_level * PURSUIT_W / PURSUIT_MAX)
		if pursuit_level > 0:
			pygame.draw.rect(win, RED, (PURSUIT_X + 1, PURSUIT_Y + 1, current_pursuit_width - 1, PURSUIT_H - 2)) 

		# Physical Pursuer Catch Collision
		if pursuer.rect.colliderect(p.rect) and pursuit_level >= 50:
			speed = 0.0
			game_page = False
			over_page = True

			tree_group.empty()
			coin_group.empty()
			fuel_group.empty()
			obstacle_group.empty()
			pursuer.rect.y = HEIGHT * 2
			continue


		# Display level, speed, and gear
		LEVEL_Y = PURSUIT_Y + 20
		
		timer_display = f'({int(gear_hold_time/FPS):.1f}s)' if gear > MIN_GEAR else ''
		gear_text = score_font.render(f'Gear: {gear}/{MAX_GEAR} {timer_display}', True, WHITE) 
		win.blit(gear_text, (20, LEVEL_Y))
		
		level_text = score_font.render(f'Level: {level}', True, WHITE)
		win.blit(level_text, (20, LEVEL_Y + 20))

		speed_text = score_font.render(f'Speed: {speed:.1f}', True, WHITE)
		win.blit(speed_text, (20, LEVEL_Y + 40))


		# COLLISION DETECTION & KILLS (Obstacles)
		for obstacle in obstacle_group:
			if obstacle.rect.y >= HEIGHT:
				if obstacle.type == 1:
					dodged += 1
				obstacle.kill() 

			if pygame.sprite.collide_mask(p, obstacle):
				pygame.draw.rect(win, RED, p.rect, 1)
				speed = 0.0

				game_page = False
				over_page = True

				tree_group.empty()
				coin_group.empty()
				fuel_group.empty()
				obstacle_group.empty()
				pursuer.rect.y = HEIGHT * 2 
				continue

		collected_coins = pygame.sprite.spritecollide(p, coin_group, True)
		for coin in collected_coins:
			coins += coin.value
			coin_fx.play()

		if pygame.sprite.spritecollide(p, fuel_group, True):
			cfuel += 25
			fuel_fx.play()
			if cfuel >= max_fuel_value: # يستخدم القيمة المحدثة
				cfuel = max_fuel_value
				
		current_coins_text = score_font.render(f'Coins: {coins}', True, GOLD)
		win.blit(current_coins_text, (WIDTH - 100, 20))


	pygame.draw.rect(win, BLUE, (0, 0, WIDTH, HEIGHT), 3)
	clock.tick(FPS)
	pygame.display.update()

pygame.quit()

import pygame
import random
import json
import os
from objects import Road, Player, Nitro, Tree, Button, \
					Obstacle, Coins, Fuel

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

# FONTS ***********************************************************************

font = pygame.font.SysFont('cursive', 32)
score_font = pygame.font.SysFont('cursive', 24)

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
# تم زيادة المعامل لزيادة الفرق في السرعة بين الغيارات
GEAR_SPEED_MULTIPLIER = 1.8 
BASE_SPEED = 2.0       
SPEED_INCREASE_PER_LEVEL = 0.3 

OBSTACLE_SPAWN_INTERVAL = 90
COLLECTIBLE_SPAWN_INTERVAL = 270

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


left_arrow = pygame.image.load('Assets/buttons/arrow.png')
right_arrow = pygame.transform.flip(left_arrow, True, False)

home_btn_img = pygame.image.load('Assets/buttons/home.png')
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
play_btn = Button(play_img, (100, 34), center(play_img)+10, HEIGHT-80)
la_btn = Button(left_arrow, (32, 42), 40, 180)
ra_btn = Button(right_arrow, (32, 42), WIDTH-60, 180)

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

tree_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
fuel_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()

# VARIABLES *******************************************************************
home_page = True
car_page = False
game_page = False
over_page = False

move_left = False
move_right = False
nitro_on = False
sound_on = True

counter = 0 
coins = 0   
counter_inc = 1
speed = BASE_SPEED
dodged = 0
cfuel = 100
level = 1 
gear = MIN_GEAR # مستوى التعشيق/السرعة الحالي

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
			
			if event.key == pygame.K_s:
				gear = 2
			
			if event.key == pygame.K_d:
				gear = 3
			
			if event.key == pygame.K_b:
				gear = 4 
				
			# مفتاح النيترو
			if event.key == pygame.K_n:
				nitro_on = True

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

		if event.type == pygame.MOUSEBUTTONUP:
			move_left = False
			move_right = False
			
			if not pygame.mouse.get_pressed()[0]:
				nitro_on = False


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

		if play_btn.draw(win):
			car_page = False
			game_page = True

			start_fx.play()

			p = Player(100, HEIGHT-120, car_type)
			counter = 0
			level = 1
			gear = MIN_GEAR 

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
			home_page = True

			coins = 0
			dodged = 0
			counter = 0
			nitro.gas = 0
			cfuel = 100
			level = 1
			gear = MIN_GEAR

			endx, enddx = 0, 0.5
			gameovery = -50

		if replay_btn.draw(win):
			over_page = False
			game_page = True

			coins = 0
			dodged = 0
			counter = 0
			nitro.gas = 0
			cfuel = 100
			level = 1
			gear = MIN_GEAR

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
		
		# 1. Level Speed (Base speed based on game level)
		level_base_speed = BASE_SPEED + (level - 1) * SPEED_INCREASE_PER_LEVEL
		
		# 2. Final Speed Calculation 
		if nitro_on and cfuel > 0:
			# سرعة النيترو الجديدة (اندفاع فائق مبرر للاستخدام)
			speed = 15.0 
			counter_inc = 7
		else:
			# السرعة الجديدة: فرق كبير وملحوظ بين الغيارات
			speed = level_base_speed * (gear * GEAR_SPEED_MULTIPLIER)
			
			counter_inc = int(speed / 2) if speed > 2 else 1
			if speed < 2.0:
				speed = 2.0

		# 3. Game Over if Fuel Runs Out
		if cfuel <= 0 and not nitro_on:
			speed = 0.0
			game_page = False
			over_page = True
			
			tree_group.empty()
			coin_group.empty()
			fuel_group.empty()
			obstacle_group.empty()
			continue

		win.blit(bg, (0,0))
		road.update(speed)
		road.draw(win)

		# LEVEL UP LOGIC: Increase BASE_SPEED and obstacle rate
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
				coin = Coins(x,-100, coin_type=2)
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
				
			# تقليل استهلاك النيترو قليلاً (كان 2.0)
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

		# FUEL BAR DRAWING
		fuel_level = cfuel
		max_fuel = 100
		
		pygame.draw.line(win, WHITE, (20, 20), (20 + max_fuel, 20), 2)
		pygame.draw.line(win, WHITE, (20 + max_fuel, 20), (20 + max_fuel, 35), 2)
		pygame.draw.line(win, WHITE, (20 + max_fuel, 35), (20, 35), 2)
		pygame.draw.line(win, WHITE, (20, 35), (20, 20), 2)
		
		if fuel_level > 0:
			pygame.draw.rect(win, GREEN, (21, 21, fuel_level - 1, 13))
			
		if cfuel <= 25:
			pygame.draw.circle(win, RED, (18, 28), 5)
			
		cfuel -= 0.05 


		# Display level, speed, and gear
		level_text = score_font.render(f'Level: {level}', True, WHITE)
		win.blit(level_text, (20, 45))
		
		gear_text = score_font.render(f'Gear: {gear}/{MAX_GEAR}', True, WHITE) 
		win.blit(gear_text, (20, 65))
		
		speed_text = score_font.render(f'Speed: {speed:.1f}', True, WHITE)
		win.blit(speed_text, (20, 85))


		# COLLISION DETECTION & KILLS
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

		collected_coins = pygame.sprite.spritecollide(p, coin_group, True)
		for coin in collected_coins:
			coins += coin.value
			coin_fx.play()

		if pygame.sprite.spritecollide(p, fuel_group, True):
			cfuel += 25
			fuel_fx.play()
			if cfuel >= 100:
				cfuel = 100
				
		current_coins_text = score_font.render(f'Coins: {coins}', True, GOLD)
		win.blit(current_coins_text, (WIDTH - 100, 20))


	pygame.draw.rect(win, BLUE, (0, 0, WIDTH, HEIGHT), 3)
	clock.tick(FPS)
	pygame.display.update()

pygame.quit()

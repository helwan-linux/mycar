import math
import pygame
import random

SCREEN = WIDTH, HEIGHT = 288, 512

BLUE = (53, 81, 92)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

lane_pos = [50, 95, 142, 190]

class Road():
	def __init__(self):
		self.image = pygame.image.load('Assets/road.png')
		self.image = pygame.transform.scale(self.image, (WIDTH-60, HEIGHT))

		self.reset()
		self.move = True

	def update(self, speed):
		if self.move:
			self.y1 += speed
			self.y2 += speed

			if self.y1 >= HEIGHT:
				self.y1 = -HEIGHT
			if self.y2 >= HEIGHT:
				self.y2 = -HEIGHT

	def draw(self, win):
		win.blit(self.image, (self.x, self.y1))
		win.blit(self.image, (self.x, self.y2))

	def reset(self):
		self.x = 30
		self.y1 = 0
		self.y2 = -HEIGHT

class Player(pygame.sprite.Sprite):
	def __init__(self, x, y, type):
		super(Player, self).__init__()
		self.image = pygame.image.load(f'Assets/cars/{type+1}.png')
		self.image = pygame.transform.scale(self.image, (48, 82))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self, left, right):
		if left:
			self.rect.x -= 5
			if self.rect.x <= 40:
				self.rect.x = 40
		if right:
			self.rect.x += 5
			if self.rect.right >= 250:
				self.rect.right = 250

		self.mask = pygame.mask.from_surface(self.image)

	def draw(self, win):
		win.blit(self.image, self.rect)

class Obstacle(pygame.sprite.Sprite):
	def __init__(self, type):
		super(Obstacle, self).__init__()
		dx = 0
		self.type = type
		self.target_lane_x = None # New attribute for lane changing
		self.change_lane_chance = 0 # New attribute

		if type == 1:
			ctype = random.randint(1, 8)
			self.image = pygame.image.load(f'Assets/cars/{ctype}.png')
			self.image = pygame.transform.flip(self.image, False, True)
			self.image = pygame.transform.scale(self.image, (48, 82))
			
			# Set chance for lane changing for car type
			self.change_lane_chance = random.randint(0, 100)
			
		if type == 2:
			self.image = pygame.image.load('Assets/barrel.png')
			self.image = pygame.transform.scale(self.image, (24, 36))
			dx = 10
		elif type == 3:
			self.image = pygame.image.load('Assets/roadblock.png')
			self.image = pygame.transform.scale(self.image, (50, 25))

		self.rect = self.image.get_rect()
		self.rect.x = random.choice(lane_pos) + dx
		self.rect.y = -100

	def update(self, speed):
		self.rect.y += speed

		# NEW: Lane Changing Logic for car type 1
		if self.type == 1 and self.change_lane_chance > 80 and self.rect.y > 100 and self.rect.y < HEIGHT - 200:
			if self.target_lane_x is None:
				# Choose a new lane position (different from current)
				current_x = self.rect.x
				possible_lanes = [l for l in lane_pos if l != current_x]
				if possible_lanes:
					self.target_lane_x = random.choice(possible_lanes)
					
			if self.target_lane_x is not None:
				# Move smoothly towards the target lane
				if self.rect.x < self.target_lane_x:
					self.rect.x += 1 # Small movement speed for lane change
				elif self.rect.x > self.target_lane_x:
					self.rect.x -= 1 # Small movement speed for lane change
				else:
					self.target_lane_x = None # Reached target
					
		self.mask = pygame.mask.from_surface(self.image)

	def draw(self, win):
		win.blit(self.image, self.rect)

class Nitro:
	def __init__(self, x, y):
		self.image = pygame.image.load('Assets/nitro.png')
		self.image = pygame.transform.scale(self.image, (42, 42))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		self.gas = 0
		self.radius = 20
		self.CENTER = self.rect.centerx, self.rect.centery

	def update(self, nitro_on):
		if nitro_on:
			self.gas -= 1
			if self.gas <= -60:
				self.gas = -60
		else:
			self.gas += 1
			if self.gas >= 359:
				self.gas = 359

	def draw(self, win):
		win.blit(self.image, self.rect)
		if self.gas > 0 and self.gas < 360:
			for i in range(self.gas):
				x = round(self.CENTER[0] + self.radius * math.cos(i * math.pi / 180))
				y = round(self.CENTER[1] + self.radius * math.sin(i * math.pi / 180))
				pygame.draw.circle(win, YELLOW, (x, y), 1)

class Tree(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super(Tree, self).__init__()

		type = random.randint(1, 4)
		self.image = pygame.image.load(f'Assets/trees/{type}.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self, speed):
		self.rect.y += speed
		if self.rect.top >= HEIGHT:
			self.kill()

	def draw(self, win):
		win.blit(self.image, self.rect)

class Fuel(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super(Fuel, self).__init__()

		self.image = pygame.image.load('Assets/fuel.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self, speed):
		self.rect.y += speed
		if self.rect.top >= HEIGHT:
			self.kill()

	def draw(self, win):
		win.blit(self.image, self.rect)

class Coins(pygame.sprite.Sprite):
	def __init__(self, x, y, coin_type=1): # Added coin_type parameter
		super(Coins, self).__init__()
		
		self.coin_type = coin_type # 1: normal coin, 2: rare coin (diamond)
		self.value = 1 if coin_type == 1 else 5 # Define value
		
		self.images = []
		if self.coin_type == 1:
			for i in range(1, 7):
				img = pygame.image.load(f'Assets/Coins/{i}.png')
				self.images.append(img)
		else: # Assuming 'diamond' image for type 2
			# NOTE: You need to ensure you have Assets/diamond/1.png to 6.png for this to work
			# For now, we will use a different image if available, or load a placeholder
			# If you don't have diamond images, you can load the coin images here again
			# and adjust the value, but for unique visual we'll assume a 'rare coin' folder
			try:
				for i in range(1, 7):
					img = pygame.image.load(f'Assets/rare_coins/{i}.png') # Placeholder path
					self.images.append(img)
			except:
				# Fallback if rare_coins folder is missing (Use default coins, but keep value)
				for i in range(1, 7):
					img = pygame.image.load(f'Assets/Coins/{i}.png')
					self.images.append(img)
					
		self.counter = 0
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self, speed):
		self.counter += 1
		if self.counter % 5 == 0:
			self.index = (self.index + 1) % len(self.images)

		self.rect.y += speed
		if self.rect.top >= HEIGHT:
			self.kill()

		self.image = self.images[self.index]

	def draw(self, win):
		win.blit(self.image, self.rect)

class Button(pygame.sprite.Sprite):
	def __init__(self, img, scale, x, y):
		super(Button, self).__init__()
		
		self.scale = scale
		self.image = pygame.transform.scale(img, self.scale)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		self.clicked = False

	def update_image(self, img):
		self.image = pygame.transform.scale(img, self.scale)

	def draw(self, win):
		action = False
		pos = pygame.mouse.get_pos()
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] and not self.clicked:
				action = True
				self.clicked = True

			if not pygame.mouse.get_pressed()[0]:
				self.clicked = False

		win.blit(self.image, self.rect)
		return action

import random
import sys
import pygame
from wordfreq import zipf_frequency

SCREEN_SIZE = WIDTH, HEIGHT, = 500, 500
BOARD_WIDTH, BOARD_HEIGHT = WIDTH * 3 // 4, HEIGHT * 3 // 4
START_X = (WIDTH - BOARD_WIDTH) // 2
START_Y = (WIDTH - BOARD_HEIGHT) // 2
FPS = 15
BLACK = (90, 90, 90)
WHITE = (200, 200, 200)
BLUE = (0, 0, 204)
GREEN = (34, 139, 34)
YELLOW = (155, 135, 12)
RED = (200, 50, 50)
COL_LIST = [WHITE, YELLOW, GREEN]


class bcolors:
	GREEN = '\033[32m'
	YELLOW = '\033[33m'
	RED = '\033[31m'
	ENDC = '\033[0m'


class WordleGame:
	def __init__(self, length: int = 5):
		self.length = length
		self.max_guesses = self.length + 1
		self.guesses = 0
		self.board = []
		for r in range(self.max_guesses):
			self.board.append([])
			for c in range(self.length):
				self.board[r].append('')
		self.scores = [[0]*self.length]*self.max_guesses
		self.wordDict = self.get_word_list("dictionary.txt")
		if self.length == 5:
			self.solutions = self.get_word_list("solutions.txt")
		else:
			self.solutions = self.get_solutions_from_freq()
		self.secret_word = self.choose_secret_word()
		self.solved = False
		self.text_col = BLACK

	def choose_secret_word(self):
		return random.choice(self.solutions)

	def get_solutions_from_freq(self):
		solutions = []
		for word in self.wordDict:
			if zipf_frequency(word, 'en') > 4:
				solutions.append(word)
		return solutions
		
	def play(self):
		while not self.solved and self.guesses < self.max_guesses:
			guess = self.get_input()
			if guess == self.secret_word:
				self.solved = True
			for i in range(self.length):
				self.board[self.guesses][i] = guess[i]
			self.scores[self.guesses] = self.get_input_result(guess)
			self.display_result()
			self.guesses += 1

		if self.solved:
			print("Solved")
		else:
			print("You lose, the word was " + self.secret_word)

	def get_input(self):
		while True:
			guess = input("Guess word: ").upper()
			if guess not in self.wordDict:
				print(f"{bcolors.RED}Not A Valid {self.length} Letter Word{bcolors.ENDC}")
				continue
			break
		return guess

	def get_input_result(self, guess) -> [int]:

		if guess == self.secret_word:
			return [2] * self.length
		let_counts = {}
		for let in self.secret_word:
			if let in let_counts:
				let_counts[let] += 1
			else:
				let_counts[let] = 1
		scores = [0] * self.length
		for i in range(self.length):
			if guess[i] == self.secret_word[i]:
				scores[i] = 2
				let_counts[guess[i]] -= 1
		for i in range(self.length):
			if guess[i] in self.secret_word and let_counts[guess[i]] > 0 and scores[i] == 0:
				scores[i] = 1
				let_counts[guess[i]] -= 1

		return scores

	def display_result(self):
		for r in range(self.max_guesses):
			for c in range(self.length):
				if self.scores[r][c] == 2:
					print(bcolors.GREEN + self.board[r][c] + bcolors.ENDC, end="")
				elif self.scores[r][c] == 1:
					print(bcolors.YELLOW + self.board[r][c] + bcolors.ENDC, end="")
				else:
					print(self.board[r][c], end="")
			print()
		print()

	def get_word_list(self, filepath: str) -> [str]:
		word_list = []
		file = open(filepath, "r")
		for line in file:
			word = line.rstrip().upper()
			if len(word) == self.length:
				word_list.append(word)
		word_list.sort()
		return word_list

	def draw_board(self, screen):
		x, y = START_X, START_Y
		LETTER_WIDTH, LETTER_HEIGHT = BOARD_WIDTH // self.length, BOARD_HEIGHT // self.max_guesses
		for r in range(self.max_guesses):
			if r == self.guesses:
				text_color = self.text_col
			else:
				text_color = BLACK
			for c in range(self.length):
				square = pygame.Rect((x, y), (LETTER_WIDTH, LETTER_HEIGHT))
				screen.fill(COL_LIST[self.scores[r][c]], square)
				font = pygame.font.SysFont('Arial', 30, bold=True)
				text = font.render(self.board[r][c], True, text_color)
				text_rect = text.get_rect(center=square.center)
				screen.blit(text, text_rect)
				x += LETTER_WIDTH
			y += LETTER_HEIGHT
			x = START_X

	def draw_result(self, screen):
		if self.solved:
			font = pygame.font.SysFont('Arial', 30, bold=True)
			text = font.render("Solved!", True, GREEN)
			text_rect = text.get_rect(midtop=(WIDTH//2, HEIGHT - (HEIGHT-BOARD_HEIGHT)//2))
			screen.blit(text, text_rect)
		elif self.guesses >= self.max_guesses:
			font = pygame.font.SysFont('Arial', 30, bold=True)
			text = font.render("Failed! The word was " + self.secret_word, True, RED)
			text_rect = text.get_rect(midtop=(WIDTH // 2, HEIGHT - (HEIGHT - BOARD_HEIGHT) // 2))
			screen.blit(text, text_rect)

	def draw_row(self, screen, row: int):
		if row >= self.max_guesses:
			return
		LETTER_WIDTH, LETTER_HEIGHT = BOARD_WIDTH // self.length, BOARD_HEIGHT // self.max_guesses
		x, y = START_X, START_Y + row * LETTER_HEIGHT
		for c in range(self.length):
			square = pygame.Rect((x, y), (LETTER_WIDTH, LETTER_HEIGHT))
			screen.fill(COL_LIST[self.scores[row][c]], square)
			font = pygame.font.SysFont('Arial', 30, bold=True)
			text = font.render(self.board[row][c], True, self.text_col)
			text_rect = text.get_rect(center=square.center)
			screen.blit(text, text_rect)
			x += LETTER_WIDTH

	def handle_input(self, event, row, col):
		self.text_col = BLACK
		if self.solved or self.guesses >= self.max_guesses:
			return row, col
		if event.key == pygame.K_RETURN:
			guess = ''.join(self.board[self.guesses])
			if guess not in self.wordDict:
				self.text_col = RED
				return row, col
			self.scores[self.guesses] = self.get_input_result(''.join(self.board[self.guesses]))
			self.guesses += 1
			if guess == self.secret_word:
				self.solved = True
			col = 0
			row += 1
		else:
			if event.key == pygame.K_BACKSPACE and col != 0:
				self.board[row][col-1] = ''
				col -= 1
				return row, col
			if not event.unicode.isalpha() or col == self.length:
				return row, col
			self.board[row][col] = event.unicode.upper()
			col += 1
		return row, col


def main(game: WordleGame):
	pygame.init()
	pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])
	screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SRCALPHA)
	pygame.display.set_caption("Wordle")
	CLOCK = pygame.time.Clock()
	running = True

	mouse_rect = pygame.rect.Rect(0, 0, 3, 3)

	font = pygame.font.SysFont('Arial', 30, bold=True)
	text = font.render("Reset", True, WHITE)
	text_rect = text.get_rect(left=5, top=5)

	row = 0
	col = 0

	screen.fill(BLUE)
	screen.blit(text, text_rect)
	game.draw_board(screen)

	while(running):
		CLOCK.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				row, col = game.handle_input(event, row, col)
				game.draw_board(screen)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == pygame.BUTTON_LEFT:
					mouse_rect.center = pygame.mouse.get_pos()
					if mouse_rect.colliderect(text_rect):
						game = WordleGame(game.length)
						row = 0
						col = 0
						screen.fill(BLUE)
						screen.blit(text, text_rect)
						game.draw_board(screen)

		game.draw_row(screen, row)
		game.draw_result(screen)
		pygame.display.flip()


if __name__ == "__main__":

	try:
		word_length = int(sys.argv[1])
		if word_length < 2 or word_length > 15:
			word_length = 5
	except Exception as e:
		word_length = 5

	W = WordleGame(word_length)
	main(W)




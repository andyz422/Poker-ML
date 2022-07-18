# Poker ML
# Andy Zhu
# June 29, 2022

import numpy as np
import pandas as pd

NUMBERS = ['A', 'K', 'Q', 'J', 'T'] + [str(i) for i in range(9, 1, -1)]
NUMBERS_RANKING = {}
for idx, NUMBER in enumerate(NUMBERS):
	NUMBERS_RANKING[NUMBER] = 14 - idx

SUITS = ['d', 'c', 'h', 's']
NUM_PLAYERS = 6
POSITIONS = ['LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB']
BUYIN = 100

SMALL_BLIND_BET = 0.5
BIG_BLIND_BET = 1
NUM_CARDS_IN_HAND = 2
NUM_CARDS_IN_FLOP = 3
NUM_CARDS_IN_TURN = 1
NUM_CARDS_IN_RIVER = 1

# Factors to consider for action: prior action x position x pot
# PREFLOP - 416 df's
# 6 df's (1 for each position)
PREFLOP_2BET_ACTIONS = ['fold', 'call', 'raise_2_bb', 'raise_3_bb', 'raise_5_bb', 'raise_8_bb']
# 60 df's ((LJ-HJ, LJ-CO, ...) x (5bb pot, 10bb pot, 20bb pot, 40bb pot, ...))
PREFLOP_3BET_ACTIONS = ['fold', 'call', 'raise_5_bb', 'raise_8_bb', 'raise_13_bb', 'raise_21_bb', 'raise_34_bb']
# 175 df's ((LJ-HJ-CO, LJ-HJ-BTN, ...) x (10bb pot, 20bb pot, 40bb pot, 70bb pot, 100bb pot, ...))
PREFLOP_4BET_ACTIONS = ['fold', 'call', 'raise_21_bb', 'raise_34_bb', 'raise_55_bb', 'raise_100_bb']
# 210 df's ((LJ-HJ-CO, LJ-HJ-BTN, ...) x (20bb pot, 40bb pot, 70bb pot, 100bb pot, 150bb pot, 200bb pot, ...))
PREFLOP_5BET_ACTIONS = ['fold', 'call', 'raise_55_bb', 'raise_100_bb']


# POSTFLOP - 462 * 3 = 1386
# 90 df's ((Headsup, Multiway) x (PFR, PFC) x (OOP, [MP], IP) x (5bb pot, 10bb pot, 20bb pot, 40bb pot, 70bb pot, 100bb pot, 150bb pot, 200bb pot, 300bb pot, ...))
POSTFLOP_BET_ACTIONS = ['check', 'raise_0.33_pot', 'raise_0.5_pot', 'raise_0.67_pot', 'raise_0.75_pot', 'raise_1_pot', 'raise_1.25_pot', 'raise_1.5_pot', 'raise_2_pot', 'raise_3_pot']
# 108 df's ((Headsup, Multiway) x (PFR, PFC) x (OOP, [MP], [MP2], IP) x (5bb pot, 10bb pot, 20bb pot, 40bb pot, 70bb pot, 100bb pot, 150bb pot, 200bb pot, 300bb pot, ...))
POSTFLOP_2BET_ACTIONS = ['fold', 'call', 'raise_0.5_pot', 'raise_0.75_pot', 'raise_1_pot', 'raise_1.25_pot', 'raise_1.5_pot', 'raise_2_pot', 'raise_3_pot']
# 108 df's ((Headsup, Multiway) x (PFR, PFC) x (OOP, [MP], [MP2], IP) x (5bb pot, 10bb pot, 20bb pot, 40bb pot, 70bb pot, 100bb pot, 150bb pot, 200bb pot, 300bb pot, ...))
POSTFLOP_3BET_ACTIONS = ['fold', 'call', 'raise_0.67_pot', 'raise_1_pot', 'raise_1.25_pot', 'raise_1.5_pot', 'raise_2_pot', 'raise_3_pot']
# 84 df's ((Headsup, Multiway) x (PFR, PFC) x (OOP, [MP], [MP2], IP) x (20bb pot, 40bb pot, 70bb pot, 100bb pot, 150bb pot, 200bb pot, 300bb pot, ...))
POSTFLOP_4BET_ACTIONS = ['fold', 'call', 'raise_1_pot', 'raise_1.25_pot', 'raise_1.5_pot', 'raise_2_pot', 'raise_3_pot']
# 72 df's ((Headsup, Multiway) x (PFR, PFC) x (OOP, [MP], [MP2], IP) x (40bb pot, 70bb pot, 100bb pot, 150bb pot, 200bb pot, 300bb pot, ...))
POSTFLOP_5BET_ACTIONS = ['fold', 'call', 'raise_1_pot', 'raise_1.5_pot', 'raise_2_pot', 'raise_3_pot']


class Game:
	def __init__(self, num_players=NUM_PLAYERS, players=[], buyin=BUYIN):
		self.deck = Deck()
		self.buyin = buyin

		self.num_players = num_players
		assert self.num_players > 1, "A game should have more than 1 player"

		self.players = players
		if self.players == []:
			for player_num in range(self.num_players):
				self.players.append(Player(buyin=self.buyin))
		assert len(self.players) == self.num_players, "len(players) != num_players"

		self.positions = Positions(self.num_players)


	def play(self):
		board = []

		# Deal hands to players
		for player in self.players:
			hand = self.deck.deal_cards(NUM_CARDS_IN_HAND)
			player.get_hand(hand)

		# Small/big blind
		self.players[self.positions.current].bet(SMALL_BLIND_BET)
		self.players[self.positions.next()].bet(BIG_BLIND_BET)

		# Preflop action
		preflop_actions = ['preflop_2bet_actions', 'preflop_3bet_actions', 'preflop_4bet_actions',
						   'preflop_5bet_actions']
		current_preflop_action_idx = 0
		last_aggressor = self.players[self.positions.current]
		current_player = self.players[self.positions.next()]

		while last_aggressor != current_player:
			strategy_matrix = current_player.strategy.preflop_strategy[preflop_actions[current_preflop_action_idx]][self.positions.current_position]

		# Deal flop; while cur_player != last_aggressor
		flop = self.deck.deal_cards(NUM_CARDS_IN_FLOP)

		# Deal turn
		turn = self.deck.deal_cards(NUM_CARDS_IN_TURN)

		# Deal river
		river = self.deck.deal_cards(NUM_CARDS_IN_RIVER)
		

		return

	def move_button(self):
		self.positions.button = (self.positions.button + 1) % self.num_players


class Positions:
	def __init__(self, num_players):
		self.num_players = num_players
		self.button = np.random.randint(self.num_players)
		self.current = (self.button + 1) % self.num_players
		self.positions = POSITIONS
		self.current_position_idx = 4
		self.current_position = self.positions[self.current_position_idx]

	def next(self, num_times_next=1):
		for num_time_next in range(num_times_next):
			self.current += 1
			self.current_position_idx += 1
		self.current = self.current % self.num_players
		self.current_position = self.positions[self.current_position_idx]
		return self.current
		

class Player:
	def __init__(self, strategy=None, buyin=BUYIN):
		if strategy:
			self.strategy = strategy
		else:
			self.strategy = Strategy()

		self.buyin = buyin
		self.stack_size = self.buyin
		self.hand = None
		self.num_dict = {}
		self.suit_dict = {}
		self.hand_strength = ''
		self.pl = 0

	def rebuy(self):
		self.stack_size = self.buyin

	def get_hand(self, hand):
		self.hand = hand

	def analyze(self, board):
		# Populate num_dict and suit_dict
		if self.num_dict == {}:
			for card in (self.hand + board):
				self.num_dict[card[0]] = self.num_dict.get(card[0], 0) + 1
				self.suit_dict[card[1]] = self.suit_dict.get(card[1], 0) + 1

		else:
			self.num_dict[board[-1][0]] = self.num_dict.get(board[-1][0], 0) + 1
			self.suit_dict[board[-1][1]] = self.suit_dict.get(board[-1][1], 0) + 1

		# Get hand number strength
		for num_dict_key, num_dict_value in self.num_dict.items():

			if num_dict_value == 4:
				self.hand_strength = 'QUAD ' + num_dict_key
				break

			elif num_dict_value == 3:
				if 'SET' in self.hand_strength:
					prev_num = NUMBERS_RANKING[self.hand_strength[-1]]
					current_num = NUMBERS_RANKING[num_dict_key]

					if current_num > prev_num:
						self.hand_strength = 'FULL HOUSE ' + num_dict_key + ' ' + self.hand_strength[-1]

					else:
						self.hand_strength = 'FULL HOUSE ' + self.hand_strength[-1] + ' ' + num_dict_key

				elif 'TWO PAIR' in self.hand_strength:
					self.hand_strength = 'FULL HOUSE ' + num_dict_key + ' ' + self.hand_strength[-3]

				elif 'PAIR' in self.hand_strength:
					self.hand_strength = 'FULL HOUSE ' + num_dict_key + ' ' + self.hand_strength[-1]

				else:
					self.hand_strength = 'SET ' + num_dict_key

			elif num_dict_value == 2:
				if 'FULL HOUSE' in self.hand_strength:
					prev_num = NUMBERS_RANKING[self.hand_strength[-1]]
					current_num = NUMBERS_RANKING[num_dict_key]
					if current_num > prev_num:
						self.hand_strength = self.hand_strength[:-1] + num_dict_key

				elif 'SET' in self.hand_strength:
					self.hand_strength = 'FULL HOUSE ' + self.hand_strength[-1] + ' ' + num_dict_key

				elif 'TWO PAIR' in self.hand_strength:
					prev_num = NUMBERS_RANKING[self.hand_strength[-3]]
					prev_num2 = NUMBERS_RANKING[self.hand_strength[-1]]
					current_num = NUMBERS_RANKING[num_dict_key]
					if current_num > prev_num:
						self.hand_strength = self.hand_strength[:-3] + num_dict_key + ' ' + self.hand_strength[-3]

					elif current_num > prev_num2:
						self.hand_strength = self.hand_strength[:-1] + num_dict_key

				elif 'PAIR' in self.hand_strength:
					prev_num = NUMBERS_RANKING[self.hand_strength[-1]]
					current_num = NUMBERS_RANKING[num_dict_key]
					if current_num > prev_num:
						self.hand_strength = 'TWO ' + self.hand_strength[:-1] + num_dict_key + ' ' + self.hand_strength[-1]
					
					else:
						self.hand_strength = 'TWO ' + self.hand_strength + ' ' + num_dict_key

				else:
					self.hand_strength = 'PAIR ' + num_dict_key


class Strategy:
	def __init__(self):
		self.preflop_col_labels = NUMBERS
		self.preflop_row_labels = NUMBERS # col > row => suited (KQs, QKo)
		self.bb_pot_scenarios = ['5_bb_pot', '10_bb_pot', '20_bb_pot', '40_bb_pot', '70_bb_pot', '100_bb_pot', '150_bb_pot', '200_bb_pot', '300_bb_pot']

		# self.preflop_strategy = {action: {position: {pot: df, ...}, ...}, ...}
		self.preflop_strategy = {'preflop_2bet_actions': {}, 'preflop_3bet_actions': {},
								 'preflop_4bet_actions': {}, 'preflop_5bet_actions': {}}

		for position_idx, position in enumerate(POSITIONS):
			self.preflop_strategy['preflop_2bet_actions'][position] = StrategyMatrix(self.preflop_col_labels, self.preflop_row_labels, PREFLOP_2BET_ACTIONS)
			
			for position2_idx, position2 in enumerate(POSITIONS[position_idx+1:]):
				self.preflop_strategy['preflop_3bet_actions'][position+'-'+position2] = {}

				for bb_pot_scenario in self.bb_pot_scenarios[:4]:
					self.preflop_strategy['preflop_3bet_actions'][position+'-'+position2][bb_pot_scenario] = StrategyMatrix(self.preflop_col_labels, self.preflop_row_labels, PREFLOP_3BET_ACTIONS)

				for position3_idx, position3 in enumerate(POSITIONS[position_idx+position2_idx+2:]):
					self.preflop_strategy['preflop_4bet_actions'][position+'-'+position2+'-'+position3] = {}
					
					for bb_pot_scenario in self.bb_pot_scenarios[1:6]:
						self.preflop_strategy['preflop_4bet_actions'][position+'-'+position2+'-'+position3][bb_pot_scenario] = StrategyMatrix(self.preflop_col_labels, self.preflop_row_labels, PREFLOP_4BET_ACTIONS)

					self.preflop_strategy['preflop_5bet_actions'][position+'-'+position2+'-'+position3] = {}
					for bb_pot_scenario in self.bb_pot_scenarios[2:-1]:
						self.preflop_strategy['preflop_5bet_actions'][position+'-'+position2+'-'+position3][bb_pot_scenario] = StrategyMatrix(self.preflop_col_labels, self.preflop_row_labels, PREFLOP_5BET_ACTIONS)

		self.postflop_strategy = {'postflop_bet_actions': {}, 'postflop_2bet_actions': {},
								  'postflop_3bet_actions': {}, 'postflop_4bet_actions': {},
								  'postflop_5bet_actions': {}}

class StrategyMatrix:
	def __init__(self, col_labels, row_labels, actions):
		self.col_labels = col_labels
		self.row_labels = row_labels
		self.actions = actions
		self.num_actions = len(self.actions)

		matrices = np.random.rand(self.num_actions-1, len(self.row_labels), len(self.col_labels))
		matrices /= matrices.sum(axis=0)
		self.matrix = pd.DataFrame(matrices[0]).astype(str)
		for action_num in range(1, self.num_actions-1):
			self.matrix += ('/' + pd.DataFrame(matrices[action_num]).astype(str))

		self.matrix.columns = self.col_labels
		self.matrix.index = self.row_labels
		del matrices


class Deck:
	def __init__(self):
		self.suits = SUITS
		self.numbers = NUMBERS
		self.all_cards = [n+s for n in self.numbers for s in self.suits]
		self.cards = self.all_cards.copy()
		self.shuffle()

	def shuffle(self):
		np.random.shuffle(self.cards)

	def deal_cards(self, num_cards):
		dealt_cards = []

		for n in range(num_cards):
			dealt_card = self.cards.pop(-1)
			dealt_cards.append(dealt_card)

		return dealt_cards

	def reset(self):
		self.cards = self.all_cards
		self.shuffle() 


if __name__ == "__main__":
	print('test')
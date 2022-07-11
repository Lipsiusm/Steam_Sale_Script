#class represents an object on sale at the steam store

class Game:

	discount_percent=''
	sale_price=''
	title=''

	def __init__(self, discount_percent, sale_price, title):
		self.discount_percent = discount_percent
		self.sale_price = sale_price
		self.title = title

	def get_title(self):
		return self.title

	def get_discount(self):
		return self.discount_percent

	def get_cost(self):
		return self.sale_price

	def __eq__(self, other_game):
		if self.title == other_game.get_title():
			return True
		else:
			return False
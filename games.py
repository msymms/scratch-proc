# Class file that defines the Games Class
# used to calculate the probabilities

class Games(object):
    """Perform calculations on Game data"""

    def __init__(self, id):
        self.gameId = id  # Game Number
        self.name = ""  # Name of Game
        self.price = 0  # Cost of Ticket
        self.totalTickets = 0  # Total number of tickets in the game
        self.totalPrizes = 0  # Total number of payable tickets
        self.prizesClaimed = 0  # Number of payable tickets turned in
        self.initialValue = 0  # Total money in the Game at the start - calculated
        self.currentValue = 0  # Amount of money left in the game

    def gameProbability(self):  # Probability of obtaining a winning ticket
        self.totalPrizes / self.totalTickets

    def numTicketsRem(self):
        self.totalTickets - (self.prizesClaimed * self.gameProbability())

    def initialValuePerTicket(self):
        self.initialValue / self.totalTickets

    def currentValuePerTicket(self):
        self.currentValue / self.numTicketsRem()

    def changeInValue(self):
        self.currentValuePerTicket() / self.initialValuePerTicket()

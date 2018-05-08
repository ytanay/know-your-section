import time

DEFAULT_GAME_DURATION = 60


class Game:

    def __init__(self, player=None, human=None, computer=None, voting_team=None, duration=DEFAULT_GAME_DURATION):
        self.player, self.human, self.computer, self.voting_team, self.duration = player, human, computer, voting_team, duration
        self.start_time = time.time()

    @property
    def active(self):
        return time.time() - self.start_time < self.duration

    @property
    def players(self):
        return self.player, self.human, self.computer

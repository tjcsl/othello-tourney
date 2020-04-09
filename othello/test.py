from othello import moderator
from othello.apps.games.models import Game

m = moderator.Moderator(Game.objects.all()[0])
m.play()

print(moderator.logs)

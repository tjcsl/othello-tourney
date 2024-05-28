from django import template

register = template.Library()

@register.filter
def parseBlack(game):
    if game.ratingDelta >= 0:
        return f"{game.blackRating} + {abs(game.ratingDelta)}"
    elif game.ratingDelta < 0:
        return f"{game.blackRating} - {abs(game.ratingDelta)}"
    return "ERROR"

@register.filter
def parseWhite(game):
    if game.ratingDelta > 0:
        return f"{game.whiteRating} - {abs(game.ratingDelta)}"
    elif game.ratingDelta <= 0:
        return f"{game.whiteRating} + {abs(game.ratingDelta)}"
    return "ERROR"

@register.filter
def parseScore(game):
    # a - b = score
    # a + b = 64
    # 2a = 64 - score
    # 2b = 64 + score
    score = game.score
    return f"{int(32-score/2)}-{int(32+score/2)}"
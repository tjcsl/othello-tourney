from decimal import Decimal, getcontext

getcontext().prec = 28


def expected_score(rating_a: Decimal, rating_b: Decimal) -> Decimal:
    return Decimal(1) / (Decimal(1) + (Decimal(10) ** ((rating_b - rating_a) / Decimal(400))))


def calculate_match_rating_change(
    rating1: Decimal,
    rating2: Decimal,
    player1_wins: int,
    player2_wins: int,
    ties: int,
    k: int = 32,
) -> tuple[Decimal, Decimal]:
    """
    Calculate Elo rating changes for a multi-game match.
    """

    total_games = player1_wins + player2_wins + ties
    if total_games == 0:
        return Decimal(0), Decimal(0)

    # Actual scores
    score1 = (Decimal(player1_wins) + Decimal("0.5") * Decimal(ties)) / Decimal(total_games)
    score2 = (Decimal(player2_wins) + Decimal("0.5") * Decimal(ties)) / Decimal(total_games)

    # Expected scores
    expected1 = expected_score(rating1, rating2)
    expected2 = Decimal(1) - expected1

    # Rating deltas
    delta1 = Decimal(k) * Decimal(total_games) * (score1 - expected1)
    delta2 = Decimal(k) * Decimal(total_games) * (score2 - expected2)

    return delta1, delta2

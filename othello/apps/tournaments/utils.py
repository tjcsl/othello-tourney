import random


def chunks(v, n):
    for i in range(len(v), step=n):
        yield v[i: i + n]


def make_pairings(players, round_num, bye_player):
    groups = list(chunks(sorted(players, key=lambda x: x.ranking), round_num))
    matches = []

    for i in range(len(groups)):
        if len(groups[i]) % 2:  # Make sure groups has an even amount of players
            if i == len(groups) - 1:  # If group is lowest rank, append a bye player
                groups[i].append(bye_player)
            else:  # Else take the first player from the subsequent group
                groups[i].append(groups[i][0])
                groups[i + 1][0].pop(0)

        for j in range(len(groups[i]), step=2):
            black = random.choice((groups[i][j], groups[i][j + 1]))
            white = groups[i][j + 1] if black == groups[i][j] else groups[i][j]
            matches.append((black, white))

    return matches

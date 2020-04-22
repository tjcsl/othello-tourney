from othello.moderator import PlayerRunner


script = '/home/vagrant/othello/othello/submissions/2021abagali/26447775-37aa-4e8d-9e82-d352f8759da1.py'

p = PlayerRunner(script)


g = p.get_move('','',5)
print([x for x in g])
print(g.return_vaule)


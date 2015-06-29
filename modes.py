from random import shuffle
from helpers import say_hands,color_hand,find_win
import sys
from defer import defer
from goals import get_goals

def hardstop(bot):
    bot.players={}
    bot.goals=[]
    bot.player_list=[]
    bot.imbal = []
    bot.state=1
    bot.say_main("===========================")
    bot.say_main("Game state completely reset")
    bot.say_main("===========================")

def start(bot):
    print('Starting with {0}'.format(bot.player_list))
    assert len(bot.players.keys()) == len(bot.colors)
    bot.state=0 #Disabled during setup
    bot.goals = get_goals(bot.colors)
    #Players names in a random order
    names = list(bot.players.keys())
    shuffle(names)
    bot.player_list=names
    print(names)
    #Assign players to a color
    for x in range(0,len(bot.colors)):
        print(x)
        bot.players[names[x]]=[x,4 * bot.colors[x],[]]
    print(bot.players)
    #Tell players their goals
    for player in names:
        bot.mserv.privmsg(player,'Your goal is to obtain "{0}"'.format(
            color_hand(bot.goals[bot.players[player][0]],bot.irc_colors)))
    #Say player hands in channel
    say_hands(bot)
    bot.state = 2

def do_moves(bot):
    bot.say_main("All players have submitted moves.")
    bot.state=0
    for player in bot.player_list:
        give=bot.players[player][2][0]
        hand = list(bot.players[player][1])
        hand.pop(hand.index(give))
        bot.players[player][1]=""
        for x in hand: bot.players[player][1] += x
        bot.players[bot.player_list[bot.players[player][2][1]]][1]+=bot.players[player][2][0]
    say_hands(bot)
    if find_win(bot):
        hardstop(bot)
    else:
        imb=[[],[]]#(more),(less)
        for player in bot.player_list:
            bot.players[player][2]=()
            if len(bot.players[player][1])>4: 
                imb[0].append(player)
            elif len(bot.players[player][1])<4: 
                imb[1].append(player)
        if imb[0]: 
            imbalence(bot,imb)
        else:
            bot.state=2

def imbalence(bot,imbal):

    bot.imbal=imbal
    bot.say_main("There is an imbalence in player hands.")
    bot.say_main("During this round, only players with more than four colors")
    bot.say_main("should submit moves. Those players have recieved messages.")
    for player in imbal[0]:
        bot.players[player][2]=[]
        bot.players[player].append(bot.players[player][1])
        bot.players[player].append(False)
        excess = len(bot.players[player][1])-4
        bot.say_main("Your hand is {0}. You have {1} more colors than normal.".format(
            color_hand(bot.players[player][1],bot.irc_colors),excess),player)
        bot.say_main("The following players have fewer than 4 colors:{0}".format(
            str(imbal[1])),player) 
        bot.say_main("You must make {0} simultanious moves, giving to {0} different people".format(excess),player)
    bot.state=3

def do_imbal(bot):
    bot.state=0
    bot.say_main("All imbalenced players have submitted moves.")
    for player in bot.imbal[0]:
        for move in bot.players[player][2]:
            bot.players[bot.player_list[move[1]]][1]+=move[0]
        bot.players[player][1]=bot.players[player][3]
        bot.players[player].pop(4)
        bot.players[player].pop(3)

    bot.imbal=[[],[]]
    say_hands(bot)
    imb=[[],[]]#(more),(less)
    for player in bot.player_list:
        bot.players[player][2]=()
        if len(bot.players[player][1])>4: 
            imb[0].append(player)
        elif len(bot.players[player][1])<4: 
            imb[1].append(player)
    if find_win(bot):
        hardstop(bot)
    elif imb[0]: 
        imbalence(bot,imb)
    else:
        bot.state=2


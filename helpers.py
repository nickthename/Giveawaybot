def color_player(bot,player):
    return bot.col_pre+bot.irc_colors[bot.colors[bot.player_list.index(player)]]+player



def say_hands(bot,target=""):
    if target == "":
        target=bot.mchan
    for player in list(bot.players.keys()):
        color = bot.colors[bot.players[player][0]]
        bot.say_main("{0}{1} {2}has {3}".format(
                bot.col_pre+bot.irc_colors[color],
                player,
                bot.col_pre+bot.irc_colors["w"],
                color_hand(bot.players[player][1],bot.irc_colors)
                ),
            target)

def check_moves(bot):
    for player in list(bot.players.keys()):
        if len(bot.players[player][2])==0:
            return False
    return True

def color_hand(hand,irc_colors):
    col_pre = "\x03"
    hand=list(hand)
    out = ""
    for letter in hand:
        out += col_pre+irc_colors[letter]+letter
    return out

def tell_move(bot,player):
    if len(bot.players[player][2])==0: 
        bot.say_main("You haven't made any moves!",player)
    elif len(bot.players[player])==3:
        #Non balencing
        move = list(bot.players[player][2])
        move[1] = bot.player_list[move[1]]
        bot.say_main("Your move is: Give {0} to {1}".format(
                move[0],
                color_player(bot,move[1])),
            player)
    elif len(bot.players[player])>3:
        bot.say_main("Your moves are:",player)
        moves = list(bot.players[player][2])
        for x in range(0,len(moves)): 
            moves[x]=list(moves[x])
            moves[x][1] = bot.player_list[moves[x][1]]
            bot.say_main("Give {0} to {1}".format(moves[x][0],moves[x][1]),player)

def find_win(bot):
    for x in range(0,len(bot.player_list)):
        if all(map(lambda y: y in bot.players[bot.player_list[x]][1],bot.goals[x])):
            bot.say_main("{0} Has won! Game reseting, congratz.".format(
                        color_player(bot.player_list[x])))
            return True
    return False

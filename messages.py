from helpers import say_hands,check_moves,tell_move,color_hand
import sys
import modes

def handler(c, e, bot):
    cmdchar = bot.config['misc']['cmdchar']
    admins = bot.config['misc']['admins'].split('/')
    nick = bot.config['network']['nick']

    if e.arguments[0][:len(cmdchar)] != cmdchar:
        return
    if e.source.nick == nick:
        return
    
    cmd = e.arguments[0][len(cmdchar):]
    args = cmd.split(' ')[1:]
    cmd = cmd.split(' ')[0]

    if e.source.nick in admins:

        if cmd == 'test':
            bot.say_main("\x0300Example")
        if cmd == 'debug':
            bot.say_main(str(bot.players),e.source.nick)
            bot.say_main(str(bot.state),e.source.nick)
            bot.say_main(str(bot.goals),e.source.nick)
            bot.say_main(str(bot.colors),e.source.nick)

        if cmd == 'reset':
            modes.hardstop(bot)

        elif cmd == 'talk':
            bot.say_main(" ".join(args))

        elif cmd == 'quit': 
            c.disconnect('Quitted from IRC by %s' % e.source)
            sys.exit(0)

        elif cmd == 'disable':
            if not bot.state == 0:
                c.privmsg(e.target, "Disabling.")
            bot.state = 0

        elif cmd == 'enable' and bot.state == 0:
            bot.state = 1
            c.privmsg(e.target, "Enabling.")

        elif cmd =='nonmovers' and bot.state == 2:
            nonmovers = []
            for player in bot.player_list:
                if not bot.players[player][2]:
                    nonmovers.append(player)
            bot.say_main(", ".join(nonmovers))


        if bot.state == 1:
            if cmd == 'start':
                if len(bot.players.keys())<6:
                    bot.say_main("Too few players")
                elif len(bot.players.keys())>6:
                    bot.say_main("Too many players")
                else:   
                    modes.start(bot)

            if (cmd == 'kick' or cmd == 'game_kick') and len(args)==1:
                if args[0] in bot.players:
                    bot.players.pop(args[0])
                    bot.say_main("Player kicked.")
                else:
                    bot.say_main("Cannot find player.")


    if bot.state == 1:

        if cmd == 'join':
            bot.players[e.source.nick]=0
            bot.say_main(
                "Join recieved. Wait for an admin to start the game.",
                e.source.nick)
            print(bot.players)

        if cmd == 'leave' and e.source.nick in bot.players:
            bot.players.pop(e.source.nick)
            print(bot.players)

        if cmd == 'players':
            player_string = ', '.join(list(bot.players.keys()))
            if e.type == "privmsg":
                bot.say_main('Players joined: ' + player_string,e.source.nick)
            else:
                bot.say_main('Players joined: ' + player_string)

    elif bot.state == 2:
        if cmd == "mymove":
            print(e.source.nick,"wants his moves")
            tell_move(bot,e.source.nick)
        if cmd == "hands":
            say_hands(bot,e.source.nick)

        if cmd == "unmove":
            bot.players[e.source.nick][2]=()

        if cmd == "goal":
            bot.mserv.privmsg(e.source.nick,'Your goal is to obtain "{0}"'.format(
                color_hand(bot.goals[bot.players[e.source.nick][0]],bot.irc_colors)))
        
        if cmd == "move" or cmd == "give":
            if e.type != "privmsg":
                bot.say_main("Moves must be in private message")
            else:
                #args= [color, <player|player color>]
                #Verify color
                if args[0] not in bot.colors:
                    bot.say_main("That isn't a color",e.source.nick)
                    return
                if args[0] not in bot.players[e.source.nick][1]:
                    bot.say_main("You don't have a token of that color",e.source.nick)
                    return
                color = args[0]
                #Verify target
                if args[1] not in bot.players and args[1] not in bot.colors:
                    bot.say_main("You must target a player by name or color",
                                e.source.nick)
                    return
                #Set target
                if args[1] in bot.players: target_id = bot.get_id(args[1])
                else: target_id = bot.colors.index(args[1])
                
                if target_id == bot.get_id(e.source.nick): 
                    bot.say_main("You can't give to yourself!",e.source.nick)
                    return

                if color in bot.players[bot.player_list[target_id]][1]:
                    bot.say_main("That player already has a token of that \
                            color.",
                            e.source.nick)
                    return
                bot.players[e.source.nick][2]=(color,target_id)
                bot.say_main("Move recieved.",e.source.nick)
                if check_moves(bot)==True:
                    modes.do_moves(bot)
    elif bot.state == 3:
        if cmd == "mymove":
            print(e.source.nick,"wants his moves")
            tell_move(bot,e.source.nick)
        if cmd == "hands":
            say_hands(bot,e.source.nick)

        if cmd == "ready":
            if len(bot.players[e.source.nick][3])==4:
                bot.players[e.source.nick][4]=True
                cont=True
                for player in bot.imbal[0]:
                    if not bot.players[player][4]: 
                        cont=False
                        break
                if cont==True: modes.do_imbal(bot)
            else:
                bot.say_main("You still have too many tokens",e.source.nick)
        if cmd == "unready":
            bot.players[e.source.nick][4]=False
            bot.say_main("You are no longer ready",e.source.nick)

        if cmd == "unmove":
            bot.players[e.source.nick][2]=[]

        if cmd == "move" or cmd == "give":
            if e.source.nick not in bot.imbal[0]: 
                bot.say_main("Only players with more than 4 tokens are moving",
                            e.source.nick)
                return

            if e.type != "privmsg":
                bot.say_main("Moves must be in private message")
                return

            #Standard checks
            if args[1] in bot.players:
                target = bot.player_list.index(args[1])
            elif args[1] in bot.colors:
                target = bot.colors.index(args[1])
            else:
                bot.say_main("You must target a player by name or color",
                            e.source.nick)
                return
            if args[0] not in bot.colors:
                bot.say_main("That isn't a color",e.source.nick)
            elif args[0] not in bot.players[e.source.nick][1]:
                bot.say_main("You don't have a token of that color",e.source.nick)
            elif args[1] not in bot.imbal[1]:
                bot.say_main("You may only give to players without a full hand",
                        e.source.nick)
            elif args[0] in bot.players[bot.player_list[target]][1]:
                bot.say_main("You may not give to a play that already has a \
                        token of that color", e.source.nick)
            else:
                move = args
                if move[1] in bot.players:
                    move[1]=bot.player_list.index(move[1])
                else:
                    move[1]=bot.colors.index(args[1])
                print("Entering move checks, move:",move)
                #FSM give me strength 
                #If we've already given away that color
                if move[0] not in bot.players[e.source.nick][3]:
                    for x in range(0,len(bot.players[e.source.nick][2])):
                        if bot.players[e.source.nick][2][x][0]==move[0]:
                            bot.players[e.source.nick][2].pop(x)
                            bot.players[e.source.nick][3]+=move[0]
                            break
                #If we've already given to that person 
                for x in range(0,len(bot.players[e.source.nick][2])):
                    if bot.players[e.source.nick][2][x][1]==move[1]:
                        #Re-add the popped element to the new hand
                        bot.players[e.source.nick][3]+=bot.players[e.source.nick][2][1][0]
                        bot.players[e.source.nick][2].pop(x)
                #If we've already done as many moves as we can
                if len(bot.players[e.source.nick][3])==4:
                    bot.players[e.source.nick][3]+=bot.players[e.source.nick][2][0][0]
                    bot.players[e.source.nick][2].pop(0)
                #We can finally add the move
                print("Adding the move:",move)
                bot.players[e.source.nick][2].append(move)
                newhand = bot.players[e.source.nick][3]
                #Remove the moved color from the new hand
                bot.players[e.source.nick][3] = \
                    newhand[:newhand.index(move[0])]+newhand[newhand.index(move[0])+1:]
    #            print("Finished applying move",bot.players)
                bot.say_main("Move recieved.",e.source.nick)
    if cmd == "help":
        bot.say_main(
        "Welcome to Giveawaybot! I am a bot that administrates the game Giveaway.",
        e.source.nick)
        bot.say_main(
        "Full documentation can be found at http://nickthename.github.io/Giveawaybot/use.html",
        e.source.nick)
        bot.say_main(
        "Basic commands:",
        e.source.nick)
        bot.say_main(
        "!join/!leave - Join or leave a game about to start",
        e.source.nick)
        bot.say_main(
        "!move <first letter of color> <player> - Makes a move",
        e.source.nick)
        bot.say_main(
        "!mymove - Tells you your current move or moves",
        e.source.nick)
        bot.say_main(
        "!ready - Only during rebalancing, readies you.",
        e.source.nick)
        bot.say_main(
        "Other commands include !players, !goal, !hands, and !unmove.",
        e.source.nick)
        bot.say_main(
        "Read the documentation for a full list.",
        e.source.nick)

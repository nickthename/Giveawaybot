from helpers import say_hands,check_moves,tell_move
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
            print(bot.players)

        if cmd == 'leave' and e.source.nick in bot.players:
            bot.players.pop(e.source.nick)
            print(bot.players)

        if cmd == 'players':
            if e.type == "privmsg":
                bot.say_main(bot.player_list,e.source.nick)
            else:
                bot.say_main(bot.player_list)

    elif bot.state == 2:
        if cmd == "mymove":
            print(e.source.nick,"wants his moves")
            tell_move(bot,e.source.nick)
        if cmd == "hands":
            say_hands(bot,e.source.nick)
        
        if cmd == "move":
            if e.type != "privmsg":
                bot.say_main("Moves must be in private message")
            else:
                if args[0] not in bot.colors:
                    bot.say_main("That isn't a color",e.source.nick)
                elif args[0] not in bot.players[e.source.nick][1]:
                    bot.say_main("You don't have that color",e.source.nick)
                elif args[1] not in bot.players and args[1] not in bot.colors:
                    bot.say_main("You must target a player or player's color",
                                e.source.nick)
                else:
                    if args[1] in bot.players:
                        bot.players[e.source.nick][2]=(args[0],bot.players[args[1]][0])
                    else:
                        bot.players[e.source.nick][2]=(args[0],bot.colors.index(args[1]))
                    if check_moves(bot)==True:
                        modes.do_moves(bot)
    elif bot.state == 3:
        if cmd == "mymove":
            print(e.source.nick,"wants his moves")
            tell_move(bot,e.source.nick)
        if cmd == "hands":
            say_hands(bot,e.source.nick)

        if cmd == "ready":
            if len(bot.players[e.source.nick][3])==6:
                bot.players[e.source.nick][4]=True
                cont=True
                for player in bot.imbal[0]:
                    if not bot.players[player][4]: 
                        cont=False
                        break
                if cont==True: modes.do_imbal(bot)
            else:
                bot.say_main("You still have too many colors",e.source.nick)

        if cmd == "move":
            if e.source.nick not in bot.imbal[0]: 
                bot.say_main("Only players with more than 6 colors are moving",
                            e.source.nick)
                return

            if e.type != "privmsg":
                bot.say_main("Moves must be in private message")
                return

            #Standard checks
            if args[0] not in bot.colors:
                bot.say_main("That isn't a color",e.source.nick)
            elif args[0] not in bot.players[e.source.nick][1]:
                bot.say_main("You don't have that color",e.source.nick)
            elif args[1] not in bot.players and args[1] not in bot.colors:
                bot.say_main("You must target a player or player's color",
                            e.source.nick)
            elif args[1] not in bot.imbal[1]:
                bot.say_main("You may only give to players without a full hand",
                        e.source.nick)
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
                if len(bot.players[e.source.nick][3])==6:
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
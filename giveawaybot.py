from irc.bot import ServerSpec, SingleServerIRCBot
import messages
import sys
import configparser
from time import sleep

class Giveawaybot(SingleServerIRCBot):
    #0 - Disabled 1 - Signup 2 - Ingame 3 - Imbalence
    colors = ["r","o","y","g","b","v"]
    goals = []
    state = 1
    imbal = [[],[]] #(too many),(too few)
    players = {}  #player: [<id>,<hand>,<move>]
    player_list = []
    mchan = "" #Main channel for game
    mserv = "" #Main server  for game
    col_pre = "\x03"
    irc_colors = {"r":"04",
                  "o": "07",
                  "y": "08",
                  "g": "03",
                  "b": "02",
                  "v": "06",
                  "w": "00"}

    #def __init__(self, server, nick, nickserv, port=6667):
    def __init__(self, config, port=6667):
        self.config = config
        self.nick = config['network']['nick']
        self.userpass=config['network']['nickserv']
        miscinfo = ServerSpec(config['network']['server'], 
                              port, 
                              config['network']['nickserv'])
        SingleServerIRCBot.__init__(self, [miscinfo], self.nick, self.nick)
    
    def say_main(self, msg, target=""):
        print(msg)
        print(target)
        if target == "":
            target=self.mchan
        self.mserv.privmsg(target,msg)


    def get_version(self):
        return "Giveaway bot. The edgiest bot on irc."

    def on_pubmsg(self, connection, e):
        messages.handler(connection, e, self)
    
    def on_namreply(self, connection,e):
        print(self.channels)
        print(self.channels[self.mchan].modes)
        print(self.channels[self.mchan].voiceddict)

    def on_join(self, connection, e):
        pass

    def on_quit(self, connection, e):
        pass

    def on_part(self, connection, e):
        pass

    def on_privmsg(self, connection, e):
        messages.handler(connection, e, self)

    def on_welcome(self, connection, e):
        self.mchan="#" + config['network']['channel']
        self.mserv=connection
        connection.join(self.mchan)

    def on_connect(self, connection, e):
        self.say_main("IDENTIFY {0} {1}".format(self.nick,self.userpass),
                    "NickServ")

    def on_kick(self, c, e):
        sleep(1)
        c.join(e.target)

if __name__ == '__main__':
    config = configparser.RawConfigParser()
    config.read('config.cfg')
    bot = Giveawaybot(config)
    bot.start()

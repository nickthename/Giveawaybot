import random 

colors = ["r","o","y","g","b","v"]
goals = []

def get_goals(colors=["r","o","y","g","b","v"]):
    return itself([],colors)

def all_o(goals):
    tot=0
    for x in range(0,len(goals)):
        if "o" in goals[x]: tot+=1
    return tot


def ran_colors(num,got_colors,exclude="q"):
    colors=list(got_colors)
    while 1:
        random.shuffle(colors)
        out=""
        for x in range(0,num):
            out=out+colors[x]
        if exclude not in out:
            return out

def legal(goals,colors):
    every=""
    colors=colors[:len(goals)]

    #check to make sure no one is seeking themself

    for x in range(0,len(colors)):
        if colors[x] in goals[x]: 
            return False
        every=every+goals[x] #Make string of all goals

    if len(goals)>1:
        for x in range(0,len(colors)):
            if colors[x] not in every: return False

    return True



def itself(goals,colors):
    if len(goals)==len(colors) and not legal(goals,colors):
#        print("Illegal:",goals)
        return -1

    if len(goals)==len(colors):
        assert legal(goals,colors)
        return goals
    
    for z in range(0,100):
        goals.append(ran_colors(3,colors,colors[len(goals)]))
        got=itself(goals,colors)
        if got != -1:
            return got
        else:
            #print(goals)
            goals.pop(-1)
    return -1


#####Tests#####  
# goals = ["oyg","ygb","gbv","bvr","vro","roy"]
#print(legal(goals,colors))
#print(ran_colors(3,colors))
#for x in range(0,100):
#    got=itself([],colors)
#    assert legal(got,colors)
#    print("winrar!:",got)
#    print(all_o(got))

import tweepy
import json
import array
import random
import time
import datetime
from PIL import Image, ImageDraw, ImageFont
from enum import IntEnum

LOWHOUR = 3
HIGHHOUR = 9
TYPES_OF_ROUND = 3
MAX_INFECT_ROUND = 3
MIN_ITERATION_OPENING = 5
NUM_ALEA_DEAD = 4
CONSUMER_API_KEY = 
CONSUMER_API_KEY_SECRET = 
ACCESS_TOKEN = 
ACCESS_TOKEN_SECRET = 

class Status(IntEnum):
    DEAD = 0
    ILL = 1
    HEALTHY = 2

class StatusEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(type(obj), Status):
            return str(Status[obj].value())
    
    def as_enum(d):
        if "__enum__" in d:
            print("enum k" + str(d))
            name, member = d["__enum__"].split(":")
            return getattr(Status[name], member)
        else:
            print(dict(d))
            return dict(d)
"""
    There are 3 types of round
    0) Infect
    1) Dead
    2) Kill
"""
class Round(IntEnum):
    INFECT = 0
    ILL_DEAD = 1
    KILL = 2

def createGameObject(followers):
    dictionary = dict()
    # Initialices the dictionary with all the followers and 
    for follower in followers:
        dictionary[follower] = Status.HEALTHY
    
    with open("game_objects/followers_game.txt", "w") as json_file:
        json_file.write(json.dumps(dictionary, cls=StatusEncoder))
    return dictionary


def importGameObject():
    with open("game_objects/followers_game.txt", "r") as json_file:
        data = json.load(json_file, object_hook=StatusEncoder.as_enum)
        # print(data)
    dictionary = dict(data)
    return dictionary

def importFollowers():
    followers_file = open("coronafollowers.txt", "r")
    followers = followers_file.read().split(",")
    for i in range(0, len(followers)-1):
        follower = followers[i].strip()
        followers[i] = follower
    return sorted(followers[0:-1], key = lambda s: s.casefold())

def playCoronaGame(dictionary, iteration):
    numInfected = sum(map(lambda x: x == Status.ILL,dictionary.values()))
    numAlive = sum(map(lambda x: (x == Status.ILL) or ( x == Status.HEALTHY),dictionary.values()))
    typeOfRound = None
    print("numInfected " + str(numInfected))
    print("numAlive: " + str(numAlive))
    if(numInfected <= 1):
        typeOfRound = Round.INFECT
    else:
        if(iteration <= MIN_ITERATION_OPENING):
            typeOfRound = Round.INFECT
        elif(numAlive == numInfected):
            typeOfRound = random.randint(1, TYPES_OF_ROUND-1)
        else:
            typeOfRound = random.randint(0, TYPES_OF_ROUND-1)
    # This switch plays the round game
    msg = "Ronda " + str(iteration) + ": "
    msg += switchRoundMode(Round(typeOfRound), dictionary)
    img = printImageCoronaGame(dictionary, iteration)
    print(msg)
    return finalRoundChecker(dictionary)

def playCoronaGameOnline(api,dictionary, iteration):
    numInfected = sum(map(lambda x: x == Status.ILL,dictionary.values()))
    numAlive = sum(map(lambda x: (x == Status.ILL) or ( x == Status.HEALTHY),dictionary.values()))
    typeOfRound = None
    print("numInfected " + str(numInfected))
    print("numAlive: " + str(numAlive))
    if(numInfected <= 1):
        typeOfRound = Round.INFECT
    else:
        if(iteration <= MIN_ITERATION_OPENING):
            typeOfRound = Round.INFECT
        elif(numAlive == numInfected):
            typeOfRound = random.randint(1, TYPES_OF_ROUND-1)
        else:
            typeOfRound = random.randint(0, TYPES_OF_ROUND-1)
    # This switch plays the round game
    msg = switchRoundMode(Round(typeOfRound), dictionary)
    img = printImageCoronaGame(dictionary, iteration)
    api.update_with_media(filename = img, status=msg)   
    return finalRoundChecker(dictionary)

def infectRoundMode(dictionary):
    numInfected = sum(map(lambda x: x == Status.ILL,dictionary.values()))
    numAlive = sum(map(lambda x: x == Status.HEALTHY,dictionary.values()))
    if(numInfected == 0):
        x = random.randint(0, len(dictionary)-1)
        # print(list(dictionary.values()))
        while(list(dictionary.values())[x] != Status.HEALTHY):
            x = random.randint(0, len(dictionary)-1)
        dictionary[list(dictionary.keys())[x]] = Status.ILL
        msg = "PRIMER INFECTADO: El usuario @" + list(dictionary.keys())[x] + " se ha infectado del coronavirus"
    else:
        infecta = random.randint(0, len(dictionary)-1)
        while(list(dictionary.values())[infecta] != Status.ILL):
            infecta = random.randint(0, len(dictionary)-1)
        numInfected = random.randint(1, min(MAX_INFECT_ROUND, numAlive))
        infectados = []
        while(len(infectados) < numInfected):
            infectado = random.randint(0, len(dictionary)-1)
            while(list(dictionary.values())[infectado] != Status.HEALTHY or infectado in infectados):
                infectado = random.randint(0, len(dictionary)-1)
            infectados.append(infectado)
        msg = "El usuario @" + list(dictionary.keys())[infecta] + " ha infectado a: "
        for person in infectados:
            dictionary[list(dictionary.keys())[person]] = Status.ILL
            msg += "@" + list(dictionary.keys())[person] + " "
    return msg


def illDeadRoundMode(dictionary):
    numInfected = sum(map(lambda x: x == Status.ILL,dictionary.values()))
    numDeadThisRandom = random.randint(0, min(NUM_ALEA_DEAD, numInfected-1))
    dead = random.randint(0, len(dictionary)-1)
    while(list(dictionary.values())[dead] != Status.ILL):
        dead = random.randint(0, len(dictionary)-1)
    dictionary[list(dictionary.keys())[dead]] = Status.DEAD
    msg = "El usuario @" + list(dictionary.keys())[dead] + " murió de coronavirus\n"
    if(numDeadThisRandom > 0):
        for count in range(0,numDeadThisRandom-1):
            dead = random.randint(0, len(dictionary)-1)
        if(list(dictionary.values())[dead] == Status.ILL):
            dictionary[list(dictionary.keys())[dead]] = Status.DEAD
            msg += "El usuario @" + list(dictionary.keys())[dead] + " murió de coronavirus\n"
    return msg
    


def killRoundMode(dictionary):
    x = random.randint(0, len(dictionary)-1)
    while(list(dictionary.values())[x] != (Status.ILL or Status.HEALTHY)):
        x = random.randint(0, len(dictionary)-1)
    if(list(dictionary.values())[x] == Status.HEALTHY):
        msg = "El usuario " + list(dictionary.keys())[x] + " se suicidó no podía más con la cuarentena en casa"
    else:
        msg = "Al usuario " + list(dictionary.keys())[x] + " lo mató la desesperación, viendo que el COVID no lo mataba"
    dictionary[list(dictionary.keys())[x]] = Status.DEAD
    return msg

def switchRoundMode(mode, dictionary):
    print("Mode: " + str(mode))
    switcher = {
        Round.INFECT or 0: lambda: infectRoundMode(dictionary),
        Round.ILL_DEAD or 1: lambda: illDeadRoundMode(dictionary),
        Round.KILL or 2: lambda: killRoundMode(dictionary)
    }
    return switcher.get(mode, lambda : "Type of round not valid")()


def finalRoundChecker(dictionary):
    numAlive = sum(map(lambda x: (x == Status.HEALTHY) or (x == Status.ILL),dictionary.values()))
    if(numAlive == 1):
        try:
            champion = list(dictionary.values()).index(Status.HEALTHY)
        except ValueError:
            champion = list(dictionary.values()).index(Status.ILL)
        print("El único superviviente a la pandemia fue: " + list(dictionary.keys())[champion] + " enhorabuena shempions")
    return numAlive == 1

"""
def playGameOnline(api, dictionary):
    x = random.randint(0, len(dictionary)-1)
    while(list(dictionary.values())[x] == False):
        x = random.randint(0, len(dictionary)-1)

    y = random.randint(0, len(dictionary)-1)
    while(list(dictionary.values())[y] == False or x == y):
        y = random.randint(0, len(dictionary)-1)
    
    msg = "El usuario @" + list(dictionary.keys())[x] + " ha asesinado a @" + list(dictionary.keys())[y] + "\r\n"
    img = printImage(dictionary)
    
    dictionary[list(dictionary.keys())[y]] = False
    left = sum(dictionary.values())
    if left > 1 :
        msg = msg + "Quedan " + str(left) + " personas vivas" + "\r\n" + "\r\n" + "#CherraWarBot"
        # print("Quedan " + str(left) + " personas vivas")
    else :
        msg = msg + "Enhorabuena has ganado los juegos de Cherra" + "\r\n" + "\r\n" + "#CherraWarBot"
        # print("Enhorabuena has ganado los juegos de Cherra") 
    api.update_with_media(filename = img, status=msg)   
"""
def printImageCoronaGame(dictionary, iteration):
    imgx = 2200
    imgy = 1100
    seedx = 10
    seedy = 10
    fontsize = 30
    margintop = 40
    marginleft = 350
    marginborder = 40
    
    words = list(dictionary.keys())
    values = list(dictionary.values())

    img = Image.new('RGB', (imgx, imgy), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype('/Library/Fonts/arial.ttf', fontsize)

    for i in range(0, len(words)):
        if values[i] == Status.ILL:
            d.text((seedx,seedy), words[i], font = fnt, fill=(24,101,25))
        elif values[i] == Status.HEALTHY:
            d.text((seedx,seedy), words[i], font = fnt, fill=(0,0,0))
        else:
            d.text((seedx,seedy), words[i], font = fnt, fill=(255,0,0))

        if seedy + fontsize + 30 > imgy :
            seedy = 10 
            seedx = seedx + marginleft
        else:
            seedy = seedy + margintop
                
    img.save('imgs/corona_'+str(iteration)+'.png')
    return 'imgs/corona_'+str(iteration)+'.png'    

def saveDictionary(dictionary, iteration):
    values = list(dictionary.values())
    with open("game_objects/corona_game_"+ str(iteration) +".txt", "w") as json_file:
        json_file.write(json.dumps(dictionary, cls=StatusEncoder))

def importGameRecovery():
    num = input("Introduce el numero de diccionario que quieres recuperar:")
    with open("game_objects/corona_game_"+ num +".txt", "r") as json_file:
        data = json.load(json_file, object_hook=StatusEncoder.as_enum)
        print(data)
    dictionary = dict(data)
    return dictionary, int(num)


def main():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(CONSUMER_API_KEY, CONSUMER_API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    # Create API object
    api = tweepy.API(auth)
    # dictionary = importGameObject()
    # iteration = 0
    # saveDictionary(dictionary, iteration)
    # img = printImageCoronaGame(dictionary, 0)
    # api.update_with_media(filename = img, status="Así van las cosas, recuerden cuanta más gente más dura esto, rulenlo por su grupo de amigos y otra gente para dar más juego #CoronaWarBot")
    dictionary, iteration = importGameRecovery()
    endGame = False
    while(not(endGame)):
        #print(datetime.datetime.now().hour)
        #if(datetime.datetime.now().hour < LOWHOUR or datetime.datetime.now().hour > HIGHHOUR):
        #playGameOnline(api, dictionary)
        endGame = playCoronaGame(dictionary, iteration)
        #printImage(dictionary)
        saveDictionary(dictionary, iteration)
        iteration += 1
        #time.sleep(1800)


if __name__== "__main__":
    main()

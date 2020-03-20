import tweepy
import json
import array
import random
import time
import datetime
from PIL import Image, ImageDraw, ImageFont
from enum import Enum

"""
    Me falta hacer JSON serializable la clase status para exportar
    el diccionario, esto solo hace falta de cara a poder recuperar
    el juego. 
"""

class Status(Enum):
    DEAD = 0
    ILL = 1
    HEALTHY = 2

"""
    There are 3 types of round
    0) Infect
    1) Dead
    2) Kill
"""
class Round(Enum):
    INFECT = 0
    ILL_DEAD = 1
    KILL = 2

LOWHOUR = 2
HIGHHOUR = 9
TYPES_OF_ROUND = 3
MAX_INFECT_ROUND = 3
MIN_ITERATION_OPENING = 5
NUM_ALEA_DEAD = 2

def createGameObject(followers):
    dictionary = dict()
    # Initialices the dictionary with all the followers and 
    for follower in followers:
        dictionary[follower] = Status.HEALTHY
    """
    with open("game_objects/followers_game.txt", "w") as json_file:
        json_file.write(json.dumps(dictionary))
    """
    return dictionary


def importGameObject():
    with open("game_objects/followers_game.txt", "r") as json_file:
        data = json.load(json_file)
        print(data)
    dictionary = dict(data)
    return dictionary

def importFollowers():
    followers_file = open("followers.txt", "r")
    followers = followers_file.read().split(",")
    for i in range(0, len(followers)-1):
        follower = followers[i].strip()
        followers[i] = follower
    return sorted(followers[0:-1], key = lambda s: s.casefold())

def playGame(dictionary):
    x = random.randint(0, len(dictionary)-1)
    while(list(dictionary.values())[x] == False):
        x = random.randint(0, len(dictionary)-1)

    y = random.randint(0, len(dictionary)-1)
    while(list(dictionary.values())[y] == False or x == y):
        y = random.randint(0, len(dictionary)-1)
    print("El usuario @" + list(dictionary.keys())[x] + " ha asesinado a @" + list(dictionary.keys())[y])
    dictionary[list(dictionary.keys())[y]] = False
    left = sum(dictionary.values())
    if left > 1 :
        print("Quedan " + str(left) + " personas vivas")
    else :
        print("Enhorabuena has ganado los juegos de Cherra")

def playCoronaGame(dictionary, iteration):
    numInfected = sum(map(lambda x: x == Status.ILL,dictionary.values()))
    numAlive = sum(map(lambda x: x == (Status.ILL or Status.HEALTHY),dictionary.values()))
    typeOfRound = None
    if(numInfected == 0):
        typeOfRound = Round.INFECT
    else:
        if(iteration <= MIN_ITERATION_OPENING):
            typeOfRound = 0
        elif(numAlive <= numInfected + MIN_ITERATION_OPENING):
            typeOfRound = random.randint(1, TYPES_OF_ROUND-1)
        else:
            typeOfRound = random.randint(0, TYPES_OF_ROUND-1)
    # This switch plays the round game
    switchRoundMode(typeOfRound, dictionary, iteration)
    printImageCoronaGame(dictionary, iteration)
    return finalRoundChecker(dictionary)

def infectRoundMode(dictionary, iteration):
    numInfected = sum(map(lambda x: x == Status.ILL,dictionary.values()))
    if(numInfected == 0):
        x = random.randint(0, len(dictionary)-1)
        print(list(dictionary.values()))
        while(list(dictionary.values())[x] != Status.HEALTHY):
            x = random.randint(0, len(dictionary)-1)
        dictionary[list(dictionary.keys())[x]] = Status.ILL
        print("El usuario @" + list(dictionary.keys())[x] + " se ha infectado del coronavirus")
    else:
        infecta = random.randint(0, len(dictionary)-1)
        while(list(dictionary.values())[infecta] != Status.ILL):
            infecta = random.randint(0, len(dictionary)-1)
        numInfected = random.randint(1, MAX_INFECT_ROUND)
        infectados = []
        while(len(infectados) < numInfected):
            infectado = random.randint(0, len(dictionary)-1)
            while(list(dictionary.values())[infectado] != Status.HEALTHY):
                infectado = random.randint(0, len(dictionary)-1)
            print(infectado)
            infectados.append(infectado)
        print("El usuario @" + list(dictionary.keys())[infecta] + " ha infectado a: ")
        for person in infectados:
            dictionary[list(dictionary.keys())[person]] = Status.ILL
            print("@" + list(dictionary.keys())[person])


def illDeadRoundMode(dictionary, iteration):
    numInfected = sum(map(lambda x: x == Status.ILL,dictionary.values()))
    numDeadThisRandom = random.randint(0, min(NUM_ALEA_DEAD, numInfected-1))
    dead = random.randint(0, len(dictionary)-1)
    while(list(dictionary.values())[dead] != Status.ILL):
        dead = random.randint(0, len(dictionary)-1)
    dictionary[list(dictionary.keys())[dead]] = Status.DEAD
    print("El usuario @" + list(dictionary.keys())[dead] + " murió de coronavirus")
    if(numDeadThisRandom > 0):
        for count in range(0,numDeadThisRandom-1):
            dead = random.randint(0, len(dictionary)-1)
        if(list(dictionary.values())[dead] == Status.ILL):
            dictionary[list(dictionary.keys())[dead]] = Status.DEAD
            print("El usuario @" + list(dictionary.keys())[dead] + " murió de coronavirus")
    


def killRoundMode(dictionary, iteration):
    print("Kill")


def switchRoundMode(mode, dictionary, iteration):
    switcher = {
        0: infectRoundMode(dictionary, iteration),
        1: illDeadRoundMode(dictionary, iteration),
        2: killRoundMode(dictionary, iteration)
    }

def finalRoundChecker(dictionary):
    numAlive = sum(map(lambda x: x == (Status.HEALTHY or Status.ILL),dictionary.values()))
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
        """
        if values[i] == Status.ILL:
            d.text((seedx,seedy), words[i], font = fnt, fill=(0,0,0))
        """
        if values[i] == Status.HEALTHY:
            d.text((seedx,seedy), words[i], font = fnt, fill=(0,0,0))
        """
        else:
            d.text((seedx,seedy), words[i], font = fnt, fill=(255,0,0))
        """
        if seedy + fontsize + 30 > imgy :
            seedy = 10 
            seedx = seedx + marginleft
        else:
            seedy = seedy + margintop
                
    img.save('imgs/corona_'+str(iteration)+'.png')
    return 'imgs/corona_'+str(iteration)+'.png'    

def saveDictionary(dictionary):
    values = list(dictionary.values())
    numberAlive = sum(values)
    with open("game_objects/corona_game_"+ str(numberAlive) +".txt", "w") as json_file:
        json_file.write(json.dumps(dictionary))


def main():
    # followers = createFollowersList("JoserraCasero")
    # Authenticate to Twitter
    # auth = tweepy.OAuthHandler("CONSUMER API KEY", "CONSUMER API KEY SECRET")
    # auth.set_access_token("ACCESS TOKEN", "ACCES TOKEN SECRET")
    # Create API object
    # api = tweepy.API(auth)
    followers = importFollowers()
    dictionary = createGameObject(followers)
    #dictionary = importGameObject()
    #saveDictionary(dictionary)
    iteration = 0
    img = printImageCoronaGame(dictionary, 0)
    endGame = False
    while(not(endGame)):
        #print(datetime.datetime.now().hour)
        #if(datetime.datetime.now().hour < LOWHOUR or datetime.datetime.now().hour > HIGHHOUR):
        #playGameOnline(api, dictionary)
        endGame = playCoronaGame(dictionary, iteration)
        #printImage(dictionary)
        #saveDictionary(dictionary)
        iteration += 1
        #time.sleep(1800)


if __name__== "__main__":
    main()

import tweepy
import json
import array
import random
import time
import datetime
from PIL import Image, ImageDraw, ImageFont

LOWHOUR = 2
HIGHHOUR = 9

# Python program to illustrate the intersection 
# of two lists using set() method 
def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2)) 

def createFollowersList(user_string):
    try:
        followers = []
        for follower in tweepy.Cursor(api.followers, screen_name=user_string).items():
            followers.append(follower.screen_name)
            print(follower.screen_name)
            time.sleep(1)

        following = []
        for follower in tweepy.Cursor(api.friends, screen_name=user_string).items():
            following.append(follower.screen_name)
            print(follower.screen_name)
            time.sleep(1)
        # followers = [friend.screen_name for friend in user.followers]
        # following = [friend.screen_name for friend in user.friends()]
    except tweepy.error.RateLimitError:
        print("Problemas con la api")
        pass
    return intersection(followers, following)

def createGameObject(followers):
    dictionary = dict()
    # Initialices the dictionary with all the followers and 
    for follower in followers:
        dictionary[follower] = True
    with open("game_objects/followers_game.txt", "w") as json_file:
        json_file.write(json.dumps(dictionary))
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

def printImage(dictionary):
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
    numberAlive = sum(values)

    for i in range(0, len(words)):
        if values[i] and numberAlive == 1:
            d.text((seedx,seedy), words[i], font = fnt, fill=(0,255,0))
        elif values[i]:
            d.text((seedx,seedy), words[i], font = fnt, fill=(0,0,0))
        else:
            d.text((seedx,seedy), words[i], font = fnt, fill=(255,0,0))
        if seedy + fontsize + 30 > imgy :
            seedy = 10 
            seedx = seedx + marginleft
        else:
            seedy = seedy + margintop
                
    img.save('imgs/names_'+str(numberAlive)+'.png')
    return 'imgs/names_'+str(numberAlive)+'.png'

def saveDictionary(dictionary):
    values = list(dictionary.values())
    numberAlive = sum(values)
    with open("game_objects/followers_game_"+ str(numberAlive) +".txt", "w") as json_file:
        json_file.write(json.dumps(dictionary))


def main():
    # followers = createFollowersList("JoserraCasero")
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler("CONSUMER API KEY", "CONSUMER API KEY SECRET")
    auth.set_access_token("ACCESS TOKEN", "ACCES TOKEN SECRET")
    # Create API object
    api = tweepy.API(auth)
    followers = importFollowers()
    createGameObject(followers)
    dictionary = importGameObject()
    saveDictionary(dictionary)
    img = printImage(dictionary)
    while(sum(dictionary.values()) > 1):
        print(datetime.datetime.now().hour)
        if(datetime.datetime.now().hour < LOWHOUR or datetime.datetime.now().hour > HIGHHOUR):
            print("Hola")
            playGameOnline(api, dictionary)
            # printImage(dictionary)
            saveDictionary(dictionary)
        time.sleep(1800)

if __name__== "__main__":
    main()

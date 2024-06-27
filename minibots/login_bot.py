from datetime import datetime
from pathlib import Path
import socket, nltk
from py2neo import *


class Login():
    def __init__(self,graph):
        self.graph = graph
        self.con = 0
        self.name = None
        self.digit = self.generateId()
        self.exe = 0 # used if the login is executed more than 2 times
        self.unknown = 0

    def generateId(self):
        botService = self.graph.evaluate("match (betabot:Bot) return (betabot.served)")
        if botService != None:
            botService+=1
        else:
            dataToGet = {
            "name":"Betabot",
            "id":0,
            "served":1
        }
            botService = self.graph.evaluate("create (betabot:Bot {name:$name,id:$id,served:$served}) return (betabot.served)",**dataToGet)
        return botService


    def interrupt(self,userInput):
        print("\nBetabot> Sorry to interrupt you but, can I have your name please?\n")
        print("\nBetabot> One more thing, if you are already a user, enter your name with your id. (i.e. username 1)\n")
        while self.exe < 2:
            self.exe += 1
            userId = self.digit
            name = input("Your input> ").lower()
           # Replacing any apostrophy found in the text
            name = name.replace("'","")
            name = name.replace("`","")
            word_token = nltk.pos_tag(nltk.word_tokenize(name))
            # Took user input in var name, separated it using pos tag, and then the loop below begans
            for word,pos in word_token: # The word is received from the word_token while, the pos var got parts of speech
              #  If the user asks why we want his/her name. If he/she says no we'll return to betabot
                if pos == "WRB":
                    print("\nBetabot> So, that I can know you better, do you want to provide your name?\n")
                    resp = input("Your input> ").lower()
                    if "yes" in resp:
                        self.con=1
                    else:
                        return None
               # if the user enters 'no' or if he/she doesn't want to provide
                elif pos == "DT" or pos == "VBP":
                    name = None
                    return name
               # The condition left are in which he/she has provided the name
                elif pos == "CD":
                    userId = word
                    for wor,post in word_token:
                        if post == "RB" or post == "JJ":
                            name = wor
                            break
                else:
                    if pos == "JJ":
                        name = word
                        print(f"Name is:{name}")
                     
                     
                        
           # If the user wants to enter his/her name after the question 'why', we'll redirect him/her back
            if self.con == 1:
                continue
           # In case of 'None', we'll return control to the betabot
            else:
                if name == None:
                    return self.name
           # If the user has provided the name, we'll send it for storage, with the input the user has provided
                else:
                    self.name = name.lower()
                    self.name = self.getInfo(name,userId)
           # Returning name to betabot, to be used for further referencing      
            return self.name
    def getInfo(self,userName,userId):
        now = datetime.now()
        time = now.strftime("%d-%m-%Y %H:%M:%S")
        if userId == self.digit:
            dataToGet = {
                "userName":userName.title(),
                "userId":userId,
                "sysName":socket.gethostname(),
                "dateCreated":time,
                "status":1,
            }
            episodes = {
                "name":userName+"'s episode",
                "episode":1,
            }
            self.graph.run("create (p:Person:User {name:$userName,id:$userId,sysName:$sysName,dateCreated:$dateCreated,status:$status})",**dataToGet)
            self.graph.run(f"match (p),(betabot) where p.id = $userId and betabot.id = 0 "
                           " merge (betabot)-[:KNOWS]->(p)",userId=userId)
            epmId = self.graph.evaluate("create (epm:EpisodicMemory {name:$name,episode:$episode}) return id(epm)",**episodes)
            epi = self.graph.evaluate("match (p:User),(epm:EpisodicMemory) where p.id = $userId and id(epm) = $epmId "
                           " create (p)-[:hasEpisodes]->(epm) return (epm.episode) ",userId=userId,epmId=epmId)
            comb = [userName,userId,epi,"sp"]
            return comb
        else:
            node = self.graph.evaluate(f"match (p:User) where p.id = {userId}  return (p.id)")
            if node:
                self.graph.run(f"match (p:User) where p.id = {node} set p.status = 1")
                epmId = self.graph.evaluate(f"match (p:User)-[*]->(epm:EpisodicMemory) where p.id = {node} return id(epm)")
                epi = self.graph.evaluate("match (epm:EpisodicMemory) where id(epm) = $epmId return (epm.episode) ",epmId=epmId)
                epi+=1
                self.graph.run("match (epm:EpisodicMemory) where id(epm) = $epmId set epm.episode = $epi",epmId=epmId,epi=epi)
                comb = [userName,userId,epi]
            return comb



def getLogin(userInput,graph):
    l = Login(graph)
    return l.interrupt(userInput)
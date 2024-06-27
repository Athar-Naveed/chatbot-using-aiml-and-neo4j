import aiml,os,socket,statistics,openai
from py2neo import Graph
from glob import glob
from datetime import datetime
from transformers import pipeline
from dotenv import load_dotenv
load_dotenv()
openai_api = os.getenv("openai_api")
# all variables here
name = "Your input "
input_text = ""
graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))
betabot = aiml.Kernel()
for file in glob("aiml/*.aiml"):
    betabot.learn(file)
lambdaCounter = 0
tempCounter = 0
senti_pipe = pipeline(
    "sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment"
)
breaker = 1
# openai.api_key = (
#     openai_api  # make sure to uncomment 'if try in msg' after adding your api key
# )
# ====================


# menu function
def menu(name):
    input_text = input(f"{name}> ")
    return input_text


def timer():
    now = datetime.now()
    time = now.strftime("%H:%M:%S")
    return time


# Enter the main input/output loop
print("\nHi I am Betabot! Your problem solver, my current capabilities are:\n")
print(
    "-> Calculation (write your expression after calculate/solve (i.e. calculate/solve 5+5 )\n-> Basic Chat\n\n\t\tSay Bye before leaving\n"
)
input_text = menu(name)
if input_text != "bye":
    from minibots.login_bot import getLogin

    resp = getLogin(input_text, graph)
    if resp != None:
        if "sp" in resp:
            print(f"I have allocated you id: '{resp[1]}', you can use this for future.")
            name = resp[0].title()
            os.mkdir(f"memory/long_term/{name}_{resp[1]}")
            print(f"Got it: {name}")
        else:
            name = resp[0].title()
            print(f"Welcome back, {name}")
            f = open(f"memory/long_term/{name}_{resp[1]}/episode_{resp[2]}.csv", "w")
            f.close()
    else:
        name = "Your input "
        lambdaCounter = graph.evaluate("match (an:AnonymousMemory) return (an.noUsers)")
        if lambdaCounter:
            lambdaCounter += 1
            f = open(f"memory/short_term/anonymous/episode_{lambdaCounter}.csv", "w")
            f.close()
        else:
            anId = graph.evaluate(
                "create (an:AnonymousMemory {name:$name,noUsers:$noUsers}) return id(an) ",
                name="Anonymous",
                noUsers=1,
            )
            graph.run(
                f"match (an:AnonymousMemory),(b:Bot) where id(an) = {anId} and b.id = 0 "
                "merge (b)-[:hasAnonymousMemory]->(an)"
            )
            lambdaCounter = 1
            dir = "memory/short_term/anonymous"
            if not os.path.exists(dir):
                os.mkdir(f"memory/short_term/anonymous")
    # -----------------------------------
    if resp != None:    #   This part is for known users
        f = open(f"memory/long_term/{name}_{resp[1]}/episode_{resp[2]}.csv", "w")
        emotions = list()
        while breaker:
            betabot.setPredicate("name", name)
            betabot.setBotPredicate("master", "Athar")
            tempCounter += 1
            comb_data = "h" + str(tempCounter)
            f.write(comb_data)
            f.write("\n")
            f.write(input_text)
            f.write("\n")
            comb_emotions = "hemotion" + str(tempCounter)
            f.write(comb_emotions)
            f.write("\n")
            emotions.append(senti_pipe(input_text)[0]["label"])
            f.write(senti_pipe(input_text)[0]["label"])
            f.write("\n")
            comb_time = "htime" + str(tempCounter)
            f.write(comb_time)
            f.write("\n")
            f.write(timer())
            f.write("\n")
            if "calculate" in input_text or "solve" in input_text:
                from minibots.calculator_bot import callCalculate

                msg = str(callCalculate(name, input_text))
            else:
                msg = betabot.respond(input_text, "Betabot")
            # if "try" in msg or "Try" in msg:
            #     msg = openai.Completion.create(engine="text-davinci-003",prompt=input_text,max_tokens=50,temperature=0.7,n=1,stop = None)
            #     msg = msg.choices[0].text.strip()
            print(f"Betabot> {msg}")
            comb_data = "b" + str(tempCounter)
            f.write(comb_data)
            f.write("\n")
            f.write(msg)
            f.write("\n")
            comb_emotions = "bemotion" + str(tempCounter)
            f.write(comb_emotions)
            f.write("\n")
            emotions.append(senti_pipe(msg)[0]["label"])
            f.write(senti_pipe(msg)[0]["label"])
            f.write("\n")
            comb_time = "btime" + str(tempCounter)
            f.write(comb_time)
            f.write("\n")
            f.write(timer())
            f.write("\n")
            input_text = menu(name)
            if input_text == "bye" or input_text == "good bye":
                breaker = 0

        container = list()
        f.close()
        f = open(f"memory/long_term/{name}_{resp[1]}/episode_{resp[2]}.csv", "r")
        store = ""
        for data in f.read():
            if data != "\n":
                store += data
            else:
                container.append(store)
                store = ""
        f.close()
        keyList = list()
        valueList = list()
        for i in range(len(container)):
            if i % 2 == 0:
                keyList.append(container[i])
            else:
                valueList.append(container[i])
        userData = str(dict(zip(keyList, valueList)))
        emotion = statistics.mode(emotions)
        data = {
            "episode": resp[2],
            "ip": socket.gethostbyname(socket.gethostname()),
            "emotion": emotion,
            "message": userData,
        }
        epi = graph.evaluate(
            "create (epi:Episode {episode:$episode,ip:$ip,emotion:$emotion,message:$message}) return id(epi)",
            **data,
        )
        userId = resp[1]
        resp = graph.evaluate(
            f"match (p:User)-[:hasEpisodes]->(epm:EpisodicMemory) where p.id = {userId}  return id(epm) "
        )
        graph.run(f"match (p:User) where p.id = {userId} set p.status = 0")
        graph.run(
            f"match (epi:Episode),(epm:EpisodicMemory) where id(epm) = {resp} and id(epi) = {epi} "
            "merge (epm)-[:has]->(epi) "
        )
        print("Betabot> Bye!!")
    else:       # This part is for unknown users
        if lambdaCounter > 0:
            f = open(f"memory/short_term/anonymous/episode_{lambdaCounter}.csv", "w")
            emotions = list()
            while breaker:
                betabot.setPredicate("name", name)
                betabot.setBotPredicate("master", "Athar")
                tempCounter += 1
                comb_data = "h" + str(tempCounter)
                f.write(comb_data)
                f.write("\n")
                f.write(input_text)
                f.write("\n")
                comb_emotions = "hemotion" + str(tempCounter)
                f.write(comb_emotions)
                f.write("\n")
                emotions.append(senti_pipe(input_text)[0]["label"])
                f.write(senti_pipe(input_text)[0]["label"])
                f.write("\n")
                comb_time = "htime" + str(tempCounter)
                f.write(comb_time)
                f.write("\n")
                f.write(timer())
                f.write("\n")
                if "calculate" in input_text or "solve" in input_text:
                    from minibots.calculator_bot import callCalculate

                    msg = str(callCalculate(name, input_text))
                else:
                    msg = betabot.respond(input_text, "Betabot")
                # if "try" in msg or "Try" in msg:
                #     msg = openai.Completion.create(engine="text-davinci-003",prompt=input_text,max_tokens=50,temperature=0.7,n=1,stop = None)
                print(f"Betabot> {msg}")
                comb_data = "b" + str(tempCounter)
                f.write(comb_data)
                f.write("\n")
                f.write(msg)
                f.write("\n")
                comb_emotions = "bemotion" + str(tempCounter)
                f.write(comb_emotions)
                f.write("\n")
                emotions.append(senti_pipe(msg)[0]["label"])
                f.write(senti_pipe(msg)[0]["label"])
                f.write("\n")
                comb_time = "btime" + str(tempCounter)
                f.write(comb_time)
                f.write("\n")
                f.write(timer())
                f.write("\n")
                input_text = menu(name)
                if input_text == "bye" or input_text == "good bye":
                    breaker = 0

            container = list()
            f.close()
            f = open(f"memory/short_term/anonymous/episode_{lambdaCounter}.csv", "r")
            store = ""
            for data in f.read():
                if data != "\n":
                    store += data
                else:
                    container.append(store)
                    store = ""
            f.close()
            keyList = list()
            valueList = list()
            for i in range(len(container)):
                if i % 2 == 0:
                    keyList.append(container[i])
                else:
                    valueList.append(container[i])
            userData = str(dict(zip(keyList, valueList)))
            emotion = statistics.mode(emotions)
            data = {
                "episode": lambdaCounter,
                "ip": socket.gethostbyname(socket.gethostname()),
                "emotion": emotion,
                "message": userData,
            }
            epi = graph.evaluate(
                "create (epi:AnonymousEpisode:User {episode:$episode,ip:$ip,emotion:$emotion,message:$message}) return id(epi)",
                **data,
            )
            graph.run(
                f"match (epi:AnonymousEpisode),(anony:AnonymousMemory) where id(epi) = {epi} "
                "merge (anony)-[:hasAnonymousEpisode]->(epi) "
            )
            print("Betabot> Bye!!")


else:
    print("Betabot> Bye!!")

#!/usr/bin/env python

import os
import sys
import random
from threading import Thread
import threading
import time

try:
    import Queue
except:
    import queue as Queue

# Parameters
viability = {"AA": 0.6, "Aa": 0.6, "aa": 0.3}
fertility = {"AA": 0.6, "Aa": 0.6, "aa": 0.3}
cycles = 20
tests = 200
popLimit = 1000
minProgeny = 0
maxProgeny = 1
threadNum = 8
nice = 20


def cliInterpeter():
    global threadNum

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "-t":
            threadNum = sys.argv[i+1]

        i += 1


def popInit(number, MODE):
    populationList = []
    if MODE == "uniform":
        i = 0
        while i < number:
                individum = []
                for j in range(0, 2):
                    seedBL = os.urandom(10)
                    random.seed(seedBL)
                    individum.append(int(random.random()*2))

                populationList.append(individum)
                i += 1

    elif MODE == "mutation":
        i = 0
        while i < number:
            individum = [0, 0]
            populationList.append(individum)
            i += 1

        seedBL = os.urandom(10)
        random.seed(seedBL)
        randomIndividum = random.randint(0, len(populationList)-1)
        randomLocus = random.randint(0, 1)
        populationList[randomIndividum][randomLocus] = 1

    return populationList


def theUnforgivingWorld(popultionList, MODE):
    global popLimit
    global fertility
    global viability

    worldEffect = len(popultionList)/float(popLimit)
    i = 0
    while i < len(popultionList):
        seedBL = os.urandom(10)
        random.seed(seedBL)
        deathChance = random.random()
        if MODE == "env":
                deathChance = deathChance + ((1-deathChance) * worldEffect)

        if popultionList[i][0] == 1 and popultionList[i][1] == 1:
            if deathChance > viability["AA"]:
                del popultionList[i]
        elif popultionList[i][0] == 0 and popultionList[i][1] == 0:
            if deathChance > viability["aa"]:
                del popultionList[i]
        else:
            if deathChance > viability["Aa"]:
                del popultionList[i]

        i += 1


def theWonderOfLife(popultionList, matches):
    global popLimit
    global fertility
    global maxProgeny
    global minProgeny

    i = 0
    while i < len(matches):
        progenyNum = random.randint(minProgeny, maxProgeny)
        j = 0
        while j < progenyNum:
            newborn = []
            for index in matches[i]:
                seedBL = os.urandom(10)
                random.seed(seedBL)
                choice = random.randint(0, 1)
                newborn.append((popultionList[index][choice]))

            popultionList.append(newborn)
            j += 1
        i += 1


def analyzer(popultionList):
    global stats

    # Purge stats
    stats = {"Npop": 0, "NAA": 0, "NAa": 0, "Naa": 0, "NA": 0, "Na": 0}

    stats["Npop"] = len(popultionList)
    for individum in popultionList:
        if individum[0] == 1 and individum[1] == 1:
            stats["NAA"] += 1
        elif individum[0] == 0 and individum[1] == 0:
            stats["Naa"] += 1
        else:
            stats["NAa"] += 1

    stats["NA"] = 2*stats["NAA"]+stats["NAa"]
    stats["Na"] = 2*stats["Naa"]+stats["NAa"]


def matchmaker(popultionList):
    matches = []
    indices = list(range(0, len(popultionList)))
    while len(indices) > 1:
        seedBL = os.urandom(10)
        random.seed(seedBL)
        pair = random.sample(indices, 2)
        for index in pair:
            indices.remove(index)

        matches.append(pair)

    return matches


def simulation(threadNumber):
    global survivedNumQ
    stats = {"Npop": 0, "NAA": 0, "NAa": 0, "Naa": 0, "NA": 0, "Na": 0}
    popultionList = popInit(1000, "mutation")
    c = 0
    while c < cycles:
        theUnforgivingWorld(popultionList, "env")
        theWonderOfLife(popultionList, matchmaker(popultionList))
        analyzer(popultionList)
        # print(c)
        c += 1

    if stats["NA"] > 0:
        survivedNumQ.put(1)
        print(stats)
    # print(stats["Npop"])
    stats = {"Npop": 0, "NAA": 0, "NAa": 0, "Naa": 0, "NA": 0, "Na": 0}
    popultionList = []
    # print("Thread number: " + str(threadNumber))


cliInterpeter()
print(threadNum)
os.nice(nice)
startTime = time.time()
stats = {"Npop": 0, "NAA": 0, "NAa": 0, "Naa": 0, "NA": 0, "Na": 0}

survivedNumQ = Queue.Queue()
trial = 0
while trial < tests:
    t = Thread(target=simulation, args=(trial,))
    t.start()
    # print(threading.activeCount())
    while threading.activeCount() == threadNum:
        time.sleep(0.01)

    trial += 1

while threading.activeCount() != 1:
    # print(threading.activeCount())
    time.sleep(0.1)

print("Elapsed time: " + str(time.time() - startTime))

"""
Licensed under GPL3 by 'selfbondageforum.de' user MxZ.
"""

import pickle
import random
import struct
import sys
from time import time, sleep
from math import ceil
from os import remove
from hashlib import shake_256


largeDigits = {
    "0": [
        " 000000 ",
        " 0    0 ",
        " 0    0 ",
        " 0    0 ",
        " 000000 ",
    ],
    "1": [
        "    1   ",
        "  1 1   ",
        "    1   ",
        "    1   ",
        " 111111 ",
    ],
    "2": [
        " 222222 ",
        "      2 ",
        " 222222 ",
        " 2      ",
        " 222222 ",
    ],
    "3": [
        " 333333 ",
        "      3 ",
        " 333333 ",
        "      3 ",
        " 333333 ",
    ],
    "4": [
        " 4    4 ",
        " 4    4 ",
        " 444444 ",
        "      4 ",
        "      4 ",
    ],
    "5": [
        " 555555 ",
        " 5      ",
        " 555555 ",
        "      5 ",
        " 555555 ",
    ],
    "6": [
        " 666666 ",
        " 6      ",
        " 666666 ",
        " 6    6 ",
        " 666666 ",
    ],
    "7": [
        " 777777 ",
        "      7 ",
        "      7 ",
        "      7 ",
        "      7 ",
    ],
    "8": [
        " 888888 ",
        " 8    8 ",
        " 888888 ",
        " 8    8 ",
        " 888888 ",
    ],
    "9": [
        " 999999 ",
        " 9    9 ",
        " 999999 ",
        "      9 ",
        " 999999 ",
    ],
    ":": [
        "        ",
        "   []   ",
        "        ",
        "   []   ",
        "        ",
    ],
    "T": [
        " TTTTTT ",
        "   TT   ",
        "   TT   ",
        "   TT   ",
        "   TT   ",
    ],
}


class Status:
    def __init__(self):
        self.code = []
        self.codeLen = 0
        self.duration = 0.0
        self.starTime = 0.0
        self.showTimer = False


def printLarge(toPrint):
    print("")
    print("")
    printList = [largeDigits[str(s)] for s in toPrint]
    for lines in zip(*printList):
        for digitLine in lines:
            print(digitLine, end="")
        print("")
    print("")
    print("")


def doSequence(codeList):
    remainingDigits = [i for i in range(len(codeList))]

    lst = [i + 10 * (i <= 5) for i in codeList]

    done = False
    while not done:
        if len(remainingDigits):
            digit = remainingDigits[random.randrange(0, len(remainingDigits))]
            if lst[digit]:
                value = random.randint(1, min(lst[digit] // 2 + 1, 4))
                input("Drehe " + str(digit + 1) + " um " + str(value) + " Stellen. ")
                lst[digit] -= value
            else:
                remainingDigits.remove(digit)
        else:
            done = True


def crypt(data: bytes) -> bytes:
    h = shake_256()
    with open(sys.argv[0], "rb") as f:
        h.update(f.read())
    key = h.digest(len(data))
    result = b""
    for i, b in enumerate(data):
        result += struct.pack("B", b ^ key[i])
    return result


if __name__ == "__main__":
    random.seed()

    pickleFile = "data.p"
    fileAvailable = True

    try:
        with open(pickleFile, "rb") as f:
            pickleBytes = f.read()
        pickleBytes = crypt(pickleBytes)
        status = pickle.loads(pickleBytes)
    except:
        fileAvailable = False

    if not fileAvailable:
        status = Status()

        while status.codeLen < 1 or status.codeLen > 8:
            try:
                status.codeLen = int(input("Code Stellen (1-8): "))
            except:
                pass

        days = -1
        while days < 0 or days > 48:
            try:
                days = int(input("Tage (0-48):    "))
            except:
                pass

        hours = -1
        while hours < 0 or hours > 23:
            try:
                hours = int(input("Stunden (0-23): "))
            except:
                pass

        mins = -1
        while mins < 0 or mins > 59:
            try:
                mins = int(input("Minuten (0-59): "))
            except:
                pass

        showTimer = "doit"
        while showTimer not in "1yj0n":
            try:
                showTimer = str(input("Verbleibende Zeit anzeigen (J/N): ")).lower()
            except:
                pass
        if showTimer in "0n":
            status.showTimer = False
        else:
            status.showTimer = True

        status.duration = (((days * 24) + hours) * 60 + mins) * 60

        for i in range(status.codeLen):
            status.code.append(random.randint(0, 9))

        inversCode = [10 - i for i in status.code]

        input("Schloss in Position für neuen Code bringen. ")
        doSequence(status.code)
        input("Schloss schliessen und fortfahren. ")
        doSequence(status.code)

        status.startTime = time()
        pickleBytes = pickle.dumps(status)
        check = hash(pickleBytes)
        pickleBytes = crypt(pickleBytes)
        with open(pickleFile, "wb") as f:
            f.write(pickleBytes)
        with open(pickleFile, "rb") as f:
            check2 = hash(crypt(f.read()))
        if check2 != check:
            ack = ""
            while ack.lower() != "ok":
                ack = input("Abspeichern der Session-Daten hat nicht geklappt. Hier ist zur Sicherheit der Code: {}. "
                            "OK eingeben zum beenden. ".format(status.code))
            exit()
        sleep(1)

    timeDiff = 0
    timerShownTime = 0
    while (time() - status.startTime) < status.duration:
        if status.showTimer and (time() - timerShownTime) >= 60:
            timerShownTime = time()
            timeDiff = status.duration - (time() - status.startTime)
            days = int(timeDiff / 60 / 60 / 24)
            hours = int(timeDiff / 60 / 60 % 24)
            mins = int(ceil(timeDiff / 60 % 60))
            printLarge("{:02}:{:02}:{:02}".format(days, hours, mins))
        else:
            sleep(1)
    printLarge(status.code)

    done = "nope"
    while done.lower() != "ok":
        done = input("Schloss entsperren. Code wird anschließend gelöscht (OK tippen zum Löschen) ")
    remove(pickleFile)
    print("Gelöscht. Bereit für eine neue Runde!")

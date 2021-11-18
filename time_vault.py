"""
Licensed under GPL3 by 'selfbondageforum.de' user MxZ.
"""
import sys
import traceback
import pickle
import random
import struct
from time import time, sleep
from math import ceil
from os import remove
from hashlib import shake_256
from dataclasses import dataclass, field
from typing import List

DEBUG = False

PICKLE_FILENAME = "data_{}.p"

LARGE_DIGITS = {
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


@dataclass
class Status:
    code: List[int] = field(default_factory=list)
    codeLen: int = 0
    duration: float = 0.0
    starTime: float = 0.0
    showTimer: bool = False


def printLarge(toPrint):
    print("")
    print("")
    printList = [LARGE_DIGITS[str(s)] for s in toPrint]
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


class Lock:
    def __init__(self, schloss_number: str):
        self.status: Status = None
        self.schloss_nummer = schloss_number
        self.filename = PICKLE_FILENAME.replace("{}", schloss_number)
        self.status = self._load(self.filename)

    def __str__(self) -> str:
        return f"Filename: {self.filename} - {self.status}"

    def _load(self, filename: str) -> Status:
        try:
            with open(filename, "rb") as f:
                pickleBytes = f.read()
            pickleBytes = crypt(pickleBytes)
            status = pickle.loads(pickleBytes)
            return status
        except:
            if DEBUG:
                print(f"Fehler beim Datei laden: {filename}")
                print(sys.exc_info()[0])
                print(traceback.format_exc())
        return None

    def _save(self, filename: str) -> bool:
        pickleBytes = pickle.dumps(self.status)
        check = hash(pickleBytes)
        pickleBytes = crypt(pickleBytes)

        with open(filename, "wb") as f:
            f.write(pickleBytes)
        with open(filename, "rb") as f:
            check2 = hash(crypt(f.read()))

        if check2 != check:
            ack = ""
            while ack.lower() != "ok":
                ack = input(
                    f"Abspeichern der Session-Daten hat nicht geklappt. Hier ist zur Sicherheit der Code: {self.status.code}.\n"
                    "OK eingeben zum beenden. "
                )
            exit()

    def _create(self) -> None:
        if self.status is None:
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
            for _ in range(status.codeLen):
                status.code.append(random.randint(0, 9))

            self.status = status

    def _prepare(self) -> None:
        inversCode = [10 - i for i in self.status.code]

        input("Schloss in Position für neuen Code bringen. ")
        doSequence(self.status.code)
        input("Schloss schliessen und fortfahren. ")
        doSequence(inversCode)

        self.status.startTime = time()
        self._save(self.filename)

    def run(self) -> None:
        if self.status is None:
            self._create()
            self._prepare()
            if DEBUG:
                print(self.status)

        timeDiff = 0
        timerShownTime = 0
        try:
            while (time() - self.status.startTime) < self.status.duration:
                if self.status.showTimer and (time() - timerShownTime) >= 60:
                    timerShownTime = time()
                    timeDiff = self.status.duration - (time() - self.status.startTime)
                    days = int(timeDiff / 60 / 60 / 24)
                    hours = int(timeDiff / 60 / 60 % 24)
                    mins = int(ceil(timeDiff / 60 % 60))
                    printLarge(f"{days:02}:{hours:02}:{mins:02}")
                else:
                    sleep(1)
        except KeyboardInterrupt:
            print("Skript wird aus Userwunsch gestoppt")
            sys.exit(0)

        printLarge(self.status.code)

        done = "nope"
        while done.lower() != "ok":
            done = input(
                "Schloss entsperren. Code wird anschließend gelöscht (OK tippen zum Löschen) "
            )
        remove(self.filename)
        print("Gelöscht. Bereit für eine neue Runde!")


def main():
    random.seed()

    lock_number = input("Bitte gib die Schlossnummer ein: ")
    if lock_number == "":
        lock_number = "0"

    lock = Lock(lock_number)
    if DEBUG:
        print(lock)

    lock.run()


if __name__ == "__main__":
    main()

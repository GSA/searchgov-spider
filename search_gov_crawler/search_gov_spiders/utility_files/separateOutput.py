# script to break up scrapyOutput into max size (3.9 MB)
from pathlib import Path
import os


def separateOutput(scrapyOutputPath, maxFileSize):
    currentFileSize = 0
    fileNumber = 1
    scrapyOutput = open(scrapyOutputPath, "r")
    shortFile = open("all-links.csv", "w")

    for line in scrapyOutput:
        if currentFileSize + len(line) > maxFileSize:
            shortFile.close()
            newName = "all-links" + str(fileNumber) + ".csv"
            os.rename("all-links.csv", newName)
            fileNumber = fileNumber + 1
            shortFile = open("all-links.csv", "w")
            currentFileSize = 0

        shortFile.write(line)
        currentFileSize = currentFileSize + len(line)

    shortFile.close()
    newName = "all-links" + str(fileNumber) + ".csv"
    os.rename("all-links.csv", newName)
    scrapyOutput.close()

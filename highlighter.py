'''
    File name: main.py
    Python Version: 3.6
'''

import csv
import re
import argparse
import time
import datetime

import logging

#https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution
start_time = time.time()

now = datetime.datetime.now()
aCurrentDateTimeString = f'{now:%B_%d_%Y_%H_%M_%S}'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler

handler = logging.FileHandler('Highlighter_'+aCurrentDateTimeString+'.log',mode='w')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

parser = argparse.ArgumentParser(description='Look for some keyword in csv file and highlight them.')

# https://stackoverflow.com/questions/15753701/argparse-option-for-passing-a-list-as-option
# This is the correct way to handle accepting multiple arguments.
# '+' == 1 or more.
# '*' == 0 or more.
# '?' == 0 or 1.
# An int is an explicit number of arguments to accept.
parser.add_argument('--FilePathListToProcess', nargs='+')

parser.add_argument('--termToHighlightFilePath', help='File with term to hightlight. One term by line')

args = parser.parse_args()

def highlight(aPost,iTermToHighlight, iTermToHighlightRegex):
    aTags=[]
    aHighlightMatch=iTermToHighlightRegex.search(aPost["content"])
    if(aHighlightMatch):
        logger.debug("This post ID " + aPost["post_uuid"] +  " was highlighted with : " + str(aHighlightMatch.group()))
        aTags.append(aHighlightMatch.group())
    return aTags

def filterFile(aFilename):
    aTermToHighlight=[]
    aTermToHighlightAsRegexString=""

    with open(args.termToHighlightFilePath, encoding="utf8") as aTermToHighlightRaw:
        for aOneLine in aTermToHighlightRaw:
            aTermToHighlight.append(aOneLine.strip())
        aTermToHighlightAsRegexString='|'.join(aTermToHighlight)

    logger.info("aTermToHighlight: " + str(aTermToHighlight))
    aTermToHighlightAsRegex = re.compile(aTermToHighlightAsRegexString)
    logger.info("aTermToHighlightAsRegexString: " + str(aTermToHighlightAsRegexString))
    logger.info("aTermToHighlightAsRegex: " + str(aTermToHighlightAsRegex))

    with open(aFilename, encoding="utf8") as f:
        #CSV header: Anonymous Link,ww_uuid,post_uuid,content,Word Count
        reader = csv.DictReader(f)

        #Also open a file to write data
        with open(aFilename + "_output"+aCurrentDateTimeString+".csv","w", encoding="utf8",newline='') as filteredFile:
            fieldnames = reader.fieldnames + ["TAGS"]
            writer = csv.DictWriter(filteredFile, fieldnames=fieldnames)
            writer.writeheader()

            for aOneEntry in reader:
                #print("Working on: ", aOneEntry)
                #print("Content to clean: ", aOneEntry["content"])
                aTags = highlight(aOneEntry,aTermToHighlight,aTermToHighlightAsRegex)
                aOneEntry["TAGS"]= '-'.join(aTags)
                writer.writerow(aOneEntry)
                


# MAIN

for aOneFile in args.FilePathListToProcess:
    logger.info("Current file: " + str(aOneFile))
    filterFile(aOneFile)

logger.info("Ending in " + str((time.time() - start_time)) + " ms")

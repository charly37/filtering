'''
    File name: main.py
    Python Version: 3.6
'''

import csv
import re
import argparse
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler

handler = logging.FileHandler('Filtering.log',mode='w')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

#https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution
start_time = time.time()

parser = argparse.ArgumentParser(description='Look for some email address or phone number in csv file.')
parser.add_argument('--filter', action='store_true')
parser.add_argument('--tag', action='store_true')

# https://stackoverflow.com/questions/15753701/argparse-option-for-passing-a-list-as-option
# This is the correct way to handle accepting multiple arguments.
# '+' == 1 or more.
# '*' == 0 or more.
# '?' == 0 or 1.
# An int is an explicit number of arguments to accept.
parser.add_argument('--filelist', nargs='+')

args = parser.parse_args()


def filtering(aPost,iMatchInfo):
    #https://stackoverflow.com/questions/3868753/find-phone-numbers-in-python-script
    # or maybe https://stackoverflow.com/questions/123559/a-comprehensive-regex-for-phone-number-validation
    aPhoneRegexAsString=r"(\d{3}[-\.\s]\d{3}[-\.\s]\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]\d{4}|\d{3}[-\.\s]\d{4})"
    aPhoneNumberRegex = re.compile(aPhoneRegexAsString)
    aPhoneNumberMatch=aPhoneNumberRegex.search(aPost["content"])
    if(aPhoneNumberMatch):
        #logger.info("This post ID " + aPost["post_uuid"] +  " need to be filter due to phone number: " + str(aPhoneNumberMatch.group()))
        #print("This post ID", aPost["post_uuid"], "need to be filter due to phone number:", aPhoneNumberMatch.group(), "with post content:", aPost["content"])
        iMatchInfo[0]=iMatchInfo[0]+1
        if (args.filter):
            aPost["content"]=re.sub(aPhoneRegexAsString,'___WARNINGPHONE___',aPost["content"])
    #https://stackoverflow.com/questions/17681670/extract-email-sub-strings-from-large-document
    aEmailRegexAsString=r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    aEmailAdressRegex = re.compile(aEmailRegexAsString)
    aEmailMatch=aEmailAdressRegex.search(aPost["content"])
    if(aEmailMatch):
        #logger.info("This post ID " + str(aPost["post_uuid"]) + " need to be filter due to email: " + str(aEmailMatch.group()))
        iMatchInfo[1]=iMatchInfo[1]+1
        if (args.filter):
            aPost["content"]=re.sub(aEmailRegexAsString,"___WARNINGEMAILADD___",aPost["content"])
    return aPost

def tagging(aPost):
    aTags=[]
    aRsvpRegex = re.compile(r"rsvp|come visit|come join|Head down|Orientation|Come on down|Head up to|Join us|Visit us|Lunch & learn|Workshop|Event|Gala|party")
    aRsvpMatch=aRsvpRegex.search(aPost["content"],re.IGNORECASE)
    if(aRsvpMatch):
        logger.info("This post ID " + aPost["post_uuid"] +  " may be a RESA because of matching keyword: " + str(aRsvpMatch.group())+ " with full post content: " + str(aPost["content"]))
        aTags.append("RSVP")

    aRequestHelpRegex = re.compile(r"hiring|how do I|anyone good at|can anyone recommend|any recommendations|what’s the best way|referral|refer")
    aRequestHelpMatch=aRequestHelpRegex.search(aPost["content"],re.IGNORECASE)
    if(aRequestHelpMatch):
        logger.info("This post ID " + aPost["post_uuid"] +  " may be a Help Request because of matching keyword: " + str(aRequestHelpMatch.group())+ " with full post content: " + str(aPost["content"]))
        aTags.append("HELP")

    aOtherRegex = re.compile(r"did anyone find|lost")
    aOtherMatch=aOtherRegex.search(aPost["content"],re.IGNORECASE)
    if(aOtherMatch):
        logger.info("This post ID " + aPost["post_uuid"] +  " may be a Other because of matching keyword: " + str(aOtherMatch.group())+ " with full post content: " + str(aPost["content"]))
        aTags.append("OTHER")

    aExchangeItemRegex = re.compile(r"charger|cable|borrow|lend me|loan me|for rent|trade me|trade for")
    aExchangeItemMatch=aExchangeItemRegex.search(aPost["content"],re.IGNORECASE)
    if(aExchangeItemMatch):
        logger.info("This post ID " + aPost["post_uuid"] +  " may be a Exchange Item because of matching keyword: " + str(aExchangeItemMatch.group())+ " with full post content: " + str(aPost["content"]))
        aTags.append("EXCHANGE")

    aPromoteRegex = re.compile(r"Discount|%")
    aPromoteMatch=aPromoteRegex.search(aPost["content"],re.IGNORECASE)
    if(aPromoteMatch):
        logger.info("This post ID " + aPost["post_uuid"] +  " may be a Promote because of matching keyword: " + str(aPromoteMatch.group())+ " with full post content: " + str(aPost["content"]))
        aTags.append("PROMO")
    return aTags

def filterFile(aFilename):
    with open(aFilename, encoding="utf8") as f:
        #CSV header: Anonymous Link,ww_uuid,post_uuid,content,Word Count
        reader = csv.DictReader(f)
        #number of phone and email
        aMatchInfo=[0,0]

        #Also open a file to write data
        with open(aFilename + "_output.csv","w", encoding="utf8",newline='') as filteredFile:
            fieldnames = reader.fieldnames + ["TAGS"]
            writer = csv.DictWriter(filteredFile, fieldnames=fieldnames)
            writer.writeheader()

            for aOneEntry in reader:
                #print("Working on: ", aOneEntry)
                #print("Content to clean: ", aOneEntry["content"])
                filtering(aOneEntry,aMatchInfo)
                if (args.tag):
                    aTags = tagging(aOneEntry)
                    aOneEntry["TAGS"]= '-'.join(aTags)
                writer.writerow(aOneEntry)
                
        logger.info("We filter " + str(aMatchInfo[0]) + " phone numbers and " + str(aMatchInfo[1]) + " emails.")


if __name__== "__main__":
    #dump some options
    if (args.filter):
        logger.info("Warning i will filter")
    logger.info("Going to work on files:" + str(args.filelist))

    for aOneFile in args.filelist:
        logger.info("Current file: " + str(aOneFile))
        filterFile(aOneFile)
    logger.info("Ending in " + str((time.time() - start_time)) + " ms")



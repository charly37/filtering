'''
    File name: main.py
    Python Version: 3.6
'''

import csv
import re
import argparse
import time

#https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution
start_time = time.time()

parser = argparse.ArgumentParser(description='Look for some email address or phone number in csv file.')
parser.add_argument('--filter', action='store_true')

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
    aPhoneNumberRegex = re.compile(r"\d{3}\d{3}\d{4}")
    aPhoneNumberMatch=aPhoneNumberRegex.search(aPost["content"])
    if(aPhoneNumberMatch):
        print("This post ID", aPost["post_uuid"], "need to be filter due to phone number:", aPhoneNumberMatch.group())
        #print("This post ID", aPost["post_uuid"], "need to be filter due to phone number:", aPhoneNumberMatch.group(), "with post content:", aPost["content"])
        iMatchInfo[0]=iMatchInfo[0]+1
        if (args.filter):
            aPost["content"]=re.sub(r"(\d{3}\d{3}\d{4})",r'___WARNINGPHONE:\1___',aPost["content"])
    #https://stackoverflow.com/questions/17681670/extract-email-sub-strings-from-large-document
    aEmailAdressRegex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    aEmailMatch=aEmailAdressRegex.search(aPost["content"])
    if(aEmailMatch):
        #print("This post ID", aPost["post_uuid"], "need to be filter due to email:", aEmailMatch.group(), "with post content:", aPost["content"])
        iMatchInfo[1]=iMatchInfo[1]+1
        if (args.filter):
            aPost["content"]=re.sub(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",r"___WARNINGEMAILADD:\1___",aPost["content"])
    return aPost

def filterFile(aFilename):
    with open(aFilename, encoding="utf8") as f:
        #CSV header: Anonymous Link,ww_uuid,post_uuid,content,Word Count
        reader = csv.DictReader(f)
        aNbEmailPost=0
        aNbPhoneNumberPost=0
        #number of phone and email
        aMatchInfo=[0,0]

        #Also open a file to write data
        with open(aFilename + "_output.csv","w", encoding="utf8",newline='') as filteredFile:
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(filteredFile, fieldnames=fieldnames)
            writer.writeheader()

            for aOneEntry in reader:
                #print("Working on: ", aOneEntry)
                #print("Content to clean: ", aOneEntry["content"])
                filtering(aOneEntry,aMatchInfo)
                writer.writerow(aOneEntry)
        print("info: ", str(aMatchInfo))

print("Ending in ", (time.time() - start_time),  " ms")


if (args.filter):
    print("Warning i will filter")

print("Going to work on files:", str(args.filelist))
for aOneFile in args.filelist:
    print("Current file:", aOneFile)
    filterFile(aOneFile)




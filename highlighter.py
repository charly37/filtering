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

import unittest

class Tag(object):
    def __init__(self, iTag, iTerms):
        self.tag = iTag
        self.searchTerms = iTerms
        self.searchRegex = None
        self.setRegexFromSearchTerms()

    def setRegexFromSearchTerms(self):
        aListWordsUpdated = [r"\b(?i)" + aOneOriginalWord + r"\b" for aOneOriginalWord in self.searchTerms]
        aTermToHighlightAsRegexString='|'.join(aListWordsUpdated )
        self.searchRegex = re.compile(aTermToHighlightAsRegexString)

    def prettyPrint(self):
        aRetStr = ""
        aRetStr = aRetStr + "The Tag: \"" + self.tag + "\""
        aRetStr = aRetStr + " will match searchTerms: \"" + str('","'.join(self.searchTerms)) + "\""
        aRetStr = aRetStr + " and use regex: \"" + str(self.searchRegex) + "\""
        return aRetStr


class MyTest(unittest.TestCase):

    def test_createRegexStr(self):
        aFakeTagFromCsv={"String to look for (seperated by ; )":"aaa;bbb;ccc","Tag to add on the post":"aaa"}
        aFakeTagObj = Tag(aFakeTagFromCsv["Tag to add on the post"], aFakeTagFromCsv["String to look for (seperated by ; )"].split(';'))
        aRegexResult = re.compile(r"\b(?i)aaa\b|\b(?i)bbb\b|\b(?i)ccc\b")
        self.assertEqual(aFakeTagObj.searchRegex, aRegexResult)

    def test_nominal(self):
        aFakePost={"post_uuid":"1","content":"test aaa test bbb test"}

        aFakeTagFromCsv={"String to look for (seperated by ; )":"aaa;aa aa","Tag to add on the post":"AAA"}
        aFakeTagObj = Tag(aFakeTagFromCsv["Tag to add on the post"], aFakeTagFromCsv["String to look for (seperated by ; )"].split(';'))
        aSmartTagList=[aFakeTagObj]

        aTagsRes = smartHighlight(aFakePost,aSmartTagList)

        #https://stackoverflow.com/questions/12813633/how-to-assert-two-list-contain-the-same-elements-in-python/35095881#35095881
        self.assertEqual(aTagsRes,["AAA"])

    def test_case_sensitive(self):
        aFakePost={"post_uuid":"1","content":"test eee test bbb test AAa test"}

        aFakeTagFromCsv={"String to look for (seperated by ; )":"aaa;aa aa","Tag to add on the post":"AAA"}
        aFakeTagObj = Tag(aFakeTagFromCsv["Tag to add on the post"], aFakeTagFromCsv["String to look for (seperated by ; )"].split(';'))
        aSmartTagList=[aFakeTagObj]

        aTagsRes = smartHighlight(aFakePost,aSmartTagList)

        self.assertEqual(aTagsRes,["AAA"])

    def test_several_tags(self):
        aFakePost={"post_uuid":"1","content":"test eee test bbb test AAa test"}

        aFakeTagFromCsv={"String to look for (seperated by ; )":"aaa;aa aa","Tag to add on the post":"AAA"}
        aFakeTagObj = Tag(aFakeTagFromCsv["Tag to add on the post"], aFakeTagFromCsv["String to look for (seperated by ; )"].split(';'))
        aFakeTag2FromCsv={"String to look for (seperated by ; )":"bbb;bb bb","Tag to add on the post":"BBB"}
        aFakeTag2Obj = Tag(aFakeTag2FromCsv["Tag to add on the post"], aFakeTag2FromCsv["String to look for (seperated by ; )"].split(';'))
        aSmartTagList=[aFakeTagObj,aFakeTag2Obj]

        aTagsRes = smartHighlight(aFakePost,aSmartTagList)

        self.assertEqual(aTagsRes,["AAA","BBB"])

    def test_no_match(self):
        aFakePost={"post_uuid":"1","content":"test eee test bbb test AAa test"}

        aFakeTagFromCsv={"String to look for (seperated by ; )":"ccc;cc cc","Tag to add on the post":"CCC"}
        aFakeTagObj = Tag(aFakeTagFromCsv["Tag to add on the post"], aFakeTagFromCsv["String to look for (seperated by ; )"].split(';'))
        aFakeTag2FromCsv={"String to look for (seperated by ; )":"ddd;dd dd","Tag to add on the post":"DDD"}
        aFakeTag2Obj = Tag(aFakeTag2FromCsv["Tag to add on the post"], aFakeTag2FromCsv["String to look for (seperated by ; )"].split(';'))
        aSmartTagList=[aFakeTagObj,aFakeTag2Obj]

        aTagsRes = smartHighlight(aFakePost,aSmartTagList)

        self.assertEqual(aTagsRes,[])


FILE_FORMAT="utf-8-sig"
#wafaa use utf-8 and jenny utf-8-sig

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
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
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
parser.add_argument('--utest', action='store_true')
parser.add_argument('--termToHighlightFilePath', help='File with term to hightlight. One term by line')

args = parser.parse_args()

def smartHighlight(aPost, iSmartTagsList):
    """Extract some specific keyword from a post content (text)
    #  @param aPost The post object (dict).
    #  @param iTermToHighlightRegex The keyword regex to use (regex).
    #  @return Returns list of tags matching the post
    """
    aTags=[]
    for aOneTag in iSmartTagsList:
        aHighlightMatch=aOneTag.searchRegex.search(aPost["content"])
        if(aHighlightMatch):
            aTags.append(aOneTag.tag)
            logger.info("Match for " + str(aOneTag.tag))
    return aTags

def extractTags(iFilePath):
    aStructuredTags=[]
    with open(iFilePath, encoding=FILE_FORMAT) as f:
        reader = csv.DictReader(f)
        for aOneEntry in reader:
                aNewTag = Tag(aOneEntry["Tag to add on the post"], aOneEntry["String to look for (seperated by ; )"].split(';'))
                aStructuredTags.append(aNewTag)
    return aStructuredTags

def smartFilterFile(iSmartTags, iFilename):
    """Process all the post in a text file to extract their keyword
    #  @param iFilename The filename path (string).
    """
    with open(iFilename, encoding=FILE_FORMAT) as f:
        reader = csv.DictReader(f)

        with open(iFilename + "_output"+aCurrentDateTimeString+".csv","w", encoding=FILE_FORMAT,newline='') as filteredFile:
            fieldnames = reader.fieldnames + ["TAGS"]
            writer = csv.DictWriter(filteredFile, fieldnames=fieldnames)
            writer.writeheader()

            for aOneEntry in reader:
                aTags = smartHighlight(aOneEntry,iSmartTags)
                aOneEntry["TAGS"]= '-'.join(aTags)
                writer.writerow(aOneEntry)
                

if __name__== "__main__":
    if (args.utest):
        logger.info("Unit test")
        runner = unittest.TextTestRunner()
        itersuite = unittest.TestLoader().loadTestsFromTestCase(MyTest)
        runner.run(itersuite)
        quit()

    aStrTags = extractTags(args.termToHighlightFilePath)
    for aOneTag in aStrTags:
        logger.info(aOneTag.prettyPrint())

    for aOneFile in args.FilePathListToProcess:
        logger.info("Current file: " + str(aOneFile))
        smartFilterFile(aStrTags,aOneFile)

    logger.info("Ending in " + str((time.time() - start_time)) + " ms")

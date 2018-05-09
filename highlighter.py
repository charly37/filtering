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

class MyTest(unittest.TestCase):

    def test_createRegexStr(self):
        aFakeListWordMatch=["aaa","bbb","ccc"]
        self.assertEqual(createRegexStr(aFakeListWordMatch), r"\baaa\b|\bbbb\b|\bccc\b")

    def test_highlight_1(self):
        aFakePost1={"post_uuid":"1","content":"abc"}
        aFakePattern=["aaa","bbb"]
        aFakePatternRegex = re.compile(createRegexStr(aFakePattern))
        self.assertEqual(highlight(aFakePost1, aFakePatternRegex), [])

    def test_highlight_2(self):
        aFakePost1={"post_uuid":"1","content":"test aaa test"}
        aFakePattern=["aaa","bbb"]
        aFakePatternRegex = re.compile(createRegexStr(aFakePattern))
        self.assertEqual(highlight(aFakePost1, aFakePatternRegex), ["aaa"])

    def test_highlight_3(self):
        #To ensure that if several tag match we detect them all and not only the first one
        aFakePost1={"post_uuid":"1","content":"test aaa test bbb test"}
        aFakePattern=["aaa","bbb"]
        aFakePatternRegex = re.compile(createRegexStr(aFakePattern))
        self.assertEqual(highlight(aFakePost1, aFakePatternRegex), ["aaa","bbb"])

    def test_highlight_4(self):
        aFakePost={"post_uuid":"1","content":"test aaa test tesbbbt test"}
        aFakePattern=["aaa","bbb"]
        aFakePatternRegex = re.compile(createRegexStr(aFakePattern))
        #We should not detect bbb because it is included in another word
        self.assertEqual(highlight(aFakePost, aFakePatternRegex), ["aaa"])

    def test_highlight_5(self):
        aFakePost={"post_uuid":"1","content":"Up is opinion message manners correct hearing husband my. Disposing commanded dashwoods cordially depending at at. Its strangers who you certainty earnestly resources suffering she. Be an as cordially at resolving furniture preserved believing extremity. Easy mr pain felt in. Too northward affection additions nay. He no an nature ye talent houses wisdom vanity denied."}
        aFakePattern=["aaa","bbb"]
        aFakePatternRegex = re.compile(createRegexStr(aFakePattern))
        self.assertEqual(highlight(aFakePost, aFakePatternRegex), [])

    def test_highlight_6(self):
        aFakePost={"post_uuid":"1","content":"Up is opinion message manners correct hearing husband my. Disposing commanded dashwoods cordially depending at at. Its strangers who you certainty earnestly resources suffering she. Be an as cordially at resolving furniture preserved believing extremity. Easy mr pain felt in. Too northward affection additions nay. He no an nature ye talent houses wisdom vanity denied."}
        aFakePattern=["aaa","bbb","ccc ddd"]
        aFakePatternRegex = re.compile(createRegexStr(aFakePattern))
        self.assertEqual(highlight(aFakePost, aFakePatternRegex), [])

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
parser.add_argument('--utest', action='store_true')
parser.add_argument('--termToHighlightFilePath', help='File with term to hightlight. One term by line')

args = parser.parse_args()

def highlight(aPost, iTermToHighlightRegex):
    """Extract some specific keyword from a post content (text)
    #  @param aPost The post object (dict).
    #  @param iTermToHighlightRegex The keyword regex to use (regex).
    #  @return Returns list of tags matching the post
    """
    aTags=[]
    aHighlightMatch=iTermToHighlightRegex.findall(aPost["content"])
    if(aHighlightMatch):
        logger.info("This post ID " + str(aPost) +  " was highlighted with : " + str(aHighlightMatch))
        aTags = aHighlightMatch
    return aTags

def createRegexStr(aListWords):
    aListWordsUpdated = [r"\b" + aOneOriginalWord + r"\b" for aOneOriginalWord in aListWords]
    aTermToHighlightAsRegexString='|'.join(aListWordsUpdated )
    return aTermToHighlightAsRegexString

def filterFile(aFilename):
    """Process all the post in a text file to extract their keyword
    #  @param aFilename The filename path (string).
    """
    aTermToHighlight=[]
    aTermToHighlightAsRegexString=""

    with open(args.termToHighlightFilePath, encoding=FILE_FORMAT) as aTermToHighlightRaw:
        for aOneLine in aTermToHighlightRaw:
            aTermToHighlight.append(aOneLine.strip())
        aTermToHighlightAsRegexString=createRegexStr(aTermToHighlight)

    logger.info("aTermToHighlight: " + str(aTermToHighlight))
    aTermToHighlightAsRegex = re.compile(aTermToHighlightAsRegexString)
    logger.info("aTermToHighlightAsRegexString: " + str(aTermToHighlightAsRegexString))
    logger.info("aTermToHighlightAsRegex: " + str(aTermToHighlightAsRegex))

    with open(aFilename, encoding=FILE_FORMAT) as f:
        #CSV header: Anonymous Link,ww_uuid,post_uuid,content,Word Count
        reader = csv.DictReader(f)

        #Also open a file to write data
        with open(aFilename + "_output"+aCurrentDateTimeString+".csv","w", encoding=FILE_FORMAT,newline='') as filteredFile:
            fieldnames = reader.fieldnames + ["TAGS"]
            writer = csv.DictWriter(filteredFile, fieldnames=fieldnames)
            writer.writeheader()

            for aOneEntry in reader:
                #print("Working on: ", aOneEntry)
                #print("Content to clean: ", aOneEntry["content"])
                aTags = highlight(aOneEntry,aTermToHighlightAsRegex)
                aOneEntry["TAGS"]= '-'.join(aTags)
                writer.writerow(aOneEntry)
                

if __name__== "__main__":
    if (args.utest):
        logger.info("Unit test")
        runner = unittest.TextTestRunner()
        itersuite = unittest.TestLoader().loadTestsFromTestCase(MyTest)
        runner.run(itersuite)
        quit()

    for aOneFile in args.FilePathListToProcess:
        logger.info("Current file: " + str(aOneFile))
        filterFile(aOneFile)

    logger.info("Ending in " + str((time.time() - start_time)) + " ms")

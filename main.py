import csv
import re


print("Starting - The file to read need to be in the same folder and called waround.csv")

def filtering(aPostContent):
    #https://stackoverflow.com/questions/3868753/find-phone-numbers-in-python-script
    reg = re.compile("\d{3}\d{3}\d{4}")
    aPhoneNumberMatch=reg.search(aPostContent)
    if(aPhoneNumberMatch):
        print("This post need to be filter due to phone number: ", aPhoneNumberMatch.group())
        return 1
    #https://stackoverflow.com/questions/17681670/extract-email-sub-strings-from-large-document
    reg2 = re.compile("[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    aEmailMatch=reg2.search(aPostContent)
    if(aEmailMatch):
        print("This post need to be filter due to email: ", aEmailMatch.group())
        return 2
    return 0

with open("waround.csv", encoding="utf8") as f:
    #CSV header: Anonymous Link,ww_uuid,post_uuid,content,Word Count
    reader = csv.DictReader(f)
    aNbImage=0
    aNbEmailPost=0
    aNbPhoneNumberPost=0
    for aOneEntry in reader:
        #print("Working on: ", aOneEntry)
        #print("Content to clean: ", aOneEntry["content"])
        if(aOneEntry["content"] == "image post"):
            aNbImage = aNbImage + 1
        aRetCode=filtering(aOneEntry["content"])
        if(aRetCode>0):
            print("Please clean the post with ID: ", aOneEntry["post_uuid"] ," and content: ", aOneEntry["content"], "\n")
            if(aRetCode==1):
                aNbPhoneNumberPost=aNbPhoneNumberPost+1
            if(aRetCode==2):
                aNbEmailPost=aNbEmailPost+1
    print("aNbPhoneNumberPost: ",str(aNbPhoneNumberPost)," aNbEmailPost: ",str(aNbEmailPost))
    #print("For info there are ", str(aNbImage), " post with only image")



print("Ending")
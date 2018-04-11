import csv
import re
import argparse
import time

#https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution
start_time = time.time()


print("Starting - The file to read need to be in the same folder and called waround.csv")

parser = argparse.ArgumentParser(description='Look for some email address or phone number in csv file.')
parser.add_argument('--filter', action='store_true')
args = parser.parse_args()


def filtering(aPost):
    #https://stackoverflow.com/questions/3868753/find-phone-numbers-in-python-script
    aPhoneNumberRegex = re.compile(r"\d{3}\d{3}\d{4}")
    aPhoneNumberMatch=aPhoneNumberRegex.search(aPost["content"])
    if(aPhoneNumberMatch):
        print("This post ID", aPost["post_uuid"], "need to be filter due to phone number:", aPhoneNumberMatch.group(), "with post content:", aPost["content"])
    #https://stackoverflow.com/questions/17681670/extract-email-sub-strings-from-large-document
    aEmailAdressRegex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    aEmailMatch=aEmailAdressRegex.search(aPost["content"])
    if(aEmailMatch):
        print("This post ID", aPost["post_uuid"], "need to be filter due to email:", aEmailMatch.group(), "with post content:", aPost["content"])
    return aPost
    


if (args.filter):
    print("Warning i will filter")

with open("waround.csv", encoding="utf8") as f:
    #CSV header: Anonymous Link,ww_uuid,post_uuid,content,Word Count
    reader = csv.DictReader(f)
    aNbEmailPost=0
    aNbPhoneNumberPost=0

    #Also open a file to write data
    with open("output.csv","w", , newline='') as filteredFile:
        fieldnames = ['Anonymous Link', 'ww_uuid','post_uuid','content','Word Count']
        writer = csv.DictWriter(filteredFile, fieldnames=fieldnames)
        writer.writeheader()

        for aOneEntry in reader:
            #print("Working on: ", aOneEntry)
            #print("Content to clean: ", aOneEntry["content"])
            filtering(aOneEntry)
            writer.writerow(aOneEntry)

print("Ending in ", (time.time() - start_time),  " ms")

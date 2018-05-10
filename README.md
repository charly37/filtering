Bunch of py36 scripts to process datasets

- main.py to remove phone and email and put some simple tags
- highliter.py to add more tags

# main.py
This will remove email and phone number (very aggressive regex - lot of false positive but we don t care).

To run the script:
```
python.exe .\main.py -h
```

# highlighter.py
This add several tags based on post content and a list of tags

To run the script:
```
python.exe .\highlighter.py -h
python.exe .\highlighter.py --FilePathListToProcess .\InputFile.csv --termToHighlightFilePath .\Search_Terms.csv
```

To run the unit test:
```
python.exe .\highlighter.py --utest
```
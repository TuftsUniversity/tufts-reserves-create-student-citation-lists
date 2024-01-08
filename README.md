# Create input list for Student Electronic Citation Listings

This script takes input from Barnes and Noble reading lists supplied by the bookstore, and merges it with the result of Collections working with the Alma Overlap Analysis report to get a list of citations with MMS ID that will be used to serve reserve needs

**Input**
- Barnes & Noble input file.  This file needs to be placed in the "Barnes and Noble" directory.  It should be the only file in there.
- result of Overlap Analysis file once Collections have chosen which records (with MMS IDs) will serve the reserve needs for each citation.  This file needs to be placed in the "Alma" directory.  It should be the only file in there.

**Method**
Matching is done between reserves and the Barnes and Noble list via ISBN-13, and it also parses the course in separate fields in the Barnes and Noble list into a Tufts-specific Alma course code  It also gets concurrent users license information, "seats", from the Alma SRU for Tufts

**Output**
It merges and parses all this data to create
- an output file with
  - Primo link
  - course information
  - seats (concurrent license use)
  - instructor information including contact

**Use**
- for this to work, you'll have to download the config folder from https://tufts.box.com/s/omlgqir4hek5dld9l45q6dj7s98qpt0g All Files/Files Between LTS and Tisch Library Collections/config
- install requirements by
  - python3 -m pip install -r requirements.txt
  - OR
  - pip install -r requirements.txt
  - (depending on how you have Python 3 set up)
- python3 BAndNToDrupalInjest.py

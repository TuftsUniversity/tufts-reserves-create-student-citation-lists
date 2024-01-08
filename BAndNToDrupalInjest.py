#!/usr/bin/env python3
import pandas as pd
# from tkinter import Tk
# from tkinter.filedialog import askopenfilename
import requests
import sys
sys.path.append('config/')
import secrets_local
import glob
import json
import os
import xml.etree.ElementTree as et
import sys
# # Initialize Tkinter and hide the main window
# Tk().withdraw()
oDir = "./Output"
if not os.path.isdir(oDir) or not os.path.exists(oDir):
    os.makedirs(oDir)

pDir = "./Alma and Barnes and Noble Merged"
if not os.path.isdir(pDir) or not os.path.exists(pDir):
    os.makedirs(pDir)

# pDir = "./Processing"
# if not os.path.isdir(pDir) or not os.path.exists(pDir):
#     os.makedirs(pDir)

bnf_files = glob.glob('Barnes and Noble/*', recursive = True)

bAndN_filename = bnf_files[0]
barnes_and_noble_df = pd.read_excel(bAndN_filename, header=1, dtype={"EAN-13": "str"}, engine='openpyxl')
courses_url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/courses?"

alma_files = glob.glob('Alma/*', recursive = True)

print(alma_files)
alma_filename = alma_files[0]
almaProcessed = pd.read_excel(alma_filename, sheet_name=0, header=0, dtype={"ISBN(Matching Identifier)": "str", "MMS ID": 'str'}, engine='openpyxl')

almaProcessed = almaProcessed[['Title', 'ISBN(13)', 'MMS ID']]

almaProcessed['ISBN(13)'] = almaProcessed['ISBN(13)'].apply(lambda x: x.split("\n\n"))
almaProcessed = almaProcessed.explode('ISBN(13)').reset_index()

merged_df = barnes_and_noble_df.merge(almaProcessed, how='inner', left_on='EAN-13', right_on="ISBN(13)")
merged_df = merged_df.drop('index', axis=1)

merged_df.to_excel('Alma and Barnes and Noble Merged/Merged Data for Reading List File Ingest.xlsx', index=False)

merged_df['course_code'] = ""
merged_df['section'] = ""
merged_df['course_name'] = ""
merged_df['instructors'] = ""
merged_df['identifiers'] = ""

merged_df['emails'] = ""

x = 0
for index, row in merged_df.iterrows():
    # if x == 100:
    #     break
    semester = row['Term']

    if 'F' in semester:
        semester = semester.replace('F', 'Fa')

    elif 'W' in semester:
        semester = semester.replace('W', 'Sp')

    request_url = courses_url + "apikey=" + secrets_local.prod_courses_api_key + "&q=name~" + semester + "*" + row['Dept'] + "*" + row['Course'] + "*" + row['Sec'] + "&format=json"

    response = requests.get(request_url).json()




    print(str(index) + "\t-" + request_url)



    try:
        course_code = response['course'][0]['code']
    except:
        course_code = "Error finding course" + json.dumps(response)

    try:
        section = response['course'][0]['section']

    except:
        section = "Error finding course" + json.dumps(response)

    try:
        course_name = response['course'][0]['name']

    except:
        course_name = "Error finding course" + json.dumps(response)

    try:
        instructors = response['course'][0]['instructor']

    except:
        instructors = ""

    emails = []
    names = []
    identifiers = []
    response = json.dumps(response)
    response = json.loads(response)

    if len(instructors) > 0:
        for instructor in instructors:
            name = instructor['last_name'] + ", " + instructor['first_name']
            names.append(name)
            identifier = instructor['primary_id']
            identifiers.append(identifier)

            response_user = requests.get("https://api-na.hosted.exlibrisgroup.com/almaws/v1/users/" + identifier + "?apikey=" + secrets_local.prod_user_api_key + "&format=json").json()

            for email in response_user['contact_info']['email']:

                print(email)
                if email['preferred'] == True:

                    emails.append(email['email_address'])

                    print(email['email_address'])
                    # sys.exit()





    merged_df.loc[index, 'course_code'] = course_code
    merged_df.loc[index, 'section'] = section
    merged_df.loc[index, 'course_name'] = course_name

    #merged_df.loc[index, 'identifiers'] = "; ".join(identifiers)
    merged_df.loc[index, 'instructors'] = "; ".join(names)
    merged_df.loc[index, 'identifiers'] = "; ".join(identifiers)
    merged_df.loc[index, 'emails'] = "; ".join(emails)
    # print(merged_df.columns)



    x += 1

print(merged_df)
merged_df.to_excel('Alma and Barnes and Noble Merged/Merged Data for Reading List File Ingest with Instructors.xlsx', index=False)

# sys.exit()
sru_url = "https://tufts.alma.exlibrisgroup.com/view/sru/01TUN_INST?version=1.2&operation=searchRetrieve&recordSchema=marcxml&query=alma.mms_id="
namespaces = {'ns1': 'http://www.loc.gov/MARC21/slim'}


api_key = secrets_local.prod_courses_api_key

def create_primo_citation_link(mms_id):
    # Assuming a similar structure to the provided output file's links
    return f"https://tufts.primo.exlibrisgroup.com/discovery/fulldisplay?docid=alma{mms_id}&context=L&vid=01TUN_INST:01TUN"

# Process the input file and create the output file
output_columns = ['processing_department', 'course_code', 'course_name', 'course_section',
                  'primo_citation_link', 'mms_id', 'format', 'title', 'isbn', 'usage_restriction']

# Creating a DataFrame for the output
output_df = pd.DataFrame(columns=output_columns)

for index, row in merged_df.iterrows():
    # Map the fields from input to output

    result = requests.get(sru_url + row['MMS ID'])
    tree_bib_record = et.ElementTree(et.fromstring(result.content.decode('utf-8')))
    root_bib_record = tree_bib_record.getroot()

    try:
        usage_restriction = root_bib_record.findall(".//ns1:datafield[@tag='AVE']/ns1:subfield[@code='n']", namespaces)[0]
        usage_restriction = usage_restriction.text
    except:
        usage_restriction = ""
    output_row = {
        'processing_department': 'Tisch Reserves',  # Placeholder value
        'course_code': row['course_code'],
        'course_name': row['course_name'],
        'course_section': row['section'],

        'primo_citation_link': create_primo_citation_link(row['MMS ID']),
        'mms_id': row['MMS ID'],
        'format': 'Electronic',  # Placeholder value
        'title': row['Title_y'],
        'isbn': row['EAN-13'],
        'usage_restriction': usage_restriction,  # Assuming ISBN is EAN-13
        'instructor': row['instructors'],
        'identifiers': row['identifiers'],
        'emails': row['emails']
    }
    output_df = pd.concat([output_df, pd.DataFrame(output_row, index=[0])])

# Saving the output file


output_df.to_excel("Output/8Data-primo output.xlsx", index=False)

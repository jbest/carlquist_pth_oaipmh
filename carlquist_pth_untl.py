#!/usr/bin/env python
# coding: utf-8

# # Sherwin Carlquist Collection - record retrieval - UNTL format

# This script retrieves public records of the Sherwin Carlquist Collection (SJCC) on the Portal to Texas History (PTH). Various fields and values are extracted and saved to a CSV file. This script is based on the original carlquist_pth.ipynb which retrieved OAI-DC format and was sufficient for creating item relationships with RSA, but didn't include all data we need for visualization.

# In[1]:


# Run this line if using cloud notebook like Google Colab
#get_ipython().system('pip install sickle')


# In[3]:


import re
import xmltodict
import xml.etree.ElementTree as ET

# Sickle is used to harvest records from the PTH using the OAI-PMH protocol
from sickle import Sickle

# Pandas is used just for exporting CSVs. Overkill but quick and easy
import pandas as pd

# static values for relationship records
accordingTo = 'TBD'
basisOfRecord = 'TBD' #Not sure how/if we'll use this 

# Generic URL regex pattern
url_pattern = re.compile(r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)")
# OCCID regex pattern
occid_pattern = re.compile(r'occid=(?P<occid>\d+)')
# RSA catalogNumber pattern
# RSA regex pattern for general, micro, and wood catalogNumbers
rsa_catnum_pattern = re.compile(r'RSAw?(?:-MICR-)?\d+')
# previous general vascular pattern for RSA
#rsa_catnum_pattern = re.compile(r'RSA\d+')

sickle = Sickle('https://texashistory.unt.edu/oai')
# Retrieve all public PTH records in the SJCC collection
#record_format = 'oai_dc'
record_format = 'untl'
#record_format = 'untl_dpla'
records = sickle.ListRecords(metadataPrefix=record_format, set='collection:SJCC')

def strip_chars(input_str, chars=['[',']', '\'']):
    for char in chars:
        input_str = input_str.replace(char, '')
    #print(input_str)
    return input_str

def parse_xml(xml_str):
    item_meta_dict = {}
    # NOTE - not parsed:
    # <ns1:primarySource>
    # <ns1:creator qualifier="pht">
    # <ns1:language>
    # <ns1:collection>
    # <ns1:institution>
    # <ns1:rights qualifier="license">
    # <ns1:resourceType>
    # <ns1:format>
    #unt_xml = xmltodict.parse(xml_content)
    unt_xml = xmltodict.parse(xml_str)
    item_meta = unt_xml['ns0:record']['ns0:metadata']['ns1:metadata']

    #print('TITLE')
    title_element = item_meta['ns1:title']
    title_list=[]
    if isinstance(title_element, list):
        # handling multiple titles
        for title_entry in title_element:
            #print(title_entry)
            title_entry_text = strip_chars(title_entry['#text'])
            title_list.append(title_entry_text)
            #title_list.append(title['#text'])
            #print(title_entry_text)
    else:
        title_entry_text = strip_chars(title_element['#text'])
        title_list.append(title_entry_text)
        #print(title_entry_text)
    #item_meta_dict['title'] = title_element['#text']
    item_meta_dict['title'] = str(title_list)
    #print(item_meta_dict['title'])

    #print('IDENTIFIERS')
    identifiers = item_meta['ns1:identifier']
    #print(identifiers)
    id_list = []
    for identifier in identifiers:
        #print(identifier)
        if identifier['@qualifier'] == 'LOCAL-CONT-NO':
            item_meta_dict['brit_id']=identifier['#text']        
        id_list.append(identifier['#text'])
    #TODO add distinct IDs
    item_meta_dict['identifiers'] = str(id_list)

    #title = record.metadata.get('title')
    #print(item_meta['title'])
    #print(title['#text'])
    #print('DATE')
    date_element = item_meta['ns1:date']
    try:
        item_meta_dict['date'] = date_element['#text']
    except Exception as e:
        print('ERROR: date assignment', e, date_element)
        item_meta_dict['date'] = None
        print(item_meta_dict)

    #print('DESCRIPTION')
    #description = item_meta['ns1:description']
    #print(description)

    #print('SUBJECTS')
    subjects = item_meta['ns1:subject']
    #print(subjects)
    subject_list = []
    subject_lcsh_list = []
    subject_kwd_list = []
    subject_aat_list = []
    subject_untl_bs_list = []    
    for subject in subjects:
        #print(subject)
        try:
            if subject['@qualifier'] == 'LCSH':
                subject_lcsh_list.append(subject['#text'])
            if subject['@qualifier'] == 'KWD':
                subject_kwd_list.append(subject['#text'])  
            if subject['@qualifier'] == 'AAT':
                subject_aat_list.append(subject['#text'])
            if subject['@qualifier'] == 'UNTL-BS':
                subject_untl_bs_list.append(subject['#text'])
            subject_list.append(subject['#text'])
        except Exception as e:
            print('ERROR: subject assignment', e)
            print(subject)
            print(item_meta_dict)
    #print(subject_list)
    item_meta_dict['subjects_lcsh'] = str(subject_lcsh_list)
    item_meta_dict['subjects_kwd'] = str(subject_kwd_list)
    item_meta_dict['subjects_aat'] = str(subject_aat_list)
    item_meta_dict['subjects_untl_bs'] = str(subject_untl_bs_list)
    item_meta_dict['subjects'] = str(subject_list)


    #print('COVERAGES')
    coverages = item_meta['ns1:coverage']
    if isinstance(coverages, list):        
        for coverage in coverages:
            #print(coverage)
            if coverage['@qualifier'] == 'placeName':
                place_name = coverage['#text']
                item_meta_dict['place_name'] = place_name
                #print('placeName:', placeName)
    else:
        if coverages['@qualifier'] == 'placeName':
            place_name = coverages['#text']
            item_meta_dict['place_name'] = place_name

    #print('CITATION')
    #citation = item_meta['ns1:citation']
    #print(citation)


    """
    print('UNT META')

    unt_metas = item_meta['ns1:meta']
    for unt_meta in unt_metas:
        #print(unt_meta)
        pass
    """

    return item_meta_dict

rec_count = 0
relation_count = 0

data = []
# test with just one
#one_record = records.next()
#print(one_record)
for record in records:
    rec_count += 1
    #testing
    #if rec_count > 100:
    #    break
    # get ARK
    rec_identifier = record.header.identifier
    ark = rec_identifier.split(':')[1]
    #PTH URL
    resourceUrl = 'https://texashistory.unt.edu/' + ark
    #metadata = record.metadata
    #format = record.metadata.get('format')
    #description = record.metadata.get('description')
    xml_str = ET.tostring(record.xml, encoding='unicode')
    item_meta_dict = parse_xml(xml_str)
    #print(item_meta_dict)
    #relation = None #temp

    #title = record.metadata.get('title')
    subject = record.metadata.get('subject', None)
    date = record.metadata.get('date')
    item_type = record.metadata.get('type')
    identifier = record.metadata.get('identifier')
    relation = record.metadata.get('relation')
    obj_format = record.metadata.get('format')
    coverage = record.metadata.get('coverage')
    creator = record.metadata.get('creator')


    if relation:
        relation_count += 1
        relation_string = relation[0]
        # extract relation_url
        url_match = url_pattern.search(relation_string)
        # extract RSA catalog number
        rsa_catnum_match = rsa_catnum_pattern.search(relation_string)
        if rsa_catnum_match:
            catalogNumber = rsa_catnum_match[0]
        else:
            catalogNumber = None
        if url_match:
            relation_url = url_match[0]
            #OCCID
            occid_match = occid_pattern.search(relation_url)
            if occid_match:
                occid = occid_match.group('occid')
            else:
                occid = None
        else:
            relation_url = None

        if 'collecting event' in relation_string:
            relation_type = 'specimen'
        elif 'population' in relation_string:
            relation_type = 'population'
        else:
            relation_type = 'undefined'

    else:
        relation_string = '' #store empty in data rather than None which was messing with strings
        relation_type = None
        relation_url = None
        catalogNumber = None
        occid = None

    brit_id = None
    for id in identifier:
        if 'local-cont-no' in id:
            brit_id_kv = id.split(':')
            brit_id = brit_id_kv[1].strip()

    data.append({'catalogNumber': catalogNumber, 
                 'occid': occid,
                 #'objectID': brit_id, 
                 'objectID': item_meta_dict['brit_id'], 
                 'resourceUrl': resourceUrl, 
                 'ark': ark,
                 #'title': title,
                 'title': strip_chars(item_meta_dict['title']),
                 'date': date,  
                 'relation': strip_chars(relation_string), 'relation_url': relation_url, 'relation_type': relation_type, 
                 'identifiers': item_meta_dict['identifiers'],
                 #'xml_str': xml_str, 
                 'format': obj_format, 
                 #'coverage': coverage,
                 'place_name': item_meta_dict.get('place_name'),
                 #'creator': creator,
                 'date': item_meta_dict['date'],
                'subjects_lcsh': strip_chars(item_meta_dict['subjects_lcsh']),
                'subjects_kwd': strip_chars(item_meta_dict['subjects_kwd']),
                'subjects_aat': strip_chars(item_meta_dict['subjects_aat']),
                'subjects_untl_bs': strip_chars(item_meta_dict['subjects_untl_bs']),
                #'subjects': item_meta_dict['subjects'],
                })

print('rec_count', rec_count)
print('relation_count', relation_count)

# convert list to dataframe
df = pd.DataFrame(data)

filename = 'sjcc_all_' + record_format + '.csv'

df.to_csv(filename, index=False)
print('Results saved to:', filename)

import os
# test if running in Google Colab
if os.getenv("COLAB_RELEASE_TAG"):
    print('File output is stored in the Colab filesystem accessible in the File pane to the left')
else:
    print('File output stored in the same directory as this notebook')


# In[ ]:





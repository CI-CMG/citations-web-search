from __future__ import print_function
import os
import json
import sys
sys.path.append('../archive-web-search/')
from DB_connect import OracleConnection

# TODO: Update format of the web page to better describe stationary datasets. Stationary
#  data won't always have a cruise or ship associated with them. Adding Dataset Name could
#  address this. Cruise and Ship fields can be n/a for these data types. Work with Chuck to
#  update html page, then update this script.

# This script queries the Cruise database for water column sonar dataset citations and creates
# a java script output file to be translated into an html page by Chuck. It also can generate
# a json output file in case we decide to use json instead. That part is commented out.

# web page url: https://www.ngdc.noaa.gov/mgg/wcd/citations.html

# Connect to database (config file located in root directory)
config_file = "cruise_prod.config"
config_path = os.path.join(os.path.expanduser("~"), '.connections', config_file)

database = OracleConnection(config_path)

# Query database for cruises
q_command = "select WCS_ID, PLATFORM_NAME, CRUISE_NAME, INSTRUMENT_NAME, SOURCE_NAME, " \
            "SOURCE_GROUP, CITATION_TEXT, CITATION_LINK, PUBLISH_DATE as ARCHIVE_DATE " \
            "from CRUISE.SURVEY_SUMMARY_AGG_MSQL where " \
            "PUBLISH='Y' ORDER BY ARCHIVE_DATE DESC"
result1 = database.fetch_all(q_command)

# Query database for stationary deployments
q_command = "select WCS_ID, SHIP_NAME, CRUISE_NAME, INSTRUMENT_NAME, SOURCE_NAME, " \
            "SOURCE_GROUP, CITATION_TEXT, CITATION_LINK, PUBLISH_DATE as ARCHIVE_DATE " \
            "from CRUISE.SURVEY_SUMMARY_AGG_MSQP where " \
            "PUBLISH='Y' ORDER BY ARCHIVE_DATE DESC"
result2 = database.fetch_all(q_command)

# Combine results
result = result1 + result2

# java script output file
java_file = open("/nfs/marine_images/wcd/data_source.js", "w")
java_file.write("var dataSet=[")

no_citation = []
# Build dictionary
data = dict()
data['data'] = []
for row in result:
    cruise = row["CRUISE_NAME"]
    instrument = row["INSTRUMENT_NAME"]
    ship = row["SHIP_NAME"]
    source_group = row["SOURCE_GROUP"].replace("|", "", 1)[: -1].replace("|", ", ")
    # clean up source names
    source = row['SOURCE_NAME'].replace("|", "", 1)[: -1].replace("|", ", ")
    if "UNOLS" in source:
        source = source.replace("UNOLS", "Rolling Deck to Repository")
    elif "Woods Hole Oceanographic Institution" in source:
        source = source.replace("Woods Hole Oceanographic Institution", "WHOI")
    citation = row['CITATION_TEXT']
    doi = row['CITATION_LINK']

    if not citation:
        print(f"No citation for {cruise} in the database")
        no_citation.append(f"{row['WCS_ID']},{cruise},{instrument}")
        continue

    if not doi:
        doi = 'None available'
        print("NO DOI")

        # create list for java file
        ds_info = f'["{cruise}","{instrument}","{source}","{citation}","{doi}","{ship}","{source_group}"],\n'

    else:
        ds_info = f'''["{cruise}","{instrument}","{source}","{citation}","<a href='{doi}' target='_blank'>{doi}</a>","{ship}","{source_group}"],\n'''

    java_file.write(ds_info)

    # create dictionary for json file
    metadata = {
                'Cruise': cruise,
                'Instrument': instrument,
                'Source': source,
                'Citation': citation,
                'DOI': doi,
                'Ship': ship,
                'Source Group': source_group
    }

    print(f"Processing {cruise}")
    data['data'].append(metadata)

database.close_connection()

# write json file
# with open("/nfs/mgg_apps/fisheries/citations-web-search/wcsd-citations.json", 'w') as outfile:
#     json.dump(data, outfile)


java_file.write("]")

# outfile.close()
java_file.close()

if no_citation:
    print("\nCruises without citations in the database")
    for cruise in no_citation:
        print(cruise)

print("done")

from __future__ import print_function
import os
import json
import sys
sys.path.append('../archive-web-search/')
from DB_connect import OracleConnection


# This script queries the water column sonar database for dataset citations and creates a java script
# output file to be translated into an html page by Chuck.  It also can generate a json output file in
# case we decide to use json instead.  That part of the code is commented out


def get_citation(db, wcs_id, instrument):
    """Query citation and doi in the database

        Args:
            db(object): database object
            wcs_id(str): dataset identifer in the database
            instrument(str): instrument name
    """
    q_command = "select CITATION_TEXT, CITATION_LINK from WCD.INSTRUMENTS " \
                "where WCS_ID = :id and INSTRUMENT_NAME= :inst"
    data = {"id": wcs_id, "inst": instrument}
    result = db.fetch_one(q_command, data)
    citation = result['CITATION_TEXT']
    doi = result['CITATION_LINK']
    return citation, doi


# Connect to database (config file located in root directory)
config_file = "wcd_prod.config"
config_path = os.path.join(os.path.expanduser("~"), '.connections', config_file)

database = OracleConnection(config_path)

# Query database
q_command = "select WCS_ID, SHIP_NAME, CRUISE_NAME, INSTRUMENT_NAME, SOURCE_NAME, " \
            "SOURCE_GROUP, PUBLISH_DATE as ARCHIVE_DATE from WCD.SURVEY_SUMMARY_AGG_MSQL where " \
            "PUBLISH='Y' ORDER BY ARCHIVE_DATE DESC"
result = database.fetch_all(q_command)

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
    citation, doi = get_citation(database, row['WCS_ID'], instrument)

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

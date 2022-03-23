#/bin/bash
#This script creates a java script file with wcsd dataset citations that supports a web page managed by Chuck 
#Veronica Martinez, 5/6/21 
#Updated, 8/2/21 to report errors in email notification

#Run script to create js file
cd /nfs/mgg_apps/fisheries/citations-web-search
python wcsd_citations.py
code=$?
#echo $code
if [ $code -ne 0 ]
then
    echo "******ERROR******"
    mail -s "citations js file FAILED" veronica.martinez@noaa.gov <<< "Error creating js file for wcsd citations web page"
    #break
else
    #Update permissions for files created
    cd /nfs/marine_images/wcd/
    chmod 775 data_source.js
    chown :mgg data_source.js

    #Send email notification
    mail -s "citations js file created" veronica.martinez@noaa.gov <<< "successful creation of js file for wcsd citations web page"
fi


#Update permissions for files created
#cd /nfs/marine_images/wcd/
#chmod 775 data_source.js
#chown :mgg data_source.js

#Send email notification
#mail -s "citations js file created" veronica.martinez@noaa.gov <<< "successful creation of js file for wcsd citations web page"

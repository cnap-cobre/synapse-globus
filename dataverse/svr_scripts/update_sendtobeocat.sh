#!/bin/bash

#Download the updated script.
wget -O send_to_beocat_manifest.json https://www.dropbox.com/s/072q6470wohf7mw/send_to_beocat_tool_manifest.json?dl=0

#Provide a list of tools so user can get the tool id.
curl http://localhost:8080/api/admin/externalTools
echo
echo -n "Please provide the tool ID of the tool you want to remove. (-1 for none)"
read -p 'Tool ID: ' TOOLS_ID
#Use the tool id to remove the current tool.

curl -X DELETE http://localhost:8080/api/admin/externalTools/$TOOL_ID

#Add the new tool.
curl -X POST -H 'Content-type: application/json' http://localhost:8080/api/admin/externalTools --upload-file send_to_beocat_manifest.json
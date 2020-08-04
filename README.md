# synapse-globus
Synapse is a browser-based interface for transferring data into and out of a Harvard's Dataverse installation utilizing Globus.

Currently we do this by transferring the data into a staging area "on" the Dataverse server, then use API calls for actually importing them in.
In the future we plan on taking very large files and only importing in a placeholder. Getting that handle, we will replace the file that the import created, with the actual file, then update the DB with the new filesize.

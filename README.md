# PRI_F1
A data processing and retrieval project regarding F1 seasons 1950-2023.

## Run Solr

- To run the startup script for the project, first run the command `docker run -p 8983:8983 --name f1_solr -v ${PWD}:/data -d solr:9.3` in the `f1db_json` folder.
- Then, from the `solr/scripts`` folder, simply run `startup.sh`.

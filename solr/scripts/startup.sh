#!/bin/bash

# This script expects a container started with the following command.
# docker run -p 8984:8984 --name f1_solr -v ${PWD}:/data -d solr:9.3 

# Run the commands to create all cores
docker exec -it f1_solr bin/solr create_core -c circuits
docker exec -it f1_solr bin/solr create_core -c constructors
docker exec -it f1_solr bin/solr create_core -c drivers

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./circuits_schema.json" \
    http://localhost:8983/solr/circuits/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./constructors_schema.json" \
    http://localhost:8983/solr/constructors/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./drivers_schema.json" \
    http://localhost:8983/solr/drivers/schema

# Populate collection using mapped path inside container.
docker exec -it f1_solr bin/post -c circuits ../../f1db_josn/circuits.json

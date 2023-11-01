#!/bin/bash

# This script expects a container started with the following command.
# docker run -p 8983:8983 --name f1_solr -v ${PWD}:/data -d solr:9.3 

# Run the commands to create all cores
docker exec -it f1_solr bin/solr create_core -c circuits
docker exec -it f1_solr bin/solr create_core -c constructors
docker exec -it f1_solr bin/solr create_core -c constructor_standings
docker exec -it f1_solr bin/solr create_core -c drivers
docker exec -it f1_solr bin/solr create_core -c driver_standings
docker exec -it f1_solr bin/solr create_core -c lap_times
docker exec -it f1_solr bin/solr create_core -c pit_stops
docker exec -it f1_solr bin/solr create_core -c qualifying
docker exec -it f1_solr bin/solr create_core -c races
docker exec -it f1_solr bin/solr create_core -c results
docker exec -it f1_solr bin/solr create_core -c seasons
docker exec -it f1_solr bin/solr create_core -c sprint_results
docker exec -it f1_solr bin/solr create_core -c status

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/circuits_schema.json" \
    http://localhost:8983/solr/circuits/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/constructors_schema.json" \
    http://localhost:8983/solr/constructors/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/constructor_standings_schema.json" \
    http://localhost:8983/solr/constructor_standings/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/drivers_schema.json" \
    http://localhost:8983/solr/drivers/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/driver_standings_schema.json" \
    http://localhost:8983/solr/driver_standings/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/lap_times_schema.json" \
    http://localhost:8983/solr/lap_times/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/pit_stops_schema.json" \
    http://localhost:8983/solr/pit_stops/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/qualifying_schema.json" \
    http://localhost:8983/solr/qualifying/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/races_schema.json" \
    http://localhost:8983/solr/races/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/results_schema.json" \
    http://localhost:8983/solr/results/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/seasons_schema.json" \
    http://localhost:8983/solr/seasons/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/sprint_results_schema.json" \
    http://localhost:8983/solr/sprint_results/schema

curl -X POST -H 'Content-type:application/json' \
    --data-binary "@../../f1db_json/status_schema.json" \
    http://localhost:8983/solr/status/schema

# Populate collection using mapped path inside container.
docker exec -it f1_solr bin/post -c circuits /data/circuits.json
docker exec -it f1_solr bin/post -c constructors /data/constructors.json
docker exec -it f1_solr bin/post -c constructor_standings /data/constructor_standings.json
docker exec -it f1_solr bin/post -c drivers /data/drivers.json
docker exec -it f1_solr bin/post -c driver_standings /data/driver_standings.json
docker exec -it f1_solr bin/post -c lap_times /data/lap_times.json
docker exec -it f1_solr bin/post -c pit_stops /data/pit_stops.json
docker exec -it f1_solr bin/post -c qualifying /data/qualifying_ms.json
docker exec -it f1_solr bin/post -c races /data/races.json
docker exec -it f1_solr bin/post -c results /data/results_ms.json
docker exec -it f1_solr bin/post -c seasons /data/seasons.json
docker exec -it f1_solr bin/post -c sprint_results /data/sprint_results_ms.json
docker exec -it f1_solr bin/post -c status /data/status.json

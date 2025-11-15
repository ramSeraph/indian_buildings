#!/bin/sh

mkdir data

# download the metadata about quads and links from MS, also get the india shape file
cd data
wget https://minedbuildings.blob.core.windows.net/global-buildings/dataset-links.csv
wget https://minedbuildings.blob.core.windows.net/global-buildings/buildings-coverage.geojson
wget https://raw.githubusercontent.com/datameet/maps/master/Country/india-composite.geojson
cd -

# filter the quads which intersect with the india shape and get their links
python pick_quads.py

# download the data using the links
cd data
cat links.txt | xargs  wget -x -c -nH --cut-dirs=3
cd -

# filter the data further based on india shape
python unzip_and_clip.py

# tile the data 
cd data
tippecanoe -x height -j '{ "*": [ "attribute-filter", "confidence", [ ">=", "$zoom", 13 ] ] }' -P -o ms_buildings_india.mbtiles --simplify-only-low-zooms --drop-densest-as-needed --extend-zooms-if-still-dropping -l ms_buildings_india -n ms_buildings_india -A '<a href="https://github.com/microsoft/GlobalMLBuildingFootprints" target="_blank" rel="noopener noreferrer">Microsoft ML Buildings</a>' ms_buildings_india.geojsonl
cd -

# break it into a mosaic of pmtiles files less than 2 GB 
uvx --from pmtiles-mosaic partition --from-source data/ms_buildings_india.mbtiles --to-pmtiles data/ms_buildings_india.pmtiles

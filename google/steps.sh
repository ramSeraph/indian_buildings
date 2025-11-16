
#!/bin/bash

# steps involved in reproducing how the data in the repo has been obtained and processed

# 0. create data dir
mkdir data

# 1. get the india shape file
wget -O data/india-composite.geojson https://github.com/datameet/maps/blob/master/Country/india-composite.geojson

# 2. manually collect the s2 level 4 tiles that cover the india shape and write them to s2_tiles.txt
# TODO: this probably can be automated using s2 tools

# 3. download and convert data from each of the s2 tiles as seperate mbtiles files
# internally uses wget, gunzip and tippecanoe( https://github.com/mapbox/tippecanoe )
uv run --with shapely process.py

# 4. join the individual mbtiles file into a single mbtiles file using tile-join from tippecanoe
tile-join -pk -o data/google-open-buildings-india.mbtiles  data/*.mbtiles
ls data/*.mbtiles | grep -v google | xargs rm 

# 5. split the mbtiles file into a mosaic of pmtiles files of size < 2 GB
uvx --from pmtiles-mosaic partition --form-source data/google-open-buildings-india.mbtiles --to-pmtiles data/google-open-buildings-india.pmtiles


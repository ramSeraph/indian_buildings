import csv
import json
import time
import subprocess
from pathlib import Path

from shapely.geometry import shape
from shapely.prepared import prep
from shapely import wkt, to_geojson

def run_external(cmd):
    print(f'running cmd - {cmd}')
    start = time.time()
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    end = time.time()
    print(f'STDOUT: {res.stdout}')
    print(f'STDERR: {res.stderr}')
    print(f'command took {end - start} secs to run')
    if res.returncode != 0:
        raise Exception(f'command {cmd} failed with exit code: {res.returncode}')


def get_url(s2_id):
    return f"https://storage.googleapis.com/open-buildings-data/v3/polygons_s2_level_4_gzip/{s2_id}_buildings.csv.gz"


def load_india_shape():
    data = json.loads(Path('data/india-composite.geojson').read_text())
    geom = data['features'][0]['geometry']
    return prep(shape(geom))


def load_file(s2, india_shape):
    if Path(f'data/{s2}.mbtiles').exists():
        return
    url = get_url(s2)
    run_external(f'wget -O data/{s2}.csv.gz {url}')
    run_external(f'gunzip data/{s2}.csv.gz')
    with open(f'data/{s2}.geojsonl', 'w') as outf:
        with open(f'data/{s2}.csv', 'r') as f:
            reader = csv.DictReader(f)
            for r in reader:
                wkt_geom = r['geometry']
                bshape = wkt.loads(wkt_geom)
                if not india_shape.intersects(bshape):
                    continue
                bgeom = json.loads(to_geojson(bshape))
                feat = { 'type': 'Feature', 'geometry': bgeom, 'properties': { 'confidence': float(r['confidence']) } }
                line = json.dumps(feat) + '\n'
                outf.write(line)
    Path(f'data/{s2}.csv').unlink()
    # the tiles in the repo were generated with "--no-duplication" flag.. but that caused clipping at tile boundaries.. so dropping it 
    run_external(f'tippecanoe -l google_buildings -n "google_buildings" -N "Google Buildings India" -A \'<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener noreferrer">CC-BY 4.0</a>\' -P --drop-densest-as-needed -o data/{s2}.mbtiles data/{s2}.geojsonl')
    Path(f'data/{s2}.geojsonl').unlink()

if __name__ == '__main__':
    india_shape = load_india_shape()

    s2_tiles = Path('s2_tiles.txt').read_text().split('\n')
    s2_tiles = [ t.strip() for t in s2_tiles ]
    s2_tiles = [ t for t in s2_tiles if t != "" ]
    for t in s2_tiles:
        load_file(t, india_shape)

import csv
import json
import time
import subprocess
from pathlib import Path

from shapely.geometry import shape
from shapely.prepared import prep

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

def load_india_shape():
    data = json.loads(Path('data/india-composite.geojson').read_text())
    geom = data['features'][0]['geometry']
    return prep(shape(geom))


india_shape = load_india_shape()

with open('data/ms_buildings_india.geojsonl', 'a') as f:
    paths = Path('data/').glob('*/*/*.csv.gz')
    #paths = Path('.').glob('*.csv.gz')
    count = 0
    for path in paths:
        count += 1
        print(f'processing {count}')
        oname = str(path)[:-3]
        run_external(f'gunzip {str(path)}')
        with open(oname, 'r') as outf:
            for line in outf:
                feat = json.loads(line)
                geom = feat['geometry']
                s = shape(geom)
                if not india_shape.intersects(s):
                    continue
                f.write(line)
                #f.write('\n')
        Path(oname).unlink()

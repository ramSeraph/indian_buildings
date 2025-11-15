import re
import csv
import json
import time
import subprocess
from pathlib import Path

from shapely.geometry import shape
from shapely.prepared import prep

units = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}

# Alternative unit definitions, notably used by Windows:
# units = {"B": 1, "KB": 2**10, "MB": 2**20, "GB": 2**30, "TB": 2**40}

def parse_size(size):
    match = re.match(r"([0-9\.]+)([A-Z]+)", size, re.I)
    if match:
        items = match.groups()
    number, unit = items[0], items[1]
    return int(float(number)*units[unit])

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

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

if __name__ == '__main__':
    india_shape = load_india_shape()
    d_infos = []
    with open('data/dataset-links.csv', 'r') as f:
        reader = csv.DictReader(f)
        for r in reader:
            d_infos.append(r)
    
    keys_to_pick = set()
    q_data = json.loads(Path('data/buildings-coverage.geojson').read_text())
    q_feats = q_data['features']
    for q_feat in q_feats:
        q_shape = shape(q_feat['geometry'])
        if not india_shape.intersects(q_shape):
            continue
        q_props = q_feat['properties']
        q_key = str(q_props['quadkey'])[:-2]
        keys_to_pick.add(q_key)
        
    links = []
    size = 0
    for d_info in d_infos:
        q_key = d_info['QuadKey']
        if q_key not in keys_to_pick:
            continue
        q_size = parse_size(d_info['Size'])
        q_link = d_info['Url']
        links.append(q_link)
        size += q_size
    Path('data/links.txt').write_text('\n'.join(links))
    print(human_readable_size(size))

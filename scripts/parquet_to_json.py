import pyarrow.parquet as pq
import json

parquet_path = '/home/temp/_CODE/DPWH_2026_GAA/data/hierarchical_tree_leaf_nodes.parquet'
output_path = '/home/temp/_CODE/DPWH_2026_GAA/data/leaf_nodes.json'

print('Reading parquet file...')
table = pq.read_table(parquet_path)

print('Converting to dictionary...')
data = table.to_pydict()

print(f'Writing {len(next(iter(data.values())))} records to JSON...')
with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)

print('Done!')

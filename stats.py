
import glob
import sys
import os

all_files = glob.glob(os.path.join(sys.argv[1], '*.json'))
all_nids = [int(os.path.split(f)[1].replace('.json', '')) for f in all_files]
print('total', len(all_nids))
print('min', min(all_nids))
print('max', max(all_nids))

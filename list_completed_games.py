import json, glob
from datetime import datetime

files = glob.glob('game_data/*.json')
now = datetime.now()
current_month = now.strftime('%Y-%m')
found = False

print('--- Checking game_data files ---\n')
for f in files:
    data = json.load(open(f))
    ts = data.get('timestamp', '')
    if data.get('game_over', False) and ts.startswith(current_month):
        print('✔ {} | score={} | nickname={} | mode={} | subject={} | timestamp={}'.format(
            f, data.get('score'), data.get('nickname'), data.get('mode'), data.get('subject'), ts))
        found = True
    else:
        print('✗ {} | game_over={} | timestamp={}'.format(f, data.get('game_over', False), ts))
print('\n--- End of check ---\n')
if not found:
    print('No completed games for this month found.')

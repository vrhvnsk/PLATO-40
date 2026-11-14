"""Load synthetic PLATO-40 data without treating missing observations as zero."""
import json
from pathlib import Path
import pandas as pd

FILES = ['bookings','access_log','room_telemetry','room_water','water_main','energy',
         'weather','weather_forecast','tariff','equipment','logistics','staff_roster',
         'work_orders','guest_requests']

class Data:
    def __init__(self, directory):
        self.path = Path(directory)
        if not self.path.is_dir():
            raise FileNotFoundError(f'Data directory does not exist: {directory}')
        self.tables = {}
        for name in FILES:
            p = self.path / (name+'.csv')
            if p.exists():
                df = pd.read_csv(p).drop_duplicates().reset_index(drop=True)
                for col in df.columns:
                    if col.endswith('_utc'):
                        df[col] = pd.to_datetime(df[col],utc=True,errors='coerce')
                self.tables[name] = df
            else:
                self.tables[name] = pd.DataFrame()
        p = self.path/'events.jsonl'
        self.events = pd.DataFrame([json.loads(line) for line in p.read_text().splitlines() if line.strip()]) if p.exists() else pd.DataFrame()
        if 'timestamp_utc' in self.events:
            self.events['timestamp_utc'] = pd.to_datetime(self.events.timestamp_utc,utc=True,errors='coerce')
        self.building = self._json('building.json')
        self.manifest = self._json('manifest.json')

    def _json(self,name):
        p=self.path/name
        return json.loads(p.read_text()) if p.exists() else {}

    def __getitem__(self,key): return self.tables[key]

    def report(self):
        return {name: {'rows':len(df), 'columns':list(df.columns)} for name,df in self.tables.items()}

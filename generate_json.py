"""
generate_json.py
讀取 lem_raw.xlsx 的 lemdata 表，
依船（Navitec）→ 汽缸（Cyl）→ 日期 排序後，
對缺失值（None）用前3次平均補值，
最後輸出 data.json 供網頁使用。
"""
import openpyxl, json
from datetime import datetime, date

# ============================================================
# 1. 讀取 Excel
# ============================================================
wb = openpyxl.load_workbook(r'd:/AntiGravity/my project 2026/lem_raw.xlsx', read_only=True)
ws = wb['lemdata']
rows = list(ws.iter_rows(values_only=True))
header = list(rows[0])
data_rows = rows[1:]

# ============================================================
# 2. 轉換每列為 dict
# ============================================================
NUMERIC_COLS = ['BN_', 'Iron_', 'PQ-Index_', 'Chromium',
                'FeedRate', 'EngineLoad', 'FOSulphur', 'Water']

def parse_row(row):
    d = dict(zip(header, row))
    # 日期格式統一
    dt = d.get('DateSample')
    if isinstance(dt, datetime):
        d['DateSample'] = dt.strftime('%Y-%m-%d')
    elif dt is not None:
        d['DateSample'] = str(dt)
    else:
        d['DateSample'] = None
    # 數值欄位確保 float 或 None
    for col in NUMERIC_COLS:
        val = d.get(col)
        try:
            d[col] = float(val) if val is not None else None
        except (TypeError, ValueError):
            d[col] = None
    return d

all_records = [parse_row(r) for r in data_rows]

# ============================================================
# 3. 組織成 vessel → cyl → 時序列表
# ============================================================
def fill_missing(series, col):
    """
    對 series（已按日期排序的 list of dict）中，
    col 欄位為 None 的資料點，用前 3 筆有效值的平均補填。
    """
    values = []  # 已填好的歷史（有效值）
    for rec in series:
        v = rec[col]
        if v is None:
            if len(values) > 0:
                last3 = values[-3:]
                rec[col] = round(sum(last3) / len(last3), 4)
                rec['_imputed'] = rec.get('_imputed', [])
                rec['_imputed'].append(col)
        if rec[col] is not None:
            values.append(rec[col])
    return series

vessels_raw = {}
for rec in all_records:
    nav = str(rec['Navitec'])
    cyl = str(rec['Cyl'])
    if nav not in vessels_raw:
        vessels_raw[nav] = {
            'VesselName': rec['VesselName'],
            'IMO': rec['IMO'],
            'EngineMake': rec['EngineMake'],
            'EngineType': rec['EngineType'],
            'Owner': rec['Owner'],
            'cyls': {}
        }
    if cyl not in vessels_raw[nav]['cyls']:
        vessels_raw[nav]['cyls'][cyl] = []
    vessels_raw[nav]['cyls'][cyl].append(rec)

# 排序 + 補值
FILL_COLS = ['BN_', 'Iron_', 'PQ-Index_', 'Chromium']
vessels_out = {}
for nav, vdata in vessels_raw.items():
    cyls_out = {}
    for cyl, recs in vdata['cyls'].items():
        # 按日期排序，只保留 2024/1/1 之後的資料
        DATE_FROM = '2024-01-01'
        recs_sorted = sorted(
            [r for r in recs if r['DateSample'] and r['DateSample'] >= DATE_FROM],
            key=lambda x: x['DateSample']
        )
        # 補值
        for col in FILL_COLS:
            fill_missing(recs_sorted, col)
        # 只保留需要的欄位輸出
        cyls_out[cyl] = [
            {
                'date': r['DateSample'],
                'BN': r['BN_'],
                'Iron': r['Iron_'],
                'PQ': r['PQ-Index_'],
                'Cr': r['Chromium'],
                'Ni': r.get('Nickel'),
                'V': r.get('Vanadium'),
                'FeedRate': r['FeedRate'],
                'EngineLoad': r['EngineLoad'],
                'FOSulphur': r['FOSulphur'],
                'FOCategory': r['FOCategory'],
                'Catfine': r.get('Catfine'),
                'LOinSample': r.get('LOinSample'),
                'Water': r.get('Water'),
                'CylOil': r['CylinderOil'],
                'BNLevel': r['BNLevel'],
                'imputed': r.get('_imputed', [])
            }
            for r in recs_sorted
        ]
    vessels_out[nav] = {
        'VesselName': vdata['VesselName'],
        'IMO': vdata['IMO'],
        'EngineMake': vdata['EngineMake'],
        'EngineType': vdata['EngineType'],
        'Owner': vdata['Owner'],
        'cyls': cyls_out
    }

# ============================================================
# 4. 輸出為 JS 常數檔（避免 file:// CORS 限制）
# ============================================================
output_path = r'd:/AntiGravity/my project 2026/data.js'
json_str = json.dumps(vessels_out, ensure_ascii=False, indent=2, default=str)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f'/* 自動生成，請勿手動修改 */\nconst SDA_DATA = {json_str};\n')

print('Done! Output:', output_path)
total_points = sum(
    len(recs)
    for v in vessels_out.values()
    for recs in v['cyls'].values()
)
print(f'Total data points: {total_points}')
print('Vessels:')
for nav, v in vessels_out.items():
    cyls_count = len(v['cyls'])
    rec_count = sum(len(recs) for recs in v['cyls'].values())
    name = v['VesselName']
    eng  = v['EngineMake'] + ' ' + v['EngineType']
    print(f'  [{nav}] {name} ({eng}) | {cyls_count} cyls | {rec_count} records')

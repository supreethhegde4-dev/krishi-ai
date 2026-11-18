import json
import duckdb

con = duckdb.connect()
df_k = con.execute("""
    SELECT DISTINCT Market, District 
    FROM 'data/historical_parquet/parquet/2026.parquet' 
    WHERE State = 'Karnataka'
    ORDER BY District, Market
""").fetchdf()

print(f"Total unique Karnataka markets in 2026.parquet: {len(df_k)}")

# Known district/town lat-lons for Karnataka
geo_table = {
    # Bangalore Rural & Urban
    "Ramanagara": (12.7209, 77.2799),
    "Channapatana": (12.6518, 77.2089),
    "Channapatna": (12.6518, 77.2089),
    "Kanakapura": (12.5461, 77.4184),
    "Magadi": (12.9577, 77.2285),
    "Bangalore": (12.9716, 77.5946),
    "Binny Mill": (12.9719, 77.5684),
    "Yeshwantpur": (13.0285, 77.5460),
    "Doddaballa Pur": (13.2929, 77.5428),
    "Doddaballapur": (13.2929, 77.5428),
    "Devanahalli": (13.2484, 77.7126),
    "Hosakote": (13.0706, 77.7981),
    "Anekal": (12.7107, 77.6961),
    
    # Mandya & Mysore
    "Mandya": (12.5218, 76.8951),
    "Maddur": (12.5844, 77.0450),
    "Malavalli": (12.3871, 77.0583),
    "Pandavapura": (12.4975, 76.6698),
    "Srirangapatna": (12.4238, 76.6830),
    "KR Pet": (12.6644, 76.4912),
    "Nagamangala": (12.8228, 76.7578),
    "Mysore": (12.2958, 76.6394),
    "Bandipalya": (12.2745, 76.6660),
    "Nanjangud": (12.1200, 76.6800),
    "T.Narasipura": (12.2100, 76.9000),
    "Hunsur": (12.3080, 76.2910),
    "Periyapatna": (12.3400, 76.1000),
    "K.R.Nagar": (12.5800, 76.3800),

    # Kolar & Chikkaballapur
    "Kolar": (13.1358, 78.1291),
    "Chintamani": (13.4024, 78.0583),
    "Bangarpet": (12.9789, 78.1969),
    "Malur": (13.0031, 77.9392),
    "Mulabagilu": (13.1636, 78.3970),
    "Mulbagal": (13.1636, 78.3970),
    "Srinivaspur": (13.3366, 78.2144),
    "Chikkaballapur": (13.4325, 77.7275),
    "Gowribidanoor": (13.6133, 77.5186),
    "Bhagepalli": (13.7844, 77.7944),
    "Sidlaghatta": (13.3917, 77.8631),
    
    # Tumakuru & Hassan
    "Tumkur": (13.3379, 77.1173),
    "Tumakuru": (13.3379, 77.1173),
    "Kunigal": (13.0244, 77.0347),
    "Tiptur": (13.2564, 76.4789),
    "Sira": (13.7444, 76.9056),
    "Madhugiri": (13.6628, 77.2089),
    "Chiknayakanahalli": (13.4167, 76.6167),
    "Gubbi": (13.3117, 76.9397),
    "Turuvekere": (13.1600, 76.6700),
    "Pavagada": (14.1000, 77.2800),
    "Hassan": (13.0072, 76.0962),
    "Channarayapatna": (12.9058, 76.3892),
    "Arasikere": (13.3150, 76.2570),
    "Holenarasipura": (12.7880, 76.2420),
    "Sakleshpur": (12.9730, 75.7870),
    "Belur": (13.1650, 75.8640),
    "Arkalgud": (12.7660, 76.0590),

    # Chitradurga, Davangere, Shimoga
    "Chitradurga": (14.2251, 76.3980),
    "Hiriyur": (13.9458, 76.6214),
    "Challakere": (14.3167, 76.6500),
    "Hosadurga": (13.8000, 76.2900),
    "Davangere": (14.4644, 75.9218),
    "Harihar": (14.5125, 75.8036),
    "Shimoga": (13.9299, 75.5681),
    "Bhadravathi": (13.8400, 75.7000),
    "Shikaripura": (14.2700, 75.3500),
    "Sagar": (14.1667, 75.0333),
    
    # Chamrajnagar & Chikmagalur
    "Chamrajnagar": (11.9261, 76.9437),
    "Chamaraj Nagar": (11.9261, 76.9437),
    "Gundlupet": (11.8000, 76.6900),
    "Kollegal": (12.1558, 77.1147),
    "Yelandur": (12.0600, 77.0300),
    "Chikmagalur": (13.3153, 75.7754),
    "Chikkamagalore": (13.3153, 75.7754),
    "Kadur": (13.5500, 76.0100),
    "Tarikere": (13.7100, 75.8100),

    # Northern Karnataka
    "Haveri": (14.7964, 75.4018),
    "Ranebennur": (14.6231, 75.6214),
    "Byadgi": (14.6800, 75.4800),
    "Dharwad": (15.4589, 75.0078),
    "Hubli": (15.3647, 75.1240),
    "Belgaum": (15.8497, 74.4977),
    "Belagavi": (15.8497, 74.4977),
    "Bailhongal": (15.8167, 74.8667),
    "Gokak": (16.1667, 74.8333),
    "Bellary": (15.1394, 76.9214),
    "Ballari": (15.1394, 76.9214),
    "Hospet": (15.2689, 76.3909),
    "Koppal": (15.3475, 76.1550),
    "Gadag": (15.4167, 75.6333),
    "Bagalkot": (16.1800, 75.7000),
    "Bijapur": (16.8302, 75.7100),
    "Vijayapura": (16.8302, 75.7100),
    "Gulbarga": (17.3297, 76.8343),
    "Kalburgi": (17.3297, 76.8343),
    "Raichur": (16.2076, 77.3463),
    "Bidar": (17.9104, 77.5199),
    "Yadgir": (16.7700, 77.1400),
    
    # Coastal Karnataka
    "Mangalore": (12.9141, 74.8560),
    "Udupi": (13.3409, 74.7421),
    "Karwar": (14.8136, 74.1297),
    "Sirsi": (14.6195, 74.8354),
    "Kumta": (14.4267, 74.4089),
    "Puttur": (12.7667, 75.2000),
    "Bantwal": (12.8900, 75.0300)
}

with open("data/coordinates_cache.json", "r", encoding="utf-8") as f:
    cache = json.load(f)

count_added = 0
for idx, row in df_k.iterrows():
    m = row['Market']
    d = row['District']
    
    # Try finding matching coords
    matched = None
    for place, coords in geo_table.items():
        if place.lower() in m.lower() or place.lower() in d.lower():
            matched = coords
            break
            
    if not matched:
        # Default to district capital if available, else Ramanagara/Bangalore
        matched = geo_table.get(d, (12.9716, 77.5946))
        
    lat, lon = matched
    
    # Add variations to cache
    variations = [
        m,
        f"{m}, {d}, Karnataka",
        f"{m}, Karnataka",
        m.replace(" APMC", "").strip(),
        f"{m.replace(' APMC', '').strip()}, {d}, Karnataka"
    ]
    for v in variations:
        if v not in cache or (abs(cache[v].get("lat", 0) - 20.5937) < 0.01):
            cache[v] = {"lat": lat, "lon": lon, "market": m, "district": d, "state": "Karnataka"}
            count_added += 1

with open("data/coordinates_cache.json", "w", encoding="utf-8") as f:
    json.dump(cache, f, indent=2)

print(f"Successfully added/updated {count_added} Karnataka market coordinates in cache. Total cached now: {len(cache)}")

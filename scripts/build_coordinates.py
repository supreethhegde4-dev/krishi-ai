"""
Build coordinates cache for all markets in marketplace dataset and key farmer production hubs.
"""
import csv
import json
import os

# Known centroid coordinates for districts and major mandis in the dataset
DISTRICT_COORDS = {
    # Karnataka
    ("Karnataka", "Bangalore"): (12.9716, 77.5946),
    ("Karnataka", "Ramanagara"): (12.7209, 77.2799),
    ("Karnataka", "Kolar"): (13.1367, 78.1291),
    ("Karnataka", "Chintamani"): (13.4011, 78.0583),
    ("Karnataka", "Bangarpet"): (12.9796, 78.1969),
    ("Karnataka", "Kanakapura"): (12.5458, 77.4173),
    ("Karnataka", "Channapatna"): (12.6518, 77.2089),
    ("Karnataka", "Channapatana"): (12.6518, 77.2089),
    ("Karnataka", "Mulabagilu"): (13.1636, 78.3965),
    ("Karnataka", "Srinivasapur"): (13.3364, 78.2147),
    ("Karnataka", "Mysore"): (12.2958, 76.6394),
    ("Karnataka", "Mandya"): (12.5218, 76.8951),
    ("Karnataka", "Chamrajnagar"): (11.9261, 76.9437),
    ("Karnataka", "Chikmagalur"): (13.3161, 75.7720),
    ("Karnataka", "Shimoga"): (13.9299, 75.5681),
    ("Karnataka", "Kalburgi"): (17.3297, 76.8343),
    ("Karnataka", "Davangere"): (14.4644, 75.9218),
    
    # Gujarat
    ("Gujarat", "Amreli"): (21.6032, 71.2221),
    ("Gujarat", "Anand"): (22.5645, 72.9289),
    ("Gujarat", "Banaskanth"): (24.1724, 72.4346),
    ("Gujarat", "Bharuch"): (21.7051, 72.9959),
    ("Gujarat", "Dahod"): (22.8378, 74.2546),
    ("Gujarat", "Gandhinagar"): (23.2156, 72.6369),
    ("Gujarat", "Jamnagar"): (22.4707, 70.0577),
    ("Gujarat", "Junagarh"): (21.5222, 70.4579),
    ("Gujarat", "Kheda"): (22.7533, 72.6841),
    ("Gujarat", "Mehsana"): (23.5880, 72.3693),
    ("Gujarat", "Navsari"): (20.9467, 72.9520),
    ("Gujarat", "Patan"): (23.8493, 72.1266),
    ("Gujarat", "Rajkot"): (22.3039, 70.8022),
    ("Gujarat", "Sabarkantha"): (23.6823, 73.0458),
    ("Gujarat", "Surat"): (21.1702, 72.8311),
    ("Gujarat", "Vadodara"): (22.3072, 73.1812),

    # Haryana
    ("Haryana", "Fatehabad"): (29.5152, 75.4556),
    ("Haryana", "Gurgaon"): (28.4595, 77.0266),
    ("Haryana", "Hissar"): (29.1492, 75.7217),
    ("Haryana", "Kaithal"): (29.8015, 76.3996),
    ("Haryana", "Kurukshetra"): (29.9695, 76.8783),
    ("Haryana", "Mewat"): (28.1065, 76.9972),
    ("Haryana", "Palwal"): (28.1447, 77.3260),
    ("Haryana", "Panchkula"): (30.6942, 76.8606),
    ("Haryana", "Panipat"): (29.3909, 76.9635),
    ("Haryana", "Rewari"): (28.1833, 76.6167),
    ("Haryana", "Rohtak"): (28.8955, 76.6066),
    ("Haryana", "Sirsa"): (29.5349, 75.0298),
    ("Haryana", "Sonipat"): (28.9931, 77.0151),
    ("Haryana", "Yamuna Nagar"): (30.1290, 77.2674),
    ("Haryana", "Karnal"): (29.6857, 76.9905),

    # Punjab
    ("Punjab", "Amritsar"): (31.6340, 74.8723),
    ("Punjab", "Fazilka"): (30.4037, 74.0254),
    ("Punjab", "Ferozepur"): (30.9237, 74.6065),
    ("Punjab", "Gurdaspur"): (32.0419, 75.4053),
    ("Punjab", "Hoshiarpur"): (31.5273, 75.9149),
    ("Punjab", "Jalandhar"): (31.3260, 75.5762),
    ("Punjab", "Kapurthala"): (31.3802, 75.3814),
    ("Punjab", "Ludhiana"): (30.9010, 75.8573),
    ("Punjab", "Mansa"): (29.9880, 75.3934),
    ("Punjab", "Moga"): (30.8165, 75.1717),
    ("Punjab", "Muktsar"): (30.4744, 74.5165),
    ("Punjab", "Patiala"): (30.3398, 76.3869),
    ("Punjab", "Ropar (Rupnagar)"): (30.9664, 76.5331),
    ("Punjab", "Sangrur"): (30.2458, 75.8421),

    # Uttar Pradesh
    ("Uttar Pradesh", "Agra"): (27.1767, 78.0081),
    ("Uttar Pradesh", "Aligarh"): (27.8974, 78.0880),
    ("Uttar Pradesh", "Amroha"): (28.9044, 78.4684),
    ("Uttar Pradesh", "Badaun"): (28.0315, 79.1235),
    ("Uttar Pradesh", "Bijnor"): (29.3724, 78.1358),
    ("Uttar Pradesh", "Bulandshahar"): (28.4069, 77.8498),
    ("Uttar Pradesh", "Etah"): (27.5614, 78.6653),
    ("Uttar Pradesh", "Etawah"): (26.7855, 79.0215),
    ("Uttar Pradesh", "Farukhabad"): (27.3826, 79.5833),
    ("Uttar Pradesh", "Firozabad"): (27.1592, 78.3957),
    ("Uttar Pradesh", "Gautam Budh Nagar"): (28.3500, 77.5500),
    ("Uttar Pradesh", "Ghaziabad"): (28.6692, 77.4538),
    ("Uttar Pradesh", "Hathras"): (27.5968, 78.0519),
    ("Uttar Pradesh", "Jhansi"): (25.4484, 78.5685),
    ("Uttar Pradesh", "Kanpur"): (26.4499, 80.3319),
    ("Uttar Pradesh", "Lakhimpur"): (27.9462, 80.7777),
    ("Uttar Pradesh", "Lucknow"): (26.8467, 80.9462),
    ("Uttar Pradesh", "Mathura"): (27.4924, 77.6737),
    ("Uttar Pradesh", "Meerut"): (28.9845, 77.7064),
    ("Uttar Pradesh", "Moradabad"): (28.8386, 78.7733),
    ("Uttar Pradesh", "Muzaffarnagar"): (29.4727, 77.7085),
    ("Uttar Pradesh", "Prayagraj"): (25.4358, 81.8463),
    ("Uttar Pradesh", "Saharanpur"): (29.9640, 77.5460),
    ("Uttar Pradesh", "Shahjahanpur"): (27.8805, 79.9120),
    ("Uttar Pradesh", "Varanasi"): (25.3176, 82.9739),
    ("Uttar Pradesh", "Maharajganj"): (27.1444, 83.5622),
    ("Uttar Pradesh", "Bareilly"): (28.3670, 79.4304),
    ("Uttar Pradesh", "Balrampur"): (27.4302, 82.1812),

    # Kerala
    ("Kerala", "Alappuzha"): (9.4981, 76.3388),
    ("Kerala", "Ernakulam"): (9.9816, 76.2999),
    ("Kerala", "Idukki"): (9.8494, 76.9810),
    ("Kerala", "Kannur"): (11.8745, 75.3704),
    ("Kerala", "Kasaragod"): (12.5102, 74.9852),
    ("Kerala", "Kollam"): (8.8932, 76.6141),
    ("Kerala", "Kottayam"): (9.5916, 76.5222),
    ("Kerala", "Kozhikode(Calicut)"): (11.2588, 75.7804),
    ("Kerala", "Malappuram"): (11.0510, 76.0711),
    ("Kerala", "Palakkad"): (10.7867, 76.6548),
    ("Kerala", "Pathanamthitta"): (9.2648, 76.7870),
    ("Kerala", "Thirssur"): (10.5276, 76.2144),
    ("Kerala", "Thiruvananthapuram"): (8.5241, 76.9366),
    ("Kerala", "Wayanad"): (11.6854, 76.1320),

    # Odisha
    ("Odisha", "Balasore"): (21.4934, 86.9135),
    ("Odisha", "Bargarh"): (21.3333, 83.6167),
    ("Odisha", "Bhadrak"): (21.0574, 86.5160),
    ("Odisha", "Boudh"): (20.8407, 84.3262),
    ("Odisha", "Dhenkanal"): (20.6667, 85.6000),
    ("Odisha", "Ganjam"): (19.3833, 85.0667),
    ("Odisha", "Jajpur"): (20.8500, 86.3333),
    ("Odisha", "Keonjhar"): (21.6289, 85.5817),
    ("Odisha", "Khurda"): (20.1812, 85.6214),
    ("Odisha", "Mayurbhanja"): (21.9287, 86.7369),
    ("Odisha", "Nayagarh"): (20.1251, 85.1070),
    ("Odisha", "Puri"): (19.8135, 85.8312),
    ("Odisha", "Sambalpur"): (21.4669, 83.9812),

    # Rajasthan
    ("Rajasthan", "Beawar"): (26.1012, 74.3218),
    ("Rajasthan", "Chittorgarh"): (24.8887, 74.6269),
    ("Rajasthan", "Churu"): (28.2900, 74.9600),
    ("Rajasthan", "Deeg"): (27.4728, 77.3258),
    ("Rajasthan", "Ganganagar"): (29.9038, 73.8772),
    ("Rajasthan", "Hanumangarh"): (29.5816, 74.3294),
    ("Rajasthan", "Jaipur"): (26.9124, 75.7873),
    ("Rajasthan", "Jaipur Rural"): (26.9124, 75.7873),
    ("Rajasthan", "Jalore"): (25.3444, 72.6156),
    ("Rajasthan", "Jhunjhunu"): (28.1289, 75.3995),
    ("Rajasthan", "Jodhpur"): (26.2389, 73.0243),
    ("Rajasthan", "Kotputli Behror"): (27.7058, 76.2025),
    ("Rajasthan", "Nagaur"): (27.2070, 73.7423),
    ("Rajasthan", "Sikar"): (27.6094, 75.1399),

    # Himachal Pradesh
    ("Himachal Pradesh", "Chamba"): (32.5534, 76.1258),
    ("Himachal Pradesh", "Hamirpur"): (31.6862, 76.5213),
    ("Himachal Pradesh", "Kangra"): (32.0998, 76.2691),
    ("Himachal Pradesh", "Kullu"): (31.9579, 77.1095),
    ("Himachal Pradesh", "Solan"): (30.9045, 77.0967),

    # Telangana
    ("Telangana", "Adilabad"): (19.6641, 78.5320),
    ("Telangana", "Hyderabad"): (17.3850, 78.4867),
    ("Telangana", "Karimnagar"): (18.4386, 79.1288),
    ("Telangana", "Khammam"): (17.2473, 80.1514),
    ("Telangana", "Mahbubnagar"): (16.7488, 77.9847),
    ("Telangana", "Nalgonda"): (17.0577, 79.2684),
    ("Telangana", "Nizamabad"): (18.6725, 78.0941),
    ("Telangana", "Ranga Reddy"): (17.3000, 78.4000),
    ("Telangana", "Warangal"): (17.9689, 79.5941),

    # Andhra Pradesh
    ("Andhra Pradesh", "Anantapur"): (14.6819, 77.6006),
    ("Andhra Pradesh", "Chittor"): (13.2172, 79.1003),
    ("Andhra Pradesh", "East Godavari"): (17.0005, 81.8040),
    ("Andhra Pradesh", "Kurnool"): (15.8281, 78.0373),
    ("Andhra Pradesh", "Nellore"): (14.4426, 79.9865),
    ("Andhra Pradesh", "Prakasam"): (15.5057, 80.0499),
    ("Andhra Pradesh", "Visakhapatnam"): (17.6868, 83.2185),

    # Uttrakhand
    ("Uttrakhand", "Champawat"): (29.3364, 80.0914),
    ("Uttrakhand", "Dehradoon"): (30.3165, 78.0322),
    ("Uttrakhand", "Haridwar"): (29.9457, 78.1642),
    ("Uttrakhand", "Nanital"): (29.3919, 79.4542),
    ("Uttrakhand", "UdhamSinghNagar"): (28.9800, 79.4000),

    # West Bengal
    ("West Bengal", "Bankura"): (23.2324, 87.0716),
    ("West Bengal", "Hooghly"): (22.8963, 88.2461),
    ("West Bengal", "Jalpaiguri"): (26.5414, 88.7196),
    ("West Bengal", "Jhargram"): (22.4500, 86.9833),
    ("West Bengal", "Malda"): (25.0108, 88.1411),
    ("West Bengal", "Murshidabad"): (24.1759, 88.2802),
    ("West Bengal", "Nadia"): (23.4710, 88.5565),
    ("West Bengal", "Paschim Bardhaman"): (23.6871, 86.9746),
    ("West Bengal", "Purba Bardhaman"): (23.2324, 87.8615),
    ("West Bengal", "Puruliya"): (23.3321, 86.3652),

    # Jammu and Kashmir
    ("Jammu and Kashmir", "Kathua"): (32.3866, 75.5222),
    ("Jammu and Kashmir", "Rajouri"): (33.3768, 74.3129),

    # Madhya Pradesh
    ("Madhya Pradesh", "Morena"): (26.4950, 77.9940),

    # Nagaland
    ("Nagaland", "Kohima"): (25.6751, 94.1086),

    # Tripura
    ("Tripura", "Dhalai"): (23.9000, 88.7000),
    ("Tripura", "Gomati"): (23.5350, 91.4900),
    ("Tripura", "Khowai"): (24.0625, 91.6053),
    ("Tripura", "North Tripura"): (24.2800, 92.1700),
    ("Tripura", "South District"): (23.2500, 91.5000),
}

# Specific town/market offsets or accurate coords
SPECIFIC_MARKETS = {
    "Ramanagara": (12.7209, 77.2799),
    "Ramanagara APMC": (12.7225, 77.2810),
    "Binny Mill (F&V), Bangalore": (12.9698, 77.5684),
    "Binny Mill (F&V), Bangalore APMC": (12.9698, 77.5684),
    "Kolar": (13.1367, 78.1291),
    "Kolar APMC": (13.1380, 78.1310),
    "Chintamani": (13.4011, 78.0583),
    "Chintamani APMC": (13.4020, 78.0600),
    "Bangarpet": (12.9796, 78.1969),
    "Kanakapura": (12.5458, 77.4173),
    "Channapatana": (12.6518, 77.2089),
    "Mulabagilu": (13.1636, 78.3965),
    "Srinivasapur": (13.3364, 78.2147),
    "Mansa(Manas Veg Yard)": (23.4264, 72.7936),
    "Bilimora": (20.7634, 72.9693),
    "Rajkot(Veg.Sub Yard)": (22.3039, 70.8022),
    "Damnagar": (21.7011, 71.5133),
    "Savarkundla": (21.3328, 71.3090),
    "Khambhat(Grain Market)": (22.3131, 72.6186),
    "Vadgam": (24.0833, 72.4833),
    "Jambusar(Kaavi)": (22.0500, 72.8000),
    "Modasa(Tintoi)": (23.4636, 73.3006),
    "Mahuva(Anaval)": (21.0833, 71.7667),
    "Achnera": (27.1833, 77.7667),
    "Ajuha": (25.5667, 81.3167),
    "Ahmedgarh": (30.6833, 75.8333),
    "Angamaly": (10.1852, 76.3869),
    "Palampur": (32.1109, 76.5363),
    "North Paravur": (10.1444, 76.2294),
    "Kottakkal": (11.0000, 76.0000),
    "Koduvayoor": (10.6833, 76.6833),
    "Kangra(Jaisinghpur)": (31.9000, 76.6000),
}


def build_cache():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "marketplace_extracted", "commodity_price.csv")
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "coordinates_cache.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    cache = {}
    
    # Add major origin towns
    cache["Ramanagara, Karnataka"] = {"lat": 12.7209, "lon": 77.2799, "type": "origin"}
    cache["Kolar, Karnataka"] = {"lat": 13.1367, "lon": 78.1291, "type": "origin"}
    cache["Bangalore, Karnataka"] = {"lat": 12.9716, "lon": 77.5946, "type": "origin"}
    cache["Anand, Gujarat"] = {"lat": 22.5645, "lon": 72.9289, "type": "origin"}
    cache["Agra, Uttar Pradesh"] = {"lat": 27.1767, "lon": 78.0081, "type": "origin"}
    cache["Karnal, Haryana"] = {"lat": 29.6857, "lon": 76.9905, "type": "origin"}

    if os.path.exists(csv_path):
        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                market = row["Market"]
                district = row["District"]
                state = row["State"]
                
                key_full = f"{market}, {district}, {state}"
                key_market_state = f"{market}, {state}"
                key_market = market
                
                lat, lon = None, None
                
                # 1. Exact market lookup
                if market in SPECIFIC_MARKETS:
                    lat, lon = SPECIFIC_MARKETS[market]
                # 2. District lookup
                elif (state, district) in DISTRICT_COORDS:
                    lat, lon = DISTRICT_COORDS[(state, district)]
                # 3. State centroid fallback
                else:
                    for (s, d), (cla, clo) in DISTRICT_COORDS.items():
                        if s == state:
                            lat, lon = cla, clo
                            break
                            
                if lat is not None and lon is not None:
                    loc_info = {
                        "lat": round(lat, 5),
                        "lon": round(lon, 5),
                        "market": market,
                        "district": district,
                        "state": state
                    }
                    cache[key_full] = loc_info
                    cache[key_market_state] = loc_info
                    cache[key_market] = loc_info

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)
        
    print(f"Coordinates cache built with {len(cache)} entries -> {out_path}")

if __name__ == "__main__":
    build_cache()

import requests
import json
import time

print("=== REAL EXTERNAL API REACHABILITY AUDIT ===")

# 1. Open-Meteo Weather API
print("\n[1] Testing Open-Meteo Weather API...")
try:
    url = "https://api.open-meteo.com/v1/forecast?latitude=12.7209&longitude=77.2799&current_weather=true"
    t0 = time.time()
    r = requests.get(url, timeout=6)
    dur = time.time() - t0
    print(f"  Status: HTTP {r.status_code} ({dur:.2f}s)")
    if r.status_code == 200:
        data = r.json().get("current_weather", {})
        print(f"  Live Reading: {data.get('temperature')}°C, wind: {data.get('windspeed')} km/h, time: {data.get('time')}")
    else:
        print(f"  Error: {r.text[:100]}")
except Exception as e:
    print(f"  FAILED: {e}")

# 2. NASA POWER Agroclimatology API
print("\n[2] Testing NASA POWER API...")
try:
    url = "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,ALLSKY_SFC_SW_DWN&community=AG&longitude=77.2799&latitude=12.7209&start=20260401&end=20260405&format=JSON"
    t0 = time.time()
    r = requests.get(url, timeout=8)
    dur = time.time() - t0
    print(f"  Status: HTTP {r.status_code} ({dur:.2f}s)")
    if r.status_code == 200:
        p_dict = r.json().get("properties", {}).get("parameter", {})
        t2m = list(p_dict.get("T2M", {}).values())
        print(f"  Live Records: {len(t2m)} data points retrieved. Sample T2M: {t2m[:2]}")
    else:
        print(f"  Error: {r.text[:100]}")
except Exception as e:
    print(f"  FAILED: {e}")

# 3. data.gov.in AGMARKNET Resource
print("\n[3] Testing data.gov.in (Unauthenticated Request)...")
try:
    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?format=json&limit=2"
    t0 = time.time()
    r = requests.get(url, timeout=6)
    dur = time.time() - t0
    print(f"  Status: HTTP {r.status_code} ({dur:.2f}s)")
    print(f"  Response Preview: {r.text[:120]}")
except Exception as e:
    print(f"  FAILED: {e}")

# 4. OpenRouteService Matrix API (Unauthenticated Request)
print("\n[4] Testing OpenRouteService (Unauthenticated Request)...")
try:
    url = "https://api.heigit.org/openrouteservice/v2/matrix/driving-car"
    t0 = time.time()
    r = requests.post(url, json={"locations": [[77.2799, 12.7209], [77.5946, 12.9716]]}, timeout=6)
    dur = time.time() - t0
    print(f"  Status: HTTP {r.status_code} ({dur:.2f}s)")
    print(f"  Response Preview: {r.text[:120]}")
except Exception as e:
    print(f"  FAILED: {e}")

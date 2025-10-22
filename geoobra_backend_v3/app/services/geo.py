import math
from typing import Tuple

def haversine_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    if None in a or None in b:
        return 999999.0
    lat1, lon1 = a
    lat2, lon2 = b
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    s = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    c = 2 * math.asin(min(1, math.sqrt(s)))
    return R * c


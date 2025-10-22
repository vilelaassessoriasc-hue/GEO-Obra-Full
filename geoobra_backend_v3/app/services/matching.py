import math
from typing import List, Dict, Optional

def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dLat = math.radians((lat2 - lat1))
    dLng = math.radians((lng2 - lng1))
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLng/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def rank_users_within_radius(users: List[Dict], center: Dict, radius_km: Optional[float]) -> List[Dict]:
    out = []
    for u in users:
        if u.get("lat") is None or u.get("lng") is None:
            continue
        if center.get("lat") is None or center.get("lng") is None:
            continue
        dist = haversine_km(center["lat"], center["lng"], u["lat"], u["lng"])
        if radius_km is None or dist <= radius_km:
            score = 1.0 / (1.0 + dist)
            out.append({**u, "distance_km": dist, "score": score})
    out.sort(key=lambda x: x["score"], reverse=True)
    return out

import math

# Calculates the distance (in miles) between two geo coordinates.
# http://stackoverflow.com/questions/365826/calculate-distance-between-2-gps-coordinates
def haversine_miles(lat1, lon1, lat2, lon2):
    R = 3956;
    dLat = math.radians(lat2-lat1)
    dLon = math.radians(lon2-lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    a = math.sin(dLat/2) * math.sin(dLat/2) + \
            math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2);
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
    d = R * c;
    return d

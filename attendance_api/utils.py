from math import radians, cos, sin, asin, sqrt

def measuring_radius(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        sqr_root = 2 * asin(sqrt(a)) 
        radius_of_earth = 6371 # Radius of earth in kilometers. Use 3956 for miles

        distance_in_km = sqr_root * radius_of_earth
        distance_in_meters = distance_in_km*1000
        return distance_in_meters

from astropy import units as u
from astropy.coordinates import SkyCoord, AltAz, EarthLocation, ICRS, Latitude, Longitude
import astropy
import time

# Lat, Long and Height of the MRO scope.
LOCATION = (46.95108305039964, -120.7245251074869, 1198)

# Underlying telescope object to store the state of the telescope.
class telescope:
    def __init__(self):
        # global dummy variables for telescope state
        # assume we are parked as the initial state.
        self.park = True
        self.tracking = False

        # SkyCoord of the telescope
        # Spec defines frame as in JNow, not ICRS, ask about that
        self.coords = SkyCoord(ra=0.0 * u.hourangle, dec=0.0 * u.deg, frame='icrs')

        # motor mode
        self.blinky = False
    
    def set_coords(self, RA, Dec):
        self.coords = SkyCoord(ra=RA * u.hourangle, dec=Dec * u.deg, frame='icrs')
    
    # note: first call of set_azalt will download iers data. it'll be slow
    def set_azalt(self, Az, Alt):
        loc = EarthLocation.from_geodetic(lon=LOCATION[1], lat=LOCATION[0], height=LOCATION[2])
        altaz = AltAz(pressure=0, location=loc, obstime=astropy.time.Time(time.time(), format='unix'))
        self.coords = SkyCoord(alt=Latitude(Alt, unit='deg'), az=Longitude(Az, unit='deg'), frame=altaz)
        # transform to ra / dec (icrs)
        self.coords = self.coords.transform_to('icrs')

    def __str__(self):
        return f"{self.park}, {self.tracking}, {self.coords.ra / 15}, {self.coords.dec}, {self.blinky}"

t = telescope()
t.set_azalt(1, 20)
print(t)
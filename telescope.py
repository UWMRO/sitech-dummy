from astropy import units as u
from astropy.coordinates import SkyCoord, AltAz, EarthLocation, Latitude, Longitude
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

        # tracking rate
        # assume we are not tracking in initial state. 
        # (therefore we are not tracking @ sidereal rate)
        self.ra_tracking_sidereal = False
        self.dec_tracking_sidereal = False

        # EarthLocation of the scope.
        loc = EarthLocation.from_geodetic(lon=LOCATION[1], 
                                          lat=LOCATION[0], 
                                          height=LOCATION[2])
        # Alt-Az reference frame for the scope.
        self.altaz = AltAz(pressure=0, 
                           location=loc, 
                           obstime=astropy.time.Time(time.time(), format='unix'))
    
    # Sets RA / Dec with degree values.
    def set_coords(self, RA, Dec):
        self.coords = SkyCoord(ra=RA * u.deg, dec=Dec * u.deg, frame='icrs')
    
    # Note: first call of set_azalt will download IERS data. it'll be slow
    def set_azalt(self, Az, Alt):
        self.coords = SkyCoord(alt=Latitude(Alt, unit='deg'), 
                               az=Longitude(Az, unit='deg'), 
                               frame=self.altaz)
        # transform to ra / dec (icrs)
        self.coords = self.coords.transform_to('icrs')

    # Standard string implementation.
    def __str__(self):
        # boolParms:
        boolParms = 0
        # Bit 00 (initialized)
        boolParms += 1
        # Bit 01 (tracking)
        if self.tracking:
            boolParms += 2
        # Bit 04 (parked)
        if self.park:
            boolParms += 16
        # Bit 06 (blinky)
        if self.blinky:
            boolParms += 64
        # Bit 15 (tracking at offset rate)
        if not (self.ra_tracking_sidereal and self.dec_tracking_sidereal):
            boolParms += 32768
        
        altaz = self.coords.transform_to(self.altaz)
        # verify ra is in hours regardless of azalt / ra / dec
        return f"{boolParms};{self.coords.ra.hourangle};{self.coords.dec.value};{altaz.alt.value};{altaz.az.value}"
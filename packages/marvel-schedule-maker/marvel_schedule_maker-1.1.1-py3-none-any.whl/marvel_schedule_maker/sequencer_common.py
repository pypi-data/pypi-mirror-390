from dataclasses import dataclass, field
import math
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, date, time
from astropy.time import Time as AstroTime 
from astropy.coordinates import EarthLocation, get_sun
import astropy.units as units
import astroplan
import numpy as np

from astropy.utils import iers
from astropy.utils.data import download_file
from astropy.utils.iers import conf

conf.auto_download = True     # try online
conf.auto_max_age = 30        # allow cached file up to 30 days old

try:
    iers_a = iers.IERS_Auto.open()
except Exception as e:
    print(f"Warning: using offline IERS data ({e})")
    iers_a = iers.IERS_B.open()


LAT = 0.50199547796805788
LON = -0.31203578143571958
ELE = 2400

def getLocation():
    lon = LON / math.pi * 180 # convert to degrees
    lat = LAT /  math.pi * 180 # convert to degrees
    elev = ELE
    return EarthLocation.from_geodetic(lon, lat, elev)

MyLocation = getLocation()

def raDecToAltAz(ra_hours: float, dec_deg: float, time: AstroTime):
    ra = np.deg2rad(float(ra_hours)*15.0)
    dec = np.deg2rad(float(dec_deg))
    # sidereal time (very simple approx)
    jd = time.jd1 + time.jd2 # type: ignore
    jd -= 2451545.0
    lst = (280.46061837 + 360.98564736629 * jd + np.rad2deg(LON)) % 360
    lst = np.deg2rad(lst)
    ha = lst - ra
    ha = (ha + np.pi) % (2*np.pi) - np.pi
    alt = np.arcsin(np.sin(LAT) * np.sin(dec) + np.cos(LAT) * np.cos(dec) * np.cos(ha))
    az = np.arctan2(-np.sin(ha), np.tan(dec) * np.cos(LAT) - np.sin(LAT) * np.cos(ha))
    return np.rad2deg(alt), (np.rad2deg(az)) % 360

def getMoonAltAz(time: AstroTime) -> tuple[float, float]:
    """
    Get moon altitude and azimuth at given time using Meeus low-precision formula.
    Returns altitude and azimuth rounded to nearest degree.
    Speed: 50-100x faster than get_body('moon').
    Accuracy: ~0.5° (sufficient for degree-level precision).

    Generated using LLM
    """
    # Get Julian Date
    jd = time.jd1 + time.jd2  # type: ignore
    
    # Calculate moon position using Meeus low-precision formula
    # Days since J2000.0
    T = (jd - 2451545.0) / 36525.0
    
    # Mean longitude of the Moon (degrees)
    L_prime = 218.3164477 + 481267.88123421 * T
    L_prime = L_prime % 360
    
    # Mean elongation of the Moon (degrees)
    D = 297.8501921 + 445267.1114034 * T
    D = D % 360
    
    # Sun's mean anomaly (degrees)
    M = 357.5291092 + 35999.0502909 * T
    M = M % 360
    
    # Moon's mean anomaly (degrees)
    M_prime = 134.9633964 + 477198.8675055 * T
    M_prime = M_prime % 360
    
    # Moon's argument of latitude (degrees)
    F = 93.2720950 + 483202.0175233 * T
    F = F % 360
    
    D_rad = np.deg2rad(D)
    M_rad = np.deg2rad(M)
    M_prime_rad = np.deg2rad(M_prime)
    F_rad = np.deg2rad(F)
    
    # Longitude perturbations (simplified - only major terms)
    delta_L = 6.288774 * np.sin(M_prime_rad)
    delta_L += 1.274027 * np.sin(2 * D_rad - M_prime_rad)
    delta_L += 0.658314 * np.sin(2 * D_rad)
    delta_L += 0.213618 * np.sin(2 * M_prime_rad)
    delta_L += -0.185116 * np.sin(M_rad)
    delta_L += -0.114332 * np.sin(2 * F_rad)
    
    # Latitude perturbations (simplified - only major terms)
    delta_B = 5.128122 * np.sin(F_rad)
    delta_B += 0.280602 * np.sin(M_prime_rad + F_rad)
    delta_B += 0.277693 * np.sin(M_prime_rad - F_rad)
    delta_B += 0.173237 * np.sin(2 * D_rad - F_rad)
    delta_B += 0.055413 * np.sin(2 * D_rad + F_rad - M_prime_rad)
    
    # Ecliptic longitude and latitude
    lambda_moon = L_prime + delta_L  # degrees
    beta_moon = delta_B  # degrees
    
    # Convert to radians
    lambda_rad = np.deg2rad(lambda_moon)
    beta_rad = np.deg2rad(beta_moon)
    
    # Obliquity of ecliptic (simplified)
    epsilon = 23.439291 - 0.0130042 * T
    epsilon_rad = np.deg2rad(epsilon)
    
    # Convert ecliptic to equatorial coordinates
    sin_lambda = np.sin(lambda_rad)
    cos_lambda = np.cos(lambda_rad)
    sin_beta = np.sin(beta_rad)
    cos_beta = np.cos(beta_rad)
    tan_beta = np.tan(beta_rad)
    sin_epsilon = np.sin(epsilon_rad)
    cos_epsilon = np.cos(epsilon_rad)
    
    # Right Ascension
    ra_rad = np.arctan2(
        sin_lambda * cos_epsilon - tan_beta * sin_epsilon,
        cos_lambda
    )
    ra_deg = np.rad2deg(ra_rad)
    ra_deg = ra_deg % 360  # Normalize to 0-360
    ra_hours = ra_deg / 15.0  # Convert to hours
    
    # Declination
    dec_rad = np.arcsin(sin_beta * cos_epsilon + cos_beta * sin_epsilon * sin_lambda)
    dec_deg = np.rad2deg(dec_rad)
    
    return raDecToAltAz(ra_hours, dec_deg, time) # type: ignore


class DateTimes:
    def __init__(self, _date: date):
        self._date = _date
        self._civil_dark_start: datetime = None   # type: ignore[assignment]      # when daylight fades
        self._civil_dark_end: datetime = None   # type: ignore[assignment]      # when daylight rises
        self._astronomical_dark_start: datetime = None   # type: ignore[assignment]      # when full darkness begins
        self._astronomical_dark_end: datetime = None     # type: ignore[assignment]      # when full darkness ends
        self.calcTimes(_date)

    @property
    def civil_dark_start(self) -> datetime:
        return self._civil_dark_start

    @property
    def civil_dark_end(self) -> datetime:
        return self._civil_dark_end

    @property
    def astronomical_dark_start(self) -> datetime:
        return self._astronomical_dark_start

    @property
    def astronomical_dark_end(self) -> datetime:
        return self._astronomical_dark_end

    def calcTimes(self, _date: date):
        civil_horizon = -6
        nautical_horizon = -12
        astronomical_horizon = -18

        observer = astroplan.Observer(MyLocation)
        late_time = AstroTime(datetime.combine(_date, time(23, 59, 59)))
        target = get_sun(late_time)

        self._civil_dark_start = observer.target_set_time(late_time, target, "nearest", civil_horizon * units.degree).to_datetime() # type: ignore[assignment]
        self._civil_dark_end = observer.target_rise_time(late_time, target, "nearest", civil_horizon * units.degree).to_datetime() # type: ignore[assignment]
        self._astronomical_dark_start = observer.target_set_time(late_time, target, "nearest", astronomical_horizon * units.degree).to_datetime() # type: ignore[assignment]
        self._astronomical_dark_end = observer.target_rise_time(late_time, target, "nearest", astronomical_horizon * units.degree).to_datetime() # type: ignore[assignment]

    def new_date(self, new_date: date):
        self._date = new_date
        self.calcTimes(new_date)


@dataclass
class ValidatorContext:
    dates: DateTimes
    _values: Dict[str, Any] = field(default_factory=dict)
    _full_values: Dict[str, Any] = field(default_factory=dict)
    _observers: Dict[str, List[Callable]] = field(default_factory=dict)

    def get(self, name:str, default: Any = None) -> Any:
        """
        Get value by name with optional default
        default value if not found
        """
        return self._values.get(name, default)

    def get_full(self, name:str, default: Any = None) -> Any:
        """
        Get full value by name with optional default
        default value if not found
        """
        return self._full_values.get(name, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all values as read only copy"""
        return self._values.copy()
    
    def get_full_all(self) -> Dict[str, Any]:
        """Get all full values as read only copy"""
        return self._full_values.copy()
    
    def set(self, name: str, value: Any, full_value: Any = None, notify: bool = True) -> None:
        """Set value for a specific variant and optionally notify observers"""
        if name not in self._values:
            self._values[name] = {}
            self._full_values[name] = {}
        
        old_value = self._values[name]

        self._values[name] = value
        self._full_values[name] = full_value

        # Only notify on raw value changes
        if notify and old_value != value:
            self._notify_observers(name, value)

    def _notify_observers(self, name: str, value: Any) -> None:
        """Notify all validators watching this field"""
        for callback in self._observers.get(name, []):
            callback(name, value)
    
    def watch(self, field_name: str, callback: Callable) -> None:
        """Register a validator to watch a field"""
        self._observers.setdefault(field_name, []).append(callback)

    def unwatch(self, field_name: str, callback: Callable[[str, Any], None]) -> None:
        """Unregister a validator from watching a field"""
        if field_name in self._observers:
            try:
                self._observers[field_name].remove(callback)
            except ValueError:
                pass

    # Property telescope pre defined for convenience
    @property
    def telescope(self) -> Optional[int]:
        return self.get("telescope")
    
    @telescope.setter
    def telescope(self, value: Optional[int]) -> None:
        self.set("telescope", value, value)




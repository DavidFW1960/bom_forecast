"""
Support for Australian BOM (Bureau of Meteorology) weather forecast service.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.bom_forecast
"""
import datetime
import ftplib
import logging
import re
import xml

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_MONITORED_CONDITIONS, TEMP_CELSIUS, CONF_NAME, ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME, ATTR_ENTITY_ID, CONF_LATITUDE, CONF_LONGITUDE, CONF_ICON)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_FIND_QUERY = "./forecast/area[@type='location']/forecast-period[@index='{}']/*[@type='{}']"
_FIND_QUERY_2 = "./forecast/area[@type='metropolitan']/forecast-period[@index='{}']/text[@type='forecast']"
            
_LOGGER = logging.getLogger(__name__)

ATTR_ICON = 'icon'
ATTR_ISSUE_TIME_LOCAL = 'issue_time_local'
ATTR_PRODUCT_ID = 'product_id'
ATTR_PRODUCT_LOCATION = 'product_location'
ATTR_PRODUCT_NAME = 'product_name'
ATTR_SENSOR_ID = 'sensor_id'
ATTR_START_TIME_LOCAL = 'start_time_local'

CONF_ATTRIBUTION = 'Data provided by the Australian Bureau of Meteorology'
CONF_DAYS = 'forecast_days'
CONF_PRODUCT_ID = 'product_id'
CONF_REST_OF_TODAY = 'rest_of_today'
CONF_FRIENDLY = 'friendly'

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(minutes=120)

PRODUCT_ID_LAT_LON_LOCATION = {
    'IDD10150': [-12.47, 130.85, 'Darwin'],
    'IDN10035': [-35.31, 149.20, 'Canberra'],
    'IDN10064': [-33.86, 151.21, 'Sydney'],
    'IDN11051': [-32.89, 151.71, 'Newcastle'],
    'IDN11052': [-33.44, 151.36, 'Central Coast'],
    'IDN11053': [-34.56, 150.79, 'Wollongong'],
    'IDN11055': [-36.49, 148.29, 'Alpine Centres'],
    'IDQ10095': [-27.48, 153.04, 'Brisbane'],
    'IDQ10610': [-27.94, 153.43, 'Gold Coast'],
    'IDQ10611': [-26.60, 153.09, 'Sunshine Coast'],
    'IDS10034': [-34.93, 138.58, 'Adelaide'],
    'IDT13600': [-42.89, 147.33, 'Hobart'],
    'IDT13610': [-41.42, 147.12, 'Launceston'],
    'IDV10450': [-37.83, 144.98, 'Melbourne'],
    'IDV10701': [-38.17, 144.38, 'Geelong'],
    'IDV10702': [-38.31, 145.00, 'Mornington Peninsula'],
    'IDW12300': [-31.92, 115.87, 'Perth']
}

SENSOR_TYPES = {
    'max': ['air_temperature_maximum', 'Max Temp C', TEMP_CELSIUS],
    'min': ['air_temperature_minimum', 'Min Temp C', TEMP_CELSIUS],
    'chance_of_rain': ['probability_of_precipitation', 'Chance of Rain', None],
    'possible_rainfall': ['precipitation_range', 'Possible Rainfall', None],
    'summary': ['precis', 'Summary', None],
    'detailed_summary': ['forecast', 'Detailed Summary', None],
    'icon': ['forecast_icon_code', 'Icon', None],
}

ICON_MAPPING = {
    "1": "mdi:weather-sunny",	
    "2": "mdi:weather-night",	
    "3": "mdi:weather-partlycloudy",	
    "4": "mdi:weather-cloudy",
    "6": "mdi:weather-sunset",
    "8": "mdi:weather-rainy",
    "9": "mdi:weather-windy",
    "10": "mdi:weather-sunset",
    "11": "mdi:weather-rainy",
    "12": "mdi:weather-pouring",
    "13": "mdi:weather-sunset",
    "14": "mdi:weather-snowy",
    "15": "mdi:weather-snowy",
    "16": "mdi:weather-lightning",
    "17": "mdi:weather-rainy"                        
}

def validate_days(days):
    """Check that days is within bounds."""
    if days not in range(1,7):
        raise vol.error.Invalid('Forecast Days is out of Range')
    return days

def validate_product_id(product_id):
    """Check that the Product ID is well-formed."""
    if product_id is None or not product_id:
        return product_id
    if not re.fullmatch(r'ID[A-Z]\d\d\d\d\d', product_id):
        raise vol.error.Invalid('Malformed Product ID')
    return product_id

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MONITORED_CONDITIONS, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_DAYS, default=6): validate_days,
    vol.Optional(CONF_FRIENDLY, default=False): cv.boolean,
    vol.Optional(CONF_NAME, default=''): cv.string,
    vol.Optional(CONF_PRODUCT_ID, default=''): validate_product_id,
    vol.Optional(CONF_REST_OF_TODAY, default=True): cv.boolean,
})

def setup_platform(hass, config, add_entities, discovery_info=None):

    days = config.get(CONF_DAYS)
    friendly = config.get(CONF_FRIENDLY)
    monitored_conditions = config.get(CONF_MONITORED_CONDITIONS)
    name = config.get(CONF_NAME)
    product_id = config.get(CONF_PRODUCT_ID)
    rest_of_today = config.get(CONF_REST_OF_TODAY)

    if not product_id:
        product_id = closest_product_id(
            hass.config.latitude, hass.config.longitude)
        if product_id is None:
            _LOGGER.error("Could not get BOM Product ID from lat/lon")
            return

    bom_forecast_data = BOMForecastData(product_id)

    bom_forecast_data.update()

    if rest_of_today:
        start = 0
    else:
        start = 1

    if friendly:
        for index in range(start, config.get(CONF_DAYS)+1):
            add_entities([BOMForecastSensorFriendly(bom_forecast_data, monitored_conditions,
            index, name, product_id)])    	
    else:
        for index in range(start, config.get(CONF_DAYS)+1):
            for condition in monitored_conditions:    
                add_entities([BOMForecastSensor(bom_forecast_data, condition,
                index, name, product_id)])


class BOMForecastSensor(Entity):
    """Implementation of a BOM forecast sensor."""

    def __init__(self, bom_forecast_data, condition, index, name, product_id):
        """Initialize the sensor."""
        self._bom_forecast_data = bom_forecast_data
        self._condition = condition
        self._index = index
        self._name = name
        self._product_id = product_id
        self.update()
        
    @property
    def name(self):
        """Return the name of the sensor."""
        if not self._name:
            return 'BOM {} {}'.format(
            SENSOR_TYPES[self._condition][1], self._index)
        return 'BOM {} {} {}'.format(self._name,
        SENSOR_TYPES[self._condition][1], self._index)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._bom_forecast_data.get_reading(
        	self._condition, self._index)

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
            ATTR_SENSOR_ID: self._condition,
            ATTR_ISSUE_TIME_LOCAL: self._bom_forecast_data.get_issue_time_local(),
            ATTR_PRODUCT_ID: self._product_id,
            ATTR_PRODUCT_LOCATION: PRODUCT_ID_LAT_LON_LOCATION[self._product_id][2],
            ATTR_START_TIME_LOCAL: self._bom_forecast_data.get_start_time_local(self._index),
        }
        if self._name:
            attr[ATTR_PRODUCT_NAME] = self._name

        return attr

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._condition][2]

    def update(self):
        """Fetch new state data for the sensor."""
        self._bom_forecast_data.update()

class BOMForecastSensorFriendly(Entity):
    """Implementation of a user friendly BOM forecast sensor."""

    def __init__(self, bom_forecast_data, conditions, index, name, product_id):
        """Initialize the sensor."""
        self._bom_forecast_data = bom_forecast_data
        self._conditions = conditions
        self._index = index
        self._name = name
        self._product_id = product_id
        self.update()
        
    @property
    def unique_id(self):
        """Return the entity id of the sensor."""
        if not self._name:
            return '{}'.format(self._index)
        return '{}_{}'.format(self._name, self._index)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._bom_forecast_data.get_reading('summary', self._index)

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {
            ATTR_ICON: self._bom_forecast_data.get_reading('icon', self._index),
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
        }
        for condition in self._conditions:
        	attr[SENSOR_TYPES[condition][1]] = self._bom_forecast_data.get_reading(condition, self._index),
        if self._name:
            attr['Name'] = self._name

        weather_forecast_date_string = self._bom_forecast_data.get_start_time_local(self._index).replace(":","")
        weather_forecast_datetime = datetime.datetime.strptime(weather_forecast_date_string, "%Y-%m-%dT%H%M%S%z")
        attr[ATTR_FRIENDLY_NAME] =  weather_forecast_datetime.strftime("%a, %e %b")            
        
        attr[ATTR_PRODUCT_ID] = self._product_id
        attr[ATTR_PRODUCT_LOCATION] = PRODUCT_ID_LAT_LON_LOCATION[self._product_id][2]
        
        return attr

    def update(self):
        """Fetch new state data for the sensor."""
        self._bom_forecast_data.update()

class BOMForecastData:
    """Get data from BOM."""

    def __init__(self, product_id):
        """Initialize the data object."""
        self._product_id = product_id

    def get_reading(self, condition, index):
        """Return the value for the given condition."""
        if condition == 'detailed_summary':
        	return self._data.find(_FIND_QUERY_2.format(index)).text
        
        find_query = (_FIND_QUERY.format(index, SENSOR_TYPES[condition][0]))
        state = self._data.find(find_query)
        if condition == 'icon':
        	return ICON_MAPPING[state.text]
        if state is None:
            return 'n/a'
        else:
            return state.text

    def get_issue_time_local(self):
        """Return the issue time of forecast."""
        issue_time = self._data.find("./amoc/next-routine-issue-time-local")
        if issue_time is None:
            return 'n/a'
        else:
            return issue_time.text

    def get_start_time_local(self, index):
        """Return the start time of forecast."""
        return self._data.find("./forecast/area[@type='location']/"
                               "forecast-period[@index='{}']".format(
                               	index)).get("start-time-local")

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from BOM."""
        ftp = ftplib.FTP("ftp.bom.gov.au")
        ftp.login()
        ftp.cwd("anon/gen/fwo/")
        ftp.retrbinary("RETR " + self._product_id + ".xml",
        open('bom_forecast.xml', 'wb').write)
        ftp.quit()
        tree = xml.etree.ElementTree.parse('bom_forecast.xml')
        self._data = tree.getroot()

def closest_product_id(lat, lon):
    """Return the closest product ID to our lat/lon."""

    def comparable_dist(product_id):
        """Create a psudeo-distance from latitude/longitude."""
        product_id_lat = PRODUCT_ID_LAT_LON_LOCATION[product_id][0]
        product_id_lon = PRODUCT_ID_LAT_LON_LOCATION[product_id][1]
        return (lat - product_id_lat) ** 2 + (lon - product_id_lon) ** 2

    return min(PRODUCT_ID_LAT_LON_LOCATION, key=comparable_dist)  

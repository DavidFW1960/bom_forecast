The bom forecast sensor platform uses the Australian Bureau of Meteorology (BOM) as a source for forecast meteorological data. This is an updated version of a fork from bremor/bom_forecast

Each sensor will be given the device_id of "bom [optionalname] friendly name units" Example: sensor.bom_gosford_chance_of_rain_0
A name is optional but if multiple BOM weather stations are used a name will be required.
The sensor checks for new data every minute, starting 30 minutes after the timestamp of the most recent data as the data is updated every half-hour.

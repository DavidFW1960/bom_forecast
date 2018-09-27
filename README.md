The `bom forecast` sensor platform uses the [Australian Bureau of Meteorology (BOM)](http://www.bom.gov.au) as a source for forecast meteorological data.

- Each sensor will be given the `device_id` of "bom [optionalname] friendlyname units"
- A name is optional but if multiple BOM weather stations are used a name will be required.
- The sensor checks for new data every minute, starting 30 minutes after the timestamp of the most recent data as the data is updated every half-hour.

To add the BOM weather observation to your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: bom_forecast
    product_id: IDV10450
    name: Melbourne
    forecast_days: 3
    rest_of_today: True
    monitored_conditions:
      - 'max'
      - 'min'
      - 'chance_of_rain'
      - 'possible_rainfall'
      - 'summary'
```

To get the product ID for any BOM city:
- Find your station on these maps: [NSW](http://www.bom.gov.au/nsw/observations/map.shtml), [QLD](http://www.bom.gov.au/qld/observations/map.shtml), [VIC](http://www.bom.gov.au/vic/observations/map.shtml), [WA](http://www.bom.gov.au/wa/observations/map.shtml), [SA](http://www.bom.gov.au/sa/observations/map.shtml), [TAS](http://www.bom.gov.au/tas/observations/map.shtml), [ACT](http://www.bom.gov.au/act/observations/canberramap.shtml), [NT](http://www.bom.gov.au/nt/observations/map.shtml).
 - alternatively, from the [BOM website](http://www.bom.gov.au/), navigate to State -> Observations -> Latest Observations -> Choose the station.
- The URL will look like: http://www.bom.gov.au/products/IDx60801/[station].shtml
 - For Adelaide, the URL will look like `http://www.bom.gov.au/products/IDS60801/IDS60801.94675.shtml`; the station ID is `IDS60801.94675`.

Configuration variables:

- **product_id** (*Optional*): The Product ID string as identified from the BOM website.  If not given, defaults to the closest city.
- **name** (*Optional*): The name you would like to give to the weather forecast.
- **forecast_days** (*Optional*): The number of days of forecast you would like, maximum is 6. If not given, defaults to 6.
- **rest_of_today** (*Optional*): Would you like to create a sensor for the forecast for the rest of today. Defaults to true.
- **monitored_conditions** (*Required*): A list of the conditions to monitor.

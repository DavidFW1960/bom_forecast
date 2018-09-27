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
      - 'detailed_summary'
```

To get the Product ID for any BOM city:
- Go to [this](http://www.bom.gov.au/nsw/observations/map.shtml) website and search for "City Forecast".
- The Product ID for your city will be in the left most column, and will look like "IDV10450"

Configuration variables:

- **product_id** (*Optional*): The Product ID string as identified from the BOM website.  If not given, defaults to the closest city.
- **name** (*Optional*): The name you would like to give to the weather forecast.
- **forecast_days** (*Optional*): The number of days of forecast you would like, maximum is 6. If not given, defaults to 6.
- **rest_of_today** (*Optional*): Would you like to create a sensor for the forecast for the rest of today. Defaults to true.
- **monitored_conditions** (*Required*): A list of the conditions to monitor.

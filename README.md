The `bom forecast` sensor platform uses the [Australian Bureau of Meteorology (BOM)](http://www.bom.gov.au) as a source for forecast meteorological data.

- Each sensor will be given the `device_id` of "bom [optionalname] friendlyname units"
- A name is optional but if multiple BOM weather stations are used a name will be required.
- The sensor checks for new data every minute, starting 30 minutes after the timestamp of the most recent data as the data is updated every half-hour.

To add the BOM weather observation to your installation, create this folder strictire in your /config directory:
- “custom_components/bom_forecast”.

Then, drop the following files into that folder:
- \_\_init__.py
- manifest.json
- sensor.py

Finally, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: bom_forecast
    product_id: !secret my_bom_product_id
    name: !secret my_bom_name
    forecast_days: 6
    rest_of_today: true
    friendly: false
    friendly_state_format: '{max}, {summary}'
    monitored_conditions:
      - 'max'
      - 'min'
      - 'chance_of_rain'
      - 'possible_rainfall'
      - 'summary'
      - 'detailed_summary'
      - 'icon'
```

This example uses the secrets.yaml file for the product_id and name. Up to you if you want to do this or not.

To get the Product ID for any BOM city:
- Go to [this](http://www.bom.gov.au/nsw/observations/map.shtml) website and search for "City Forecast", or "Town Forecast".
- The Product ID for your city will be in the left most column, or at the bottom of the page, and will look like "IDV10450"

Configuration variables:

- **product_id** (*Optional*): The Product ID string as identified from the BOM website.  If not given, defaults to the closest city.
- **name** (*Optional*): The name you would like to give to the weather forecast.
- **forecast_days** (*Optional*): The number of days of forecast you would like, maximum is 6. If not given, defaults to 6.
- **rest_of_today** (*Optional*): Would you like to create a sensor for the forecast for the rest of today. Defaults to true.
- **friendly** (*Optional*): Friendly mode will only create one sensor per day of forecast, and will have all the forecast information as sensor attributes. Defaults to false.
- **friendly_state_format** (*Optional*): Friendly state format allows you to format the state of your forecast sensors when in friendly mode. For example, '{min} to {max}, {summary}' will display the state as '10 to 25, Cloudy'. Defaults to '{summary}'.
- **monitored_conditions** (*Required*): A list of the conditions to monitor.

## Alternate Install
Download my weather.yaml package and install in your /config/packages folder. Make sure your configuration.yaml includes packages folder.

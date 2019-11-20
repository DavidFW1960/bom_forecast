The bom forecast sensor platform uses the Australian Bureau of Meteorology (BOM) as a source for forecast meteorological data. This is an updated version of a fork from bremor/bom_forecast


Each sensor will be given the device_id of "bom [optionalname] friendly name units" Example: sensor.bom_gosford_chance_of_rain_0
A name is optional but if multiple BOM weather stations are used a name will be required.
The sensor checks for new data every minute, starting 30 minutes after the timestamp of the most recent data as the data is updated every half-hour.

Thanks to @exxamalte for the code assistance to enable the new conditions.
See the new uv_alert and fire_danger monitored conditions. Checkout readme in the repository for full details.

With this component you can create a lovelace card like this:


![BOM Forecast Card](https://github.com/DavidFW1960/bom_forecast/blob/master/bom_forecast.png)



Or you can combine with the BOM Weather Custom Card.


Full configuration for this component will look like this:

```yaml
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
      - 'uv_alert'
      - 'fire_danger'
```
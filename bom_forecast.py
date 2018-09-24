import appdaemon.plugins.hass.hassapi as hass
from ftplib import FTP
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, time, tzinfo
import datetime as DT
from pytz import utc

class BOMForecast(hass.Hass):

    def initialize(self):

        self.run_hourly(self.bom_forecast, DT.time(0, 10, 0))
  
    def bom_forecast(self, kwargs=None):
  
        # Set your location here. Make sure it appears in the dicionaries below.
        # Currently only 'cities' are supported ('towns' and 'districts' are not supported)
        state = "VIC"
        city = "Melbourne"
        fire_district = "Central"

        weather_forecast_product_id = {
            "Darwin": "IDD10150",
            "Canberra": "IDN10035",
            "Sydney": "IDN10064",
            "Newcastle": "IDN11051",
            "Central Coast": "IDN11052",
            "Wollongong": "IDN11053",
            "Alpine Centres": "IDN11055",
            "Brisbane": "IDQ10095",
            "Gold Coast": "IDQ10610",
            "Sunshine Coast": "IDQ10611",
            "Adelaide": "IDS10034",
            "Hobart": "IDT13600",
            "Launceston": "IDT13610",
            "Melbourne": "IDV10450",
            "Geelong": "IDV10701",
            "Mornington Peninsula": "IDV10702",
            "Perth": "IDW12300"
        }

        uv_forecast_product_id = {
            "NSW": "IDZ00107",
            "NT": "IDZ00108",
            "QLD": "IDZ00109",
            "SA": "IDZ00110",
            "TAS": "IDZ00111",
            "VIC": "IDZ00112",
            "WA": "IDZ00113"
        }

        fire_danger_rating_forecast_product_id = {
            "NT": "IDD10731",	
            "NSW": "IDN10016",	
            "QLD": "IDQ13016",	
            "SA": "IDS10070",	
            "TAS": "IDT13151",	
            "VIC": "IDV18555",	
            "WA": "IDW15100"	
        }

        fire_danger_rating_fire_district = {
        	# VIC fire districts can be found here:
        	# http://www.bom.gov.au/vic/forecasts/fire-forecasts.shtml
            "Mallee": "VIC_FW001",
            "Wimmera": "VIC_FW002",
            "Northern Country": "VIC_FW003",
            "North Central": "VIC_FW008",
            "North East": "VIC_FW004",
            "South West": "VIC_FW009",
            "Central": "VIC_FW007",
            "West and South Gippsland": "VIC_FW006",
            "East Gippsland": "VIC_FW005",
        	# QLD fire districts can be found here:
        	# http://www.bom.gov.au/qld/forecasts/fire-forecasts.shtml
            "Peninsula": "QLD_FW001",
            "Gulf Country": "QLD_FW002",
            "Northern Goldfields and Upper Flinders": "QLD_FW003",
            "North Tropical Coast and Tablelands": "QLD_FW004",
            "Herbert and Lower Burdekin": "QLD_FW005",
            "Central Coast and Whitsundays": "QLD_FW006",
            "Capricornia": "QLD_FW007",
            "Central Highlands and Coalfields": "QLD_FW008",
            "Central West": "QLD_FW009",
            "North West": "QLD_FW010",
            "Channel Country": "QLD_FW011",
            "Maranoa and Warrego": "QLD_FW012",
            "Darling Downs and Granite Belt": "QLD_FW013",
            "Wide Bay and Burnett": "QLD_FW014",
            "Southeast Coast": "QLD_FW015",
            # NT fire districts can be found here:
            # http://www.bom.gov.au/nt/forecasts/fire-forecasts.shtml
            "Darwin and Adelaide River": "NT_FW001",
            "Northern Fire Protection Area": "NT_FW002",
            "Daly South": "NT_FW003",
            "Tiwi": "NT_FW004",
            "Arnhem West": "NT_FW005",
            "Arnhem East": "NT_FW006",
            "Katherine Fire Protection Area": "NT_FW007",
            "Carpentaria West": "NT_FW008",
            "Carpentaria East": "NT_FW009",
            "Gregory North West": "NT_FW010",
            "Gregory South East": "NT_FW011",
            "Barkly North": "NT_FW012",
            "Barkly South": "NT_FW013",
            "Alice Springs Fire Protection Area": "NT_FW014",
            "Simpson West": "NT_FW015",
            "Simpson East": "NT_FW016",
            "Lasseter West": "NT_FW017",
            "Lasseter East": "NT_FW018",
            "Tanami North": "NT_FW019",
            "Tanami South": "NT_FW020",
            # WA fire districts can be found here:
            # http://www.bom.gov.au/wa/forecasts/fire-forecasts.shtml
            "North Kimberley Coast": "WA_FW001",
            "West Kimberley Coast": "WA_FW002",
            "Kimberley Inland": "WA_FW003",
            "East Pilbara Coast": "WA_FW004",
            "West Pilbara Coast": "WA_FW005",
            "East Pilbara Inland": "WA_FW006",
            "Ashburton Inland": "WA_FW007",
            "Exmouth Gulf Coast": "WA_FW008",
            "Gascoyne Coast": "WA_FW009",
            "Gascoyne Inland": "WA_FW010",
            "Goldfields": "WA_FW011",
            "Eucla": "WA_FW012",
            "North Interior": "WA_FW013",
            "South Interior": "WA_FW014",
            "Coastal Central West - North": "WA_FW015",
            "Inland Central West - North": "WA_FW016",
            "Coastal Central West - South": "WA_FW017",
            "Inland Central West - South": "WA_FW018",
            "Lower West Coast": "WA_FW019",
            "Lower West Inland": "WA_FW020",
            "Geographe": "WA_FW021",
            "Leeuwin": "WA_FW022",
            "Nelson": "WA_FW023",
            "Stirling Coast": "WA_FW024",
            "Stirling Inland": "WA_FW025",
            "Ravensthorpe Shire Coast": "WA_FW026",
            "Ravensthorpe Shire Inland": "WA_FW027",
            "Esperance Shire Coast": "WA_FW028",
            "Esperance Shire Inland": "WA_FW029",
            "Upper Great Southern": "WA_FW030",
            "Roe": "WA_FW031",
            "Beaufort": "WA_FW032",
            "Lakes": "WA_FW033",
            "Mortlock": "WA_FW034",
            "Ninghan": "WA_FW035",
            "Avon": "WA_FW036",
            "Jilbadgie": "WA_FW037",
            # NSW fire districts can be found here:
            # http://www.bom.gov.au/nsw/forecasts/fire-forecasts.shtml
            "Far North Coast": "NSW_FW001",
            "North Coast": "NSW_FW002",
            "Greater Hunter": "NSW_FW003",
            "Greater Sydney Region": "NSW_FW004",
            "Illawarra/Shoalhaven": "NSW_FW005",
            "Far South Coast": "NSW_FW006",
            "Monaro Alpine": "NSW_FW007",
            "The Australian Capital Territory": "NSW_FW008",
            "Southern Ranges": "NSW_FW009",
            "Central Ranges": "NSW_FW010",
            "New England": "NSW_FW011",
            "Northern Slopes": "NSW_FW012",
            "North Western": "NSW_FW013",
            "Upper Central West Plains": "NSW_FW014",
            "Lower Central West Plains": "NSW_FW015",
            "Southern Slopes": "NSW_FW016",
            "Eastern Riverina": "NSW_FW017",
            "Southern Riverina": "NSW_FW018",
            "Northern Riverina": "NSW_FW019",
            "South Western": "NSW_FW020",
            "Far Western": "NSW_FW021"
        }

        weather_forecast_icon = {
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
    

        # Connect to the FTP server and download xml files
        ftp = FTP("ftp.bom.gov.au")
        ftp.login()
        ftp.cwd("anon/gen/fwo/")
        ftp.retrbinary("RETR " + weather_forecast_product_id[city] + ".xml", open('weather_forecast.xml', 'wb').write)
        ftp.retrbinary("RETR " + uv_forecast_product_id[state] + ".xml", open('uv_forecast.xml', 'wb').write)
        ftp.retrbinary("RETR " + fire_danger_rating_forecast_product_id[state] + ".xml", open('fire_danger_rating_forecast.xml', 'wb').write)
        ftp.quit()
    
        # Parse the weather forecast xml file into a tree and get the root
        weather_forecast_tree = ET.parse('weather_forecast.xml')
        weather_forecast_root = weather_forecast_tree.getroot()
    
        # Parse the uv forecast xml file into a tree and get the root
        uv_forecast_tree = ET.parse('uv_forecast.xml') 
        uv_forecast_root = uv_forecast_tree.getroot()
  
        # Parse the fire danger rating forecast xml file into a tree and get the root
        fire_danger_rating_forecast_tree = ET.parse('fire_danger_rating_forecast.xml') 
        fire_danger_rating_forecast_root = fire_danger_rating_forecast_tree.getroot()
  
        for x in range(0, 7):
  
            weather_forecast = weather_forecast_root.find(f"./forecast/area[@type='location']/forecast-period[@index='{x}']")

            # Parse information from the weather forecast xml
            weather_forecast_icon_code = weather_forecast.find("./element[@type='forecast_icon_code']").text
            weather_forecast_summary = weather_forecast.find("./text[@type='precis']").text
            weather_forecast_chance_of_rain = weather_forecast.find("./text[@type='probability_of_precipitation']").text
            
            # The minimum will be omitted for the forecast for the rest of today. Protect against the case
            # where minimum has been omitted from the xml
            weather_forecast_min = weather_forecast.find("./element[@type='air_temperature_minimum']")
            if weather_forecast_min is None:
                weather_forecast_min = "n/a"
            else:
                weather_forecast_min = weather_forecast_min.text

            # The maximum will be omitted for the afternoon forecast for the rest of today. Protect against the case
            # where maximum has been omitted from the xml
            weather_forecast_max = weather_forecast.find("./element[@type='air_temperature_maximum']")
            if weather_forecast_max is None:
                weather_forecast_max = "n/a"
            else:
                weather_forecast_max = weather_forecast_max.text
    
            # If possible rainfall is zero it will be omitted from the xml, protect against the case
            # where possible rainfall has been omitted from the xml
            weather_forecast_possible_rainfall = weather_forecast.find("./element[@type='precipitation_range']")
            if weather_forecast_possible_rainfall is None:
                weather_forecast_possible_rainfall = "0 mm"
            else:
                weather_forecast_possible_rainfall = weather_forecast_possible_rainfall.text
            
            # Retreive the date of the forecast and make it user friendly
            weather_forecast_date_string = (weather_forecast.get("start-time-local")).replace(":","")
            weather_forecast_datetime = datetime.strptime(weather_forecast_date_string, "%Y-%m-%dT%H%M%S%z")
            weather_forecast_friendly_date = weather_forecast_datetime.strftime("%a, %e %b")
    
            # Retreive the section of the forecast which holds the detailed summary
            weather_forecast = weather_forecast_root.find(f"./forecast/area[@type='metropolitan']/forecast-period[@index='{x}']")
            weather_forecast_detailed = weather_forecast.find("./text[@type='forecast']").text

            # UV is only available for the next 4 days, so protect against the case
            # where UV has been omitted from the xml
            uv_forecast = uv_forecast_root.find(f"./forecast/area[@description='{city}']/forecast-period[@index='{x}']/text[@type='uv_alert']")
            if uv_forecast is None:
                uv_forecast = "n/a"
            else:
                uv_forecast = uv_forecast.text
                
            # Fire danger is only available for the next 4 days, so protect against the case
            # where fire danger rating has been omitted from the xml
            fire_danger_rating_forecast = fire_danger_rating_forecast_root.find(f"./forecast/area[@aac='{fire_danger_rating_fire_district[fire_district]}']/forecast-period[@index='{x}']/text[@type='fire_danger']")
            if fire_danger_rating_forecast is None:
                fire_danger_rating_forecast = "n/a"
            else:
                fire_danger_rating_forecast = fire_danger_rating_forecast.text

            # Publish the state of the forecast to home assistant
            self.set_state(f"sensor.bom_forecast_{x}", state = weather_forecast_summary, attributes = {"Min": weather_forecast_min, "Max": weather_forecast_max, "Chance of rain": weather_forecast_chance_of_rain, "Detailed": weather_forecast_detailed, "friendly_name": weather_forecast_friendly_date, "icon": weather_forecast_icon[weather_forecast_icon_code], "Possible rainfall": weather_forecast_possible_rainfall, "UV Alert": uv_forecast, "Fire danger rating": fire_danger_rating_forecast})
         
        # Find out when the next forecast will be published and make it user friendly
        next_update = (weather_forecast_root.find("./amoc/next-routine-issue-time-local").text).replace(":","")
        next_update_datetime = datetime.strptime(next_update, "%Y-%m-%dT%H%M%S%z")
        next_update_friendly_date = next_update_datetime.strftime("%a, %e %b, %H:%M")

        # Find out when this forecast was published and make it user friendly
        issued_at = ((weather_forecast_root.find("./amoc/issue-time-local").text).split("+"))[0]
        issued_at_datetime = datetime.strptime(issued_at, "%Y-%m-%dT%H:%M:%S")
        issued_at_friendly_date = issued_at_datetime.strftime("%a, %e %b, %H:%M") 
    
        # Publish the state of the next forecast update
        self.set_state("sensor.bom_next_update", state = next_update_friendly_date, attributes = {"friendly_name": "Next update", "icon": "mdi:calendar-clock", "Issued at": issued_at_friendly_date})
        

    
    

import requests
from tkinter import *
from tkinter import ttk
from datetime import datetime
from tkinter import PhotoImage

# API Keys for the weather, air pollution, pollen levels, etc.
API_KEY = '7332d43383fe51b4a175d661efbd5ce2'
AirP_API_Key = '2cbd9b31e4a99060859b0eca92524bdeb3122e379f8a3538f9e43fd541d8b7ec'
TOMORROW_API_KEY = 'W7hAJuLMvMKehYImv6IwrvBq4OZhxj72'

# Original weather app functionality
def get_weather_data(city_name):
    params = {'q': city_name, 'appid': API_KEY}
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}"
    response = requests.get(url, params=params)
    data = response.json()
    return data

def get_weather_icon(icon_id):
    # Assuming that the icon_id parameter is not being used for now
    icon_path = "weather_image.png"
    icon_data = PhotoImage(file=icon_path)
    return icon_data

def display_temperature_fahrenheit(city_name):
    data = get_weather_data(city_name)
    temperature_kelvin = data['main']['temp']
    temperature_fahrenheit = (temperature_kelvin - 273.15) * 9/5 + 32
    return temperature_fahrenheit

def display_temperature_celsius(city_name):
    data = get_weather_data(city_name)
    temperature_kelvin = data['main']['temp']
    temperature_celsius = temperature_kelvin - 273.15
    return temperature_celsius

def forecast(city_name):
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}"
    response = requests.get(forecast_url)
    data = response.json()

    forecast_window = Toplevel(app)
    forecast_window.title("5-Day Forecast")
    forecast_window.geometry('800x600')

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
    style.configure("Treeview", font=("Arial", 12), rowheight=25)

    tree = ttk.Treeview(forecast_window, columns=('Date and Time', 'Temperature (Fahrenheit)', 'Temperature (Celsius)'),
                        show='headings', selectmode='none')
    tree.grid(row=0, column=0, sticky='nsew')

    tree.heading('Date and Time', text='Date and Time')
    tree.heading('Temperature (Fahrenheit)', text='Temperature (Fahrenheit)')
    tree.heading('Temperature (Celsius)', text='Temperature (Celsius)')

    tree.column('Date and Time', width=200, anchor='center')
    tree.column('Temperature (Fahrenheit)', width=200, anchor='center')
    tree.column('Temperature (Celsius)', width=200, anchor='center')

    scroll_y = ttk.Scrollbar(forecast_window, orient='vertical', command=tree.yview)
    scroll_y.grid(row=0, column=1, sticky='ns')
    tree.configure(yscrollcommand=scroll_y.set)

    for entry in data['list']:
        date_time = datetime.utcfromtimestamp(entry['dt']).strftime('%Y-%m-%d %H:%M:%S')
        temp_c = entry['main']['temp'] - 273.15
        temp_f = temp_c * 9/5 + 32

        tree.insert('', 'end', values=(date_time, f'{temp_f:.2f}°F', f'{temp_c:.2f}°C'))

    forecast_window.grid_rowconfigure(0, weight=1)
    forecast_window.grid_columnconfigure(0, weight=1)

def get_air_pollution(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}"
    params = {'q': city_name, 'appid': AirP_API_Key}
    response = requests.get(url, params=params)
    data = response.json()

    lat = data['coord']['lat']
    lon = data['coord']['lon']
    air_pollution_url = f'https://api.ambeedata.com/latest/by-lat-lng?lat={lat}&lng={lon}'
    headers = {'x-api-key': AirP_API_Key}
    response = requests.get(air_pollution_url, headers=headers)
    air_quality_data = response.json()

    return air_quality_data['stations'][0]['AQI']

def get_pollen_levels(city_name):
    city_weather_data = get_weather_data(city_name)

    lat = city_weather_data['coord']['lat']
    lon = city_weather_data['coord']['lon']
    pollen_url = f'https://api.ambeedata.com/latest/pollen/by-lat-lng?lat={lat}&lng={lon}'

    headers = {'x-api-key': AirP_API_Key}
    response = requests.get(pollen_url, headers=headers)
    data = response.json()

    pollen_data = data['data']
    return pollen_data

def display_humidity(city_name):
    data = get_weather_data(city_name)
    humidity = data['main']['humidity']
    return humidity

def clothing_recommendation(temperature):
    if temperature >= 80:
        return "Please wear breathable clothes for the heat"
    elif 60 <= temperature < 80:
        return "Wear light layers for the moderate weather"
    elif 40 <= temperature < 60:
        return "Wear a jacket for the cool weather"
    else:
        return "Wear multiple layers for the cold weather"

def display_weather_icon(city_name):
    data = get_weather_data(city_name)

    icon_id = "01d"  # Use the clear sky icon (icon_id "01d" for daytime)
    icon = get_weather_icon(icon_id)

    if not hasattr(display_weather_icon, 'weather_icon_label') or display_weather_icon.weather_icon_label is None:
        display_weather_icon.weather_icon_label = Label(app, image=icon, bg="dark blue")
        display_weather_icon.weather_icon_label.pack(pady=10)
    else:
        display_weather_icon.weather_icon_label.config(image=icon)
        display_weather_icon.weather_icon_label.image = icon

    display_weather_icon.weather_icon_label.update_idletasks()

def display_weather_info(city_name):
    data = get_weather_data(city_name)
    fahrenheit_temp = display_temperature_fahrenheit(city_name)
    celsius_temp = display_temperature_celsius(city_name)

    info_text.delete(1.0, END)  # Clear existing text

    # Display Temperature Information
    info_text.insert(END, "Temperature Information\n", 'heading')
    info_text.insert(END, f"Fahrenheit: {fahrenheit_temp:.2f}°F\n", 'normal_weather')
    info_text.insert(END, f"Celsius: {celsius_temp:.2f}°C\n\n", 'normal_weather')

    # Display Clothing Recommendation
    info_text.insert(END, "Clothing Recommendation\n", 'heading')
    info_text.insert(END, f"{clothing_recommendation(celsius_temp)}\n\n", 'normal_weather')

    # Display Humidity Information
    humidity = display_humidity(city_name)
    info_text.insert(END, "Humidity Information\n", 'heading')
    info_text.insert(END, f"Humidity: {humidity}%\n\n", 'normal_weather')

    # Display Air Quality Information
    air_quality = get_air_pollution(city_name)
    info_text.insert(END, "Air Quality Information\n", 'heading')
    info_text.insert(END, f"Air Quality Index: {air_quality}\n\n", 'normal_weather')

    # Display Pollen Levels
    pollen_data = get_pollen_levels(city_name)
    info_text.insert(END, "Pollen Levels\n", 'heading')

    for pollen_entry in pollen_data:
        if 'Species' in pollen_entry:
            pollen_name = pollen_entry['Species']
            pollen_count = pollen_entry.get('Count', 'N/A')
            pollen_risk = pollen_entry.get('Risk', 'N/A')
            info_text.insert(END, f"{pollen_name} Pollen:\nCount: {pollen_count}\nRisk Level: {pollen_risk}\n\n", 'normal_weather')
        else:
            info_text.insert(END, "Invalid Pollen Entry\n", 'normal_weather')

    # Display Weather Icon
    display_weather_icon(city_name)


def get_current_weather_data(city_name):
    params = {
        'key': '97b6f86e49924711b1d30046231911',
        'q': city_name,
        'days': 1,  # Assuming you want current weather data
    }

    url = "https://api.weatherapi.com/v1/forecast.json"
    response = requests.get(url, params=params)
    data = response.json()

    return data

def display_historical_weather_data(city_name):
    historical_data = get_current_weather_data(city_name)

    historical_window = Toplevel(app)
    historical_window.title("Historical Weather Data")
    historical_window.geometry('800x600')

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
    style.configure("Treeview", font=("Arial", 12), rowheight=25)

    tree = ttk.Treeview(historical_window, columns=('Date', 'Max Temp (F)', 'Min Temp (F)', 'Avg Temp (F)',
                                                    'Max Wind Speed (mph)', 'Total Precipitation (in)', 'Weather Condition'),
                        show='headings', selectmode='none')
    tree.grid(row=0, column=0, sticky='nsew')

    tree.heading('Date', text='Date')
    tree.heading('Max Temp (F)', text='Max Temp (F)')
    tree.heading('Min Temp (F)', text='Min Temp (F)')
    tree.heading('Avg Temp (F)', text='Avg Temp (F)')
    tree.heading('Max Wind Speed (mph)', text='Max Wind Speed (mph)')
    tree.heading('Total Precipitation (in)', text='Total Precipitation (in)')
    tree.heading('Weather Condition', text='Weather Condition')

    tree.column('Date', width=150, anchor='center')
    tree.column('Max Temp (F)', width=100, anchor='center')
    tree.column('Min Temp (F)', width=100, anchor='center')
    tree.column('Avg Temp (F)', width=100, anchor='center')
    tree.column('Max Wind Speed (mph)', width=150, anchor='center')
    tree.column('Total Precipitation (in)', width=200, anchor='center')
    tree.column('Weather Condition', width=200, anchor='center')

    scroll_y = ttk.Scrollbar(historical_window, orient='vertical', command=tree.yview)
    scroll_y.grid(row=0, column=1, sticky='ns')
    tree.configure(yscrollcommand=scroll_y.set)

    # Check if 'forecast' key is present in the API response
    if 'forecast' in historical_data:
        for entry in historical_data['forecast']['forecastday']:
            date_time = entry['date']
            max_temp_f = entry['day']['maxtemp_f']
            min_temp_f = entry['day']['mintemp_f']
            avg_temp_f = entry['day']['avgtemp_f']
            max_wind_speed_mph = entry['day']['maxwind_mph']
            total_precipitation_in = entry['day']['totalprecip_in']
            weather_condition = entry['day']['condition']['text']

            tree.insert('', 'end', values=(date_time, f'{max_temp_f:.2f}', f'{min_temp_f:.2f}', f'{avg_temp_f:.2f}',
                                           f'{max_wind_speed_mph:.2f}', f'{total_precipitation_in:.2f}', weather_condition))
    else:
        tree.insert('', 'end', values=('No data available', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'))

    historical_window.grid_rowconfigure(0, weight=1)
    historical_window.grid_columnconfigure(0, weight=1)

# Function to get severe weather alerts
def get_severe_weather_alerts(city_name):
    params = {'q': city_name, 'key': TOMORROW_API_KEY, 'alerts': 'yes'}
    url = "https://api.weatherapi.com/v1/forecast.json"
    response = requests.get(url, params=params)
    data = response.json()

    if 'alerts' in data:
        return data['alerts']['alert']
    else:
        return []
    

# Function to display severe weather alerts
def display_severe_weather_alerts(city_name):
    alerts = get_severe_weather_alerts(city_name)

    if not alerts:
        info_text.insert(END, "No severe weather alerts for the selected city.\n", 'normal_weather')
        return

    info_text.insert(END, "Severe Weather Alerts:\n", 'severe_alert_header')

    for alert in alerts:
        headline = alert['headline']
        severity = alert['severity']
        areas = alert['areas']
        event = alert['event']
        effective = alert['effective']
        expires = alert['expires']
        description = alert['desc']

        info_text.insert(END, f"Headline: {headline}\nSeverity: {severity}\nAreas: {areas}\nEvent: {event}\n"
                              f"Effective: {effective}\nExpires: {expires}\nDescription: {description}\n\n", 'severe_alert')

# Function to get severe weather shelters
def get_severe_weather_shelters(city):
    base_url = "https://www.fema.gov/api/open/v1/DisasterShelters"
    query_params = {"$filter": f"city eq '{city}'", "$top": 10, "$format": "json"}

    try:
        response = requests.get(base_url, params=query_params)
        response.raise_for_status()  # Check for HTTP errors

        shelters = response.json()
        return shelters

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    
# Function to display severe weather shelters
def display_severe_weather_shelters(city):
    shelters_data = get_severe_weather_shelters(city)

    if not shelters_data:
        info_text.insert(END, "No severe weather shelters found for the selected city.\n", 'normal_weather')
        return

    info_text.insert(END, "Severe Weather Shelters:\n", 'severe_shelter_header')

    for shelter in shelters_data:
        shelter_name = shelter.get('name', 'N/A')
        location = shelter.get('location', 'N/A')
        capacity = shelter.get('capacity', 'N/A')

        info_text.insert(END, f"Shelter Name: {shelter_name}\nLocation: {location}\nCapacity: {capacity}\n\n", 'severe_shelter')

    
    
# GUI setup
app = Tk()
app.title("WeatherWonders - Unveiling the Secrets of the Skies")
app.geometry('1000x600+200+100')
app.resizable(FALSE, FALSE)
app.config(bg="#CCE5FF")  # Changed background color

# Styled the title label
title_label = Label(app, text="Weather App", font=("Arial", 24, "bold"), bg="#CCE5FF", fg="#005A8C")
title_label.pack(pady=10)

# Search Frame
search_frame = Frame(app, bg="#CCE5FF")  # Changed background color
search_frame.pack(side=TOP, pady=20)

city_label = Label(search_frame, text="Enter City:", font=("Arial", 14), bg="#CCE5FF", fg="#005A8C")
city_label.grid(row=0, column=0, pady=10)

entry = Entry(search_frame, font=("Arial", 14))
entry.grid(row=0, column=1, pady=10, padx=10)

submit_button = ttk.Button(search_frame, text="Submit", command=lambda: display_weather_info(entry.get()))
submit_button.grid(row=0, column=2, pady=20, padx=10)

forecast_button = ttk.Button(search_frame, text="5-Day Forecast", command=lambda: forecast(entry.get()))
forecast_button.grid(row=0, column=3, pady=20, padx=10)

historical_button = ttk.Button(search_frame, text="Historical Weather Data", command=lambda: display_historical_weather_data(entry.get()))
historical_button.grid(row=0, column=4, pady=20, padx=10)

# Weather Information Frame
info_frame = Frame(app, bg="#CCE5FF")
info_frame.pack(side=TOP, pady=20)

# Styled the text widget
info_text = Text(info_frame, wrap=WORD, height=20, width=70, font=("Arial", 14), bg="#CCE5FF", fg="#005A8C")
info_text.pack(pady=10, padx=10)
# Add styles for headings
info_text.tag_configure('heading', font=("Arial", 16, "bold"), foreground="#005A8C")
info_text.tag_configure('normal_weather', font=("Arial", 14), foreground="#005A8C")

scrollbar = Scrollbar(info_frame)
scrollbar.pack(side=RIGHT, fill=Y)

scrollbar.config(command=info_text.yview)
info_text.config(yscrollcommand=scrollbar.set)

# Forecast Frame
forecast_frame = Frame(app, bg="#CCE5FF")
forecast_frame.pack(side=TOP, pady=20)

# Historical Frame
historical_frame = Frame(app, bg="#CCE5FF")
historical_frame.pack(side=TOP, pady=20)

# Severe Weather Alerts Button
severe_alerts_button = ttk.Button(search_frame, text="Severe Weather Alerts", command=lambda: display_severe_weather_alerts(entry.get()))
severe_alerts_button.grid(row=0, column=5, pady=20, padx=10)

severe_shelters_button = ttk.Button(search_frame, text="Severe Weather Shelters", command=lambda: display_severe_weather_shelters(entry.get()))
severe_shelters_button.grid(row=0, column=6, pady=20, padx=10)
app.mainloop()
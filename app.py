import os
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-GUI rendering
import matplotlib.pyplot as plt
from flask import Flask, request, render_template
import requests
import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def weather():
    weather_data = None
    graph_filename = None
    if request.method == 'POST':
        city = request.form['city']
        
        # Geocoding to get latitude and longitude for the city
        geocoding_response = requests.get(f'https://geocoding-api.open-meteo.com/v1/search?name={city}')
        
        if geocoding_response.status_code == 200 and geocoding_response.json().get('results'):
            location = geocoding_response.json()['results'][0]
            latitude, longitude = location['latitude'], location['longitude']
            
            # Fetch hourly forecast data
            weather_response = requests.get(
                f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,wind_speed_10m,precipitation,relative_humidity_2m&timezone=auto'
            )
            
            if weather_response.status_code == 200:
                weather_data = weather_response.json()
                graph_filename = generate_weather_graphs(weather_data)
            else:
                weather_data = {'error': 'Unable to retrieve weather data.'}
        else:
            weather_data = {'error': 'City not found'}
            
    return render_template('dashboard.html', weather_data=weather_data, graph_filename=graph_filename)

def generate_weather_graphs(weather_data):
    # Parse hourly data
    times = weather_data['hourly']['time'][:24]  # Take data for the next 24 hours
    temperatures = weather_data['hourly']['temperature_2m'][:24]
    wind_speeds = weather_data['hourly']['wind_speed_10m'][:24]
    precipitation = weather_data['hourly']['precipitation'][:24]
    humidity = weather_data['hourly']['relative_humidity_2m'][:24]

    time_labels = [datetime.datetime.fromisoformat(time).strftime('%H:%M') for time in times]

    # Plot graphs
    plt.figure(figsize=(12, 8))
    
    # Temperature plot
    plt.subplot(2, 2, 1)
    plt.plot(time_labels, temperatures, marker='o', linestyle='-', color='b')
    plt.xticks(rotation=45)
    plt.xlabel('Time (24 hours)')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature')

    # Wind speed plot
    plt.subplot(2, 2, 2)
    plt.plot(time_labels, wind_speeds, marker='o', linestyle='-', color='g')
    plt.xticks(rotation=45)
    plt.xlabel('Time (24 hours)')
    plt.ylabel('Wind Speed (km/h)')
    plt.title('Wind Speed')

    # Precipitation plot
    plt.subplot(2, 2, 3)
    plt.plot(time_labels, precipitation, marker='o', linestyle='-', color='purple')
    plt.xticks(rotation=45)
    plt.xlabel('Time (24 hours)')
    plt.ylabel('Precipitation (mm)')
    plt.title('Precipitation')

    # Humidity plot
    plt.subplot(2, 2, 4)
    plt.plot(time_labels, humidity, marker='o', linestyle='-', color='orange')
    plt.xticks(rotation=45)
    plt.xlabel('Time (24 hours)')
    plt.ylabel('Relative Humidity (%)')
    plt.title('Relative Humidity')

    plt.tight_layout()

    # Save plot as image
    if not os.path.exists('static'):
        os.mkdir('static')
    graph_filename = './static/weather_plots.png'
    plt.savefig(graph_filename)
    plt.close()
    
    return graph_filename


if __name__ == '__main__':
    if not os.path.exists('static'):
        os.mkdir('static')
    app.run(debug=True)

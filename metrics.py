import uvicorn
from fastapi import FastAPI, Request, Response
from prometheus_client import generate_latest
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
import requests
import os

# Initialize FastAPI app
app = FastAPI()

# Get port from environment variable, default to 9093 if not set
PORT = os.getenv('PORT', '9093')
HOST = os.getenv('HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Define units for each metric
UNIT_MAPPING = {
    "voltage": "V",
    "current": "A",
    "active_power": "W",
    "apparent_power": "VA",
    "reactive_power": "var",
    "power_factor": "",  # No unit for power factor (0-1 ratio)
    "energy_today": "kWh",
    "energy_yesterday": "kWh",
    "energy_total": "kWh",
}

class TasmotaCollector:
    def __init__(self, target):
        self.target = target
        
        # Get user and password from environment variables
        self.username = os.getenv('USER')
        self.password = os.getenv('PASSWORD')

        # If both USER and PASSWORD are provided, we'll use basic authentication
        self.auth = (self.username, self.password) if self.username and self.password else None
    
    def fetch_status_10(self):
        try:
            response = requests.get(f'http://{self.target}/cm?cmnd=STATUS%2010', timeout=5, auth=self.auth)
            response.raise_for_status()
            return response.json().get("StatusSNS", {}).get("ENERGY", {})
        except requests.exceptions.RequestException as e:
            print(f"Error scraping Tasmota device {self.target}: {e}")
            return {}
        
    def fetch_power_state(self):
        try:
            response = requests.get(f'http://{self.target}/cm?cmnd=POWER', timeout=5, auth=self.auth)
            response.raise_for_status()

            data = response.json()
            power_state = data.get("POWER", "OFF")  # Default to OFF if missing
            return 1 if power_state == "ON" else 0

        except requests.exceptions.RequestException as e:
            print(f"Error fetching switch state from {self.target}: {e}")

    def collect(self):
        power_state = self.fetch_power_state()
        metric_name = f"tasmota_switch_power_state"
        r = GaugeMetricFamily(metric_name, 'Switch Power State of the Tasmota Device', labels=["device"])
        r.add_metric([self.target], power_state)
        yield r

        status_10 = self.fetch_status_10()
        for key in status_10:
            metric_value = None
            try:
                metric_value = float(status_10[key])  # Ensure numeric value
            except ValueError:
                continue  # Skip non-numeric values (timestamps, etc.)

            # Normalize key and get unit
            metric_base_name = key.lower().replace(" ", "_")
            unit = UNIT_MAPPING.get(metric_base_name, "")

            # Construct metric name with unit
            if unit:
                metric_name = f"tasmota_energy_{metric_base_name}_{unit}"
            else:
                metric_name = f"tasmota_energy_{metric_base_name}"

            # Choose metric type dynamically
            if "today" in metric_base_name or "yesterday" in metric_base_name or "total" in metric_base_name:
                r = CounterMetricFamily(metric_name, key, labels=["device"])
            else:
                r = GaugeMetricFamily(metric_name, key, labels=["device"])

            r.add_metric([self.target], metric_value)
            yield r

# FastAPI root endpoint
@app.get("/")
async def root():
    return {
        "message": "Tasmota Prometheus Exporter",
        "info": "Scrape metrics from a Tasmota device",
        "example": "http://localhost:9093/tasmota?target=192.168.1.10"
    }

# Prometheus metrics endpoint
@app.get("/tasmota")
async def metrics_endpoint(request: Request):
    target = request.query_params.get('target')
    if not target:
        return {"error": "No target provided"}, 400

    collector = TasmotaCollector(target)
    metrics_data = generate_latest(collector)
    return Response(content=metrics_data, media_type="text/plain")

# Start the Prometheus exporter using Uvicorn
if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=int(PORT))

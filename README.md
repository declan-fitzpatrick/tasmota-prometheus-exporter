# Tasmota Prometheus Exporter

A simple Python-based exporter for scraping metrics from Tasmota devices and exposing them for Prometheus monitoring.

This exporter collects metrics from Tasmota devices that support the STATUS 10 and POWER commands, which include energy consumption, power states, and other metrics. It uses the prometheus_client library to expose these metrics in a format suitable for Prometheus scraping.

## Features

* Exposes metrics like voltage, current, power, energy (today, yesterday, total), and power state of a Tasmota device.
* Supports dynamic metric creation based on Tasmota status response.
* Flask-based web service to serve Prometheus metrics.
* Allows easy integration with Prometheus for monitoring and alerting.

## Prerequisites

* Python 3.6 or higher
* Tasmota device with enabled API (ensure the device has STATUS 10 and POWER commands accessible)

## Configuration

You can configure the target Tasmota device's IP address by passing it as a query parameter in the `/tasmota` endpoint. For example:
```bash
curl "http://localhost:8000/tasmota?target=192.168.1.10"
```
Where `192.168.1.10` is the IP address of the Tasmota device you want to scrape metrics from.

## Usage

You can run the Tasmota Prometheus Exporter using Docker. 

```yaml
services:
  tasmota:
    image: declanfitzpatrick/tasmota-prometheus-exporter:latest
    container_name: tasmota-prometheus-exporter
    restart: always
    ports:
      - 9093:9093
    environment:
      - PORT=9093 #optional, default is 9093
      - HOST=0.0.0.0 #optional, default is 0.0.0.0
      - USERNAME=admin #optional, tasmota http username
      - PASSWORD=<PASSWORD> #optional, tasmota http password
```
### Prometheus Integration

To integrate with Prometheus, add the following scrape configuration to your `prometheus.yml`:

```yaml
scrape_configs:
   - job_name: "tasmota"
     metrics_path: /tasmota
     scheme: http 
     static_configs:
       - targets:
         - <ip and port of the tasmota device>
         labels: 
           any: label
     relabel_configs:
       - source_labels: [__address__]
         target_label: __param_target
       - source_labels: [__param_target]
         target_label: device
       - target_label: __address__
         replacement: <ip and port of the tasmota prometheus exporter>
```

## Contributing

You can run the Tasmota Prometheus Exporter using Docker. The repository includes a `docker-compose.yml` file for easy container deployment. Clone the repository and run the following commands to build and run the container:

```shell
docker-compose up --build
```

This will start the Flask application and the Prometheus metrics server on:

```shell
http://localhost:9093/tasmota?target=<device_ip>
```

Replace <device_ip> with the actual IP address of your Tasmota device.

## Output

```text
# HELP tasmota_switch_power_state Switch Power State of the Tasmota Device
# TYPE tasmota_switch_power_state gauge
tasmota_switch_power_state{device="192.168.1.10"} 0.0
# HELP tasmota_energy_total Total
# TYPE tasmota_energy_total counter
tasmota_energy_total{device="192.168.1.10"} 5.484
# HELP tasmota_energy_yesterday_total Yesterday
# TYPE tasmota_energy_yesterday_total counter
tasmota_energy_yesterday_total{device="192.168.1.10"} 4.088
# HELP tasmota_energy_today_total Today
# TYPE tasmota_energy_today_total counter
tasmota_energy_today_total{device="192.168.1.10"} 1.396
# HELP tasmota_energy_power Power
# TYPE tasmota_energy_power gauge
tasmota_energy_power{device="192.168.1.10"} 0.0
# HELP tasmota_energy_apparentpower ApparentPower
# TYPE tasmota_energy_apparentpower gauge
tasmota_energy_apparentpower{device="192.168.1.10"} 0.0
# HELP tasmota_energy_reactivepower ReactivePower
# TYPE tasmota_energy_reactivepower gauge
tasmota_energy_reactivepower{device="192.168.1.10"} 0.0
# HELP tasmota_energy_factor Factor
# TYPE tasmota_energy_factor gauge
tasmota_energy_factor{device="192.168.1.10"} 0.0
# HELP tasmota_energy_voltage_V Voltage
# TYPE tasmota_energy_voltage_V gauge
tasmota_energy_voltage_V{device="192.168.1.10"} 0.0
# HELP tasmota_energy_current_A Current
# TYPE tasmota_energy_current_A gauge
tasmota_energy_current_A{device="192.168.1.10"} 0.0
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
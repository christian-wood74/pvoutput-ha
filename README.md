# PVOutput Uploader for Home Assistant

The **PVOutput Uploader** is a custom Home Assistant integration that allows you to upload solar power, energy generation, and temperature data from your Home Assistant sensors to [PVOutput.org](https://pvoutput.org/).

## Features

- **Automated Uploads**: Automatically push data to PVOutput at configurable intervals.
- **Sensor Integration**: Select existing Home Assistant sensors for:
  - PV Power Generation (W/kW)
  - PV Energy Generation (Wh/kWh)
  - Temperature (°C/°F)
- **Configurable Interval**: Choose how often data is uploaded (default: 5 minutes).
- **Easy Setup**: Full support for Home Assistant Config Flow (UI-based configuration).

## Installation

### Manual Installation

1. Navigate `custom_components` dir in your Home Assistant `config` directory. 
   1. i.e ` /path_to_ha_installation/config/custom_components`
2. `git clone https://github.com/deishelon/pvoutput-ha.git`
3. Restart Home Assistant.
4. Add the integration in the Home Assistant UI.

## Configuration

1. In the Home Assistant UI, go to **Settings** → **Devices & Services**.
2. Click **Add Integration** and search for **PVOutput Uploader**.
3. Enter your **PVOutput API Key** and **System ID**. You can find these in your [PVOutput Account Settings](https://pvoutput.org/account.jsp).
4. Select the sensors you want to upload:
   - **PV Power Entity**: A sensor providing current power generation (e.g., `sensor.solar_power`).
   - **PV Energy Entity**: A sensor providing cumulative energy generation (e.g., `sensor.solar_energy`).
   - **Temperature Entity**: (Optional) A sensor providing outdoor temperature.
5. Set the **Upload Interval** (in minutes).


## Supported Entities

- **Power**: Sensors with `device_class: power`.
- **Energy**: Sensors with `device_class: energy`.
- **Temperature**: Sensors with `device_class: temperature`.

## Documentation

For more information on PVOutput's API and how to set up your account, visit the [PVOutput API Documentation](https://pvoutput.org/help/api_specification.html).

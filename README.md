# Anthem Shower

A custom [Home Assistant](https://www.home-assistant.io/) integration for Anthem Shower systems. It communicates with the Anthem hub over your local network to expose shower status as a binary sensor.

## Features

- Binary sensor indicating whether the shower is currently running
- Local polling (no cloud dependency)
- Configurable polling interval

## Installation

1. Copy the `anthem_shower` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration** and search for **Anthem Shower**.
4. Enter the IP address of your Anthem hub and your PIN.

## Requirements

- An Anthem Shower hub reachable on your local network
- The PIN configured on your hub
- Home Assistant 2024.1 or later
- Python package `cryptography >= 42.0.0` (installed automatically)

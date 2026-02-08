# Kohler Anthem+ Digital Shower Home Assistant Custom Component

A custom [Home Assistant](https://www.home-assistant.io/) integration for Kohler Anthem+ Digital Shower systems. It communicates with the Anthem hub over your local network to expose shower status as a binary sensor. At this time, I haven't implemented any further sensors or control. But I hope to be able to do this as time allows.

This has only been tested on Anthem+ firmware **2.72**

## Features

- **Auto-discovery** - Anthem shower hubs are automatically detected on your network via mDNS/Zeroconf
- Binary sensor indicating whether the shower is currently running
- Local polling (no cloud dependency)
- Configurable polling interval
- Graceful handling of authentication errors through Home Assistant repairs
- Optional PIN authentication for future control features

## Installation

### HACS (recommended)

1. Install [HACS](https://hacs.xyz/) if you haven't already.
2. In Home Assistant, go to **HACS > Integrations**.
3. Open the three-dot menu in the top right and select **Custom repositories**.
4. Enter `https://github.com/nclpl/anthem_shower` and select **Integration** as the category.
5. Click **Add**, then find **Anthem Shower** in the list and click **Download**.
6. Restart Home Assistant.

### Manual

1. Copy the `anthem_shower` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

### Configuration

#### Automatic Discovery (Recommended)

If your Anthem shower hub is on the same network as Home Assistant, it should be **automatically discovered**. You'll see a notification in Home Assistant asking if you want to add it.

1. Click on the notification or go to **Settings > Devices & Services**.
2. Click **Configure** on the discovered Anthem Shower hub.
3. Optionally enter your PIN if you plan to use control features in the future (not currently implemented).
4. Click **Submit**.

#### Manual Setup

If auto-discovery doesn't work, you can add it manually:

1. Go to **Settings > Devices & Services > Add Integration** and search for **Anthem Shower**.
2. Enter the IP address of your Anthem hub (or use `kohler-myshower.local`).
3. Optionally enter your PIN if you plan to use control features in the future (not currently implemented).
4. Click **Submit**.

## Requirements

- An Anthem Shower hub reachable on your local network
- Home Assistant 2024.1 or later

### About the PIN

The PIN is **optional** for basic functionality. The integration can read the shower running state without authentication - it only requires the hub's IP address.

The PIN is only needed for write operations like starting/stopping water tests or controlling the shower. Since these features are not yet implemented, you can safely leave the PIN blank during setup.

If you do configure a PIN and later change it using the "Generate PIN" function on the Anthem web interface, you'll need to update the PIN in Home Assistant through the integration's re-authentication flow.

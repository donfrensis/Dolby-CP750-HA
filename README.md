# Dolby CP750 Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

Home Assistant integration for Dolby CP750 Cinema Audio Processor.

## Features

- Control and monitor your Dolby CP750 through Home Assistant
- Fader level control (-90.0 to +10.0 dB)
- Input source selection:
  - Digital 1-4
  - Multi-Ch Analog
  - NonSync
  - Mic
- Mute control
- Optional integration with external power switch
- Real-time status monitoring
- Configuration through UI

## Requirements

- Dolby CP750 device accessible via network
- Home Assistant 2024.1.0 or newer
- Optional: power switch entity in Home Assistant

## Installation

### HACS (Recommended)

1. Install [HACS](https://hacs.xyz) if you haven't already
2. Add this repository as a custom repository in HACS:
   - Navigate to HACS → Integrations → ⋮ (top right menu) → Custom repositories
   - Add URL: `https://github.com/donfrensis/dolby-cp750-ha`
   - Category: Integration
3. Click Install
4. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/dolby_cp750` directory to your `config/custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Dolby CP750"
4. Enter:
   - IP address of your CP750
   - Port (default: 61408)
   - Name (optional)
   - Power switch entity (optional)

## Available Services

### dolby_cp750.set_fader
Set fader level
```yaml
service: dolby_cp750.set_fader
target:
  entity_id: dolby_cp750.processor
data:
  value: -20.0  # Range: -90.0 to +10.0
```

### dolby_cp750.set_input
Select input source
```yaml
service: dolby_cp750.set_input
target:
  entity_id: dolby_cp750.processor
data:
  source: "Digital 1"  # One of: Digital 1-4, Multi-Ch Analog, NonSync, Mic
```

### dolby_cp750.set_mute
Set mute state
```yaml
service: dolby_cp750.set_mute
target:
  entity_id: dolby_cp750.processor
data:
  mute: true  # or false
```

## Attributes

The integration exposes the following attributes:
- `fader`: Current fader level (-90.0 to +10.0)
- `input`: Current input source
- `mute`: Current mute state
- `connected`: Connection status
- `power`: Power switch entity (if configured)

## Example Automations

```yaml
# Set fader level when movie starts
automation:
  - alias: "Movie Start - Set Fader"
    trigger:
      platform: state
      entity_id: media_player.projector
      to: 'on'
    action:
      service: dolby_cp750.set_fader
      target:
        entity_id: dolby_cp750.processor
      data:
        value: -20.0

# Switch to NonSync during intermission
automation:
  - alias: "Intermission Audio"
    trigger:
      platform: event
      event_type: intermission_start
    action:
      service: dolby_cp750.set_input
      target:
        entity_id: dolby_cp750.processor
      data:
        source: "NonSync"
```

## Contributing

Feel free to contribute to this project! Whether it's:
- Reporting a bug
- Discussing implementation
- Submitting a fix
- Proposing new features

Just open an issue or submit a pull request!

## License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.

[commits-shield]: https://img.shields.io/github/commit-activity/y/donfrensis/dolby-cp750-ha.svg
[commits]: https://github.com/donfrensis/dolby-cp750-ha/commits/main
[license-shield]: https://img.shields.io/github/license/donfrensis/dolby-cp750-ha.svg
[releases-shield]: https://img.shields.io/github/release/donfrensis/dolby-cp750-ha.svg
[releases]: https://github.com/donfrensis/dolby-cp750-ha/releases
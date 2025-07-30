# AppleTVRemote-GUI

A modern, feature-rich Linux GUI application for controlling Apple TV and HomePod devices using the pyatv library.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)

## Features

### 🔍 Device Discovery & Management
- **Auto-discovery** of Apple TV and HomePod devices on your network
- **Device information** display (name, model, IP address, services)
- **Manual device addition** support
- **Connection status indicators** with real-time updates
- **Device credentials management** with secure storage

### 🔐 Comprehensive Pairing System
- **Full pairing workflow** for different authentication methods
- **PIN-based pairing** for older Apple TV models
- **Device code pairing** for newer Apple TVs (4th gen and later)
- **Secure credential storage** using system keyring
- **Re-pairing capabilities** when credentials expire

### 🎵 Now Playing Controls
- **Media information display** (title, artist, album, artwork)
- **Playback controls** (play/pause, next/previous, seek)
- **Volume control** with visual feedback
- **Progress bar** with seek functionality
- **Real-time artwork** display with automatic updates
- **Playback state** monitoring (repeat, shuffle status)

### 📱 Apple TV Remote Interface
- **Full directional pad** (up, down, left, right, select)
- **System buttons** (Menu, Home, Play/Pause)
- **Volume controls** (up/down with visual feedback)
- **Siri button support** (where available)
- **Keyboard shortcuts** for all remote functions
- **Button press animations** and hover effects

### 🎨 Modern UI Design
- **Clean, modern interface** built with PyQt6
- **Dark/Light theme support** with system integration
- **Responsive layout** that adapts to different screen sizes
- **Smooth animations** and transitions
- **Icon-based controls** with helpful tooltips
- **Professional styling** with contemporary design patterns

## Screenshots

### Main Interface
*Screenshot showing the main application window with device manager and remote control tabs*

### Device Discovery
*Screenshot showing the device discovery interface with found Apple TV devices*

### Now Playing
*Screenshot showing the now playing interface with album artwork and media controls*

## Installation

### Prerequisites

- **Python 3.8+** (tested with Python 3.8, 3.9, 3.10, 3.11)
- **Linux distribution** (Ubuntu 20.04+, Fedora 34+, or equivalent)
- **Network access** to Apple TV/HomePod devices

### Install from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ZProLegend007/AppleTVRemote-GUI.git
   cd AppleTVRemote-GUI
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install system dependencies** (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pyqt6 python3-pyqt6.qtmultimedia
   ```

4. **Install system dependencies** (Fedora/CentOS):
   ```bash
   sudo dnf install python3-PyQt6 python3-PyQt6-multimedia
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

### Install using pip (Development)

```bash
pip install -e .
appletv-remote-gui
```

## Usage

### Getting Started

1. **Launch the application:**
   ```bash
   python main.py
   ```

2. **Discover devices:**
   - The app will automatically scan for devices on startup
   - Click "Discover Devices" to manually scan
   - Found devices appear in the Device Manager panel

3. **Connect to a device:**
   - Click "Connect" next to your Apple TV/HomePod
   - If pairing is required, follow the on-screen instructions
   - Enter the PIN shown on your Apple TV when prompted

4. **Control your device:**
   - Use the **Remote Control** tab for navigation and system controls
   - Use the **Now Playing** tab for media playback control

### Keyboard Shortcuts

#### Remote Control
- **Arrow Keys**: Navigation (up/down/left/right)
- **Enter/Return**: Select
- **Space**: Play/Pause
- **M**: Menu button
- **H**: Home button
- **+/-**: Volume up/down

#### Application
- **Ctrl+D**: Discover devices
- **Ctrl+Q**: Quit application
- **Ctrl+,**: Open preferences

### Device Pairing

#### PIN Pairing (Legacy Apple TVs)
1. Click "Pair" next to your device
2. A PIN will appear on your Apple TV screen
3. Enter the PIN in the dialog box
4. Click "Pair" to complete the process

#### Device Code Pairing (Apple TV 4th gen+)
1. Click "Pair" next to your device
2. A code will be displayed in the app
3. Confirm the code matches on your Apple TV
4. Select "Pair" on your Apple TV to complete

### Configuration

The application stores its configuration in:
- **Linux**: `~/.config/appletv-remote-gui/config.json`
- **Credentials**: Stored securely in system keyring

#### Settings Options
- **Theme**: Choose between Dark and Light themes
- **Auto-discovery**: Enable/disable automatic device discovery on startup
- **Discovery timeout**: Set how long to scan for devices (5-60 seconds)
- **Connection timeout**: Set device connection timeout (5-30 seconds)
- **Debug logging**: Enable detailed logging for troubleshooting

## Troubleshooting

### Common Issues

#### "No devices found"
- Ensure your Apple TV/HomePod is on the same network
- Check that your devices are powered on and connected to WiFi
- Try increasing the discovery timeout in settings
- Verify firewall settings aren't blocking network discovery

#### "Connection failed"
- Device may require pairing - click "Pair" button
- Restart the Apple TV if connection issues persist
- Clear stored credentials in Settings > Devices
- Check network connectivity between your computer and Apple TV

#### "Pairing failed"
- Ensure you're entering the correct PIN from the Apple TV screen
- Make sure no other devices are trying to pair simultaneously
- Restart the Apple TV and try pairing again
- Try using a different pairing method if available

#### Application won't start
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.8+)
- Install PyQt6 system packages for your distribution
- Check console output for specific error messages

### Debug Mode

Enable debug logging in Settings > General > Debug to get detailed information about:
- Device discovery process
- Connection attempts
- Pairing workflows
- API communication

Debug logs are printed to the console when running from terminal.

### Network Requirements

- **Multicast DNS (mDNS)**: Required for device discovery
- **TCP connections**: Various ports for different Apple TV services
- **Same network segment**: Apple TV and computer must be on the same local network

## Development

### Project Structure

```
AppleTVRemote-GUI/
├── main.py                 # Application entry point
├── ui/                     # User interface modules
│   ├── main_window.py      # Main application window
│   ├── device_manager.py   # Device discovery and management
│   ├── remote_control.py   # Apple TV remote interface
│   ├── now_playing.py      # Now playing controls
│   ├── pairing_dialog.py   # Pairing workflow dialogs
│   └── settings.py         # Application settings
├── backend/                # Backend logic modules
│   ├── device_controller.py # PyATV integration
│   ├── pairing_manager.py   # Pairing logic
│   └── config_manager.py    # Configuration management
├── resources/              # Application resources
│   ├── icons/              # UI icons and images
│   ├── styles/             # CSS/QSS stylesheets
│   └── config/             # Default configurations
├── requirements.txt        # Python dependencies
├── setup.py               # Installation script
└── README.md              # This file
```

### Building from Source

1. **Set up development environment:**
   ```bash
   git clone https://github.com/ZProLegend007/AppleTVRemote-GUI.git
   cd AppleTVRemote-GUI
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run in development mode:**
   ```bash
   python main.py
   ```

3. **Run with debug output:**
   ```bash
   PYTHONPATH=. python main.py --debug
   ```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Create a Pull Request

## Dependencies

### Python Packages
- **PyQt6** (>=6.4.0) - Modern GUI framework
- **pyatv** (>=0.14.0) - Apple TV communication library
- **qasync** (>=0.24.0) - Async/await support for Qt
- **aiohttp** (>=3.8.0) - HTTP client/server for asyncio
- **cryptography** (>=3.4.0) - Cryptographic library
- **Pillow** (>=9.0.0) - Image processing library
- **keyring** (>=23.0.0) - Secure credential storage

### System Requirements
- **Linux** with X11 or Wayland
- **Python 3.8+**
- **Qt6** libraries
- **Network access** to local Apple TV/HomePod devices

## Technical Details

### Architecture
- **Async/await** support using qasync for non-blocking operations
- **Separation of concerns** between UI and backend logic
- **Signal-slot** communication for loose coupling
- **Secure credential storage** using system keyring
- **Robust error handling** with user-friendly feedback

### Supported Protocols
- **MRP** (Media Remote Protocol) - Primary Apple TV protocol
- **DMAP** (Digital Media Access Protocol) - Legacy iTunes protocol
- **AirPlay** - Audio/video streaming protocol
- **Companion** - Modern pairing and control protocol

### Supported Devices
- **Apple TV HD** (4th generation)
- **Apple TV 4K** (5th generation and later)
- **HomePod** (original and mini)
- **Legacy Apple TV** models (with limited functionality)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **pyatv library** - Excellent Apple TV communication library by Pierre Ståhl
- **PyQt6** - Powerful cross-platform GUI toolkit
- **Apple** - For creating innovative devices that inspire projects like this
- **Open Source Community** - For the tools and libraries that make this possible

## Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/ZProLegend007/AppleTVRemote-GUI/issues)
- **Discussions**: Join conversations on [GitHub Discussions](https://github.com/ZProLegend007/AppleTVRemote-GUI/discussions)
- **Wiki**: Check the [project wiki](https://github.com/ZProLegend007/AppleTVRemote-GUI/wiki) for additional documentation

## Roadmap

### Planned Features
- [ ] **Multi-device support** - Control multiple Apple TVs simultaneously
- [ ] **Playlist management** - Create and manage playlists
- [ ] **Screen mirroring** - View Apple TV screen on computer
- [ ] **Automation scripts** - Programmable device control
- [ ] **Plugin system** - Extensible functionality
- [ ] **Mobile companion** - Android/iOS remote apps
- [ ] **Voice control** - Integration with speech recognition
- [ ] **Statistics tracking** - Usage analytics and reports

### Version History
- **v1.0.0** - Initial release with core functionality
  - Device discovery and pairing
  - Remote control interface
  - Now playing controls
  - Settings management
  - Dark/Light themes

---

**Made with ❤️ for the Apple TV community**
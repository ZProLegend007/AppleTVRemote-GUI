# ApplerGUI

🍎 **Modern Linux GUI for Apple TV & HomePod Control**

## 🚀 Installation

### ⚡ One-Line Installer (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/install.sh | bash
```
This installer will:
- ✅ Check system dependencies
- ✅ Install ApplerGUI and all requirements
- ✅ Create desktop entry (Linux)
- ✅ Configure PATH if needed

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/ZProLegend007/ApplerGUI.git
cd ApplerGUI

# Install dependencies and the application
pip3 install --user -r requirements.txt
pip3 install --user .
```

### Local Development
```bash
git clone https://github.com/ZProLegend007/ApplerGUI.git
cd ApplerGUI
./install.sh  # Automatically detects local repository
```

## 🔄 Updates

### ⚡ One-Line Updater
```bash
curl -sSL https://raw.githubusercontent.com/ZProLegend007/ApplerGUI/main/update.sh | bash
```
The updater will:
- ✅ Backup your configuration
- ✅ Update to the latest version
- ✅ Preserve your settings
- ✅ Restart the application

### 🏃 Run
```bash
applergui
```
Or if not in PATH:
```bash
~/.local/bin/applergui
```
Or as a Python module:
```bash
python3 -m applergui
```

## ✨ Features

- 🎮 Full Apple TV remote control
- 🎵 Now playing display with artwork
- 📱 Device discovery and pairing
- 🎨 Modern dark/light themes
- ⌨️ Keyboard shortcuts
- 🔧 Easy configuration

## 📖 Usage

After installation, launch from:
- **GUI**: Application menu → ApplerGUI
- **Terminal**: `applergui`

## 🛠️ Troubleshooting

Visit our [Wiki](wiki) for help with common issues.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

---

## Detailed Documentation

### Installation Details

The professional installer provides:
- **Smart dependency detection** - Automatically installs required packages
- **Sudo management** - Only requests elevated privileges when necessary
- **Interactive configuration** - Choose installation options that suit your needs
- **Error recovery** - Graceful handling of installation issues
- **Multiple distributions** - Support for Ubuntu, Fedora, Arch, and more

### Installation Options

During installation, you'll be prompted for:

- **Desktop integration** - Add to application menu
- **System-wide vs user installation** - Install for all users or current user
- **Command-line access** - Create 'applergui' terminal command
- **Development tools** - Additional dependencies for contributors
- **Auto-start configuration** - Launch on system boot
- **Additional themes and codecs** - Enhanced UI and media support

### System Requirements

- **Linux** (Ubuntu 20.04+, Fedora 34+, Arch, or equivalent)
- **Python 3.8+** (automatically installed if needed)
- **Network access** to Apple TV/HomePod devices

### Supported Devices

- **Apple TV HD** (4th generation)
- **Apple TV 4K** (5th generation and later)
- **HomePod** (original and mini)
- **Legacy Apple TV** models (with limited functionality)

### Architecture & Implementation

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

### Troubleshooting

#### Installation Issues

- **"Permission denied"**: Don't run as root - installer will ask for sudo when needed
- **"Package not found"**: Update package manager first (`sudo apt update`)
- **Python version issues**: Ensure Python 3.8+ is installed
- **"Command not found: applergui"**: Restart terminal or run `source ~/.bashrc`

#### Application Issues

- **"No devices found"**: Ensure Apple TV is on same network and powered on
- **"Connection failed"**: Device may require pairing - click "Pair" button
- **"Pairing failed"**: Enter correct PIN from Apple TV screen
- **GUI issues**: Update graphics drivers or try `QT_QUICK_BACKEND=software`

#### Debug Mode

Enable debug logging:
```bash
python main.py --debug
```

### Development

#### Quick Start
```bash
git clone https://github.com/ZProLegend007/ApplerGUI.git
cd ApplerGUI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

#### Project Structure
```
ApplerGUI/
├── main.py                 # Application entry point
├── ui/                     # User interface modules
├── backend/                # Backend logic modules
├── resources/              # Application resources
├── requirements.txt        # Python dependencies
└── install.sh             # Professional installer
```

## Dependencies

### Python Packages
- **PyQt6** (>=6.4.0) - Modern GUI framework
- **pyatv** (>=0.14.0) - Apple TV communication library
- **qasync** (>=0.24.0) - Async/await support for Qt
- **aiohttp** (>=3.8.0) - HTTP client/server for asyncio
- **cryptography** (>=3.4.0) - Cryptographic library
- **Pillow** (>=9.0.0) - Image processing library
- **keyring** (>=23.0.0) - Secure credential storage

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/ZProLegend007/ApplerGUI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ZProLegend007/ApplerGUI/discussions)
- **Wiki**: [Project Wiki](https://github.com/ZProLegend007/ApplerGUI/wiki)

---

**Made with ❤️ for the Apple TV community**
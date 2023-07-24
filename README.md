# XMRANSOM

**Disclaimer**: This ransomware script is meant for educational and informational purposes only. Unauthorized use of this script for any malicious or illegal activities is strictly prohibited. The author of this script bears no responsibility for any misuse or damage caused by the implementation and use of this ransomware. Use this script responsibly and only on your own systems or with explicit permission from system owners.

## Prerequisites

To run this ransomware script, ensure you have the following installed:

- Python 3.x
- `tkinter` library (standard with most Python installations)
- `screeninfo` library (`pip install screeninfo`)
- `cryptography` library (`pip install cryptography`)
- `psutil` library (`pip install psutil`)

## Features

This ransomware script demonstrates the following features:

- A graphical user interface (GUI) created with Tkinter, displaying a threatening message and a button to open a tutorial on how to pay the ransom.
- A text file (`labels.txt`) is used to store the threatening message and the XMR (Monero) address for ransom payment.
- The script attempts to gain admin privileges and sets itself to run at startup, ensuring persistence on Windows systems.
- On Unix systems, the script tries to add itself to the user's crontab to run at startup with elevated privileges.
- All accessible drives are enumerated (excluding system drives, empty CD drives, and disconnected network drives).
- The script attempts to kill all currently running tasks, which ensures that the ransomware is the only running task on the machine.
- All files in the accessible drives are encrypted using AES encryption with PBKDF2HMAC for key generation and CFB mode for encryption.
- The key to decrypt the files is generated from a hardcoded password for simplicity (`123456789`) and can ofc be changed by you.

## Usage

1. **Clone the Repository**: Download or clone the repository containing the ransomware script and related files.

2. **Install Dependencies**: Make sure you have all the required dependencies installed. Open a terminal or command prompt and run the following commands:
- `pip install screeninfo`
- `pip install cryptography`
- `pip install psutil`
- `pip install pyinstaller` [optional if you want to build the python file to .exe or .pkg]

3. **Run the Ransomware**: Execute the ransomware script with Python: python main.py
4. **Build the Ransomware [optional]**: Execture the following command to build the script: 
- `pyinstaller --onefile --windowed --add-data "images;images" --add-data "labels.txt;." main.py`

**Warning**: Please be extremely cautious while running this ransomware script. It is designed for educational purposes and should never be used maliciously. Always test such scripts on isolated systems and with explicit permission. Use of ransomware for illegal activities can lead to severe legal consequences.

**Disclaimer**: This script is provided for educational purposes only. I (The Author) bear no responsibility for any misuse or harm caused by the use of this script. Use it responsibly, ethically, and legally.
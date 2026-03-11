VEER AI – Complete Setup Guide

This guide explains how to install and run the VEER Offline Hindi Voice Assistant on Raspberry Pi.

The assistant works completely offline using speech recognition and text-to-speech models.

1. Hardware Requirements

The following hardware is required to run VEER AI:

Raspberry Pi 4 or Raspberry Pi 5
MicroSD card (32GB recommended)
USB microphone
Speaker or headphones
USB sound card (recommended for stable audio)
Power adapter

Optional components:

LED for GPIO demonstration
Camera module for future upgrades

2. Install Raspberry Pi OS

Download Raspberry Pi Imager from the official Raspberry Pi website.

Install Raspberry Pi OS Lite (64-bit) on the microSD card.

While flashing the OS, enable:

SSH access
Wi-Fi (optional if using wireless connection)

Insert the SD card into the Raspberry Pi and boot the system.

3. Connect to the Raspberry Pi

You can connect to the Raspberry Pi using SSH from your computer.

Example command:

ssh pi@raspberrypi.local

or

ssh username@raspberrypi.local

Enter the password when prompted.

4. Update the System

Update the Raspberry Pi system packages.

Run the following commands:

sudo apt update
sudo apt upgrade -y

5. Install Required System Packages

Install the required system dependencies.

sudo apt install python3 python3-pip python3-venv git mpg123 ffmpeg alsa-utils -y

These packages are required for:

Python environment
Audio playback
System utilities

6. Download the Project Files

Download the VEER project files from the GitHub repository.

Example:

git clone https://github.com/Shinde-Digvijay/Offline_Hindi_Assistant_On_Raspberrypi4.git

Move into the project directory:

cd veer-ai-assistant

7. Create Python Virtual Environment

Create a virtual environment for Python.

python3 -m venv venv

Activate the environment:

source venv/bin/activate

8. Install Python Libraries

Install the required Python libraries.

pip install vosk sounddevice gpiozero numpy

These libraries are used for:

Speech recognition
Audio input processing
GPIO control
Data processing

9. Download VOSK Speech Recognition Model

Download the Hindi speech recognition model.

wget https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip

Unzip the model:

unzip vosk-model-small-hi-0.22.zip

Rename the folder to model:

mv vosk-model-small-hi-0.22 model

The model folder should now be inside the project directory.

10. Download Piper Hindi Voice Model

Download the Hindi text-to-speech model used by the assistant.

wget https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx

Place this file in the main project folder.

11. Verify Audio Devices

Check that the speaker and microphone are detected by the system.

List playback devices:

aplay -l

List microphone devices:

arecord -l

Test microphone recording:

arecord test.wav

Play the recorded file:

aplay test.wav

If you hear your voice, the microphone and speaker are working correctly.

12. Add Songs (Optional Feature)

Create a folder for songs inside the project directory.

mkdir songs

Add MP3 or WAV files to this folder.

The assistant will randomly play songs from this directory when asked.

13. Run the VEER Assistant

Activate the virtual environment.

source venv/bin/activate

Run the assistant:

python main.py

If everything is working correctly, the assistant will say:

“वीर आपकी सहायता के लिए तैयार है”

The assistant is now listening for commands.

14. Example Commands

Some example commands you can try:

Veer time kya hai
Veer aaj ki date kya hai
Veer gaana chalao
Veer 5 minute ka timer lagao
Veer alarm lagao 7 baje
Veer reminder lagao

15. Enable Auto Start on Boot (Optional)

If you want the assistant to start automatically when the Raspberry Pi boots, create a system service.

Create a service file:

sudo nano /etc/systemd/system/veer.service

Paste the following configuration inside the file.

[Unit]
Description=VEER AI Offline Assistant
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/veer-ai-assistant
ExecStart=/home/pi/veer-ai-assistant/venv/bin/python /home/pi/veer-ai-assistant/main.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
SupplementaryGroups=audio

[Install]
WantedBy=multi-user.target

Save and exit the file.

16. Enable the Service

Reload system services.

sudo systemctl daemon-reload

Enable the VEER service.

sudo systemctl enable veer.service

Start the service.

sudo systemctl start veer.service

Check service status.

sudo systemctl status veer.service

17. Test Boot Startup

Restart the Raspberry Pi.

sudo reboot

After the system boots, the assistant should automatically start and say:

“वीर आपकी सहायता के लिए तैयार है”

Final Notes

The VEER assistant runs completely offline using:

VOSK Speech Recognition
Piper Text-to-Speech
Python command processing

The system has been tested on Raspberry Pi with USB microphone and external speaker
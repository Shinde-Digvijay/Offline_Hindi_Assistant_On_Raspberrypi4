# 🎙 VEER AI – Offline Hindi Voice Assistant

Fully offline Hindi voice assistant built on Raspberry Pi 4.

---

## 🚀 Features

- Wake word: **"Veer"**
- Alarm system
- Timer
- Reminders
- Date & Day lookup
- Relative week date lookup
- Multiplication tables (पाड़ा)
- Hindi calculator
- Music player
- GPIO light control
- Fully offline (Vosk + Piper)

---

## 🧰 Requirements

- Raspberry Pi 4
- Python 3
- Vosk Hindi Model
- Piper Hindi TTS
- mpg123
- aplay

---

## 🛠 Installation

### 1️⃣ Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 2️⃣ Install Required System Packages

```bash
sudo apt install python3 python3-venv python3-pip mpg123 git -y
sudo apt install python3-lgpio
```

### 3️⃣ Clone Repository

```bash
git clone https://github.com/Shinde-Digvijay/Hindi_Assistant.git
cd Hindi_Assistant
```

### 4️⃣ Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 5️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 📥 Download Required Models

### 🔹 Vosk Hindi Model

Download from:  
https://alphacephei.com/vosk/models  

Recommended:
```
vosk-model-small-hi-0.22
```

Extract into:
```
Hindi_Assistant/model/
```

---

### 🔹 Piper TTS

Download from:  
https://github.com/rhasspy/piper/releases  

Extract into:
```
Hindi_Assistant/piper/
```

---

### 🔹 Hindi Voice Model

Download:
```
hi_IN-pratham-medium.onnx
hi_IN-pratham-medium.onnx.json
```

Place both files in the project root folder.

---

## 📁 Project Structure

```
Hindi_Assistant/
│
├── main.py
├── config_data.json
├── alarm.mp3
├── hi_IN-pratham-medium.onnx
├── hi_IN-pratham-medium.onnx.json
├── model/
├── piper/
├── songs/
├── requirements.txt
├── README.md
├── .gitignore
└── docs/
    └── supported_commands.txt
```

---

## ▶ Run Assistant

```bash
python main.py
```

You should see:

```
🟢 VEER AI READY
🎤 Listening...
```

---

## 📌 Notes

- Fully offline – no cloud APIs used
- Designed for Raspberry Pi 4
- Optimized for low-latency voice interaction

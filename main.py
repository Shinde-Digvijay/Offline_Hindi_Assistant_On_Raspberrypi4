import os
import sys
import json
import queue
import datetime
import time
import subprocess
import sounddevice as sd
import vosk
import threading
import random
import re
import signal
from gpiozero import LED

# GLOBALS

is_song_paused = False
song_list = []
current_song_index = -1
q = queue.Queue()
piper_process = None
aplay_process = None
is_speaking = False
last_response_time = 0
COOLDOWN_TIME = 0.5
timer_active = False
timer_thread = None
reminder_active = False
reminder_thread = None
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SONG_FOLDER = os.path.join(CURRENT_DIR, "songs")
song_process = None
is_song_playing = False
alarm_thread = None
alarm_active = False
alarm_process = None
last_spoken_text = ""
ALARM_KEYWORDS = [
    "अलार्म",
    "आलार्म",
    "आलराम",
    "अलराम"
]

CONFIG_FILE = "config_data.json"
VOSK_MODEL_PATH = "model"
WAKE_WORDS = ["veer", "वीर"]
HINDI_DAY_TO_INDEX = {
    "सोमवार": 0,
    "मंगलवार": 1,
    "बुधवार": 2,
    "गुरुवार": 3,
    "शुक्रवार": 4,
    "शनिवार": 5,
    "रविवार": 6
}

DAY_MAP = {
    "Monday": "सोमवार",
    "Tuesday": "मंगलवार",
    "Wednesday": "बुधवार",
    "Thursday": "गुरुवार",
    "Friday": "शुक्रवार",
    "Saturday": "शनिवार",
    "Sunday": "रविवार"
}
MONTH_MAP = {
    "जनवरी": 1,
    "फरवरी": 2,
    "मार्च": 3,
    "अप्रैल": 4,
    "मई": 5,
    "जून": 6,
    "जुलाई": 7,
    "अगस्त": 8,
    "सितंबर": 9,
    "अक्टूबर": 10,
    "नवंबर": 11,
    "दिसंबर": 12
}
ENGLISH_TO_HINDI_MONTH = {
    "January": "जनवरी",
    "February": "फरवरी",
    "March": "मार्च",
    "April": "अप्रैल",
    "May": "मई",
    "June": "जून",
    "July": "जुलाई",
    "August": "अगस्त",
    "September": "सितंबर",
    "October": "अक्टूबर",
    "November": "नवंबर",
    "December": "दिसंबर"
}

LED_PIN = 17  
light_led = LED(LED_PIN)

HINDI_NUMS = {}
REVERSE_HINDI = {}

try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        HINDI_NUMS = data.get("hindi_numbers", {})
        REVERSE_HINDI = {v: k for k, v in HINDI_NUMS.items()}
except Exception as e:
    print("⚠ Number dictionary not loaded:", e)

# TTS

def start_tts():
    global piper_process, aplay_process
    piper_path = os.path.join(CURRENT_DIR, "piper", "piper")
    model_path = os.path.join(CURRENT_DIR, "hi_IN-pratham-medium.onnx")

    piper_process = subprocess.Popen(
        [piper_path, "--model", model_path, "--output-raw"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    aplay_process = subprocess.Popen(
        ["aplay", "-D", "default", "-r", "22050",
        "-f", "S16_LE", "-t", "raw"],
        stdin=piper_process.stdout
    )

def speak(text):
    global is_speaking, last_response_time, last_spoken_text

    print("🗣️", text)

    last_spoken_text = text.lower()  
    is_speaking = True

    with q.mutex:
        q.queue.clear()

    piper_process.stdin.write((text + "\n").encode("utf-8"))
    piper_process.stdin.flush()

    last_response_time = time.time()
    time.sleep(COOLDOWN_TIME)
    is_speaking = False

def clean_speech_text(text):

    filler_words = [
        "अ", "आ", "आँ", "अं",
        "हम्म", "हूं", "हूँ",
        "मतलब",
        "तो",
        "जैसे",
        "वो",
        "ना",
        "है ना",
        "उह",
        "ओह"
    ]

    words = text.split()
    cleaned_words = []

    for word in words:
        if word not in filler_words:
            cleaned_words.append(word)

    return " ".join(cleaned_words)
def remove_stutter(text):

    words = text.split()
    cleaned = []
    previous = ""

    for word in words:
        if len(word) == 1 and word == previous:
            continue
        if word == previous:
            continue

        cleaned.append(word)
        previous = word

    return " ".join(cleaned)
def normalize_spacing(text):
    return " ".join(text.split())
def preprocess_text(text):

    text = clean_speech_text(text)
    text = remove_stutter(text)
    text = normalize_spacing(text)

    return text

# SONG SYSTEM

def play_random_song():
    global song_process, is_song_playing, song_list, current_song_index, is_song_paused

    if not os.path.exists(SONG_FOLDER):
        speak("सॉन्ग फोल्डर नहीं मिला")
        return

    song_list = [f for f in os.listdir(SONG_FOLDER)
                if f.endswith((".mp3", ".wav"))]

    if not song_list:
        speak("कोई गाना नहीं मिला")
        return

    current_song_index = random.randint(0, len(song_list) - 1)
    song_path = os.path.join(SONG_FOLDER, song_list[current_song_index])

    if song_process:
        try:
            song_process.terminate()
        except:
            pass

    is_song_playing = True
    is_song_paused = False

    print(f"🎵 Playing: {song_list[current_song_index]}")
    speak("गाना चला रहा हूँ")

    song_process = subprocess.Popen(
        ["mpg123", song_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def stop_song():
    global song_process, is_song_playing, is_song_paused

    if song_process:
        try:
            song_process.terminate()
        except:
            pass
        song_process = None
        is_song_playing = False
        is_song_paused = False
        speak("गाना बंद कर दिया")
    else:
        speak("कोई गाना चालू नहीं है")

def pause_song():
    global song_process, is_song_paused
    if song_process and not is_song_paused:
        song_process.send_signal(signal.SIGSTOP)
        is_song_paused = True
        speak("गाना रोक दिया")

def resume_song():
    global song_process, is_song_paused
    if song_process and is_song_paused:
        song_process.send_signal(signal.SIGCONT)
        is_song_paused = False
        speak("गाना फिर से चालू किया")

def play_next_song():
    if song_list:
        global current_song_index
        current_song_index = (current_song_index + 1) % len(song_list)
        play_random_song()

def play_previous_song():
    if song_list:
        global current_song_index
        current_song_index = (current_song_index - 1) % len(song_list)
        play_random_song()

# NUMBER EXTRACTION (HINDI + DIGIT)

def extract_number_from_text(text):
    # First try digit
    digit_match = re.search(r'\d+', text)
    if digit_match:
        return int(digit_match.group())

    # Then try Hindi word
    words = text.split()
    for word in words:
        if word in REVERSE_HINDI:
            return int(REVERSE_HINDI[word])

    return None

# MULTIPLICATION TABLE

def tell_table(text):
    global REVERSE_HINDI, HINDI_NUMS

    if not any(word in text for word in ["टेबल", "पढ़ा", "पाड़ा", "पारा"]):
        return False

    match = re.search(r'(.+?) का', text)
    if not match:
        return False

    number_word = match.group(1).strip()

    if number_word in REVERSE_HINDI:
        number = int(REVERSE_HINDI[number_word])
    elif number_word.isdigit():
        number = int(number_word)
    else:
        return False

    if number > 20:
        speak("मैं अभी बीस तक का टेबल बता सकता हूँ")
        return True

    number_word_spoken = HINDI_NUMS.get(str(number), str(number))

    speak(f"{number_word_spoken} का टेबल सुनिए")

    for i in range(1, 11):
        result = number * i

        i_word = HINDI_NUMS.get(str(i), str(i))
        result_word = HINDI_NUMS.get(str(result), str(result))

        speak(f"{number_word_spoken} गुणा {i_word} बराबर {result_word}")

    return True

# TIMER

def start_timer(minutes):
    global timer_active, timer_thread

    if timer_active:
        speak("टाइमर पहले से चल रहा है")
        return

    timer_active = True
    speak(f"{minutes} मिनट का टाइमर शुरू किया")

    def timer_worker():
        global timer_active
        time.sleep(minutes * 60)
        if timer_active:
            speak("टाइमर पूरा हो गया")
            timer_active = False

    timer_thread = threading.Thread(target=timer_worker, daemon=True)
    timer_thread.start()


def stop_timer():
    global timer_active
    timer_active = False
    speak("टाइमर बंद कर दिया")

# REMINDER

def start_reminder(minutes, task):
    global reminder_active, reminder_thread

    reminder_active = True
    speak(f"{minutes} मिनट बाद आपको {task} याद दिलाऊंगा")

    def reminder_worker():
        global reminder_active
        time.sleep(minutes * 60)
        if reminder_active:
            speak(f"{task} करने का समय हो गया है")
            reminder_active = False

    reminder_thread = threading.Thread(target=reminder_worker, daemon=True)
    reminder_thread.start()

# FIXED TIME REMINDER

def start_fixed_time_reminder(hour, minute, task):
    def reminder_worker():
        now = datetime.datetime.now()

        reminder_time = now.replace(hour=hour, minute=minute,
                                    second=0, microsecond=0)

        if reminder_time <= now:
            reminder_time += datetime.timedelta(days=1)

        wait_seconds = (reminder_time - now).total_seconds()

        time.sleep(wait_seconds)

        speak(f"याद दिला रहा हूँ, {task}")

    threading.Thread(target=reminder_worker, daemon=True).start()


def stop_reminder():
    global reminder_active
    reminder_active = False
    speak("रिमाइंडर बंद कर दिया")

def cancel_reminder():
    global reminder_active
    reminder_active = False
    speak("रिमाइंडर रद्द कर दिया गया है")

def extract_hour_minute(text):
    hour = None
    minute = 0

    # Convert Hindi numbers → digits first
    for word, num in REVERSE_HINDI.items():
        text = text.replace(word, num)

    match = re.search(r'(\d+)\s*बज[ेकर]*\s*(\d+)?', text)

    if match:
        hour = int(match.group(1))
        if match.group(2):
            minute = int(match.group(2))

    return hour, minute

# ALARM SYSTEM

def start_alarm(hour, minute):
    global alarm_thread, alarm_active

    if alarm_active:
        speak("अलार्म पहले से सेट है")
        return

    alarm_active = True
    speak(f"{hour} बजकर {minute} मिनट का अलार्म लगा दिया गया है")

    def alarm_worker():
        global alarm_active, alarm_process

        now = datetime.datetime.now()

        alarm_time = now.replace(hour=hour, minute=minute,
                                second=0, microsecond=0)

        if alarm_time <= now:
            alarm_time += datetime.timedelta(days=1)

        wait_seconds = (alarm_time - now).total_seconds()

        time.sleep(wait_seconds)

        if alarm_active:
            speak("अलार्म बज रहा है")

            alarm_path = os.path.join(CURRENT_DIR, "alarm.mp3")

            alarm_process = subprocess.Popen(
                ["mpg123", alarm_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

    alarm_thread = threading.Thread(target=alarm_worker, daemon=True)
    alarm_thread.start()


def stop_alarm():
    global alarm_active, alarm_process

    if not alarm_active:
        speak("कोई अलार्म चालू नहीं है")
        return

    alarm_active = False

    if alarm_process:
        try:
            alarm_process.terminate()
        except:
            pass

    speak("अलार्म बंद कर दिया गया है")

# TIME / DATE / DAY

def tell_time():
    now = datetime.datetime.now()
    speak(f"अभी {now.hour} बजकर {now.minute} मिनट हुए हैं")

def tell_day():
    english_day = datetime.datetime.now().strftime('%A')
    hindi_day = DAY_MAP.get(english_day, english_day)
    speak(f"आज {hindi_day} है")

def tell_date():
    today = datetime.date.today()

    day = today.day
    year = today.year

    english_month = today.strftime('%B')
    hindi_month = ENGLISH_TO_HINDI_MONTH.get(english_month, english_month)

    speak(f"आज {day} {hindi_month} {year} है")

def normalize_hindi_number(word):
    word = word.replace("इस", "ईस")
    word = word.replace("बिस", "बीस")
    word = word.replace("सतरह", "सत्रह")
    word = word.replace("अट्ठारह", "अट्ठारह")
    word = word.replace("अठाईस", "अट्ठाईस")
    word = word.replace("छे", "छः",)

    word = word.replace("ट्ट", "ट्ठ")

    return word

def tell_day_of_date(text):
    today = datetime.date.today()
    year = today.year
    words = text.split()

    # Step 1: Find month
    month = None
    month_name_found = None

    for month_name in MONTH_MAP:
        if month_name in text:
            month = MONTH_MAP[month_name]
            month_name_found = month_name
            break

    if not month:
        return False

    # Step 2: Extract word before month as day
    try:
        month_index = words.index(month_name_found)
        day_word = words[month_index - 1]
    except:
        return False

    # Normalize word
    day_word = normalize_hindi_number(day_word)

    day = None

    # 1️ Direct match
    if day_word in REVERSE_HINDI:
        day = int(REVERSE_HINDI[day_word])

    # 2️ Digit
    elif day_word.isdigit():
        day = int(day_word)

    # 3️ Fuzzy match by first 3 letters
    else:
        for hindi_word, number in REVERSE_HINDI.items():
            if day_word[:3] == hindi_word[:3]:
                day = int(number)
                break

    if day is None:
        return False

    # Step 3: Extract year (look for 4 digit number first)
    for w in words:
        if w.isdigit() and len(w) == 4:
            year = int(w)
            break

    try:
        date_obj = datetime.date(year, month, day)
        english_day = date_obj.strftime('%A')
        hindi_day = DAY_MAP.get(english_day, english_day)

        speak(f"{day} {month_name_found} {year} को {hindi_day} था")
        return True

    except:
        speak("यह तारीख मान्य नहीं है")
        return True

def tell_date_of_relative_day(text):

    today = datetime.date.today()
    today_index = today.weekday()

    words = text.split()
    direction = None

    # Direction detection
    if any(w in words for w in ["पिछला", "पिछले", "पिछली"]):
        direction = "previous"
    elif any(w in words for w in ["अगला", "अगले", "अगली"]):
        direction = "next"
    elif "इस" in words:
        direction = "this"

    if not direction:
        return False

    # Detect day
    target_day_index = None
    target_day_name = None

    for day_name, index in HINDI_DAY_TO_INDEX.items():
        if day_name in text:
            target_day_index = index
            target_day_name = day_name
            break

    if target_day_index is None:
        return False

    # ---- STRICT WEEK LOGIC ----

    if direction == "next":
        diff = (target_day_index - today_index + 7) % 7
        if diff == 0:
            diff = 7

    elif direction == "previous":
        diff = -((today_index - target_day_index + 7) % 7)
        if diff == 0:
            diff = -7

    elif direction == "this":
        diff = target_day_index - today_index

    result_date = today + datetime.timedelta(days=diff)

    english_month = result_date.strftime('%B')
    hindi_month = ENGLISH_TO_HINDI_MONTH.get(english_month, english_month)

    # Proper prefix
    if direction == "previous":
        prefix = "पिछले"
    elif direction == "next":
        prefix = "अगले"
    else:
        prefix = "इस"

    # Proper tense
    if direction == "previous":
        speak(f"{prefix} {target_day_name} की तारीख {result_date.day} {hindi_month} {result_date.year} थी")
    else:
        speak(f"{prefix} {target_day_name} की तारीख {result_date.day} {hindi_month} {result_date.year} है")

    return True

# CALCULATOR

def extract_all_numbers(text):
    words = text.split()
    numbers = []
    current_value = 0

    for word in words:
        # Digit
        if word.isdigit():
            numbers.append(int(word))
            continue

        # Hindi number word
        if word in REVERSE_HINDI:
            value = int(REVERSE_HINDI[word])

            if value == 100:
                current_value *= 100
            elif value == 1000:
                current_value *= 1000
            else:
                current_value += value
        else:
            if current_value != 0:
                numbers.append(current_value)
                current_value = 0

    if current_value != 0:
        numbers.append(current_value)

    return numbers

def tell_calculation(text):

    words = text.split()

    numbers = extract_all_numbers(text)

    if len(numbers) < 2:
        return False

    num1, num2 = numbers[0], numbers[1]

    result = None

    # Addition
    if any(op in text for op in ["जोड़", "प्लस", "और"]):
        result = num1 + num2

    # Subtraction
    elif any(op in text for op in ["घटा", "माइनस"]):
        result = num1 - num2

    # Multiplication
    elif any(op in text for op in ["गुणा", "इंटू", "गुना"]):
        result = num1 * num2

    # Division
    elif any(op in text for op in ["भाग", "डिवाइड"]):
        if num2 == 0:
            speak("शून्य से भाग नहीं कर सकते")
            return True
        result = num1 / num2

    if result is None:
        return False

    # Convert result to Hindi 
    result_str = str(int(result)) if result == int(result) else str(result)

    result_word = HINDI_NUMS.get(result_str, result_str)

    speak(f"उत्तर {result_word} है")

    return True

# MAIN COMMAND ROUTER

def process_command(text):
    
    # ALARM OFF

    if any(k in text for k in ALARM_KEYWORDS) and \
    any(x in text for x in ["बंद", "ऑफ", "रोक"]):
        stop_alarm()
        return


    # ALARM SET

    if any(k in text for k in ALARM_KEYWORDS) and \
        ("बजे" in text or "बजकर" in text):

        hour, minute = extract_hour_minute(text)

        if hour is not None:
            start_alarm(hour, minute)
        else:
            speak("कितने बजे का अलार्म लगाना है?")

        return

    #  CANCEL REMINDER 

    if "रिमाइंडर बंद" in text or "याद बंद" in text:
        cancel_reminder()
        return

    #  FIXED TIME REMINDER 

    if ("बजे" in text or "बजकर" in text) and ("याद" in text or "रिमाइंडर" in text):

        hour, minute = extract_hour_minute(text)

        if hour is not None:

            cleaned_text = re.sub(r'\d+\s*बज[ेकर]*\s*\d*', '', text)
            cleaned_text = cleaned_text.replace("मुझे", "")
            cleaned_text = cleaned_text.replace("याद दिलाना", "")
            cleaned_text = cleaned_text.replace("रिमाइंडर", "")
            cleaned_text = cleaned_text.replace("पर", "")
            cleaned_text = cleaned_text.strip()

            task = cleaned_text if cleaned_text else "आपका काम"

            start_fixed_time_reminder(hour, minute, task)
            speak(f"{hour} बजकर {minute} मिनट पर याद दिला दूँगा")
            return

    #  TIMER

    if "टाइमर" in text:
        minutes = extract_number_from_text(text)
        if minutes:
            start_timer(minutes)
        else:
            speak("कितने मिनट का टाइमर लगाना है?")
        return

    #  RELATIVE REMINDER (After X Minutes)

    if "याद" in text or "रिमाइंडर" in text:

        minutes = extract_number_from_text(text)

        if minutes:
            task = ""

            if "बाद" in text:
                task = text.split("बाद")[-1]

            task = task.replace("याद दिलाना", "")
            task = task.replace("मुझे", "")
            task = task.strip()

            if not task:
                task = "आपका काम"

            start_reminder(minutes, task)
        else:
            speak("कितने मिनट बाद याद दिलाना है?")

        return

    #  LIGHT CONTROL

    if any(x in text for x in ["चालू"]) and any(x in text for x in ["लाइट", "बत्ती", "तुबेलाइट"]):
        light_led.on()
        speak("लाइट चालू कर दी")
        return

    if any(x in text for x in ["बंद"]) and any(x in text for x in ["लाइट", "बत्ती", "तुबेलाइट"]):
        light_led.off()
        speak("लाइट बंद कर दी")
        return

    #  SONG CONTROLS

    if "बंद करो" in text:
        if is_song_playing:
            stop_song()
        else:
            speak("कुछ भी चालू नहीं है")
        return

    if any(w in text for w in ["अगला", "next"]):
        play_next_song()
        return

    if any(w in text for w in ["पिछला", "previous"]):
        play_previous_song()
        return

    if any(x in text for x in ["रोक", "pause"]):
        pause_song()
        return

    if any(x in text for x in ["फिर से", "resume"]):
        resume_song()
        return

    if any(w in text for w in ["गाना", "गीत", "संगीत", "सॉन्ग"]):
        play_random_song()
        return

    # CALCULATOR

    if tell_calculation(text):
        return

    #  MULTIPLICATION TABLE

    if tell_table(text):
        return

    #  RELATIVE WEEK DATE LOOKUP
    words = text.split()

    if (any(w in words for w in ["अगला", "अगले", "अगली",
                                "पिछला", "पिछले", "पिछली",
                                "इस"])) and \
    any(day in text for day in HINDI_DAY_TO_INDEX):

        if tell_date_of_relative_day(text):
            return

    #  SPECIFIC DATE DAY LOOKUP

    if ("को" in text) and any(x in text for x in ["कौनसा", "कौन सा", "वार", "दिन"]):
        if tell_day_of_date(text):
            return

    #  CURRENT TIME
    
    if any(x in text for x in ["कितने बज", "टाइम", "समय"]):
        tell_time()
        return

    #  CURRENT DATE
    if any(x in text for x in ["तारीख", "डेट"]):
        tell_date()
        return

    #  CURRENT DAY
    if any(x in text for x in ["दिन", "वार", "डे"]):
        tell_day()
        return

    #  PM OF INDIA
    if any(x in text for x in ["प्राइम मिनिस्टर", "प्रधानमंत्री", "पि एम"]):
        speak("भारत के प्रधानमंत्री नरेंद्र मोदी हैं")
        return

    #  CAPITAL OF INDIA
    
    if any(x in text for x in ["भारत", "इंडिया", "हिन्दुस्थान"]) and \
    any(x in text for x in ["कैपिटल", "राजधानी"]):

        speak("भारत की राजधानी नई दिल्ली है")
        return

    # ❌ FALLBACK

    speak("क्षमा करें, मैं इसमें आपकी सहायता नहीं कर सकता")
    
# VOSK

if not os.path.exists(VOSK_MODEL_PATH):
    print("Model missing")
    sys.exit(1)

model = vosk.Model(VOSK_MODEL_PATH)
rec = vosk.KaldiRecognizer(model, 44100)

def callback(indata, frames, time_info, status):
    if not is_speaking:
        q.put(bytes(indata))

# MAIN LOOP

if __name__ == "__main__":

    start_tts()
    print("🟢 VEER AI READY")

    with sd.RawInputStream(
        samplerate=44100,
        blocksize=4096,
        dtype='int16',
        channels=1,
        callback=callback
    ):

        print("🎤 Listening...")

        try:
            while True:
                data = q.get()

                if rec.AcceptWaveform(data):

                    if is_speaking:
                        continue

                    if time.time() - last_response_time < 0.7:
                        continue

                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip().lower()

                    if last_spoken_text and last_spoken_text in text:
                        print("Ignored self echo")
                        continue

                    if not text:
                        continue

                    print("🎙 Heard:", text)

                    words = text.split()
                    if not words:
                        continue

                    if words[0] not in WAKE_WORDS:
                        print("Wake word missing")
                        continue

                    command = " ".join(words[1:])
                    command = preprocess_text(command)
                    process_command(command)

        except KeyboardInterrupt:
            print("\n🛑 VEER AI shutting down safely...")

            # Stop song if playing
            if song_process:
                try:
                    song_process.terminate()
                except:
                    pass
            # Turn off LED safely
            try:
                light_led.off()
            except:
                pass

            # Stop Piper
            if piper_process:
                try:
                    piper_process.terminate()
                except:
                    pass

            # Stop aplay
            if aplay_process:
                try:
                    aplay_process.terminate()
                except:
                    pass

            print("✅ Shutdown complete.")
            sys.exit(0)

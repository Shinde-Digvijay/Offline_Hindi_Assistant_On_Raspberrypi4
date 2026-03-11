VEER AI – Common Errors and Troubleshooting Guide



This section lists the most common problems that may occur while setting up the VEER Offline Hindi Voice Assistant and the solutions that successfully resolved them during development.



1\. Microphone Not Detected



Problem



When running the assistant you may see errors like:



Mic init failed: No input device matching 'hw:0,0'



or the assistant does not respond to voice commands.



Cause



The microphone device index may change depending on the USB audio device or Raspberry Pi configuration.



Solution



Check available microphone devices using:



arecord -l



or



python -c "import sounddevice as sd; print(sd.query\_devices())"



Modify the code so that the program automatically detects the microphone instead of using a fixed device index.



Example logic used in the project:



Select the first device that has input channels greater than zero.



2\. Robotic or Fast Voice Output



Problem



The assistant’s voice sounds robotic, distorted, or too fast to understand.



Cause



Audio sample rate mismatch between Piper TTS output and ALSA playback.



Piper generates audio at 22050 Hz.



Solution



Force the correct sample rate when playing audio through ALSA.



The correct configuration is:



aplay -D plug:dmix -r 22050 -f S16\_LE -t raw



This ensures the audio output matches Piper’s audio format.



3\. Speaker Works but Songs Do Not Play



Problem



The assistant voice works correctly but music playback commands do not produce sound.



Cause



The audio device may be locked by another process.



Solution



Use the ALSA dmix device, which allows multiple audio streams to share the sound card.



Example command:



aplay -D plug:dmix song.wav



This allows both the assistant voice and music playback to run simultaneously.



4\. “Device or Resource Busy” Audio Error



Problem



Running aplay commands results in the error:



audio open error: Device or resource busy



Cause



Another program is already using the audio device.



Solution



Use the shared audio device plug:dmix instead of directly accessing the hardware device.



Example:



aplay -D plug:dmix song.wav



5\. Service Runs but No Sound After Boot



Problem



The VEER assistant service starts automatically on boot, but no sound is heard.



Cause



The audio system may not be fully initialized when the service starts.



Solution



Modify the service file to start only after the sound system is ready.



Add the following in the service configuration:



After=network.target sound.target



This ensures the assistant starts after the audio system becomes available.



6\. Python Module Not Found



Problem



Running the program produces an error like:



ModuleNotFoundError: No module named 'sounddevice'



Cause



The Python virtual environment is not activated.



Solution



Activate the virtual environment before running the assistant.



source venv/bin/activate



Then run the program:



python main.py



7\. Assistant Responds to Its Own Voice



Problem



The assistant sometimes hears its own voice output and triggers commands again.



Cause



The microphone captures the assistant’s speaker output.



Solution



Ignore microphone input while the assistant is speaking.



This is done using a flag that prevents command processing during speech output.



8\. Wake Word Not Detected



Problem



The assistant prints:



Wake word missing



even though speech is detected.



Cause



Commands must begin with the wake word.



Solution



Always start commands with the wake word “Veer”.



Examples:



Veer time kya hai

Veer gaana chalao

Veer reminder lagao



9\. Microphone Works but Commands Are Not Recognized



Problem



Audio is captured but speech recognition does not produce text.



Cause



Incorrect sample rate used by the speech recognizer.



Solution



Ensure the VOSK recognizer sample rate matches the microphone stream.



Correct configuration:



44100 Hz



10\. Assistant Does Not Start Automatically



Problem



After rebooting the Raspberry Pi, the assistant does not start automatically.



Cause



The systemd service was not enabled.



Solution



Enable the service using:



sudo systemctl enable veer.service



Start the service using:



sudo systemctl start veer.service



Check service status:



sudo systemctl status veer.service



11\. Songs Folder Not Found



Problem



The assistant says:



“सॉन्ग फोल्डर नहीं मिला”



Cause



The songs directory is missing.



Solution



Create the songs folder inside the project directory.



mkdir songs



Add music files inside this folder.



12\. Checking System Logs



If the assistant fails to start or behaves unexpectedly, system logs can help identify the problem.



Use the following command:



journalctl -u veer.service -n 50



This displays recent logs for the VEER service.



Final Note



VEER AI has been tested on the following configuration:



Raspberry Pi 4

Raspberry Pi OS Lite

USB microphone

USB sound card

External speaker



Following the setup instructions carefully should result in a stable offline voice assistant.


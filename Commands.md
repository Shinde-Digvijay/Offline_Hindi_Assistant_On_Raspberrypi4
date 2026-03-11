2. Time Commands

VEER can tell the current system time.

Examples:

Veer time kya hai
Veer abhi kitne baje hain

Example response:

अभी 12 बजकर 40 मिनट हुए हैं

3. Date Commands

VEER can tell the current date.

Examples:

Veer aaj ki date kya hai
Veer aaj ki taarikh kya hai

Example response:

आज 20 फरवरी 2026 है

4. Day Commands

VEER can tell the current day.

Examples:

Veer aaj ka din kya hai
Veer aaj kaun sa din hai

Example response:

आज गुरुवार है

5. Relative Date Queries

VEER can calculate the date of a specific weekday.

Examples:

Veer agla somvar kab hai
Veer pichla ravivar kab tha
Veer is shukrvar ki date kya hai

Example response:

अगले सोमवार की तारीख 23 फरवरी 2026 है

6. Calculator Commands

VEER supports basic arithmetic calculations.

Examples:

Veer 12 guna 12 kitna hota hai
Veer 20 plus 15 kitna hota hai
Veer 50 minus 12 kitna hota hai
Veer 100 divide 5 kitna hota hai

Example response:

उत्तर एक सौ चवालीस है

7. Multiplication Table Commands

VEER can recite multiplication tables.

Examples:

Veer 5 ka table sunao
Veer 10 ka pahada sunao
Veer 7 ka table batao

Example output:

पाँच गुणा एक बराबर पाँच
पाँच गुणा दो बराबर दस
पाँच गुणा तीन बराबर पंद्रह

8. Timer Commands

VEER can start countdown timers.

Examples:

Veer 5 minute ka timer lagao
Veer 10 minute ka timer lagao

Example response:

5 मिनट का टाइमर शुरू किया

When the timer finishes:

टाइमर पूरा हो गया

9. Reminder Commands

VEER can remind the user after a certain amount of time.

Examples:

Veer 10 minute baad pani pine ka yaad dilana
Veer 15 minute baad study yaad dilana

Example response:

10 मिनट बाद आपको पानी पीने का याद दिलाऊंगा

10. Fixed Time Reminder

VEER can remind the user at a specific time.

Examples:

Veer 6 baje mujhe padhai yaad dilana
Veer 8 bajkar 30 minute par meeting yaad dilana

Example response:

6 बजकर 0 मिनट पर याद दिला दूँगा

11. Alarm Commands

VEER supports alarm functionality.

Examples:

Veer alarm lagao 7 baje
Veer alarm lagao 6 bajkar 30 minute

To stop the alarm:

Veer alarm band karo

12. Music Commands

VEER can play songs stored locally in the songs folder.

Examples:

Veer gaana chalao
Veer ek gaana sunao

Music control commands:

Veer next gaana
Veer pichla gaana
Veer gaana rok do
Veer gaana fir se chalao
Veer gaana band karo

13. Light Control Commands (GPIO)

If an LED or relay is connected to Raspberry Pi GPIO.

Examples:

Veer light chalu karo
Veer light band karo

This demonstrates voice-controlled hardware automation.

14. Information Commands

VEER can answer simple knowledge questions.

Examples:

Veer Bharat ka capital kya hai
Veer Bharat ke pradhan mantri kaun hain

Example response:

भारत की राजधानी नई दिल्ली है

15. Wake Word Requirement

The assistant only responds when the wake word “Veer” is spoken.

Example:

Correct command:

Veer time kya hai

Ignored command:

time kya hai

This prevents accidental triggers.

16. Language Support

The assistant currently supports:

Hindi speech recognition
Hindi voice responses
Hindi mixed with simple English words

Example:

Veer timer lagao 5 minute

Summary

The VEER assistant can perform the following tasks:

Voice interaction
Daily assistant tasks
Music playback
Mathematical calculations
Multiplication tables
Alarm and reminders
GPIO hardware control

All features operate completely offline on Raspberry Pi.
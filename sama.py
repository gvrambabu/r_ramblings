import sys
import sqlite3
import win32com.client

# Database file
DB_FILE = "meeting_templates.db"

# Function to initialize the SQLite database
def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            attendees TEXT,
            duration TEXT,
            timing TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to save meeting details to SQLite
def save_meeting_template(topic, attendees, duration, timing):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO meetings (topic, attendees, duration, timing) VALUES (?, ?, ?, ?)", 
                   (topic, attendees, duration, timing))
    conn.commit()
    conn.close()
    print("Meeting template saved.")

# Function to send email via Outlook
def send_email(topic, attendees, duration, timing):
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0 = MailItem
    mail.To = "admin@example.com"  # Change this to your Admin's email
    mail.Subject = f"Meeting Request: {topic}"
    mail.Body = f"""Hi,  

Could you please set up a meeting with the following details?  

- **Topic:** {topic}  
- **Attendees:** {attendees}  
- **Duration:** {duration}  
- **Preferred Timing:** {timing}  

Let me know if you need any changes.  

Thanks,  
[Your Name]
"""
    mail.Send()
    print("Email sent successfully.")

# Function to fetch and display saved templates
def list_saved_meetings():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, topic, attendees, duration, timing FROM meetings")
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        print("Saved Meeting Templates:")
        for row in rows:
            print(f"ID: {row[0]}, Topic: {row[1]}, Attendees: {row[2]}, Duration: {row[3]}, Timing: {row[4]}")
    else:
        print("No saved meetings found.")

# Function to load a saved template by ID and send an email
def send_saved_meeting(meeting_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT topic, attendees, duration, timing FROM meetings WHERE id=?", (meeting_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        send_email(row[0], row[1], row[2], row[3])
    else:
        print(f"No meeting found with ID {meeting_id}")

# Main function to process command-line arguments
def main():
    initialize_db()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  schedule_meeting.py new '<Topic>' '<Attendees>' '<Duration>' '<Timing>'")
        print("  schedule_meeting.py save '<Topic>' '<Attendees>' '<Duration>' '<Timing>'")
        print("  schedule_meeting.py list")
        print("  schedule_meeting.py send <Meeting_ID>")
        return

    command = sys.argv[1].lower()

    if command == "new" and len(sys.argv) == 6:
        _, _, topic, attendees, duration, timing = sys.argv
        send_email(topic, attendees, duration, timing)
    
    elif command == "save" and len(sys.argv) == 6:
        _, _, topic, attendees, duration, timing = sys.argv
        save_meeting_template(topic, attendees, duration, timing)

    elif command == "list":
        list_saved_meetings()

    elif command == "send" and len(sys.argv) == 3:
        _, _, meeting_id = sys.argv
        send_saved_meeting(meeting_id)

    else:
        print("Invalid command or missing parameters.")

if __name__ == "__main__":
    main()
    
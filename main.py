import pandas as pd
import spacy
from flask import Flask, request, render_template
from dateutil.parser import parse
from datetime import datetime,timedelta

app = Flask(__name__)

# Load the CSV file
appointments_df = pd.read_csv('appointments.csv')

# Load spaCy models
nlp_en = spacy.load('en_core_web_sm')
nlp_de = spacy.load('de_core_news_sm')
nlp_multilingual = spacy.load('xx_ent_wiki_sm')

def detect_language(text):
    """Detect the language of the input text."""
    if any(word in text.lower() for word in ['today', 'tomorrow', 'next week', 'next month']):
        return 'en'
    elif any(word in text.lower() for word in ['heute', 'morgen', 'nächste woche', 'nächsten monat']):
        return 'de'
    elif any(word in text.lower() for word in ['hari ini', 'besok', 'minggu depan', 'bulan depan']):
        return 'id'
    else:
        return 'en'  # Default to English

def get_nlp_model(language):
    """Get the appropriate spaCy model based on the detected language."""
    if language == 'de':
        return nlp_de
    elif language == 'id':
        return nlp_multilingual
    else:
        return nlp_en

def check_availability(date, start_time, end_time):
    """Check if the specified date and time range is available."""
    for index, row in appointments_df.iterrows():
        if row['Date'] == date and not (end_time <= row['Start'] or start_time >= row['End']):
            return False
    return True

def book_appointment(name, date, start_time, end_time):
    """Book an appointment by adding it to the DataFrame and saving to CSV."""
    global appointments_df
    new_appointment = {'Name': name, 'Date': date, 'Start': start_time, 'End': end_time}
    appointments_df = appointments_df._append(new_appointment, ignore_index=True)
    appointments_df.to_csv('appointments.csv', index=False)

def convert_to_24_hour_format(time_str):
    """Convert 12-hour format time string to 24-hour format."""
    try:
        dt = datetime.strptime(time_str, '%I %p')
        return dt.strftime('%H:%M')
    except ValueError:
        return None

def extract_name_date_time(user_input):
    """Extract name, date, and time from user input using spaCy and dateutil."""
    language = detect_language(user_input)
    nlp = get_nlp_model(language)
    doc = nlp(user_input)
    name = None
    date = None
    times = []

    # Extract entities from the user input
    for ent in doc.ents:
        if (ent.label_ == "PERSON" or ent.label_ == "GPE") and not name:
            name = ent.text
        elif ent.label_ in ["DATE", "TIME"]:
            if language == 'de':
                if ent.label_ == "DATE" and not date:
                    date = ent.text
                elif ent.label_ == "TIME":
                    if 'bis' in ent.text:
                        times.extend(ent.text.split(' bis '))
                    else:
                        times.append(ent.text)
            elif language == 'id':
                if ent.label_ == "DATE" and not date:
                    date = ent.text
                elif ent.label_ == "TIME":
                    if 'sampai' in ent.text:
                        times.extend(ent.text.split(' sampai '))
                    else:
                        times.append(ent.text)
            else:
                if ent.label_ == "DATE" and not date:
                    date = ent.text
                elif ent.label_ == "TIME":
                    if 'to' in ent.text:
                        times.extend(ent.text.split(' to '))
                    else:
                        times.append(ent.text)

    today = datetime.today().date()
    if date:
        try:
            parsed_date = parse(date, fuzzy=True)
            date = parsed_date.date().isoformat()
            print(date)
        except ValueError:
            date = None

        # get language
        if language == 'de':
            if 'heute' in date.lower():
                date = today.isoformat()
            elif 'morgen' in date.lower():
                date = (today + timedelta(days=1)).isoformat()
            elif 'nächste woche' in date.lower():
                date = (today + timedelta(days=7)).isoformat()
            elif 'nächsten monat' in date.lower():
                next_month = today.replace(day=28) + timedelta(days=4)  # this will never fail
                date = next_month.replace(day=1).isoformat()
        elif language == 'id':
            if 'hari ini' in date.lower():
                date = today.isoformat()
            elif 'besok' in date.lower():
                date = (today + timedelta(days=1)).isoformat()
            elif 'minggu depan' in date.lower():
                date = (today + timedelta(days=7)).isoformat()
            elif 'bulan depan' in date.lower():
                next_month = today.replace(day=28) + timedelta(days=4) 
                date = next_month.replace(day=1).isoformat()
        else:
            if 'today' in date.lower():
                date = today.isoformat()
            elif 'tomorrow' in date.lower():
                date = (today + timedelta(days=1)).isoformat()
            elif 'next week' in date.lower():
                date = (today + timedelta(days=7)).isoformat()
            elif 'next month' in date.lower():
                next_month = today.replace(day=28) + timedelta(days=4)  
                date = next_month.replace(day=1).isoformat()


    if times:
        start_time_24 = convert_to_24_hour_format(times[0])
        if not start_time_24:
            try:
                parsed_start_time = parse(times[0], fuzzy=True).time()
                start_time = parsed_start_time.strftime('%H:%M')
            except ValueError:
                start_time = None
        else:
            start_time = start_time_24
        
        if len(times) > 1:
            end_time_24 = convert_to_24_hour_format(times[1])
            if not end_time_24:
                try:
                    parsed_end_time = parse(times[1], fuzzy=True).time()
                    end_time = parsed_end_time.strftime('%H:%M')
                except ValueError:
                    end_time = None
            else:
                end_time = end_time_24
        else:
            end_time = None
    else:
        start_time = end_time = None

    if name and date and start_time and end_time:
        return name, date, start_time, end_time
    else:
        print({'name': name, 'date': date, 'start': start_time, 'end': end_time})
        raise ValueError("Name, date, and/or time not found")


def find_available_slots(message):
    """Find available slots based on the specified message."""
    available_slots = []
    today = datetime.today().date()

    if 'today' in message.lower():
        start_date = end_date = today
    elif 'next week' in message.lower():
        start_date = today + timedelta(days=1)
        end_date = start_date + timedelta(days=6)
    else:
        raise ValueError("Please specify 'today' or 'next week' in your message.")

    current_date = start_date

    while current_date <= end_date:
        for hour in range(9, 17):  #sample office hour
            start_time = f"{hour:02d}:00"
            end_time = f"{hour + 1:02d}:00"
            if check_availability(current_date.isoformat(), start_time, end_time):
                available_slots.append((current_date.isoformat(), start_time, end_time))
        current_date += timedelta(days=1)

    return available_slots


@app.route('/')
def index():
    return render_template('index.html')


def reschedule_appointment(name, old_date, old_start_time, new_date, new_start_time, new_end_time):
    """Reschedule an appointment by updating the DataFrame and saving to CSV."""
    global appointments_df
    today = datetime.today().date()
    old_date_obj = datetime.strptime(old_date, '%Y-%m-%d').date()

    # check if the reschedule is allowed (not D-1)
    if (old_date_obj - today).days < 1:
        raise ValueError("Rescheduling is not allowed for appointments less than a day away.")

    # find the appointment to reschedule
    appointment_index = appointments_df[
        (appointments_df['Name'] == name) &
        (appointments_df['Date'] == old_date) &
        (appointments_df['Start'] == old_start_time)
    ].index

    if not appointment_index.empty:
        # update the appointment details
        appointments_df.at[appointment_index[0], 'Date'] = new_date
        appointments_df.at[appointment_index[0], 'Start'] = new_start_time
        appointments_df.at[appointment_index[0], 'End'] = new_end_time
        appointments_df.to_csv('appointments.csv', index=False)
    else:
        raise ValueError("Appointment not found.")


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['message']
    if 'book' in user_input.lower() or 'buchen' in user_input.lower() or 'pesan' in user_input.lower():
        try:
            name, date_str, start_time_str, end_time_str = extract_name_date_time(user_input)
            if check_availability(date_str, start_time_str, end_time_str):
                book_appointment(name, date_str, start_time_str, end_time_str)
                if detect_language(user_input) == 'de':
                    response = f"Ihr Termin wurde gebucht {name} für {date_str} von {start_time_str} bis {end_time_str}"
                elif detect_language(user_input) == 'id':
                    response = f"Janji Anda telah dipesan {name} untuk {date_str} dari {start_time_str} hingga {end_time_str}"
                else:
                    response = f"Your appointment has been booked {name} for {date_str} from {start_time_str} to {end_time_str}"
            else:
                if detect_language(user_input) == 'de':
                    response = f"Entschuldigung, der Slot am {date_str} von {start_time_str} bis {end_time_str} ist bereits gebucht. Bitte buchen Sie einen anderen Termin."
                elif detect_language(user_input) == 'id':
                    response = f"Maaf, slot pada {date_str} dari {start_time_str} hingga {end_time_str} sudah dipesan. Silakan pesan jadwal lain."
                else:
                    response = f"Sorry, the slot on {date_str} from {start_time_str} to {end_time_str} is already booked. Please book another schedule."
        except ValueError:
            if detect_language(user_input) == 'de':
                response = "Bitte geben Sie den Namen, das Datum und die Uhrzeit in einem erkennbaren Format an."
            elif detect_language(user_input) == 'id':
                response = "Harap berikan nama, tanggal, dan waktu dalam format yang dapat dikenali."
            else:
                response = "Please provide the name, date, and time in a recognizable format."
    elif 'reschedule' in user_input.lower():
        try:
            # extract old and new appointment details from user input
            name, old_date_str, old_start_time_str, _ = extract_name_date_time(user_input)
            _, new_date_str, new_start_time_str, new_end_time_str = extract_name_date_time(user_input)

            if check_availability(new_date_str, new_start_time_str, new_end_time_str):
                reschedule_appointment(name, old_date_str, old_start_time_str, new_date_str, new_start_time_str, new_end_time_str)
                response = f"Your appointment has been rescheduled {name} to {new_date_str} from {new_start_time_str} to {new_end_time_str}"
            else:
                response = f"Sorry, the new slot on {new_date_str} from {new_start_time_str} to {new_end_time_str} is already booked. Please choose another schedule."
        except ValueError as e:
            response = str(e)
    elif any(keyword in user_input.lower() for keyword in ['available', 'have', 'timeslot', 'free']):
        try:
            today = datetime.today().date()
            next_week = today + timedelta(days=7)
            available_slots = find_available_slots(user_input)
            if available_slots:
                response = []
                for date, start, end in available_slots:
                    response.append(f"Available slot: {date} from {start} to {end}")
                response = "\n".join(response)
            else:
                response = "No available slots in the next week."
        except Exception as e:
            response = f"An error occurred: {str(e)}"
    else:
        response = "I'm here to help you book or reschedule appointments. Please provide your name, a date, and a time."
    
    return render_template('index.html', response=response)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

import spacy
from dateutil.parser import parse

from datetime import datetime,timedelta

def convert_to_24_hour_format(time_str):
    """Convert 12-hour format time string to 24-hour format."""
    try:
        dt = datetime.strptime(time_str, '%I %p')
        return dt.strftime('%H:%M')
    except ValueError:
        return None


# nlp = spacy.load('en_core_web_sm')
nlp_en = spacy.load('en_core_web_sm')
# nlp_de = spacy.load('./models/de_lang_model')
# nlp_multilingual = spacy.load('xx_ent_wiki_sm')
# # nlp_custom = spacy.load('./models/custom_lang_model')
# nlp_id = spacy.load('./models/id_lang_model')

user_input_de = "Hallo, das ist Rafi Pratama. Ich möchte einen Termin am 27. Juli von 14:00 bis 15:00 Uhr vereinbaren."
user_input = "Hi, this is Rafi Pratama. I'd like to book an appointment today from 2 PM to 3 PM."

user_input_id = "Halo, ini Rafi Pratama. Saya ingin pesan pada minggu depan dari jam 2 siang sampai jam 3 sore."

doc = nlp_en(user_input)

print(doc)

times = []

for ent in doc.ents:
    print(ent)
    print(ent.label_)
    if ent.label_ == "TIME":
        if 'to' in ent.text:
            times.extend(ent.text.split(' to '))
        else:
            times.append(ent.text)
        

print(len(doc.ents))
print("tes",times)


def extract_name_date_time(user_input):
    """Extract name, date, and time from user input using spaCy and dateutil."""
    doc = nlp_en(user_input)
    name = None
    date = None
    times = []

    # Extract entities from the user input
    for ent in doc.ents:
        if (ent.label_ == "PERSON" or ent.label_ == "GPE") and not name:
            name = ent.text
        elif ent.label_ in ["DATE", "TIME"]:
            if ent.label_ == "DATE" and not date:
                date = ent.text
                print(date)
            elif ent.label_ == "TIME":
                if 'to' in ent.text:
                    times.extend(ent.text.split(' to '))
                else:
                    times.append(ent.text)
    today = datetime.today().date()
    if date.lower() in ['today','tomorrow','next week','next month']:
        pass
    else:
        try:
            parsed_date = parse(date, fuzzy=True)
            date = parsed_date.date().isoformat()
            print(date)
        except ValueError:
            date = None

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


print(extract_name_date_time(user_input))




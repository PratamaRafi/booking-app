# Appointment Booking Agent

Appointment Booking Chat Application:Palm-Code

## Overview
This project implements a simple conversational agent to book appointments.

## Requirements
- Python 3.7+
- Flask
- pandas
- spacy 
- python-dateutil
- boto3 -> optional, if needed use AWS services

## Setup
1. Install the required packages:
    pip install -r requirements.txt



2. Run the Flask server:
    python main.py

## Testing
3. Use a tool like Postman to send POST requests to `http://127.0.0.1:5000/chat`.

## Example
To book an appointment, send a POST request with the following JSON payload:
```json
{
    "message": "Hi, this is Rafi Pratama. I'd like to book an appointment on July 27 from 2 PM to 3 PM."
}
```
4. Visit to `http://127.0.0.1:5000/` and send message to chat UI
### Booking Exact Date
```json
{
    "message": "Hi, this is Rafi Pratama. I'd like to book an appointment on July 27 from 2 PM to 3 PM."
}
```
### Booking Relative date
```json
{
    "message": "Hi, this is Rafi Pratama. I'd like to book an appointment on Today from 2 PM to 3 PM."
}
```
### Check Availablity Schedule
```json
{
    "message": "Do you have some schedule for next week?"
}
```

### Ask for reschedule
```json
{
    "message": "Hi, this is Rafi. I need to reschedule my appointment from 27 July at 2 PM to 3 PM"
}
```

### Decide for reschedule
```json
{
    "message": "The new date and time is August 2nd from 10 AM to 11 AM."
}
```

### Multiple Language -> Future Development
```json
{
    "message": "Halo, ini Rafi Pratama. Saya ingin pesan hari ini dari jam 2 siang sampai jam 3 sore.",
    "message": "Hallo, das ist Rafi Pratama. Ich möchte heute von 14 bis 15 Uhr bestellen."
}
```
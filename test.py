import spacy

nlp = spacy.load('en_core_web_sm')

user_input = "Hi, this is Rafi Pratama. I'd like to book an appointment on July 27 from 2 PM to 3 PM."

doc = nlp(user_input)

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





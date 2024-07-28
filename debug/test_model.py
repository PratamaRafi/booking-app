import spacy
from spacy.training import offsets_to_biluo_tags

# Example text and entities
text =  "Halo, saya Dinda. Saya ingin janji pada tanggal 3 Agustus dari jam 10 pagi sampai jam 11 siang."
entities = {"entities": [[12, 17, "PERSON"], [48, 58, "DATE"], [66, 79, "TIME"]]}


print(text[11:17])
print(len(text))

# Load a spaCy model
nlp = spacy.blank("id")

# Create a Doc object
doc = nlp.make_doc(text)
print(doc)

# Check the alignment
biluo_tags = offsets_to_biluo_tags(doc, entities)
print(biluo_tags)

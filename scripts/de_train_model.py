import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random
import json

# Load training data
with open('./data/de_training_data.json', 'r') as f:
    TRAIN_DATA = json.load(f)

# Load a blank model
nlp = spacy.blank("xx")  # Use a blank multi-language model

# Create the NER component and add it to the pipeline
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner", last=True)
else:
    ner = nlp.get_pipe("ner")

# Add labels to the NER component
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable other pipes during training
other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
with nlp.disable_pipes(*other_pipes):
    optimizer = nlp.begin_training()
    for itn in range(100):  # Number of iterations
        random.shuffle(TRAIN_DATA)
        losses = {}
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        for batch in batches:
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp.update([example], drop=0.5, losses=losses)
        print(f"Losses at iteration {itn}: {losses}")

# Save the model
nlp.to_disk("./models/de_lang_model")
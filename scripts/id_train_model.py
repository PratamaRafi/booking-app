# import spacy
# from spacy.training.example import Example
# from spacy.util import minibatch, compounding
# import random
# import json

# # Load training data
# with open('./data/id_training_data.json', 'r') as f:
#     TRAIN_DATA = json.load(f)

# # # Load a pre-trained multilingual model
# nlp = spacy.load('xx_ent_wiki_sm')  # Use a pre-trained multilingual model

# # Load a blank model
# # nlp = spacy.blank("id")  # Use a blank model for Indonesian

# # Create the NER component and add it to the pipeline
# if "ner" not in nlp.pipe_names:
#     ner = nlp.add_pipe("ner", last=True)
# else:
#     ner = nlp.get_pipe("ner")

# # Add labels to the NER component
# for _, annotations in TRAIN_DATA:
#     for ent in annotations.get("entities"):
#         ner.add_label(ent[2])

# # Disable other pipes during training
# other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
# with nlp.disable_pipes(*other_pipes):
#     optimizer = nlp.begin_training()
#     best_loss = float('inf')  # Initialize best loss
#     patience = 10  # Number of iterations to wait for improvement
#     patience_counter = 0

#     for itn in range(200):  # Number of iterations
#         random.shuffle(TRAIN_DATA)
#         losses = {}
#         batches = minibatch(TRAIN_DATA, size=compounding(4.0, 16.0, 1.001))  # Reduced batch size
#         for batch in batches:
#             for text, annotations in batch:
#                 doc = nlp.make_doc(text)
#                 example = Example.from_dict(doc, annotations)
#                 nlp.update([example], drop=0.6, losses=losses)  # Keep dropout rate

#         # Check for early stopping
#         current_loss = losses.get('ner', float('inf'))
#         if current_loss < best_loss:
#             best_loss = current_loss
#             patience_counter = 0  # Reset counter if loss improves
#         else:
#             patience_counter += 1

#         if patience_counter >= patience:
#             print("Early stopping triggered.")
#             print(patience_counter)
#             break

#         print(f"Losses at iteration {itn}: {losses}")


# # Save the model
# nlp.to_disk("./models/id_lang_model")



import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
import random
import json
import optuna 
import pickle  

# Load training data
with open('./data/id_training_data.pickle', 'rb') as f:  # Change to .pickle and use 'rb' mode
    TRAIN_DATA = pickle.load(f)  # Use pickle to load the data

# Load training data
# with open('./data/id_training_data.json', 'r') as f:
#     TRAIN_DATA = json.load(f)



def train_model(trial):
    # Hyperparameters to tune
    learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-1)
    batch_size = trial.suggest_int('batch_size', 4, 64)
    dropout_rate = trial.suggest_uniform('dropout_rate', 0.1, 0.6)

    # Load a blank model
    nlp = spacy.blank("id")  # Use a blank model for Indonesian

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
        best_loss = float('inf')  # Initialize best loss
        patience = 10  # Number of iterations to wait for improvement
        patience_counter = 0

        for itn in range(200):  # Number of iterations
            random.shuffle(TRAIN_DATA)
            losses = {}
            batches = minibatch(TRAIN_DATA, size=compounding(batch_size, batch_size * 2, 1.001))  # Use tuned batch size
            for batch in batches:
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    nlp.update([example], drop=dropout_rate, losses=losses)  # Use tuned dropout rate

            # Check for early stopping
            current_loss = losses.get('ner', float('inf'))
            if current_loss < best_loss:
                best_loss = current_loss
                patience_counter = 0  # Reset counter if loss improves
            else:
                patience_counter += 1

            if patience_counter >= patience:
                print("Early stopping triggered.")
                break

            print(f"Losses at iteration {itn}: {losses}")

    return best_loss  # Return the best loss for Optuna

# Create a study and optimize the objective function
study = optuna.create_study(direction='minimize')
study.optimize(train_model, n_trials=20)  # Number of trials for hyperparameter tuning

# Save the best hyperparameters
print("Best hyperparameters: ", study.best_params)

# Save the model with the best hyperparameters
# Load the model again with the best hyperparameters for final training
best_params = study.best_params
nlp_final = spacy.blank("id")  # Use a blank model for Indonesian
# Repeat the training process with the best hyperparameters
# (You can copy the training logic here or create a separate function for final training)

# Create the NER component and add it to the pipeline
if "ner" not in nlp_final.pipe_names:
    ner = nlp_final.add_pipe("ner", last=True)
else:
    ner = nlp_final.get_pipe("ner")

# Add labels to the NER component
for _, annotations in TRAIN_DATA:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Disable other pipes during training
other_pipes = [pipe for pipe in nlp_final.pipe_names if pipe != "ner"]
with nlp_final.disable_pipes(*other_pipes):
    optimizer = nlp_final.begin_training()
    for itn in range(200):  # Number of iterations
        random.shuffle(TRAIN_DATA)
        losses = {}
        batches = minibatch(TRAIN_DATA, size=compounding(best_params['batch_size'], best_params['batch_size'] * 2, 1.001))
        for batch in batches:
            for text, annotations in batch:
                doc = nlp_final.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp_final.update([example], drop=best_params['dropout_rate'], losses=losses)

        print(f"Losses at iteration {itn}: {losses}")

# Save the final model
nlp_final.to_disk("./models/id_lang_model")
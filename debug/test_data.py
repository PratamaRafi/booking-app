import json,pickle

# Load training data
with open('./data/id_training_data.pickle', 'rb') as f:  # Change to .pickle and use 'rb' mode
    TRAIN_DATA = pickle.load(f) 

print(len(TRAIN_DATA))
# print((TRAIN_DATA))
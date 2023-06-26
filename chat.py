# imports
import nltk
from nltk.stem.lancaster import LancasterStemmer

nltk.download('punkt')
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
import json
import pickle
import random

b_response = ''

# reads json file
with open("static/intents.json") as file:
    data = json.load(file)

try:
    m
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    # grouping json data
    # words list
    words = []
    # labels list
    labels = []
    # list of all the different "patterns" from data
    docs_x = []
    docs_y = []

    # loops through dictionary
    for intent in data["intents"]:
        # stemming - takes each word and brings it down to its rute word
        # egt. I'm => I
        for pattern in intent["patterns"]:
            # tokenize words inorder to stem them
            wrds = nltk.word_tokenize(pattern)
            # adds tokenized words to word list
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        # adds each "tag" from the json data dictionary to the labels list
        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    # stemming every word in word list
    words = [stemmer.stem(w.lower()) for w in words if w not in "?"]
    # removes any word that has already been seen once
    # removes duplicates
    words = sorted(list(set(words)))

    # removes any labels that has already been seen once
    labels = sorted(labels)

    training = []
    output = []

    # uses one hot encoding to determine what words we have and what words we don't have
    # egt. [0,0,1,0,1,1,0,0,1]
    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        # stems all the patterns in docs_x
        wrds = [stemmer.stem(w) for w in doc]

        # if a word in words list also exist in wrds list then a 1 will be added to the bag list
        for w in words:
            if w in wrds:
                bag.append(1)
            # if not, then a 0 is added to the bag list
            else:
                bag.append(0)

        # adds the empty list of 0 to output_row based off of the labels index
        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        # adds the bag list to the training list
        # egt. training = [[0,0,1,0,1,1,0,0,1]]
        training.append(bag)
        # adds the output_row list to the output list
        # egt. output = [[0,0,0,0,0,0,0,0,0]]
        output.append(output_row)

    # turns the training and output lists into arrays
    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

# - model -

tensorflow.compat.v1.reset_default_graph()

# define input shape that is expected for the model
# input takes in a bag of words
net = tflearn.input_data(shape=[None, len(training[0])])
# adds hidden lair into neural network with 8 nodes
# figures out what word best represents an output
net = tflearn.fully_connected(net, 8)
# adds another hidden lair into neural network with 8 nodes
net = tflearn.fully_connected(net, 8)
# output lair
# predicts which "tag" from the data list would be best to give back to the user
# output gives labels("tag") with responses
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

# train model
model = tflearn.DNN(net)

try:
    model = tflearn.DNN(net)
    model.load("model.tflearn")
except:
    model = tflearn.DNN(net)
    # pass training data into the model
    # show the model the data 1000 times (n_epoch=1000)
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    # saves model
    model.save("model.tflearn")


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)


def chat(u_input):
    print("Start talking with the bot (type quit to stop)!")

    inp = u_input

    results = model.predict([bag_of_words(inp, words)])[0]
    results_index = numpy.argmax(results)
    tag = labels[results_index]

    if results[results_index] > 0.7:
        for tg in data["intents"]:
            if tg['tag'] == tag:
                responses = tg['responses']

        return random.choice(responses)
    else:
        return "I didn't get that, try again. "

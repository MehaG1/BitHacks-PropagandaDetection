# -*- coding: utf-8 -*-
"""Bit.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K7tbCW4C5C_C4fkIiq_jra0HNNAYClEz
"""
import flask
import pickle
import pandas as pd
import math
import numpy as np

# Use pickle to load in the pre-trained model
with open(f'model/tweet_class_model_1.pkl', 'rb') as f:
  model_3 = pickle.load(f)

# Initialise the Flask app
app = flask.Flask(__name__, template_folder='templates')
    
def keyword_featurizer(text):
    features = {}
    
    keywords = ['clinton', 'soros', 'liberal', 'antifa', 'mainstream', 'protesters', 'hillary', 'God', 'wiretap', 'riot', 'obama', 'troll', 'leftist']
    
    for phrase in keywords:
      features[phrase + ' keyword'] = math.log(1 + text.count(phrase.lower()))
    
    return features

from gensim.test.utils import get_tmpfile, common_texts
from gensim.models import Word2Vec
model = Word2Vec(common_texts, size=300, window=5, min_count=1, workers=4)
# Returns word vector for word if it exists, else return None.
def get_word_vector(word):
    try:
      return model[word]
    except KeyError:
      return None

def glove_transform(tweet_content):
    X = np.zeros((len(tweet_content), 300))
    for i, tweet_content in enumerate(tweet_content):
        found_words = 0.0
        tweet_content = tweet_content.strip()
        for word in tweet_content.split(): 
            vec = get_word_vector(word)
            if vec is not None:               
                found_words += 1
                X[i] += vec

        if found_words > 0:
            X[i] /= found_words
            
    return X

def dict_to_features(features_dict):
            X = np.array(list(features_dict.values())).astype('float')
            X = X[np.newaxis, :]
            return X
        
from sklearn.feature_extraction.text import CountVectorizer

def featurize_data(tweet_stuff):
    
    troll_data = pd.read_csv("troll_tweets.csv", encoding='latin-1')
    reg_tweet_data = pd.read_csv("real_tweets.csv")

    # trimming troll_data so we have an equal number of examples for genuine and troll tweets
    troll_data = troll_data.truncate(after=86459)

    # 1 == troll tweet
    troll_data['Type'] = np.ones(86460, dtype = int).tolist()
    # 0 == genuine tweet
    reg_tweet_data['Type'] = np.zeros(86460, dtype = int).tolist()

    troll_data = troll_data.drop(['external_author_id', 'region', 'language', 'publish_date', 'harvested_date', 'following', 'followers', 'updates', 'post_type', 'account_type', 'new_june_2018',  'retweet',  'account_category'], 1)
    reg_tweet_data = reg_tweet_data.drop(['Party'], 1)

    reg_tweet_data.columns = ['author', 'content', 'Type']
    total_data = pd.concat([reg_tweet_data, troll_data])

    from sklearn.model_selection import train_test_split
    X = total_data.drop(['Type'], 1)
    y = total_data['Type']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    vectorizer = CountVectorizer(max_features=2000)
    vectorizer.fit(X_train[['content']].values.ravel())
    
    
    keyword_X = dict_to_features(keyword_featurizer(tweet_stuff))
    bow_X = vectorizer.transform(tweet_stuff).todense()
    glove_X = glove_transform(tweet_stuff)
    X_list = [keyword_X, bow_X, glove_X]
    X = np.concatenate(X_list, axis=1)
    return X

# Set up the main route
@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        # Just render the initial form, to get input
        return(flask.render_template('index.html'))
    
    else:
        # Extract the input
        tweet = flask.request.form.get("propText", False)
        # Make DataFrame for model
        input_variable = tweet

        # THIS IS WHERE THE METHODS WERE

        curr_X = featurize_data([input_variable])
        
        # Get the model's prediction
        prediction = model_3.predict(curr_X)[0]
    
        # Render the form again, but add in the prediction and remind user
        # of the values they input before
        return flask.render_template('index.html',
                                     original_input={'Tweet': tweet},
                                     result=prediction
                                     )

if __name__ == '__main__':
    app.run(debug=True)



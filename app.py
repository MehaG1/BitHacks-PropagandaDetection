# -*- coding: utf-8 -*-
"""Bit.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K7tbCW4C5C_C4fkIiq_jra0HNNAYClEz
"""

import flask
import pickle
import pandas as pd

# Use pickle to load in the pre-trained model
with open(f'model/tweet_class_model.pkl', 'rb') as f:
  model = pickle.load(f)

# Initialise the Flask app
app = flask.Flask(__name__, template_folder='templates')

# Set up the main route
@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        # Just render the initial form, to get input
        return(flask.render_template('index.html'))
    
    elif flask.request.method == 'POST':
        # Extract the input
        tweet = flask.request.form['tweet']
        # Make DataFrame for model
        input_variable = pd.DataFrame([[tweet]],
                                       columns=['tweet'],
                                       dtype=str,
                                       index=['input'])

        # Get the model's prediction
        prediction = model.predict(input_variable)[0]
    
        # Render the form again, but add in the prediction and remind user
        # of the values they input before
        return flask.render_template('index.html',
                                     original_input={'Tweet': tweet},
                                     result=prediction
                                     )

if __name__ == '__main__':
    app.run(debug = True)



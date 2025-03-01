import tensorflow as tf
import numpy as np
import pandas as pd
from typing import overload
#from sklearn.model_selection import train_test_split
import os
import glob
import ast
from g_media_pipe import list_files_in_directory
"""
Backend approach
Train a LSTM model on time-series classification using data from a particular squat to determine whether it is being done right
Labels: 1->Correct,2->Too fast,3->Not low enough
Break the sequence of live stream input from the app into time series samples and predict using the LSTM model 
https://www.kaggle.com/code/szaitseff/classification-of-time-series-with-lstm-rnn
"""

class LSTM_Squat(tf.keras.Model):
    def __init__(self,video_sequence, class_mapping: dict,batch_size:int) -> None:
        """
        video_sequence = ideal number of frames
        Since LSTM models can't predict on a varrying number of frames per video, padding needs to be added
        """
        super().__init__()
        self.num_classes = len(class_mapping)
        self.video_sequence_limit = video_sequence
        # mask_value same as the padding in process data
        self.inputs = tf.keras.Input(
        batch_shape=(batch_size, video_sequence, 33*3), 
        name="input_layer"
        )
        self.masking = tf.keras.layers.Masking(mask_value=-1.0)

        self.lstm1 = tf.keras.layers.LSTM(128, activation='relu', return_sequences=True, stateful=True)
        self.lstm2 = tf.keras.layers.LSTM(256, activation='relu', return_sequences=True, stateful=True)
        self.lstm3 = tf.keras.layers.LSTM(128, activation='relu', stateful=True)
        self.dense1 = tf.keras.layers.Dense(128, activation='relu')
        self.dense2 = tf.keras.layers.Dense(64, activation='relu')
        self.output_layer = tf.keras.layers.Dense(self.num_classes, activation='softmax')

    def call(self, inputs, training=False):
        x = self.masking(inputs)
        x = self.lstm1(x)
        x = self.lstm2(x)
        x = self.lstm3(x)
        x = self.dense1(x)
        x = self.dense2(x)
        return self.output_layer(x)

    def train(self,X,y):
        hot_encoder = tf.keras.utils.to_categorical
        y_one_hot_encoded = hot_encoder(y, num_classes=self.num_classes)
        #pad_sequences = tf.keras.preprocessing.sequence.pad_sequences
        #padded_data = pad_sequences(X, padding='post', dtype='float32',value=-1.0)
        self.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        self.fit(X, y_one_hot_encoded)
        save_directory = os.path.join("models","LSTM_Squats.h5")
        self.save_weights(save_directory)

    def test(self):
        pass

    def predict(self,x_val):
        assert len(x_val.shape) == 3, f"Prediction input for the model {type(self.model)} must be a 3D array "
        self.load_weights(os.path.join("models","LSTM_Squats.h5"))
        return self(x_val)
    
    def set_states(self,states):
        self.lstm1.states = states[0]
        self.lstm2.states = states[1]
        self.lstm3.states = states[2]

    def reset_states(self):
        self.lstm1.reset_states()
        self.lstm2.reset_states()
        self.lstm3.reset_states()
    
    def get_states(self):
        return [self.lstm1.states,self.lstm2.states,self.lstm3.states]

    
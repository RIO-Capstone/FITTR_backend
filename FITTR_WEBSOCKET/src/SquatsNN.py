from FITTR_WEBSOCKET.src.utils import ExerciseSession
from typing import overload
import numpy as np
import pandas as pd
import tensorflow as tf

class SquatNN(ExerciseSession):
    def __init__(self,classes,video_sequence):
        super().__init__()
        self.num_classes = len(classes)

        self.input_shape =  (video_sequence,33*3) # (timestamps, features)
        
        self.model = tf.keras.models.Sequential()


        self.model.add(tf.keras.layers.LSTM(units=128, activation='relu', return_sequences=True, input_shape=self.input_shape))
        self.model.add(tf.keras.layers.LSTM(units=256, activation='relu', return_sequences=True))
        self.model.add(tf.keras.layers.LSTM(units=128, activation='relu', return_sequences=False))
        #self.model.add(tf.keras.layers.BatchNormalization())
        self.model.add(tf.keras.layers.Dense(units=128, activation='relu'))
        self.model.add(tf.keras.layers.Dense(units=64, activation='relu'))
        self.model.add(tf.keras.layers.Dense(units=self.num_classes, activation='softmax'))
        # Compile the model
        self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    @overload
    def process_data(self,video_file:str):
        # TODO: Normalizations and feature engineering can be done here
        video_data = pd.read_csv(video_file)
        rows,cols = video_data.shape
        assert cols == 33, "Incorrect number of body landmarks, supposed to be 33 but are actually ${cols} "
        computed_flatten_data = video_data.apply(lambda frame: computed_flatten_data(frame,cols),axis=1)
        return computed_flatten_data
    
    def euclidean(self,joint1,joint2):
        xi,yi,zi = joint1
        xj,yj,zj = joint2
        return (np.square(xi-xj)+np.square(yi-yj)+np.square(zi-zj))**0.5
    
    def compute_frame(self,row:pd.Series,features:int):
        n = len(row)
        output = np.zeros((features,features))
        for i in range(n):
            for j in range(n):
                output[i][j] = self.euclidean(row.iloc[i],row.iloc[j])
        return output[np.triu_indices(33,k=1)]

    @overload
    def train(self):
        X,y = super().read_data()
        

    
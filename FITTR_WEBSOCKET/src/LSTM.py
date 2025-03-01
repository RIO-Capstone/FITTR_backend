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

class LSTM:
    def __init__(self,name:str, video_sequence, class_mapping: dict,data_path:str,batch_size:int) -> None:
        """
        video_sequence = ideal number of frames
        Since LSTM models can't predict on a varrying number of frames per video, padding needs to be added
        """
        self.num_classes = len(class_mapping)
        self.name = name
        self.data_path = data_path
        self.video_sequence_limit = video_sequence
        self.input_shape =  (video_sequence,33*3) # (timestamps, features)
        self.save_path = os.path.join("FITTR_WEBSOCKET","models", f"{self.name}.h5")
        self.model = tf.keras.models.Sequential()
        # mask_value same as the padding in process data
        self.model.add(tf.keras.layers.Masking(mask_value=-1.0, batch_input_shape=(batch_size,self.video_sequence_limit,33*3)))

        self.model.add(tf.keras.layers.LSTM(units=128, activation='relu', return_sequences=True, input_shape=self.input_shape,stateful=True, batch_input_shape=(batch_size,self.video_sequence_limit,33*3)))
        self.model.add(tf.keras.layers.LSTM(units=256, activation='relu', return_sequences=True,stateful=True))
        self.model.add(tf.keras.layers.LSTM(units=128, activation='relu', return_sequences=False,stateful=True))
        self.model.add(tf.keras.layers.BatchNormalization())
        self.model.add(tf.keras.layers.Dense(units=128, activation='relu'))
        self.model.add(tf.keras.layers.Dense(units=64, activation='relu'))
        self.model.add(tf.keras.layers.Dense(units=self.num_classes, activation='softmax')) # output a probability vector of length num_classes
        # Compile the model, Adam clipnorm helps with gradient exploding
        self.model.compile(optimizer=tf.keras.optimizers.Adam(clipnorm=1.0), loss='categorical_crossentropy', metrics=['accuracy'])


    def train(self,epochs=10):
        X,y = self.read_data()
        assert not np.isnan(X).any(), "Input data X contains NaN values!"
        assert not np.isinf(X).any(), "Input data X contains infinite values!"
        assert not np.isnan(y).any(), "Labels y contain NaN values!"
        assert not np.isinf(y).any(), "Labels y contain infinite values!"

        assert len(X.shape) == 3, "X must have a 3D shape of (batch_size,video_sequence_limit,features)"
        hot_encoder = tf.keras.utils.to_categorical
        y_one_hot_encoded = hot_encoder(y, num_classes=self.num_classes)
        dataset = tf.data.Dataset.from_tensor_slices((X, y_one_hot_encoded))
        dataset = dataset.batch(1, drop_remainder=True)
        for epoch in range(epochs):
            print(f"Epoch {epoch + 1}/{epochs}")
            # Train for one epoch, ensuring batch_size = 1 and shuffle = False
            # this ensures that predictions are done with one batch_size and data is processed sequentially
            self.model.fit(dataset, epochs=1, verbose=1,batch_size=1,shuffle=False,steps_per_epoch=X.shape[0])
            # Reset states at the end of each epoch
            self.model.reset_states()

        self.model.save(self.save_path)

    def test(self):
        pass

    def predict(self,x_val):
        assert len(x_val.shape) == 3, f"Prediction input for the model {type(self.model)} must be a 3D array "
        assert x_val.shape[2] == 33*3, f"Input data must have 99 features but has {x_val.shape[2]} features"
        if not os.path.exists(self.save_path):
            print(f"Model not found at {self.save_path}")
            return
        self.model.load_weights(filepath=self.save_path)
        return self.model.predict(x_val)

    def read_data(self)->tuple:
        # read then label
        proper_data = self.directory_to_numpy(os.path.join(self.data_path, "Proper"))
        improper_data = self.directory_to_numpy(os.path.join(self.data_path, "Improper"))
        # TODO: Labelling needs to be changed based on the type of exercise
        proper_labels = np.ones((len(proper_data),))
        improper_labels = np.zeros((len(improper_data),))

        combined_data = np.concatenate((proper_data, improper_data), axis=0)
        combined_labels = np.concatenate((proper_labels, improper_labels), axis=0)
        assert combined_data.shape[0] == combined_labels.shape[0], f"Number of samples and labels does not match. Samples: {combined_data.shape[0]} , Labels: {combined_labels.shape[0]}"
        assert combined_data.shape[2] == 33*3, f"Number of features is not 99 but is instead {combined_data.shape[1]}"
        return combined_data, combined_labels

    def directory_to_numpy(self,directory:str)->np.array:
        # Find all .csv files in the directory
        csv_files = list_files_in_directory(directory_path=directory)
        if len(csv_files) == 0: return np.empty((0, 0, 0))
        data = []
        # Process each .csv file
        for file in csv_files:
            processsed_video_data:pd.DataFrame = self.process_data(file)
            if processsed_video_data.empty:
                print(f"No valid data in CSV file: {file}")
                continue
            assert len(processsed_video_data.shape) == 2, f"Incorrect processed data shape for file: ${os.path.basename(file)}: Data needs to be 2D but is instead ${processsed_video_data.shape}"
            data.append(processsed_video_data.to_numpy())

        data = np.array(data)
        assert len(data.shape) == 3, f"Incorrect data shape when reading from directory: ${directory}. Data needs to be 3D but is currently of shape: ${data.shape}"
        return data
    
    def process_data(self,video_file:str)->pd.DataFrame:
        # video_file is a path to a csv file
        video_data = pd.read_csv(video_file)
        if video_data is None: 
            print("No data found for csv file: {}".format(video_file))
            return []
        video_data = video_data.map(ast.literal_eval) # converting all the strings to list[float]
        x_coors = video_data.map(lambda coords: coords[0])  # Get the X coordinates
        y_coors = video_data.map(lambda coords: coords[1])  # Get the Y coordinates
        z_coors = video_data.map(lambda coords: coords[2])  # Get the Z coordinates

        # Combine these into a single DataFrame with columns like NOSE_x, NOSE_y, NOSE_z, etc.
        x_coors.columns = [f'{col}_x' for col in x_coors.columns]
        y_coors.columns = [f'{col}_y' for col in y_coors.columns]
        z_coors.columns = [f'{col}_z' for col in z_coors.columns]

        # Combine the x, y, z data into a single DataFrame
        coordinates_df = pd.concat([x_coors, y_coors, z_coors], axis=1)
        current_length = len(coordinates_df)
        if current_length < self.video_sequence_limit:
            # Pad with -1.0 as there will be no euclian distance < 0
            padding = np.full((self.video_sequence_limit - current_length, coordinates_df.shape[1]), -1.0)
            coordinates_df = pd.DataFrame(np.vstack([coordinates_df.values, padding]), columns=coordinates_df.columns)
        # cap the amount of video being used by the video_sequence_limit
        assert coordinates_df.shape[0] >= self.video_sequence_limit, f"Batch shape compromised expected: {self.video_sequence_limit}, received {coordinates_df.shape[0]}"
        assert coordinates_df.shape[1] == 33*3, f"Incorrect number of features expected: {33*3}, received: {coordinates_df.shape[1]}"
        return coordinates_df.iloc[:self.video_sequence_limit]
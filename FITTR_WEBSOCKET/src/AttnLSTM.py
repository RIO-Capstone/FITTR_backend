import os
import time
import numpy as np
import pandas as pd
import tensorflow as tf
from g_media_pipe import list_files_in_directory
import ast

class AttentionLSTM:
    def __init__(self, name, classes, video_sequence, data_path):
        super().__init__()
        self.name = name
        self.num_classes = len(classes)
        self.input_shape = (video_sequence, 33 * 3)
        self.data_path = data_path
        self.video_sequence_limit = video_sequence
        self.padding_value = -1.0
        self.hidden_units = 128
        self.save_path = os.path.join("FITTR_WEBSOCKET","models", f"{self.name}.h5")
        # Define the Attention LSTM model using the functional API
        self._build_model()
        
        # Optimizer with reduced learning rate and gradient clipping
        opt = tf.keras.optimizers.Adam(learning_rate=0.001, clipnorm=1.0)
        
        # Compile model
        self.model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    
    def _build_model(self):
        # Input layer
        inputs = tf.keras.layers.Input(shape=self.input_shape)
        
        # Masking layer to handle padding
        masked_inputs = tf.keras.layers.Masking(mask_value=self.padding_value)(inputs)
        
        # Normalization layer
        normalized = tf.keras.layers.Normalization(axis=-1)(masked_inputs)
        
        # First Bidirectional LSTM layer
        lstm_out1 = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(self.hidden_units, 
                                     return_sequences=True,
                                     activation='tanh',
                                     recurrent_activation='sigmoid',
                                     kernel_initializer='glorot_uniform',
                                     recurrent_regularizer=tf.keras.regularizers.l2(1e-5),
                                     kernel_constraint=tf.keras.constraints.MaxNorm(3)))(normalized)
        bn1 = tf.keras.layers.BatchNormalization()(lstm_out1)
        drop1 = tf.keras.layers.Dropout(0.3)(bn1)
        
        # Second Bidirectional LSTM layer
        lstm_out2 = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(self.hidden_units, 
                                     return_sequences=True,
                                     activation='tanh',
                                     recurrent_activation='sigmoid',
                                     kernel_initializer='glorot_uniform',
                                     recurrent_regularizer=tf.keras.regularizers.l2(1e-5),
                                     kernel_constraint=tf.keras.constraints.MaxNorm(3)))(drop1)
        bn2 = tf.keras.layers.BatchNormalization()(lstm_out2)
        drop2 = tf.keras.layers.Dropout(0.3)(bn2)
        
        # Apply attention mechanism
        attention_mul = self.attention_block(drop2, self.video_sequence_limit)
        
        # Flatten the output
        flattened = tf.keras.layers.Flatten()(attention_mul)
        
        # Dense layers
        dense1 = tf.keras.layers.Dense(2 * self.hidden_units, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(1e-5))(flattened)
        drop3 = tf.keras.layers.Dropout(0.5)(dense1)
        dense2 = tf.keras.layers.Dense(self.hidden_units, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(1e-5))(drop3)
        
        # Output layer
        outputs = tf.keras.layers.Dense(self.num_classes, activation='softmax')(dense2)
        
        # Create model
        self.model = tf.keras.models.Model(inputs=inputs, outputs=outputs)
    
    
    def train(self, batch_size=1, max_epochs=10):
        X, y = self.read_data()
        print(X.shape)
        print(y.shape)
        
        hot_encoder = tf.keras.utils.to_categorical
        y_one_hot_encoded = hot_encoder(y, num_classes=self.num_classes)
        
        # Define callbacks with modified parameters
        es_callback = tf.keras.callbacks.EarlyStopping(
            monitor='loss', 
            min_delta=1e-4, 
            patience=15,
            mode='min',
            restore_best_weights=True
        )
        
        lr_callback = tf.keras.callbacks.ReduceLROnPlateau(
            monitor='loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            mode='min',
            verbose=1
        )
        
        # Add a callback to terminate training if NaN loss is encountered
        nan_callback = tf.keras.callbacks.TerminateOnNaN()
        
        log_dir = os.path.join(os.getcwd(), 'logs', f"ExerciseRecognition-LSTM-{int(time.time())}")
        callbacks = [es_callback, lr_callback, nan_callback]
        
        # Train the model
        self.model.fit(
            X, 
            y_one_hot_encoded, 
            epochs=max_epochs, 
            batch_size=batch_size,
            callbacks=callbacks,
            shuffle=True,
            validation_split=0.2
        )
        
        self.model.save(self.save_path)
    
    def predict(self, x_val):
        assert len(x_val.shape) == 3, "Prediction input must be a 3D array but is instead {}".format(x_val.shape)
        assert x_val.shape[2] == 99, f"Input data must have 99 features, but has {x_val.shape[2]}"
        if os.path.exists(self.save_path) == False:
            print(f"Warning: Model weights not found at {self.save_path}")
            return
        # Load the model if needed
        try:
            self.model.load_weights(filepath=self.save_path)
        except:
            print(f"Warning: Couldn't load weights from {self.save_path}")
        
        return self.model.predict(x_val)
    
    def attention_block(inputs, time_steps):
        """
        Attention layer for deep neural network
        """
        # Attention weights
        a = tf.keras.layers.Permute((2, 1))(inputs)
        a = tf.keras.layers.Dense(time_steps, activation='softmax')(a)
        
        # Attention vector
        a_probs = tf.keras.layers.Permute((2, 1), name='attention_vec')(a)
        
        # Luong's multiplicative score
        output_attention_mul = tf.keras.layers.multiply([inputs, a_probs], name='attention_mul') 
        
        return output_attention_mul
    
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
        assert combined_data.shape[2] == 33*3, f"Number of features is not 99 but is instead {combined_data.shape[2]}"
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
            # Pad with self.padding_value
            padding = np.full((self.video_sequence_limit - current_length, coordinates_df.shape[1]), self.padding_value)
            coordinates_df = pd.DataFrame(np.vstack([coordinates_df.values, padding]), columns=coordinates_df.columns)
        # cap the amount of video being used by the video_sequence_limit
        assert coordinates_df.shape[0] >= self.video_sequence_limit, f"Batch shape compromised expected: {self.video_sequence_limit}, received {coordinates_df.shape[0]}"
        assert coordinates_df.shape[1] == 33*3, f"Incorrect number of features expected: {33*3}, received: {coordinates_df.shape[1]}"
        return coordinates_df.iloc[:self.video_sequence_limit]

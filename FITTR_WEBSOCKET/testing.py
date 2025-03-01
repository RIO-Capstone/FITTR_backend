import tensorflow as tf
from g_media_pipe import extract_data_from_video, save_data, process_and_save_mp4_to_csv, list_files_in_directory
import pandas as pd
import numpy as np
import os
import ast
from typing import List
from src.LSTM import LSTM
from src.SquatsNN import SquatNN
from FITTR_WEBSOCKET.src.AttnLSTM import AttentionLSTM

curdir = os.path.dirname(__file__)
# Directories
MP4_DATASETS = os.path.join(curdir,"datasets")
SQUATS_MP4 = os.path.join(MP4_DATASETS,"Squats")
PROPER_SQUATS_MP4 = os.path.join(SQUATS_MP4,"Proper")
IMPROPER_SQUATS_MP4 = os.path.join(SQUATS_MP4,"Improper")
CSV_SAVE_LOCATION = os.path.join(curdir,"model_data")
SQUATS_CSV = os.path.join(CSV_SAVE_LOCATION,"Squats")
PROPER_SQUATS_CSV = os.path.join(SQUATS_CSV,"Proper")
IMPROPER_SQUATS_CSV = os.path.join(SQUATS_CSV,"Improper")
IDEAL_FRAME_LENGTH = 60

def read_data()->tuple:
        # read then label
        proper_data = directory_to_numpy(os.path.join(SQUATS_CSV, "Proper"))
        improper_data = directory_to_numpy(os.path.join(SQUATS_CSV, "Improper"))
        # TODO: Labelling needs to be changed based on the type of exercise
        proper_labels = np.ones((len(proper_data),))
        improper_labels = np.zeros((len(improper_data),))
        combined_data = np.concatenate((proper_data, improper_data), axis=0)
        combined_labels = np.concatenate((proper_labels, improper_labels), axis=0)
        assert combined_data.shape[0] == combined_labels.shape[0], f"Number of samples and labels does not match. Samples: {combined_data.shape[0]} , Labels: {combined_labels.shape[0]}"
        assert len(combined_data.shape) == 3, f"Data shape is not 3D but is instead {combined_data.shape}"
        assert combined_data.shape[2] == 33*3, f"Number of features is not {33*3} but is instead {combined_data.shape[2]}"
        return combined_data, combined_labels

def directory_to_numpy(directory:str)->np.array:
    # Find all .csv files in the directory
    csv_files = list_files_in_directory(directory_path=directory)
    if len(csv_files) == 0: 
        return np.empty((0, 0, 0))
    data = []
    # Process each .csv file
    for file in csv_files:
        processsed_video_data:pd.DataFrame = process_data(file)
        if processsed_video_data.empty:
            print(f"No valid data in CSV file: {file}")
            continue
        assert len(processsed_video_data.shape) == 2, f"Incorrect processed data shape for file: ${os.path.basename(file)}: Data needs to be 2D but is instead ${processsed_video_data.shape}"
        data.append(processsed_video_data.to_numpy())
    data = np.array(data)
    assert len(data.shape) == 3, f"Incorrect data shape when reading from directory: ${directory}. Data needs to be 3D but is currently of shape: ${data.shape}"
    return data
    
def process_data(csv_file:str)->pd.DataFrame:
    video_data = pd.read_csv(csv_file)
    if video_data is None: 
        print("No data found for csv file: {}".format(csv_file))
        return pd.DataFrame()
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
    if current_length < IDEAL_FRAME_LENGTH:
        # Pad with -1.0 as there will be no euclian distance < 0, this padding is used by the masking layer
        padding = np.full((IDEAL_FRAME_LENGTH - current_length, coordinates_df.shape[1]), -1.0)
        coordinates_df = pd.DataFrame(np.vstack([coordinates_df.values, padding]), columns=coordinates_df.columns)
    # cap the amount of video being used by the video_sequence_limit
    return coordinates_df.iloc[:IDEAL_FRAME_LENGTH]

# improper_squat_files = list_files_in_directory(os.path.join(IMPROPER_SQUATS_MP4))
# for file in improper_squat_files:
#     print(f"Processing {file}")
#     video_data = extract_data_from_video(file)
#     file_name = os.path.basename(file)
#     output_file_name = os.path.join(IMPROPER_SQUATS_CSV,os.path.splitext(file_name)[0] + ".csv")
#     if video_data is not None:
#         save_data(video_data,output_path=output_file_name)
#     print(f"Finished processing {file_name} --> {output_file_name}")

#df = pd.read_csv(r"D:\NirwanaWarehouse\uniWork\Term 7\Capstone\backend\model_data\Squats\Proper\properSquat1.csv")
def spread_data(csv_file:str)->pd.DataFrame:
    video_data = pd.read_csv(csv_file)
    if video_data is None: 
        print("No data found for csv file: {}".format(csv_file))
        return pd.DataFrame()
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
    return coordinates_df
# print(IDEAL_FRAME_LENGTH)
TRAINING = False
prediction_classes = [1,0]
y = 1
model = SquatNN("SquatsNN",prediction_classes,IDEAL_FRAME_LENGTH,SQUATS_CSV)
attnModel = AttentionLSTM("SquatsAttnNN",prediction_classes,IDEAL_FRAME_LENGTH,SQUATS_CSV)
if TRAINING:
    attnModel.train(batch_size=4)
else:
    first = spread_data(r"D:\NirwanaWarehouse\uniWork\Term 7\Capstone\backend\FITTR_WEBSOCKET\datasets\Test\Squats_8_reps.csv")
    data = first.to_numpy() #converting to numpy array.
    chunks = []
    num_chunks = (len(data) + IDEAL_FRAME_LENGTH - 1) // IDEAL_FRAME_LENGTH #calculates the number of chunks.

    for i in range(num_chunks):
        start = i * IDEAL_FRAME_LENGTH
        end = min((i + 1) * IDEAL_FRAME_LENGTH, len(data))
        chunk = data[start:end]

        if len(chunk) < IDEAL_FRAME_LENGTH:
            chunk = tf.keras.preprocessing.sequence.pad_sequences([chunk], maxlen=IDEAL_FRAME_LENGTH, padding='post', dtype='float32')[0] #pad the last chunk.

        chunks.append(chunk)

    print(f"Number of chunks: {len(chunks)}")

    for chunk in chunks:
        print(f"Chunk shape: {chunk.shape}")

        if chunk.shape == (IDEAL_FRAME_LENGTH, 99): #added check for correct shape.
            chunk = chunk.reshape(1, IDEAL_FRAME_LENGTH, 99)
            res = attnModel.predict(chunk)
            print(f"Prediction: {res}")
            print(f"Prediction class: {np.argmax(res)}")
        else:
            print("Error: Chunk shape is incorrect")
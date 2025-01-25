import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2 as cv
import numpy as np
import pandas as pd
import csv
from typing import List
import os

MODEL_PATH = r'D:\NirwanaWarehouse\uniWork\Term 7\Capstone\backend\models\pose_landmarker_full.task'
VIDEO_PATH = r"D:\NirwanaWarehouse\uniWork\Term 7\Capstone\backend\datasets\Squats\Proper\video6109184528624915062.mp4"
OUTPUT_PATH = "./model_data/properSquat1.csv"

# for file in dir(OUTPUT_DIRECTORY):
#     # use each file to store the landmark locations for respective exercises
#     # label the exercises: 0 --> Improper, 1 --> Proper
#     # train a multi-classification model to work on out of sample data
#     pass
mp_pose = mp.solutions.pose


def list_files_in_directory(directory_path: str) -> List[str]:
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")
        return []

    if not os.path.isdir(directory_path):
        print(f"Path {directory_path} is not a directory.")
        return []

    # List all files in the directory
    files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    return files


def populate_csv(data,output_path):
    with open(output_path, mode='w', newline='') as file:
        writer = csv.writer(file)

        header = data.keys()
        writer.writerow(header)
        
        # Determine the number of frames by checking the length of values for the first key
        num_frames = len(next(iter(data.values())))
        
        for i in range(num_frames):
            row = []
            for key in data:
                row.append(str(data[key][i]))
            writer.writerow(row)
    
def write_landmarks_to_csv(landmarks,data,verbose):
    for idx, landmark in enumerate(landmarks):
        current_coordinates = [landmark.x, landmark.y, landmark.z]
        body_part = mp_pose.PoseLandmark(idx).name
        if verbose:
            print(f"{body_part}: (x: {landmark.x}, y: {landmark.y}, z: {landmark.z})")
        if body_part not in data:
            data[body_part] = []
        data[body_part].append(current_coordinates)

def extract_data_from_video(video_path:str,verbose=False):
    PostEstimator = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.6, min_tracking_confidence=0.6)
    if not os.path.exists(video_path):
        print("The video path given does not exist!")
        return
    print(f"Extracting data from video file: {video_path}")
    video = cv.VideoCapture(video_path)
    if not video.isOpened():
        print("Error: Could not open the video file.")
        exit()
    frameCounter = 0
    videoData = {}
    while video.isOpened():
        success, frame = video.read()
        if not success: break
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        # Convert the RGB frame to a MediaPipe Image object.
        #mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        # Process the MediaPipe Image object using PoseLandmarker.
        landmarks = PostEstimator.process(rgb_frame)
        if landmarks.pose_landmarks:
            # Draw landmarks or handle results here.
            write_landmarks_to_csv(landmarks.pose_landmarks.landmark,videoData,verbose)
        else:
            print("No frames detected for file {}".format(video_path))
            return 
        frameCounter += 1
    video.release()
    return videoData
    
def save_data(videoData,output_path:str):
    populate_csv(videoData,output_path)

def process_and_save_mp4_to_csv(files:List[str],output_directory:str):
    total_files = len(files)
    print("Starting processing of {} .mp4 files".format(total_files))
    for idx,file in enumerate(files):
        assert file.endswith('.mp4'), f"File {file} is not an .mp4 file."
        video_data =  extract_data_from_video(file)
        file_name = os.path.splitext(os.path.basename(file))[0]
        output_path = os.path.join(output_directory, f"{file_name}.csv")
        save_data(video_data,output_path)
        print(f"Saved csv file: {idx+1}/{total_files} to {output_directory}")
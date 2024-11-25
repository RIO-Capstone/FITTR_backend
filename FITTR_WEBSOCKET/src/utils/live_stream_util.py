import pandas as pd
import numpy as np
from ..utils.ExerciseType import ExerciseType
import ast
from typing import Callable

# list copied from https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker
pose_labels = [
    "nose",
    "left eye (inner)",
    "left eye",
    "left eye (outer)",
    "right eye (inner)",
    "right eye",
    "right eye (outer)",
    "left ear",
    "right ear",
    "mouth (left)",
    "mouth (right)",
    "left shoulder",
    "right shoulder",
    "left elbow",
    "right elbow",
    "left wrist",
    "right wrist",
    "left pinky",
    "right pinky",
    "left index",
    "right index",
    "left thumb",
    "right thumb",
    "left hip",
    "right hip",
    "left knee",
    "right knee",
    "left ankle",
    "right ankle",
    "left heel",
    "right heel",
    "left foot index",
    "right foot index",
]

landmark_labels = list(map(lambda x: "_".join(x.split(" ")).upper(),pose_labels))

def process_raw_record(landmarks:pd.Series)->pd.Series:

    #landmarks = raw_result["results"][0]["landmarks"][0]
    landmark_arrays = [{"x": point["x"], "y": point["y"], "z": point["z"]} for point in landmarks]

    # Create a dictionary where each label is a column, and its value is the [x, y, z] array
    landmark_dict = {
        label: list(landmark_arrays[i].values())  # Flatten the dictionary values into a 1D array
        for i, label in enumerate(landmark_labels[:len(landmarks)])
    }
    raw_record = pd.Series(landmark_dict)
    s_record = spread_record(raw_record)
    return s_record
    

def spread_record(record:pd.Series) -> pd.Series:
        if isinstance(record.iloc[0],str):
            record = record.map(ast.literal_eval)

        x_coors = record.map(lambda coords: coords[0])  # Get the X coordinates
        y_coors = record.map(lambda coords: coords[1])  # Get the Y coordinates
        z_coors = record.map(lambda coords: coords[2])  # Get the Z coordinates

        # Combine the x, y, z data into a single record
        new_series = pd.concat([pd.Series({
            f'{index}_x': x for index, x in zip(record.index, x_coors)
        }),pd.Series({
            f'{index}_y': y for index, y in zip(record.index, y_coors)
        }),pd.Series({
            f'{index}_z': z for index, z in zip(record.index, z_coors)
        })])

        return new_series

def min_max_scaler(col:pd.Series,min_value,max_value)->pd.Series:
        return col.map(lambda x: (x-min_value)/(max_value-min_value))
    
def smooth_gaussian(data:pd.Series, sigma=2)->pd.Series:
    """
    Smoothen the curves using a Gaussian filter.
    Parameters:
    - data: NumPy array, the input signal to smooth.
    - sigma: Standard deviation of the Gaussian kernel.
    Returns:
    - smoothed_data: NumPy array of the smoothed data.
    """
    kernel_radius = int(3 * sigma)  # 3 standard deviations cover ~99% of data
    x = np.arange(-kernel_radius, kernel_radius + 1)
    gaussian_kernel = np.exp(-x**2 / (2 * sigma**2))
    gaussian_kernel /= gaussian_kernel.sum()  # Normalize the kernel
    
    # Padding to avoid edge effects
    padded_data = np.pad(data, pad_width=kernel_radius, mode='edge')
    
    # Convolution with Gaussian kernel
    smoothed_data = np.convolve(padded_data, gaussian_kernel, mode='valid')
    
    return pd.Series(smoothed_data,index=data.index)

def exercise_to_algo_map(exercise_type:str)->Callable:
    if exercise_type == ExerciseType.SQUATS:
        return squat_reps
    else:
        pass

def squat_reps(current_record:pd.Series,past_record:pd.Series | None)->int:
    if past_record is None or past_record.empty: return 0
    thr = ExerciseType.SQUATS_THRESHOLD
    if "RIGHT_KNEE_z" not in current_record.index:
         return 0
    if current_record["RIGHT_KNEE_z"] <= thr and past_record["RIGHT_KNEE_z"] > thr:
        return 1
    else:
        return 0
    
def exercise_to_filter_map(exercise_type:str)->Callable:
    if exercise_type == ExerciseType.SQUATS:
          return get_relevant_squat_joints
    else:
        pass
    
def get_relevant_squat_joints(record: pd.Series) -> pd.Series:
    """
    Drops data that isn't relevent for Squats.
    """
    prefixes_to_drop = [
        'NOSE', 'LEFT_EYE', 'RIGHT_EYE', 'LEFT_EAR', 'RIGHT_EAR',
        'MOUTH', 'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 'RIGHT_ELBOW',
        'LEFT_WRIST', 'RIGHT_WRIST', 'LEFT_PINKY', 'RIGHT_PINKY', 'LEFT_INDEX',
        'RIGHT_INDEX', 'LEFT_THUMB', 'RIGHT_THUMB', 'LEFT_ANKLE', 'RIGHT_ANKLE',
        'LEFT_HEEL', 'RIGHT_HEEL', 'LEFT_FOOT_INDEX', 'RIGHT_FOOT_INDEX'
    ]
    
    # Identify columns to drop based on prefixes
    columns_to_drop = [col for col in record.index if any(col.startswith(prefix) for prefix in prefixes_to_drop)]
    return record.drop(columns_to_drop)

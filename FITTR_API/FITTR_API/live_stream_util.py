import pandas as pd
import numpy as np
from FITTR_API.ExerciseType import ExerciseType
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
    return raw_record
    #s_record = spread_record(raw_record)
    #return s_record
    

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

def smooth_gaussian_live(record: pd.Series, window_data: pd.DataFrame, sigma: float = 2, window_size: int = 30) -> pd.Series:
    """
    Apply Gaussian smoothing to a live stream without affecting past smoothed values.

    Parameters:
    - record: pd.Series, the current live data point.
    - window_data: pd.DataFrame, past raw data points (not smoothed).
    - sigma: float, standard deviation of the Gaussian kernel.
    - window_size: int, size of the smoothing window.

    Returns:
    - pd.Series: Smoothed version of the current record.
    """
    # Append current record to the window data
    window_data = pd.concat([window_data, record.to_frame().T], axis=0)
    
    # Ensure window size limit
    window_data = window_data.iloc[-window_size:]
    
    # Apply Gaussian kernel
    kernel_radius = int(3 * sigma)
    x = np.arange(-kernel_radius, kernel_radius + 1)
    gaussian_kernel = np.exp(-x**2 / (2 * sigma**2))
    gaussian_kernel /= gaussian_kernel.sum()  # Normalize kernel

    # Apply Gaussian smoothing on each column separately
    smoothed_values = {}
    for column in window_data.columns:
        padded_column = np.pad(window_data[column].values, (kernel_radius, 0), mode='constant')
        convolved_column = np.convolve(padded_column, gaussian_kernel, mode='valid')
        smoothed_values[column] = convolved_column[-1]  # Take the latest smoothed value

    # Return as a Series with the same index as the current record
    return pd.Series(smoothed_values, index=record.index)

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
    padded_data = np.pad(data, pad_width=kernel_radius, mode='symmetric')
    
    # Convolution with Gaussian kernel
    smoothed_data = np.convolve(padded_data, gaussian_kernel, mode='valid')
    
    return pd.Series(smoothed_data,index=data.index)

def calculate_angle(joint_a, joint_b, joint_c):
    """
    Calculate the angle between three joints in 3D space using numpy.
    
    Args:
    joint_a (tuple): The (x, y, z) coordinates of the first joint.
    joint_b (tuple): The (x, y, z) coordinates of the second joint (vertex joint).
    joint_c (tuple): The (x, y, z) coordinates of the third joint.
    
    Returns:
    float: The angle in degrees between the three joints.
    """
    # Convert joint coordinates to numpy arrays
    joint_a = np.array(joint_a)
    joint_b = np.array(joint_b)
    joint_c = np.array(joint_c)
    
    # Calculate vectors: Joint A to B and Joint B to C
    vector_ab = joint_b - joint_a
    vector_bc = joint_c - joint_b
    
    # Calculate dot product and magnitudes using numpy
    dot_product = np.dot(vector_ab, vector_bc)
    magnitude_ab = np.linalg.norm(vector_ab)
    magnitude_bc = np.linalg.norm(vector_bc)
    
    # Avoid division by zero by ensuring valid magnitude values
    if magnitude_ab == 0 or magnitude_bc == 0:
        raise ValueError("One of the vectors has zero length, can't calculate angle.")
    
    # Calculate the cosine of the angle
    cos_theta = dot_product / (magnitude_ab * magnitude_bc)
    
    # Ensure cos_theta is within [-1, 1] to avoid domain errors
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    
    # Calculate the angle in radians, then convert to degrees
    angle_rad = np.arccos(cos_theta)
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg

def joint_angles_per_record(record, joints):
    """
    Calculate the joint angle for a single record (pd.Series).
    
    Args:
    record (pd.Series): A single row from a DataFrame containing joint positions.
    joints (list): List of three joint names as strings (column names).
    
    Returns:
    float: The calculated angle for the given joints in the record.
    """
    joint_a, joint_b, joint_c = joints

    # Extract joint coordinates directly from the record
    a_coords = record[joint_a]
    b_coords = record[joint_b]
    c_coords = record[joint_c]

    if isinstance(a_coords, (list, tuple)):
        pass  # already in (x, y, z) format
    else:
        a_coords = tuple(a_coords)
        b_coords = tuple(b_coords)
        c_coords = tuple(c_coords)

    # Calculate the angle between the joints
    angle = calculate_angle(a_coords, b_coords, c_coords)
    
    return angle


def exercise_to_algo_map(exercise_type:str)->Callable:
    if exercise_type == ExerciseType.SQUATS:
        return squat_reps
    elif exercise_type == ExerciseType.LEFT_BICEP_CURLS:
        return left_bicep_curl_reps
    elif exercise_type == ExerciseType.RIGHT_BICEP_CURLS:
        return right_bicep_curl_reps
    else:
        pass

def squat_reps(current_record:pd.Series,past_record:pd.Series | None)->int:
    if past_record is None or past_record.empty: return 0
    angle_threshold = ExerciseType.SQUATS_THRESHOLD
    # if "RIGHT_KNEE_z" not in current_record.index:
    #      return 0
    # if current_record["RIGHT_KNEE_z"] <= thr and past_record["RIGHT_KNEE_z"] > thr:
    #     return 1
    # else:
    #     return 0
    if "LEFT_ANGLE" not in current_record.index or "RIGHT_ANGLE" not in current_record.index:
         return 0
    left_check = current_record["LEFT_ANGLE"] >= angle_threshold and past_record["LEFT_ANGLE"] < angle_threshold
    right_check = current_record["RIGHT_ANGLE"] >= angle_threshold and past_record["RIGHT_ANGLE"] < angle_threshold
    if left_check and right_check:
        return 1
    return 0
    
def left_bicep_curl_reps(current_record:pd.Series,past_record:pd.Series|None)->int:
    if past_record is None or past_record.empty: return 0
    thr = ExerciseType.LEFT_BICEP_CURLS_THRESHOLD
    if "LEFT_INDEX" not in current_record.index: return 0
    if current_record["LEFT_INDEX"] >= thr and past_record["LEFT_INDEX"] < thr:
        return 1
    return 0

def right_bicep_curl_reps(current_record:pd.Series,past_record:pd.Series|None)->int:
    if past_record is None or past_record.empty: return 0
    thr = ExerciseType.RIGHT_BICEP_CURLS_THRESHOLD
    if "RIGHT_INDEX" not in current_record.index: return 0
    if current_record["RIGHT_INDEX"] >= thr and past_record["RIGHT_INDEX"] < thr:
        return 1
    return 0
    
def exercise_to_filter_map(exercise_type:str)->Callable:
    if exercise_type == ExerciseType.SQUATS:
          return get_relevant_squat_joints
    elif exercise_type == ExerciseType.LEFT_BICEP_CURLS:
        return get_left_bicep_curl_joints
    elif exercise_type == ExerciseType.RIGHT_BICEP_CURLS:
        return get_right_bicep_curl_joints
    else:
        return
    
def get_relevant_squat_joints(record: pd.Series) -> pd.Series:
    """
    Drops data that isn't relevent for Squats.
    """
    return record[["LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE","RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE"]]
    # prefixes_to_drop = [
    #     'NOSE', 'LEFT_EYE', 'RIGHT_EYE', 'LEFT_EAR', 'RIGHT_EAR',
    #     'MOUTH', 'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 'RIGHT_ELBOW',
    #     'LEFT_WRIST', 'RIGHT_WRIST', 'LEFT_PINKY', 'RIGHT_PINKY', 'LEFT_INDEX',
    #     'RIGHT_INDEX', 'LEFT_THUMB', 'RIGHT_THUMB', 'LEFT_ANKLE', 'RIGHT_ANKLE',
    #     'LEFT_HEEL', 'RIGHT_HEEL', 'LEFT_FOOT_INDEX', 'RIGHT_FOOT_INDEX'
    # ]
    # prefixes_to_drop = [
    #     'NOSE', 'LEFT_EYE', 'RIGHT_EYE', 'LEFT_EAR', 'RIGHT_EAR',
    #     'MOUTH', 'LEFT_ELBOW', 'RIGHT_ELBOW',
    #     'LEFT_WRIST', 'RIGHT_WRIST', 'LEFT_PINKY', 'RIGHT_PINKY', 'LEFT_INDEX',
    #     'RIGHT_INDEX', 'LEFT_THUMB', 'RIGHT_THUMB',
    #     'LEFT_HEEL', 'RIGHT_HEEL', 'LEFT_FOOT_INDEX', 'RIGHT_FOOT_INDEX'
    # ]
    
    # # Identify columns to drop based on prefixes
    # columns_to_drop = [col for col in record.index if any(col.startswith(prefix) for prefix in prefixes_to_drop)]
    # return record.drop(columns_to_drop)

def get_left_bicep_curl_joints(record:pd.Series) -> pd.Series:
    return record[["LEFT_INDEX"]]
def get_right_bicep_curl_joints(record:pd.Series) -> pd.Series:
    return record[["RIGHT_INDEX"]]
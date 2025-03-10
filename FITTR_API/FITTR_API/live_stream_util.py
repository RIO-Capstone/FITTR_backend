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
        return squat_rep_factory_function()
    elif exercise_type == ExerciseType.LEFT_BICEP_CURLS:
        return left_bicep_curl_reps
    elif exercise_type == ExerciseType.RIGHT_BICEP_CURLS:
        return right_bicep_curl_reps
    else:
        pass

def squat_rep_factory_function()->Callable:
    SQUATTING = False
    def squat_reps(current_record:pd.Series,past_record:pd.Series|None = None)->int:
        nonlocal SQUATTING # using SQUATTING as almost a global variable
        angle_threshold = ExerciseType.SQUATS_THRESHOLD
        if "LEFT_ANGLE" not in current_record.index or "RIGHT_ANGLE" not in current_record.index:
            return 0
        TEMP_SQUAT_STATE = current_record["LEFT_ANGLE"] >= angle_threshold and current_record["RIGHT_ANGLE"] >= angle_threshold
        if TEMP_SQUAT_STATE and SQUATTING == False:
            SQUATTING = True
            return 1
        elif current_record["LEFT_ANGLE"] < angle_threshold and current_record["RIGHT_ANGLE"] < angle_threshold and SQUATTING:
            SQUATTING = False
            return 0
        return 0
    return squat_reps
    
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
    if current_record["RIGHT_INDEX"] <= thr and past_record["RIGHT_INDEX"] > thr:
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

def get_left_bicep_curl_joints(record:pd.Series) -> pd.Series:
    return record[["LEFT_INDEX"]]
def get_right_bicep_curl_joints(record:pd.Series) -> pd.Series:
    return record[["RIGHT_INDEX"]]

def ema_smoothing(current_record:pd.Series,past_record:pd.Series,alpha=0.5)->pd.Series:
    if past_record is None or past_record.empty:
        return current_record
    return alpha * current_record + (1 - alpha) * past_record
import pytest
import pandas as pd
import numpy as np
from FITTR_API.live_stream_util import (
    process_raw_record,
    calculate_angle,
    joint_angles_per_record,
    exercise_to_algo_map,
    left_bicep_curl_reps,
    right_bicep_curl_reps,
    get_relevant_squat_joints,
    get_left_bicep_curl_joints,
    get_right_bicep_curl_joints
)

# Sample landmarks for testing
@pytest.fixture
def sample_landmarks():
    return pd.Series([
        {"x": 0.1, "y": 0.2, "z": 0.3},
        {"x": 0.4, "y": 0.5, "z": 0.6},
        {"x": 0.7, "y": 0.8, "z": 0.9}
    ])

# Test process_raw_record
def test_process_raw_record(sample_landmarks):
    result = process_raw_record(sample_landmarks)
    assert isinstance(result, pd.Series)
    assert "NOSE" in result.index  # Checking if a label is correctly mapped
    assert len(result) == len(sample_landmarks)  # Ensure all landmarks are processed

# Test calculate_angle
def test_calculate_angle():
    joint_a = (0, 0, 0)
    joint_b = (1, 1, 1)
    joint_c = (2, 2, 2)
    angle = calculate_angle(joint_a, joint_b, joint_c)
    assert isinstance(angle, float)
    assert 0 <= angle <= 180  # Angle should be within valid range

# Test joint_angles_per_record
def test_joint_angles_per_record():
    record = pd.Series({
        "LEFT_HIP": [0, 1, 2],
        "LEFT_KNEE": [3, 4, 5],
        "LEFT_ANKLE": [6, 7, 8]
    })
    angle = joint_angles_per_record(record, ["LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"])
    assert isinstance(angle, float)

# Test exercise_to_algo_map
@pytest.mark.parametrize("exercise_type", ["SQUATS", "LEFT_BICEP_CURLS", "RIGHT_BICEP_CURLS"])
def test_exercise_to_algo_map(exercise_type):
    func = exercise_to_algo_map(exercise_type)
    assert callable(func)

# Test left_bicep_curl_reps
def test_left_bicep_curl_reps():
    current_record = pd.Series({"LEFT_INDEX": 0.8})
    past_record = pd.Series({"LEFT_INDEX": 0.2})
    reps = left_bicep_curl_reps(current_record, past_record)
    assert reps in [0, 1]

# Test right_bicep_curl_reps
def test_right_bicep_curl_reps():
    current_record = pd.Series({"RIGHT_INDEX": 0.2})
    past_record = pd.Series({"RIGHT_INDEX": 0.8})
    reps = right_bicep_curl_reps(current_record, past_record)
    assert reps in [0, 1]

# Test filtering functions
def test_get_relevant_squat_joints():
    record = pd.Series({
        "LEFT_HIP": [0, 0, 0],
        "LEFT_KNEE": [0, 0, 0],
        "LEFT_ANKLE": [0, 0, 0],
        "RIGHT_HIP": [0, 0, 0],
        "RIGHT_KNEE": [0, 0, 0],
        "RIGHT_ANKLE": [0, 0, 0]
    })
    filtered = get_relevant_squat_joints(record)
    assert len(filtered) == 6

def test_get_left_bicep_curl_joints():
    record = pd.Series({"LEFT_INDEX": [0, 0, 0]})
    filtered = get_left_bicep_curl_joints(record)
    assert "LEFT_INDEX" in filtered

def test_get_right_bicep_curl_joints():
    record = pd.Series({"RIGHT_INDEX": [0, 0, 0]})
    filtered = get_right_bicep_curl_joints(record)
    assert "RIGHT_INDEX" in filtered

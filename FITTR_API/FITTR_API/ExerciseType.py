class ExerciseType:
    """
    Acts as a type enumerated class for the different types of exercises that can be performed.
    Ensure that the exercise type strings match with the ones on the app
    """
    SQUATS = "SQUATS"
    
    SQUATS_THRESHOLD = 155 # angular threshold
    
    LEFT_BICEP_CURLS = "LEFT_BICEP_CURLS"

    LEFT_BICEP_CURLS_THRESHOLD = 0.4 # scaled coordinate threshold

    RIGHT_BICEP_CURLS = "RIGHT_BICEP_CURLS"

    RIGHT_BICEP_CURLS_THRESHOLD = 0.4 # scaled coordinate threshold
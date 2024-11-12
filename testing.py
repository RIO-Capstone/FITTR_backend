from src.LSTM import LSTM
from g_media_pipe import extract_data_from_video, save_data, process_and_save_mp4_to_csv
import pandas as pd
import numpy as np
import os
import glob
from typing import List

MP4_DATASETS = "datasets"
SQUATS_MP4 = os.path.join(MP4_DATASETS,"Squats")
PROPER_SQUATS_MP4 = os.path.join(SQUATS_MP4,"Proper")
IMPROPER_SQUATS_MP4 = os.path.join(SQUATS_MP4,"Improper")
CSV_SAVE_LOCATION = "model_data"
SQUATS_CSV = os.path.join(CSV_SAVE_LOCATION,"Squats")
PROPER_SQUATS_CSV = os.path.join(SQUATS_CSV,"Proper")
IMPROPER_SQUATS_CSV = os.path.join(SQUATS_CSV,"Improper")



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
IDEAL_FRAME_LENGTH = 107
print(IDEAL_FRAME_LENGTH)

prediction_classes = {1,0}
squat_predictor = LSTM("Squats",IDEAL_FRAME_LENGTH,prediction_classes,data_path=SQUATS_CSV)
squat_predictor.train()

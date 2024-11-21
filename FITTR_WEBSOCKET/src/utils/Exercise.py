import os
import glob
import numpy as np
from typing import List
import pandas as pd

class Exercise:
    def __init__(self,name) -> None:
        self.name = name
    
    def process_data(self,video_file):
        pass


    def read_data(self):
        directory = os.path.join("model_data", self.name)
        # read then label
        proper_data = self.read_proper_data(os.path.join(directory, "Proper"))
        improper_data = self.read_improper_data(os.path.join(directory, "Improper"))

        proper_labels = np.ones((proper_data.shape[0],))
        improper_labels = np.zeros((improper_data.shape[0],))

        combined_data = np.concatenate((proper_data, improper_data), axis=0)
        combined_labels = np.concatenate((proper_labels, improper_labels), axis=0)

        return combined_data, combined_labels

    def read_proper_data(self,directory):
        # Find all .csv files in the directory
        proper_directory = os.path.join(directory, "*.csv")
        csv_files = glob.glob(proper_directory)
        if len(csv_files) == 0: return
        data = []
        # Process each .csv file
        for file in csv_files:
            data.append(pd.read_csv(file))
        data = np.array(data)
        assert len(data.shape) == 3, f"Improper data shape when reading from directory: ${proper_directory}. Data needs to be 3 dimensional but is currently of shape: ${data.shape}"
        return data
    
    def read_improper_data(self,directory):
        # Find all .csv files in the directory
        improper_directory = os.path.join(directory, "*.csv")
        csv_files = glob.glob(improper_directory)
        if len(csv_files) == 0: return []
        data = []
        # Process each .csv file
        for file in csv_files:
            data.append(pd.read_csv(file))
        data = np.array(data)
        assert len(data.shape) == 3, f"Improper data shape when reading from directory: ${improper_directory}. Data needs to be 3 dimensional but is currently of shape: ${data.shape}"
        return data

    def train(self):
        pass
    def test(self):
        pass
    def predict(self,y_val):
        pass

"""
Created on Nov 3 2023

@author: Tingwei Du
"""


import numpy as np
import pandas as pd
import os
import math
import Modules.ael as L


# Define the folder containing the database
data_folder = r'.\Modules\Assets\GPR' 
image_folder = r".\Modules\Assets\Drones\Road"
table_ael = L.call_ael(image_folder)


# detect high values
def detect_high_values(data, threshold, window_size):
  detected_indices = []
  # i from 0，when index less than len(data) - window_size - 1 
  for i in range(len(data) - window_size - 1):
    # data[i]as start，indicate a new list for storage
    temp_list = []
    # temperary threshold：100 + data[i]
    temp_threshold = threshold + data[i]
    # j is a pointer that keeps moving backward from i + 1 until it moves to the last value, or data[j] is less than the threshold (at which point it is discontinuous)
    j = i + 1
    while j < len(data):
      if data[j] > temp_threshold: 
        temp_list.append(j)
        j += 1
      else:
        break
    # If the staged array meets the continuous length window_size: requirement, it is added to the final result
    if len(temp_list) > window_size:
      detected_indices.append(temp_list)
  return detected_indices


# detect the position of the crack and remaining
def get_index_ranges(df):
  # Define parameter settings that rise abruptly and continuously
  # # Sample data (replace with your dataset)
  data = df.iloc[:, 1]

  # # Set the threshold for detecting high values
  threshold = 8000
  # # Set the window size for analyzing the data
  window_size =445

  # # Detect sudden increases and consistent high values
  detected_indices = detect_high_values(data, threshold, window_size)


  # Detect index of the remaining
  crack = [item for sublist in detected_indices for item in sublist]
  index = df.index.tolist()
  remain = list(set(index).difference(set(crack)))
  res = []
  for i in range(len(remain)):
      if not res:
        res.append([remain[i]])
      elif remain[i-1]+1 == remain[i]:
        res[-1].append(remain[i])
      else:
        res.append([remain[i]])
  return [(min(sublist), max(sublist)) for sublist in res]    


# detect the reamaining width of the road
def calculate_length(point):
    x1, y1 = point
    return y1 - x1
def get_remaining_length(position, df):
  index_ranges = get_index_ranges(df)
  result = []

  for start, end in index_ranges:
      values = position[start-1:end]  # Adjust for 0-based indexing
      result.append(values)

  # Using List Derivatives to Remove Empty Sublists
  result_1 = [sublist for sublist in result if sublist]

  result_ranges = [(min(sublist), max(sublist)) for sublist in result_1]


  # Detect length of the remaining


  lengths = [calculate_length(t) for t in result_ranges]
  return max(lengths)


# read the folder
def read_du (data_folder):
  # # Initialize an empty list to store the results
  results = []
  for filename in os.listdir(data_folder):
    if filename.endswith('.csv'):
      file_path = os.path.join(data_folder, filename)
    
      # Read the CSV file into a DataFrame
      df = pd.read_csv(file_path)

      # Access the first column
      position_ = df.iloc[:, 0]

      # Convert the first column to a Python list
      position = position_.tolist()
      

      # # Append the results to the list
      results.append((filename, get_remaining_length(position, df)))
  return results


# du library
def call_du(data_folder):
  results = read_du (data_folder)

  # Create a DataFrame from the collected results
  table_du = pd.DataFrame(results, columns=["File", "Max Width"])

  # Update table_one with table_two based on their indices
  table_ael['Distance'] = table_du['Max Width']

  return table_ael


print(call_du(data_folder))


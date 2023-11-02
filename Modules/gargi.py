#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 10:35:19 2023

@author: alyafaraht
"""

import cv2
import numpy as np
import pandas as pd
import os
import math
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from fractions import Fraction
import osmnx as ox

#-----------------------------Extracting the GPS data-----------------------------
def fraction_to_decimal(fraction):
    return float(fraction.numerator) / float(fraction.denominator)

def extract_gps(image_loc):
    img = Image.open(image_loc)
    exif_data = img._getexif()
    if exif_data is not None:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'GPSInfo':
                gps_info = {}
                for subtag, subvalue in value.items():
                    subtag_name = GPSTAGS.get(subtag, subtag)
                    gps_info[subtag_name] = subvalue
                longitude = gps_info.get('GPSLongitude', None)
                latitude = gps_info.get('GPSLatitude', None)
                if latitude and longitude:
                    lon_deg = fraction_to_decimal(longitude[0])
                    lon_min = fraction_to_decimal(longitude[1])
                    lon_sec = fraction_to_decimal(longitude[2])
                    lon_dir = gps_info.get('GPSLongitudeRef', 'E')
                    lat_deg = fraction_to_decimal(latitude[0])
                    lat_min = fraction_to_decimal(latitude[1])
                    lat_sec = fraction_to_decimal(latitude[2])
                    lat_dir = gps_info.get('GPSLatitudeRef', 'N')
                    longitude_decimal = lon_deg + lon_min / 60 + lon_sec / 3600
                    if lon_dir == 'W':
                        longitude_decimal = -longitude_decimal
                    latitude_decimal = lat_deg + lat_min / 60 + lat_sec / 3600
                    if lat_dir == 'S':
                        latitude_decimal = -latitude_decimal
    data_gps = {'Longitude': [longitude_decimal], 'Latitude': [latitude_decimal]}
    df_gps = pd.DataFrame(data_gps)
    return df_gps
    print (df_gps) if df_gps is not None else print ("no data")


#-----------------------------Analyzing the image-----------------------------
threshold_mask = 200
threshold_width_mm = 2.0

def processing_image(image_loc):
    img = cv2.imread(image_loc)
    blurred_img = cv2.GaussianBlur(img, (5, 5), 0)
    hsv = cv2.cvtColor(blurred_img, cv2.COLOR_BGR2HSV)
    lower_concrete_crack = np.array([0, 0, 0])
    upper_concrete_crack = np.array([200, 200, 150])
    mask = cv2.inRange(hsv, lower_concrete_crack, upper_concrete_crack)
    return mask

def analyze_masked_image(image_loc):
    binary_mask = np.where(processing_image(image_loc) > threshold_mask, 1, 0)
    scale_factor = 0.1
    column_pixel_counts_x = np.sum(binary_mask, axis=0)
    column_pixel_counts_y = np.sum(binary_mask, axis=1)
    column_widths_mm_x = column_pixel_counts_x * scale_factor
    column_widths_mm_y = column_pixel_counts_y * scale_factor
    
    if np.count_nonzero(column_pixel_counts_x) > np.count_nonzero(column_pixel_counts_y):
        max_direction = "X"
        column_pixel_counts = column_pixel_counts_x
        column_widths_mm = column_widths_mm_x
    else:
        max_direction = "Y"
        column_pixel_counts = column_pixel_counts_y
        column_widths_mm = column_widths_mm_y

    unsafe_cracks = column_widths_mm > threshold_width_mm

    # Calculate the angle with respect to the X direction
    angle_radians = math.atan2(column_pixel_counts_y.sum(), column_pixel_counts_x.sum())
    angle_degrees = math.degrees(angle_radians)

    # Find the contours in the binary mask
    contours, _ = cv2.findContours((processing_image(image_loc)), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Choose the largest contour as the crack (you can add more logic to select the appropriate contour)
        largest_contour = max(contours, key=cv2.contourArea)

        # Fit a rotated rectangle around the crack contour
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]

        # Classify cracks based on the crack angle
        crack_type = 'Shear' if angle > 15 else 'Flexure'

        bridge_safety = "Not Safe" if any(unsafe_cracks) else "Safe"
    else:
        angle = 0  # Default angle when no contours are found
        crack_type = 'No Crack'
        bridge_safety = "Safe"

    data = {
    'Max Column Width (mm)': [max(column_widths_mm_x)],
    'Crack Angle (degrees)': [angle],
    'Crack Type': [crack_type],
    'Safety Status': [bridge_safety]
    }
    df_safety = pd.DataFrame(data)
    return df_safety


#-----------------------------Making .csv file and dataframe-----------------------------

#the safety status will be used for dijkstra
#the .csv file will be used for retrofitting team

def call_gargi(image_folder_G):
    # Create a list to store DataFrames for each image
    df_list = []

    # Loop through the images in the folder
    for filename in os.listdir(image_folder_G):
        if filename.endswith((".jpg", ".jpeg")):
            image_loc = os.path.join(image_folder_G, filename)
            # Extract GPS coordinates
            df_gps = extract_gps(image_loc)
            # Extract safety information
            df_safety = analyze_masked_image(image_loc)
            # Combine the data into a single DataFrame row
            df_row = pd.concat([df_gps, df_safety], axis=1)
            # Append the row to the list
            df_list.append(df_row)
            

    # make safety status dataframe
    df_all = pd.concat(df_list, ignore_index=True)
    df_final = df_all[["Longitude", "Latitude", "Safety Status"]]
    not_safe_data = df_final[df_final["Safety Status"] == "Not Safe"]
    return not_safe_data
    
    #make .csv, it's gonna be inside the assets folder
    output_file = os.path.join(image_folder_G, 'For Retroffiting Team.csv')
    df_all.to_csv(output_file, index=False)




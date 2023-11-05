#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 21:59:27 2023

@author: alyafaraht
"""

import Modules.Du as D
import Modules.gargi as G

# # Define the folder containing the database
data_folder = r".\Modules\Assets\GPR"
image_folder_gargi = r".\Modules\Assets\Drones\Bridge"

du_result = D.call_du(data_folder) #calling the result
gargi_result = G.call_gargi(image_folder_gargi)
# print(du_result)  # Print to see the result
print(du_result)
print(gargi_result)

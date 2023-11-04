#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 21:59:27 2023

@author: alyafaraht
"""

import Modules.Du as D

# # Define the folder containing the database
data_folder = r".\Modules\Assets\GPR"

du_result = D.call_du(data_folder) #calling the result
# print(du_result)  # Print to see the result
print(du_result)
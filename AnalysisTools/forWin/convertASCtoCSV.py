#!/usr/bin/python

import csv
import os
import sys
import numpy as np
import tkFileDialog

directory = tkFileDialog.askdirectory()
strings = ["CALIB", "calib", "INTRO"]

if not os.path.exists(os.path.dirname(sub_folder + '/calib/')):
    print('making directory')
    os.makedirs(os.path.dirname(sub_folder + '/calib/'))

for fn in os.listdir(directory): # we want to loop through all the files in the folder
    print fn
    if any(s in fn for s in strings):  # check for calibration files, and move them to a "calib" folder
        if fn.endswith('.asc') or fn.endswith('.EDF') or fn.endswith('.csv'):
            os.rename(directory + '/' + fn, directory + '/calib/' + fn)
            # print fn
    elif fn.endswith('.asc'):
        print(fn)
        filename = fn

        csv_fn = filename[:-4]+'.csv'
        new_csv = open(directory + '/' + csv_fn, 'wb')
        writer = csv.writer(new_csv)

        with open(directory+'/'+filename, 'rb') as eye_data:

            read = csv.reader(eye_data, delimiter ='\t')
            for row in read:
    
                new_row = row + ['.']*(10-len(row))
                writer.writerow(new_row)
    
        print('end' + filename)
        eye_data.close()
        new_csv.close()

print('end!')
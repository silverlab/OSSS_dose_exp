#!/usr/bin/python

import csv  # module to read CSV functions
import os  # operating system module
import sys  # provides information about constants, functions and methods of the Python interpreter
import numpy as np  # np is an alias pointing to numpy
import tkFileDialog  # helps choose file from local directory
import fnmatch

directory = tkFileDialog.askdirectory()
strings = ["CALIB", "calib", "INTRO"]

if not os.path.exists(os.path.dirname(directory + '/calib/')):
    #print('making directory')
    os.makedirs(os.path.dirname(directory + '/calib/'))

for fn in os.listdir(directory):  # we want to loop through all the files in the folder
    if any(s in fn for s in strings):  # check for calibration files, and move them to a "calib" folder
        if fn.endswith('.asc') or fn.endswith('.EDF') or fn.endswith('.csv'):
            os.rename(directory + '/' + fn, directory + '/calib/' + fn)
            # print fn
    elif fn.endswith('.asc'):
        print(fn)
        filename = fn

        csv_fn = filename[:-4] + '.csv'  # grabs file name without .asc
        # 'wb' = file mode, write binary
        new_csv = open(directory + '/' + csv_fn, 'wb')
        writer = csv.writer(new_csv)

        with open(directory + '/' + filename, 'rb') as eye_data:  # 'rb' = read binary

            read = csv.reader(eye_data, delimiter='\t')  # tab delimited file
            for row in read:

                new_row = row + ['.'] * (10 - len(row))
                writer.writerow(new_row)

        print('end' + filename)
        eye_data.close()
        new_csv.close()
print('end!')

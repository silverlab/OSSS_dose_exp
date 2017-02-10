#!/usr/bin/python

import csv
import os
import sys
import numpy as np
import tkFileDialog

directory = tkFileDialog.askdirectory()


for fn in os.listdir(directory): # we want to loop through all the files in the folder
    print fn

    if fn.endswith('.asc'):
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
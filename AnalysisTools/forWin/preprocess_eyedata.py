import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
from psychopy import gui
from matplotlib.mlab import csv2rec
import csv

from scipy.optimize import leastsq
import Tkinter as tk
import tkFileDialog
#from tkFileDialog import askopenfilename


    
# Set up some constants to use:
win_width = 1150
win_height = 880
annulus_center_x = win_width/2
annulus_center_y = win_height/2
annulus_radius_x = 101
annulus_radius_y = 103

class Get_initials(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.entry = tk.Entry(self)
        self.title("Subject Initials")
        self.button = tk.Button(self, text="Subject Initials:", command=self.on_button)
        self.button.pack()
        self.entry.pack()

    def on_button(self):
        self.input = self.entry.get()
        self.quit()



def dfScatter(df, xcol, ycol, catcol):
    ''' This function plots a scatter plot of a dataframe where each category is plotted with a different color'''
    fig, ax = plt.subplots()
    categories = np.unique(df[catcol])
    colors = np.linspace(0, 1, len(categories))
    colordict = dict(zip(categories, colors))
   
    df["color"] = df[catcol].apply(lambda x: colordict[x])
    ax.scatter(df[xcol], df[ycol], c=(df.color)) 
    return fig 
   
if __name__ =="__main__":
    ### Get subject name and folder to analyze:
    sub_folder = tkFileDialog.askdirectory()
    print sub_folder
    subject_name = Get_initials()
    subject_name.mainloop()
    
    current_subject = subject_name.input
    date = sub_folder[-8:]
    
    if not os.path.exists(os.path.dirname(sub_folder+'/processed/')):
        print('making directory')
        os.makedirs(os.path.dirname(sub_folder+'/processed/'))
    dataFrameSaved = pd.ExcelWriter(sub_folder+'/processed/'+ current_subject+'_'+date+'_master_file.xlsx', engine='xlsxwriter')
    
    for fn in os.listdir(sub_folder):
        eye_track = ''
        if fn.endswith('.csv')==True and fn.endswith('coords.csv') != True:
            print(fn)
            if fn == '._KB_calibration_coords.csv':
                print('break')
            # now we check the eyetrack file for marked trials that break fixation
            # we have eyetrack data!
            eye_track = fn[:-4] # so now eye_track is just the file name which will be SubjectInitials_EXpScheme
                                # and this will correspond with the .psydat file such that the .psydat filename will
                                # be = 'SS_' + eye_track + '_experiment data.psydat
                                
            ### now we do eye_track anaylsis:
            # Read in out data
            data = pd.read_csv(sub_folder + '/' + fn)
            final_col = ['trial', 'time', 'x', 'y', 'In_Bound', 'Stimuli_On', 'Out_Bounds_stim_On', 'Blink'] # 11/28 removed: , 'Out_bounds_Stim_On'
            df_data = pd.DataFrame([], columns=final_col)
            
            temp_columns = ['time', 'x', 'y', '1', '2', '3', '4', '5', '6', '7']
            data.columns = temp_columns
            trial = '0' # want to index which trial we're on
            marked_trials = []
            blinked_time = []
            trial = 0
            marked = 0 # going to use this as 0 or 1 to show if a trial is marked or not: 0 -assumes not, 1 - marked as out of bounds
            flag = 0
            
            stimuli_on = 0
            in_blink = False
            saccade = False
            hold_blink = False
            current_time = 0
            collect_sacc = []
            
            
            # Need to come up with a better way to do this, but
            for index, row in data.iterrows(): # we are iterating through the whole data frame
               
                marked = 0
                #if row['time'].isdigit() == False: # we have a string in the time column, so now we
                
                if isinstance(row['time'], basestring) == True and row['time'].isdigit() == False: # then we have a string 
                # handle what kind of string we have
                    
                    
                    if row['time'] == 'MSG': # check to see if we have a time point or a message
                       
                        # note: 9 is the number of characters from the start of string to any relevant information
                        if row['x'][9:16] == 'TRIALID':
                            
                            trial = (row['x'][17:])
                           
                        # if we're given a trial ID change trial to match
                        
                        # next we want to handle any special time-points - and unfortunately, we'll handle this on a case
                        # by case basis - I'll deal with this later
                        #elif row['time'][
                        
                        elif row['x'][-14:] == 'START_STIMULUS':
                            stimuli_on = 1
                           
                        elif row['x'][-12:] == 'END_STIMULUS':
                            stimuli_on = 0
                    
                    if row['time'][:6] == 'SBLINK':
                        in_blink = True
                        hold_blink = True
                        
                    elif row['time'][:6] == 'EBLINK':
                        in_blink = False
                        saccade = False
                        
                    if row['time'][:5] == 'SSACC':
                        saccade = True
                        collect_sacc.append(row['time'][-8])
                       
                        
                    elif row['time'][:5] == 'ESACC':
                        if hold_blink == True:
                            # then saccade was due to a blink 
                            blinked_time = blinked_time + collect_sacc
                        saccade = False
                        collect_sacc = []
               
                        
                else: # row['time'] has a string of digits, so we're looking at a time-point
                    # check to see if the eye is in bounds of fixation
                    marked = 0
                    flag = 0
                    
                    #if stimuli_on == 1: 
                    try:
                        current_time = row['time']
                        x = float(row['x'])
                        y = float(row['y'])
                        
                        if saccade == True:
                            collect_sacc.append(current_time)
                        
                        
                        if (((x-annulus_center_x)**2)/annulus_radius_x**2 + ((y-annulus_center_y)**2)/annulus_radius_y**2) > 1: # and x> 0 
                            #print('OUT OF BOUNDS')
                            marked = 1
                            marked_trials.append(trial)
                            
                        # Check to see if out of bounds AND stimulus is on
                        if stimuli_on and marked:
                            flag = 1
                        
                        current_row = pd.DataFrame({'trial':[trial], 'time':[row['time']], 'x':[row['x']], 'y':row['y'], 
                            'In_Bound':[marked], 'Stimuli_On':[stimuli_on], 'Out_Bounds_stim_On':[flag], 'Blink':[0]}, index=[0]) # 11/28; removed: 'Out_bounds_Stim_On':[flag]; added: Blink
                        df_data = pd.concat([df_data, current_row], ignore_index=True)
                    
                    except ValueError:
                        marked = 'A'
            
            # 11/28: Make a Column of Blinked trials
            for i in blinked_time:
                df_data.loc[df_data.time == i, 'Blink'] = 1
                
            
            # Clean up the data values -> make sure everything is a numeric -> convert strings of words to 0s
            df_data.trial = df_data.trial.convert_objects(convert_numeric=True)
            df_data.x = df_data.x.convert_objects(convert_numeric=True)
            df_data.x = df_data.x.fillna(value=0)
            df_data.y = df_data.y.convert_objects(convert_numeric=True)
            df_data.y = df_data.y.fillna(value=0)
            
            #Out_Bounds_stim_On = df_data.In_Bound & df_data.Stimuli_On
            #df_data = pd.concat([df_data, Out_Bounds_stim_On], axis=1)
            
            df_data.to_excel(dataFrameSaved, sheet_name=eye_track)
            
            print('saved sheet')
            print(eye_track)
       
    
    dataFrameSaved.save()
    print('end!')

             
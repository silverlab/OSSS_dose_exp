import gc
import wx
from psychopy import core, visual, event, gui


from pylink import *
#from pygame import *
import sys
import time
import os
import numpy as np
import pandas as pd
import xlsxwriter

import psychopy.monitors.calibTools as calib

RIGHT_EYE = 1
LEFT_EYE = 0
BINOCULAR = 2


def create_indices(h, w):
    '''h and w are height and width resp.This will return 16x4 points to calibrate'''
    indices = np.array([(0, 0)])
    x = w / 2 - 10
    y = h / 2 - 10

    for j in range(4):
        i = j + 1
        indices = np.concatenate((indices, [(0, y / i), (0, -y / i), (x / i, 0), (-x / i, 0),
                                            (x / i, y / i), (-x / i, -y / i), (-x / i, y / i), (x / i, -y / i)]), axis=0)
    return indices


# if __name__ == "__main__":


# Initiate Eyetracking
spath = os.path.dirname(sys.argv[0])
if len(spath) != 0:
    os.chdir(spath)


eyelinktracker = EyeLink()


subject_initials = "EL"

EDF_filename = subject_initials + '_CALIB.EDF'

getEYELINK().openDataFile(EDF_filename)

pylink.flushGetkeyQueue()
getEYELINK().setOfflineMode()

win = visual.Window(fullscr=True, monitor='testMonitor',
                    screen=1, units='pixels')
getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %
                         (win.size[0] - 1, win.size[1] - 1))
height = win.size[0]
width = win.size[1]
waitTime = 2
print(height, width)

indices = create_indices(height, width)
getEYELINK().doTrackerSetup()

error = getEYELINK().startRecording(1, 1, 1, 1)
if error:
    print error

# begin the realtime mode
pylink.beginRealTimeMode(100)

if(getEYELINK().isConnected() and not getEYELINK().breakPressed()):
    message = "starting calibration"
    getEYELINK().sendCommand(message)
    # PASTING HERE
    eye_used = getEYELINK().eyeAvailable()  # determine which eye(s) are available
    if eye_used == RIGHT_EYE:
        getEYELINK().sendMessage("EYE_USED 1 RIGHT")
    elif eye_used == LEFT_EYE or eye_used == BINOCULAR:
        getEYELINK().sendMessage("EYE_USED 0 LEFT")
        eye_used = LEFT_EYE
    else:
        print("Error in getting the eye information!")

    getEYELINK().flushKeybuttons(0)
    startTime = currentTime()
    start_message = 'psychopy start time: ' + str(startTime)
    getEYELINK().sendMessage(start_message)

    # AFTER PASTE
    df_calib = pd.DataFrame(columns=['gaze', 'start_time', 'end_time', 'fix'])
    for fix_position in indices:
        # print fix_position
        circle = visual.Circle(win, radius=5, lineWidth=1, fillColor='white',
                               lineColor='white', edges=32, pos=(fix_position[1], fix_position[0]))
        #circleR = visual.Circle(win, radius = 5, lineWidth=1, fillColor='red', lineColor='red', edges=32, pos=(0,0))
        circle.draw()
        # circleR.draw()
        message = 'fixation point: ' + str(fix_position)
        getEYELINK().sendMessage(message)
        win.flip()
        newFixTime = currentTime()
        message = 'fixation point display time: ' + str(newFixTime)
        getEYELINK().sendMessage(message)

        gaze_collection = []
        response = []
        while True:
            keys = event.getKeys()
            response += keys
            dt = getEYELINK().getNewestSample()  # check for gaze_data
            # print(dt)
            if(dt != None):

                if eye_used == RIGHT_EYE and dt.isRightSample():
                    gaze_position = dt.getRightEye().getGaze()
                elif eye_used == LEFT_EYE and dt.isLeftSample():
                    gaze_position = dt.getLeftEye().getGaze()

                gaze_collection.append(gaze_position)
            if 'space' in response:
                endTime = currentTime()
                break

        # df_calib.append([gaze_position; j] <- this will give eye position for a specific fixation position
        # save gaze_position and fix_position
        new_row = pd.DataFrame({'gaze': [gaze_collection], 'start_time': [
                               newFixTime], 'end_time': [endTime], 'fix': [fix_position.tolist()]}, index=[0])
        df_calib = df_calib.append(new_row, ignore_index=True)

    print(df_calib)
    # save df_calib

    if getEYELINK() != None:
        # File transfer and cleanup!
        getEYELINK().setOfflineMode()
        msecDelay(500)

    # Close the file and transfer it to Display PC
    getEYELINK().closeDataFile()
    getEYELINK().receiveDataFile(EDF_filename, EDF_filename)
    getEYELINK().close()

df_calib.to_csv(subject_initials + '_calibration_coords.csv', sep='\t')
#df_calib.to_excel(calibration_coords, sheet_name='calibration')
# calibration_coords.save()
#

# TO DO:
# incorporate eye-tracker X
# get gaze coordinates at times of fixation X
# compare gaze coord to actual stimuli presentation
# calculate offset
# save subject calibration
# recalculate bounds of annulus (i.e. area where subjects are not allowed to look) based off gaze shifts
# use this criteria to send information back to python code when fixation is broken to alert subject
# different tone to represent broken fixation -> or message
# Go through nb to make sure there's not a method I'm forgetting

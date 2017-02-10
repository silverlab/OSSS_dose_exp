"""
Surround suppression experiment, based on Zenger-Landolt and Heeger (2003)

And on the Psychtoolbox version used to get the data in Yoon et al. (2009 and
2010).x

Reference
Yoon, J., Rokem, A., Silver, M., Minzenberg, M., Ursu, S., Ragland, J., & Carter, C. (2009). Diminished orientation-specific surround suppression of visual processing in schizophrenia. Schizophrenia Bulletin, 35(6), 1078-1084.
Yoon, Jong H, Maddock, R. J., Rokem, A., Silver, M. A., Minzenberg, M. J., Ragland, J. D., & Carter, C. S. (2010). GABA concentration is reduced in visual cortex in schizophrenia and correlates with orientation-specific surround suppression. Journal of Neuroscience, 30(10), 3777-3781.
Kosovicheva, A. A., Sheremata, S. L., Rokem, A., Landau, A. N., & Silver, M. A. (2012). Cholinergic enhancement reduces orientation-specific surround suppression but not visual crowding. Frontiers in behavioral neuroscience, 6: 61.

"""

from psychopy import visual, core, event
import psychopy.monitors.calibTools as calib
from pylink import *
from pygame import *
import time
import gc
import sys
import os
import platform
import numpy as np
import wx
import random
import ss_run_eyetrack
import ss_introduction
import ss_calibration

from ss_classes import *
from ss_tools import start_data_file, GetFromSimpleGui

spath = os.path.dirname(sys.argv[0])
if len(spath) != 0:
    os.chdir(spath)

user_choice = GetFromSimpleGui(None, -1, 'Session Params',
                               ['Parallel', 'Orthogonal'])
# success is achieved if the user presses 'done':
user_params = {
    "subject": user_choice.subject,
    "run number": user_choice.run_num}

initials = user_choice.subject
run_num = user_choice.run_num
number_of_blocks = user_choice.block_num

current_dir = os.path.dirname(os.path.realpath((__file__)))
subject_folder = current_dir + '/data/' + initials
# if the current subject doesn't have a data folder make it
if not os.path.exists(subject_folder):
    os.makedirs(subject_folder)


# list_data_dir = subject_folder + ('/%s'
# %time.strftime('%m%d%Y')+str(run_num)) =
list_data = "{0}_{1}".format(time.strftime("%m%d%Y"), run_num)
list_data_dir = os.path.join(subject_folder, list_data)

print(list_data_dir)

try:
    os.stat(list_data_dir)
except:
    os.mkdir(list_data_dir)

# Initiate Eyelink
eyelinktracker = EyeLink()
gui_on = False
intro_ON = True

hold_last_contrasts = {}


""" Before we open the PsychoPy window, run Eyelink Calibration"""
# Calibration
#calib.monitorFolder = './calibration/'
#mon = calib.Monitor('404_CRT_Saved')
mon = '404_CRT_Saved'
win = visual.Window(fullscr=True, monitor=mon, units="deg", screen=0)
win.mouseVisible = False

message = """ Welcome to the Center-Surround experiment! To begin, your eye gaze will be calibrated. Please fixate on the dot on the screen at
each corner of the screen. Press 'SPACE' to start"""
Text(win, text=message, height=0.7, keys=['space'])()
win.flip()

win_x = 1152
win_y = 870

#pylink.openGraphics((win.size[0]-1, win.size[1]-1), 32)
pylink.openGraphics((win_x, win_y), 32)
pylink.setCalibrationColors((0, 0, 0), (192, 192, 192))
#pylink.setTargetSize(int((win.size[0]-1))/70, int((win.size[1]-1))/300)
pylink.setTargetSize(int((win_x - 1)) / 70, int((win_y - 1)) / 300)
pylink.setCalibrationSounds("", "", "")
pylink.setDriftCorrectSounds("", "off", "off")
getEYELINK().doTrackerSetup()
pylink.closeGraphics()
win.close()
"""End Calibration Part 1"""

# Here is the starting point of the experiment:
# Want to use a dictionary for this
# block_runs = {'1':['OSH1', 'NSV1', 'PSH1', 'NSH1', 'OSV1', 'PSV1'],
#    '2': ['OSH1', 'NSV1', 'PSH1', 'NSH1', 'OSV1', 'PSV1', 'OSV2', 'PSH2', 'NSH2', 'PSV2', 'OSH2', 'NSV2'],
#    '3': ['OSH1', 'NSV1', 'PSH1', 'NSH1', 'OSV1', 'PSV1', 'OSV2', 'PSH2', 'NSH2', 'PSV2', 'OSH2', 'NSV2',
#    'OSH3', 'NSV3', 'PSH3', 'NSH3', 'OSV3', 'PSV3'],
#    '4': ['OSH1', 'NSV1', 'PSH1', 'NSH1', 'OSV1', 'PSV1', 'OSV2', 'PSH2', 'NSH2', 'PSV2', 'OSH2', 'NSV2',
#    'OSH3', 'NSV3', 'PSH3', 'NSH3', 'OSV3', 'PSV3', 'OSV4', 'PSH4', 'NSH4', 'PSV4', 'OSH4', 'NSV4']}
# list = ['OSH1', 'NSV1', 'PSH1', 'NSH1', 'OSV1', 'PSV1'] #, 'OSV2', 'PSH2', 'NSH2', 'PSV2', 'OSH2', 'NSV2']
#list = ['OSH1', 'NSV1', 'PSH1', 'NSH1', 'OSV1', 'PSV1', 'OSV2', 'PSH2', 'NSH2', 'PSV2', 'OSH2', 'NSV2', 'OSH3', 'NSV3', 'PSH3', 'NSH3', 'OSV3', 'PSV3', 'OSV4', 'PSH4', 'NSH4', 'PSV4', 'OSH4', 'NSV4']
# list = ['PSV1', 'PSH1', 'PSV2', 'PSH2']# 'NSV1', 'NSH1', 'OSV1', 'OSH1', 'PSV2', 'PSH2', 'NSV2', 'NSH2', 'OSV2', 'OSH2']
#list = block_runs[number_of_blocks]
run_list = []

for run in range(int(number_of_blocks)):
    run_num = str(run + 1)
    condition_types = ['PSH', 'PSV', 'OSH', 'OSV', 'NSH', 'NSV']
    if run == 0:
        pick = random.randint(0, 5)
        run_list.append(condition_types[pick] + '1')
        condition_types.remove(condition_types[pick])
#        run_list.append('PSH1')
#        condition_types.remove('PSH')
    while condition_types != []:
        # our run list is a collection of strings
        if run_list[len(run_list) - 1][:-1] == 'PSH':
            # since our last condition was parallel, we want to display
            # orthogonal or no surround
            pick = random.randint(0, 1)
            if pick == 1 and 'OSV' in condition_types:
                run_list.append('OSV' + run_num)
                condition_types.remove('OSV')
            elif pick == 0 and 'NSV' in condition_types:
                run_list.append('NSV' + run_num)
                condition_types.remove('NSV')

        # our run list is a collection of strings
        elif run_list[len(run_list) - 1][:-1] == 'PSV':
            # since our last condition was parallel, we want to display
            # orthogonal or no surround
            pick = random.randint(0, 1)
            if pick == 1 and 'OSH' in condition_types:
                run_list.append('OSH' + run_num)
                condition_types.remove('OSH')
            elif pick == 0 and 'NSH' in condition_types:
                run_list.append('NSH' + run_num)
                condition_types.remove('NSH')

        # our run list is a collection of strings
        elif run_list[len(run_list) - 1][:-1] == 'NSH':
            # since our last condition was parallel, we want to display
            # orthogonal or no surround
            pick = random.randint(0, 1)
            if pick == 1 and 'OSV' in condition_types:
                run_list.append('OSV' + run_num)
                condition_types.remove('OSV')
            elif pick == 0 and 'PSV' in condition_types:
                run_list.append('PSV' + run_num)
                condition_types.remove('PSV')

        # our run list is a collection of strings
        elif run_list[len(run_list) - 1][:-1] == 'NSV':
            # since our last condition was parallel, we want to display
            # orthogonal or no surround
            pick = random.randint(0, 1)
            if pick == 1 and 'OSH' in condition_types:
                run_list.append('OSH' + run_num)
                condition_types.remove('OSH')
            elif pick == 0 and 'PSH' in condition_types:
                run_list.append('PSH' + run_num)
                condition_types.remove('PSH')

        # our run list is a collection of strings
        elif run_list[len(run_list) - 1][:-1] == 'OSH':
            # since our last condition was parallel, we want to display
            # orthogonal or no surround
            pick = random.randint(0, 1)
            if pick == 1 and 'PSV' in condition_types:
                run_list.append('PSV' + run_num)
                condition_types.remove('PSV')
            elif pick == 0 and 'NSV' in condition_types:
                run_list.append('NSV' + run_num)
                condition_types.remove('NSV')

        # our run list is a collection of strings
        elif run_list[len(run_list) - 1][:-1] == 'OSV':
            # since our last condition was parallel, we want to display
            # orthogonal or no surround
            pick = random.randint(0, 1)
            if pick == 1 and 'PSH' in condition_types:
                run_list.append('PSH' + run_num)
                condition_types.remove('PSH')
            elif pick == 0 and 'NSH' in condition_types:
                run_list.append('NSH' + run_num)
                condition_types.remove('NSH')


print(run_list)
with open(list_data_dir + '/run_list.txt', 'wb') as run_list_f:
    run_list_f.write(', '.join(run_list))


block_num = 1
for block in run_list:
    print('running block: ' + str(block_num))

    TaskType = 'Annulus'
    replay_contrast = None
    if block[:3] == 'PSV':
        # parallel surround vertical
        annulus_ori = 0
        surround_ori = 0
        SurroundType = 'yes'
    elif block[:3] == 'PSH':
        annulus_ori = 90
        surround_ori = 90
        SurroundType = 'yes'
    elif block[:3] == 'OSV':
        annulus_ori = 0
        surround_ori = 90
        SurroundType = 'yes'
    elif block[:3] == 'OSH':
        annulus_ori = 90
        surround_ori = 0
        SurroundType = 'yes'
    elif block[:3] == 'NSH':
        annulus_ori = 90
        surround_ori = 0
        SurroundType = 'no'
    elif block[:3] == 'NSV':
        annulus_ori = 0
        surround_ori = 0
        SurroundType = 'no'

    # Plug these values in instead of gui
    subject = initials + '_' + block
    # Liz Comment: Hypridizing OSSS experiment to work with Eyetracker, so first we'll set up params:
# Initialize params from file:
    params = Params()
    if block_num != 1 and int(block[-1]) != 1:
        params.start_target_contrastA = hold_last_contrasts[block[:3]]
        params.start_target_orthog_contrastA = hold_last_contrasts[block[:3]]

    if gui_on == True:
        # For some reason, if this call is inside ss_classes, just importing
        # ss_classes starts an instance of the GUI, so we put it out here:
        app = wx.App()
        app.MainLoop()
        params.set_by_gui()
    elif gui_on == False:
        # Replacing set_by_gui
        user_params = {
            "subject": subject,
            "surround_ori": surround_ori,
            "annulus_ori": annulus_ori,
            "task": TaskType,
            "_replay": replay_contrast,
            "SurroundType": SurroundType}

        for k in user_params.keys():
            params.__setattr__(k, user_params[k])

    f = start_data_file(params.subject, list_data_dir)

    # Start by saving in the parameter setting:
    params.save(f)

    # For now, assume that the target and the annulus are going to have the same
    # orientation:
    params.target_ori = params.annulus_ori

    # NOW, we set up the window, win
    # This initializes the window:
    # This is the folder where we keep the calibration data:
    calib.monitorFolder = './calibration/'  # over-ride the usual setting of
    #                                          # where monitors are store
    mon = calib.Monitor(params.monitor)  # Get the monitor object and pass that
    #                                        #as an argument to win:
    #
    # win = visual.Window(monitor=mon,
    #                        screen=params.screen,
    #                        fullscr=params.fullscreen,
    #                        units=params.display_units)
    # Initialize all the instances of stimulus bits and pieces for reuse:
    win = visual.Window(fullscr=params.fullscreen,
                        monitor=mon, units="deg", screen=params.screen)
    #win = visual.Window(fullscr= params.fullscreen, monitor=params.monitor, units="deg",screen=params.screen)
    win.mouseVisible = False

    # Set up Stimulus Bank
    bank = StimulusBank(win, params)

    # Make a trial list:
    trial_list = make_trial_list(win, params)

    # Initialize the staircase, depending on which task is performed
    if params.paradigm == 'rapid_fire':
        staircaseA = Staircase(params.start_target_contrastA,
                               params.annulus_contrast / params.contrast_increments,
                               harder=1,  # For this task, lower values aref
                               # actually harder => closer to the annulus
                               # value
                               n_up=2, n_down=1,
                               ub=params.targetA_contrast_max,
                               lb=params.targetA_contrast_min)  # )
    if params.task == 'Annulus' and params.paradigm == 'block':
        staircaseA = Staircase(params.start_target_contrastA,
                               params.annulus_contrast / params.contrast_increments,
                               harder=1,  # For this task, higher values are
                               # actually harder => closer to the annulus
                               # value
                               ub=params.targetA_contrast_max,
                               lb=params.targetA_contrast_min,
                               n_up=2, n_down=1,)
        staircaseB = Staircase(params.start_target_contrastB,
                               params.annulus_contrast / params.contrast_increments,
                               harder=1,  # For this task, higher values are
                               # actually harder => closer to the annulus
                               # value
                               ub=params.targetB_contrast_max,
                               lb=params.targetB_contrast_min,
                               n_up=2, n_down=1,)
    if params.task == 'Annulus':
        if params.surround_ori == params.annulus_ori:
            staircaseA = Staircase(params.start_target_contrastA,
                                   params.annulus_contrast / params.contrast_increments,
                                   harder=1,  # For this task, higher values are
                                   # actually harder => closer to the annulus
                                   # value
                                   ub=params.targetA_contrast_max,
                                   lb=params.targetA_contrast_min,
                                   n_up=2, n_down=1)
        else:
            staircaseA = Staircase(params.start_target_orthog_contrastA,
                                   params.annulus_contrast / params.contrast_increments,
                                   harder=1,  # For this task, higher values are
                                   # actually harder => closer to the annulus
                                   # value
                                   ub=params.targetA_contrast_max,
                                   lb=params.targetA_contrast_min,
                                   n_up=2, n_down=1)
        staircaseB = staircaseA
        if params._replay is None:
            # The fixation target appears but has a constant contrast set to the
            # starting point
            other_contrast = np.ones(len(trial_list)) * params.fix_target_start
        else:
            # Replay a previous run
            other_contrast = params._replay

    elif params.task == 'Fixation':
        # Just one staircase:
        staircaseA = staircaseB = Staircase(params.fix_target_start,
                                            params.fix_target_start / params.contrast_increments,
                                            harder=1,
                                            ub=params.fix_target_max,
                                            lb=params.fix_target_min,
                                            n_up=2, n_down=1)
        if params._replay is None:
            # The annulus target appears and has a constant contrast set to the
            # starting point:
            other_contrast = np.ones(len(trial_list)) * params.fix_target_start
        else:
            # Replay a previous run:
            other_contrast = params._replay

    # Before we get into the main trial loop, we'll run the introduction trials
    if block_num == 1 and intro_ON == True:
        """ Calibration Part II"""
        message = "Next, you'll see another set of white dots. Please fixate on each dot and hit 'SPACE' while fixating. Press 'SPACE' to continue"
        #message = 'Next'
        Text(win, text=message, height=0.7, keys=['space'])()

        ss_calibration.run_calibration(initials, win, list_data_dir)
        intro_trials = 'intro_' + initials
        ss_introduction.Run_Intro_Trials(
            win, params, intro_trials, subject, list_data_dir)

    elif block_num != 1:
        message = """Press 'SPACE' to continue!"""
        # Send a message to the screen and wait for a subject keypress:
        Text(win, text=message, height=0.7, keys=['space'])()
        win.flip()

    win.setMouseVisible(False)
    # If this is in the scanner, we would want to wait for the ttl pulse right
    # here:
    if params.scanner:
        Text(win, text='', keys=['t'])()  # Assuming a TTL is a 't' key

    # Liz Comment: NOW we do more Eyelink Initialization
    if platform.system() == 'Darwin':
        mixer.init()

    # Opens the EDF file.

    edfFileName = params.subject[0:8] + '.edf'
    getEYELINK().openDataFile(edfFileName)
    pylink.flushGetkeyQueue()
    getEYELINK().setOfflineMode()

    # Gets the display surface and sends a mesage to EDF file;
    getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %
                             (win.size[0] - 1, win.size[1] - 1))
    getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d" %
                             (win.size[0] - 1, win.size[1] - 1))

    tracker_software_ver = 0
    eyelink_ver = getEYELINK().getTrackerVersion()
    if eyelink_ver == 3:
        tvstr = getEYELINK().getTrackerVersionString()
        vindex = tvstr.find("EYELINK CL")
        tracker_software_ver = int(
            float(tvstr[(vindex + len("EYELINK CL")):].strip()))
    if eyelink_ver >= 2:
        getEYELINK().sendCommand("select_parser_configuration 0")
        if eyelink_ver == 2:  # turn off scenelink camera stuff
            getEYELINK().sendCommand("scene_camera_gazemap = NO")
    else:
        getEYELINK().sendCommand("saccade_velocity_threshold = 35")
        getEYELINK().sendCommand("saccade_acceleration_threshold = 9500")

    # set EDF file contents
    getEYELINK().sendCommand(
        "file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT")
    if tracker_software_ver >= 4:
        getEYELINK().sendCommand(
            "file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET,INPUT")
    else:
        getEYELINK().sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,INPUT")

    # set link data (used for gaze cursor)
    getEYELINK().sendCommand(
        "link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,INPUT")
    if tracker_software_ver >= 4:
        getEYELINK().sendCommand(
            "link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET,INPUT")
    else:
        getEYELINK().sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT")

    # Here is the run script for the experiment
    if(getEYELINK().isConnected() and not getEYELINK().breakPressed()):
        block_contrast = ss_run_eyetrack.run_trials(
            win, params, trial_list, bank, f, staircaseA, staircaseB, other_contrast)

    hold_last_contrasts[block[:3]] = block_contrast

    if getEYELINK() != None:
        # File transfer and cleanup!
        getEYELINK().setOfflineMode()
        msecDelay(500)

        # Close the file and transfer it to Display PC
        getEYELINK().closeDataFile()

        if not os.path.exists(list_data_dir):
            os.makedirs(list_data_dir)
        getEYELINK().receiveDataFile(edfFileName, list_data_dir + '/' + edfFileName)

    if block_num == len(run_list):
        end_message = """You are done! Press 'SPACE' to close the experiment"""
        # Send a message to the screen and wait for a subject keypress:
        Text(win, text=end_message, height=0.7, keys=['space'])()
    win.close()
    block_num += 1

getEYELINK().close()

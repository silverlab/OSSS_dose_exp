from psychopy import visual, core, event
from pylink import *
from pygame import *
import time
import gc
import sys
import os
import platform
import psychopy.monitors.calibTools as calib
import numpy as np
import time
import wx
from ss_classes import *
import copy

RIGHT_EYE = 1
LEFT_EYE = 0
BINOCULAR = 2


def Run_Intro_Trials(win, params, f, subject_initials,data_dir):
    """ This will run the intro text and trials. Will show the appearance of orthogonal and parallel stimuli and will conduct 5 trials of each
    type of presentation between: Parallel surround, orthogonal surround, and no surround."""
    print("starting intro")
    subject = subject_initials[:2]
    INTRO_filename = subject+'_INTRO.EDF'
    
    # Part 0: set up eyetraciing file
    getEYELINK().openDataFile(INTRO_filename);
    pylink.flushGetkeyQueue(); 
    getEYELINK().setOfflineMode(); 
        
    #win = visual.Window(fullscr= True, monitor='testMonitor', screen=1, units='pixels')
    getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %(win.size[0] - 1, win.size[1] - 1))
    getEYELINK().doTrackerSetup()
    error = getEYELINK().startRecording(1,1,1,1)
    if error:
       print error
    
    #begin the realtime mode
    pylink.beginRealTimeMode(100)
        
    if(getEYELINK().isConnected() and not getEYELINK().breakPressed()):
        message = "starting calibration"
        getEYELINK().sendCommand(message)
        ### PASTING HERE
        eye_used = getEYELINK().eyeAvailable() #determine which eye(s) are available 
        if eye_used == RIGHT_EYE:
            getEYELINK().sendMessage("EYE_USED 1 RIGHT")
        elif eye_used == LEFT_EYE or eye_used == BINOCULAR:
            getEYELINK().sendMessage("EYE_USED 0 LEFT")
            eye_used = LEFT_EYE
        else:
            print("Error in getting the eye information!")
        
        getEYELINK().flushKeybuttons(0)
        startTime = currentTime()
        start_message = 'Introduction start time: '+str(startTime)
        getEYELINK().sendMessage(start_message)
#        
    # 1. First Introduction message 
    message = """ In this experiment you'll be deciding if a quadrant in a center annulus (ring) has a lower contrast than the rest of the ring. You'll be asked
            to report the quadrant with keys: '4', '6', '1', or '3'. press 'SPACE' to continue"""
    Text(win, text=message, height=0.7, keys=['space'])()
    win.flip()

    # 21. Show an example of all three stimulus 
#    text = visual.TextStim(win,text=message, height=0.7)
#    text.draw()
#    win.flip()
#    core.wait(secs=5)

    img = visual.ImageStim(win, image='AllThreeWithText.png', size=(32, 24))
    #img.size = (img.size[0]/win.size[0], img.size[1]/win.size[1])
    img.draw()
    win.flip()

    key_press = None

    keys = ['space']
    while key_press == None:
    
        img.draw()
        # visual.ImageStim(win, image='DEMO.png')
        win.flip()
        for key in event.getKeys():
            if key == 'space':
                key_press = 1
                break
    win.flip()
    
    # 2.2 Show specific Parallel Surround example
    
    img = visual.ImageStim(win, image='PS_Example.png',size=(32, 24))
    img.draw()
    win.flip()

    key_press = None
    
    keys = ['num_1']
    while key_press == None:
    
        img.draw()
        # visual.ImageStim(win, image='DEMO.png')
        win.flip()
        for key in event.getKeys():
            if key == 'num_1':
                # play correct tone
                correct_tone = Sound(sound_freq_sweep(1000, 1000, .1))
                correct_tone.play()
                key_press = 1
                break
    win.flip()


    # 3. Demonstrate incorrect and correct tones
    message = """That tone signifies that you got the trial correct! If you get a trial incorrect you'll hear a different tone.
    press '1' to hear the correct tone again. press '3' to hear the incorrect tone. Please familiarize yourself with the tones then hit 
    'SPACE' to continue"""
    display = visual.TextStim(win, text=message, height=0.7)
    display.draw()
    win.flip()
    all_keys = []

    key_press = None
    keys = ['num_1', 'num_3', 'space']
    while key_press == None:
        display.draw()
        win.flip()
    
        for key in event.getKeys():
            all_keys += key
            if key in keys:
            
                if key == 'num_1': # play the correct tone
                    correct_tone = Sound(sound_freq_sweep(1000, 1000, .1))
                    correct_tone.play()
                elif key == 'num_3': # play the incorrect tone
                    incorrect_tone = Sound(sound_freq_sweep(8000, 200, .1))
                    incorrect_tone.play()
                elif key == 'space': # ready to move on
                    key_press = 1
                    break

    print(all_keys)

    # 4. Prep for dummy trials
    message = """During the experiment, the task may seem difficult, but that's OK! It's designed so that you'll never reach 100% accuracy.
    To get familar with the trials, we'll present a short block of them with more time. After this block, the trials will become much shorter, 
    and you'll be ready to begin. Hit 'SPACE' to start"""
    Text(win, text=message, height=0.7, keys=['space'])()
    win.flip()

    # 5.0 Dummy Trials Parameters
    dummy_num = 50
    dummy_params = copy.deepcopy(params) # but want to change a couple of things
    dummy_params.trials_per_block = 50
    dummy_params.num_blocks = 1
    dummy_params.stimulus_duration = 2.75
    dummy_params.annulus_contrast = 0.6*1.14 #set to 0.35 in real trials
    dummy_params.surround_contrast = 1
    
    
    dummy_params.start_target_contrastA = 0.25*1.14
    dummy_params.start_target_orthog_contrastA = 0.25*1.14 
    dummy_params.start_target_contrastB = 0.25*1.14
    
    dummy_params.contrast_increments = 0.1
    dummy_params.targetA_contrast_max = 0.25*1.14
    dummy_params.targetA_contrast_min = 0.25*1.14
    dummy_params.targetB_contrast_min = 0.25*1.14
    dummy_params.targetB_contrast_max = 0.25*1.14
    

    for i in range(3):
        bank0=[]
        if i == 0:
            # 5.1 Parallel Surround Condition
            # message to the eyeTRACKER that we're in dummy trials
            msg = "START_DUMMY_PS"
            getEYELINK().sendMessage(msg)
            dummy_params.surround_ori = 0;
            dummy_params.annulus_ori = 0;
            dummy_params.SurroundType = 'yes';
            message = """First you'll practice with a parallel surround. Hit 'SPACE' to continue"""
            Text(win, text=message, height=0.7, keys=['space'])()
            win.flip()
        elif i == 1:
            # 5.2 Orthogonal Surround Condition
            # message to the eyeTRACKER that we're in dummy trials
            msg = "START_DUMMY_OS"
            getEYELINK().sendMessage(msg)
            dummy_params.surround_ori = 90;
            dummy_params.annulus_ori = 0;
            dummy_params.SurroundType = 'yes';
            message = """Next, you'll practice with a perpendicular surround. Hit 'SPACE' to continue"""
            Text(win, text=message, height=0.7, keys=['space'])()
            win.flip()
        elif i == 2:
            # 5.3 No Surround Condition
            # message to the eyeTRACKER that we're in dummy trials
            msg = "START_DUMMY_NS"
            getEYELINK().sendMessage(msg)
            dummy_params.surround_ori = 0;
            dummy_params.annulus_ori = 0;
            dummy_params.SurroundType = 'no';
            message = """Finally you'll practice with no surround. Hit 'SPACE' to continue"""
            Text(win, text=message, height=0.7, keys=['space'])()
            win.flip()
        
        # loop through the dummy trials 
        dummy_params.target_ori = dummy_params.annulus_ori
        getEYELINK().sendMessage(msg)
        bank0 = StimulusBank(win, dummy_params)
        dummy_trials = make_trial_list(win, dummy_params)
        other_contrast0 = np.ones(len(dummy_trials)) * dummy_params.fix_target_start
        if dummy_params.surround_ori == dummy_params.annulus_ori:
            staircase0 = Staircase(dummy_params.start_target_contrastA,
                            dummy_params.annulus_contrast/dummy_params.contrast_increments,
                            harder = 10, #For this task, higher values are
                                          #actually harder => closer to the annulus
                                          #value
                            ub=dummy_params.targetA_contrast_max,
                            lb=dummy_params.targetA_contrast_min,
                            n_up=2,n_down=1)
        else:
            staircase0 = Staircase(dummy_params.start_target_orthog_contrastA,
                            dummy_params.annulus_contrast/dummy_params.contrast_increments,
                            harder = 10, #For this task, higher values are
                                      #actually harder => closer to the annulus
                                      #value
                            ub=dummy_params.targetA_contrast_max,
                            lb=dummy_params.targetA_contrast_min,
                            n_up=2,n_down=1)
        
        correct_response = 0
        trial_count = 0
        #for dtrial_idx, dthis_trial in enumerate(dummy_trials):
        while correct_response < 5:
            dthis_trial = dummy_trials[trial_count]
            dtrial_idx = trial_count
            dummy_clock = core.Clock()
            dthis_trial.finalize_stim(dummy_params, bank0, staircase0, other_contrast0[dtrial_idx])
            dthis_trial.stimulus()
            dthis_trial.finalize_fix(dummy_params,bank0,staircase0,[dtrial_idx])
            dthis_trial.finalize_fix(dummy_params,bank0,staircase0,other_contrast0[dtrial_idx])
            dthis_trial.fixation()
            #print(dthis_trial.target_loc)
            dthis_trial.response.finalize(correct_key = dthis_trial.correct_key,
                                     file_name=f)
            dthis_trial.response()
            if dthis_trial.correct_key is not None:
                dthis_trial.feedback.finalize(dthis_trial.response.correct)
            if dthis_trial.response.correct == 1:#'correct':
                correct_response += 1
                
            else:
                correct_response = 0
            print('correct total')
            print(correct_response)
            dthis_trial.feedback()
        
            dthis_trial.wait_iti(dummy_clock)
            trial_count+=1
        
        event.clearEvents()


    #Flush unwanted events that may still be hanging out: 
    event.clearEvents()

    # message to the eyeTRACKER that we're out of dummy trials
    msg = "END_DUMMY"
    getEYELINK().sendMessage(msg)
    
    if getEYELINK() != None:
        # File transfer and cleanup!
        getEYELINK().setOfflineMode()                          
        msecDelay(500)                 
        
    #Close the file and transfer it to Display PC
    getEYELINK().closeDataFile()
    getEYELINK().receiveDataFile(INTRO_filename, data_dir + '/' + INTRO_filename)

    # 6. Last message before start
    message = """ Great! You are ready to start the trials. Please press 'SPACE' to begin!"""
    Text(win, text=message, height=0.7, keys=['space'])()
    win.flip()

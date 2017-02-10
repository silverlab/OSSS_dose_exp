from pylink import *
import time
import gc
import sys
import wx
import numpy as np
from psychopy import core, event
import psychopy.monitors.calibTools as calib
from ss_classes import *
from ss_tools import start_data_file


RIGHT_EYE = 1
LEFT_EYE = 0
BINOCULAR = 2


def do_trial(trial_idx, this_trial, win, staircaseA, staircaseB, other_contrast, exp_clock, params, bank, f):
    '''Does the simple trial'''
    print('in do_trial')
    trial_clock = core.Clock()
    if this_trial.block_type == 'A':
        this_trial.finalize_stim(
            params, bank, staircaseA, other_contrast[trial_idx])
    elif this_trial.block_type == 'B':
        this_trial.finalize_stim(
            params, bank, staircaseB, other_contrast[trial_idx])
    # This supplies the title at the bottom of the eyetracker display
    eye_message = "record_status_message 'Trial %d %s'" % (
        trial_idx, this_trial.block_type)  # !!! change trial_condition
    getEYELINK().sendCommand(eye_message)

    # Always send a TRIALID message before starting to record.
    # EyeLink Data Viewer defines the start of a trial by the TRIALID message.
    # This message is different than the start of recording message START that is logged when the trial recording begins.
    # The Data viewer will not parse any messages, events, or samples, that
    # exist in the data file prior to this message.
    msg = "TRIALID %s" % trial_idx
    getEYELINK().sendMessage(msg)

    getEYELINK().setOfflineMode()
    msecDelay(50)

    error = getEYELINK().startRecording(1, 1, 1, 1)
    if error:
        return error
    gc.disable()
    # begin the realtime mode
    pylink.beginRealTimeMode(100)
    try:
        getEYELINK().waitForBlockStart(100, 1, 0)
    except RuntimeError:
        if getLastError()[0] == 0:  # wait time expired without link data
            end_trial()
            print ("ERROR: No link samples received!")
            return TRIAL_ERROR
        else:  # for any other status simply re-raise the exception
            raise

    getEYELINK().sendMessage("saving start_time")
    current_time = exp_clock.getTime()
    this_trial.save_time(current_time, 0)  # start time

    msg = "START_STIMULUS"
    getEYELINK().sendMessage(msg)
    startTime = currentTime()
    # THIS SHOWS THE STIMULUS -> SO WANT TO COMMUNICATE WITH EYETRACKER IN
    # THIS LOOP
    check_saccade = this_trial.stimulus()
    # check_saccade = 0 if no saccade; = 1 if saccade during trial
    if this_trial.block_type == 'A':
        this_trial.finalize_fix(params, bank, staircaseA,
                                other_contrast[trial_idx])
    if this_trial.block_type == 'B':
        this_trial.finalize_fix(params, bank, staircaseB,
                                other_contrast[trial_idx])

    this_trial.fixation()
    msg = "END_STIMULUS"
    getEYELINK().sendMessage(msg)
    this_trial.response.finalize(correct_key=this_trial.correct_key,
                                 file_name=f)
    msg = "STARTING_RESPONSE"
    getEYELINK().sendMessage(msg)
    this_trial.response()
    msg = "END_RESPONSE"
    getEYELINK().sendMessage(msg)
    if this_trial.correct_key is not None:
        this_trial.feedback.finalize(this_trial.response.correct)
    this_trial.feedback()
    msg = "SENT_FEEDBACK"
    getEYELINK().sendMessage(msg)
    print("feedback section")

    current_time = exp_clock.getTime()
    this_trial.save_time(current_time, 1)  # end time
    getEYELINK().sendMessage("saving end_time")

    # On the first trial, insert the header:
    if trial_idx == 0:
        this_trial.save(f, insert_header=True)
    else:
        # On other , just insert the data:
        this_trial.save(f)
    # update after saving:
    if this_trial.block_type == 'A':
        staircaseA.update(this_trial.response.correct, check_saccade)
        print("update staircase")
    elif this_trial.block_type == 'B':
        staircaseB.update(this_trial.response.correct, check_saccade)

    this_trial.wait_iti(trial_clock)
    print("wait on the trial clock")

    # Flush unwanted events that may still be hanging out:
    event.clearEvents()
    getEYELINK().sendMessage("SYNCTIME %d" % (currentTime() - startTime))

    # Get EYETRACKER STATUS:
    eye_used = getEYELINK().eyeAvailable()  # determine which eye(s) are available
    if eye_used == RIGHT_EYE:
        getEYELINK().sendMessage("EYE_USED 1 RIGHT")
    elif eye_used == LEFT_EYE or eye_used == BINOCULAR:
        getEYELINK().sendMessage("EYE_USED 0 LEFT")
        eye_used = LEFT_EYE
    else:
        print("Error in getting the eye information!")
        return TRIAL_ERROR

    getEYELINK().flushKeybuttons(0)
    last_time = currentTime()
#    while 1:
#        print('in while loop in run_stimuli')
#        error = getEYELINK().isRecording()  # First check if recording is aborted
#        if error!=0:
#            end_trial()
#            return error
#
#        if(getEYELINK().breakPressed()):        # Checks for program termination or ALT-F4 or CTRL-C keys
#            end_trial()
#            return ABORT_EXPT
#        elif(getEYELINK().escapePressed()): # Checks for local ESC key to abort trial (useful in debugging)
#            end_trial()
#            return SKIP_TRIAL
#
#        buttons = getEYELINK().getLastButtonPress() # Checks for eye-tracker buttons pressed
#        if(buttons[0] != 0):
#            getEYELINK().sendMessage("ENDBUTTON %d"%(buttons[0]))
#            end_trial()
#            break
#
#        dt = getEYELINK().getNewestSample() # check for new sample update
#        if(dt != None):
#            last_time = currentTime()
#            # Gets the gaze position of the latest sample,
#            if eye_used == RIGHT_EYE and dt.isRightSample():
#                gaze_position = dt.getRightEye().getGaze()
#            elif eye_used == LEFT_EYE and dt.isLeftSample():
#                gaze_position = dt.getLeftEye().getGaze()

    # end_trial()

    # The TRIAL_RESULT message defines the end of a trial for the EyeLink Data Viewer.
    # This is different than the end of recording message END that is logged when the trial recording ends.
    # Data viewer will not parse any messages, events, or samples that exist
    # in the data file after this message.
    buttons = getEYELINK().getLastButtonPress()
    getEYELINK().sendMessage("TRIAL_RESULT %d" % (buttons[0]))
    ret_value = getEYELINK().getRecordingStatus()

    pylink.endRealTimeMode()
    gc.enable()
    return ret_value


def run_trials(win, params, trial_list, bank, f, staircaseA, staircaseB, other_contrast):
    ''' This function is used to run individual trials and handles the trial return values. '''

    ''' Returns a successful trial with 0, aborting experiment with ABORT_EXPT (3); It also handles
    the case of re-running a trial. '''
    # Do the tracker setup at the beginning of the experiment.
    print('In experiment main function')
    getEYELINK().doTrackerSetup()
    experiment_clock = core.Clock()

# The following does drift correction at the begin of each trial
#    while 1:
#     #   print('in while loop in do_trial')
#        # Checks whether we are still connected to the tracker
#    #    if not getEYELINK().isConnected():
#    #        return ABORT_EXPT
#
#        # Does drift correction and handles the re-do camera setup situations
#        try:
#            error = getEYELINK().doDriftCorrect(win.size[0]//2,win.size[1]//2,1,1)  #!!! change to win dimensions
#            if error != 27
#                break
#            else:
#                getEYELINK().doTrackerSetup()
#        except:
#            getEYELINK().doTrackerSetup()
# !!! UNCOMMENT THIS WITH HUMAN SUBJECT

    # Loop over the event list, while consuming each event, by callin it:
    for trial_idx, this_trial in enumerate(trial_list):
        if(getEYELINK().isConnected() == 0 or getEYELINK().breakPressed()):
            break

        while 1:
            ret_value = do_trial(trial_idx, this_trial, win, staircaseA,
                                 staircaseB, other_contrast, experiment_clock, params, bank, f)
            endRealTimeMode()

            if (ret_value == TRIAL_OK):
                getEYELINK().sendMessage("TRIAL OK")
                break
            elif (ret_value == SKIP_TRIAL):
                getEYELINK().sendMessage("TRIAL ABORTED")
                break
            elif (ret_value == ABORT_EXPT):
                getEYELINK().sendMessage("EXPERIMENT ABORTED")
                return ABORT_EXPT
            elif (ret_value == REPEAT_TRIAL):
                getEYELINK().sendMessage("TRIAL REPEATED")
            else:
                getEYELINK().sendMessage("TRIAL ERROR")
                break

        # Want to get the last contrast to start the next block (of the same
        # condition), of that trial_clock
        if trial_idx == (len(trial_list) - 1):
            final_contrast = this_trial.stimulus.nominal_target_co

    return final_contrast

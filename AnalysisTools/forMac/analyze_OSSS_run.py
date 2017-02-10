from __future__ import division
import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import sys
from matplotlib.mlab import csv2rec
import csv
import seaborn as sns
from scipy.optimize import leastsq
import ast

# class Get_initials(tk.Tk):
#     def __init__(self):
#         tk.Tk.__init__(self)
#         self.entry = tk.Entry(self)
#         self.title("Subject Initials")
#         self.button = tk.Button(self, text="Subject Initials:", command=self.on_button)
#         self.button.pack()
#         self.entry.pack()
#
#     def on_button(self):
#         self.input = self.entry.get()
#         self.quit()
#


def weib_fit(pars, x):
    thresh, slope = pars
    return weibull(x, thresh, slope, guess, flake)


def err_func(pars, x, y):
    return y - weib_fit(pars, x)


def weibull(x, threshx, slope, guess, flake, threshy=None):

    if threshy is None:
        threshy = 1 - (1 - guess) * np.exp(-1)

    k = (-np.log((1 - threshy) / (1 - guess)))**(1 / slope)
    weib = flake - (flake - guess) * np.exp(-(k * x / threshx)**slope)

    return weib


def do_kdtree(x_y_array, points):
    mytree = spatial.cKDTree(x_y_array)
    dist, indexes = mytree.query(points)
    return indexes


def correct_gaze():
    """based on the fixation points used in the subject controlled calibration, we find
    the displacement from fixation to where the eyetracker thought their eye was
    and then we'll use to adjust all of the other gaze data """
    new_fix = ([0, 0], [0, 566], [0, -566], [425, 0], [-425, 0], [425, 566], [-425, -566], [-425, 566],
               [425, -566], [0, 283], [0, -283], [212, 0], [-213,
                                                            0], [212, 283], [-213, -283], [-213, 283],
               [212, -283], [0, 188], [0, -189], [141, 0], [-142,
                                                            0], [141, 188], [-142, -189], [-142, 188],
               [141, -189], [0, 141], [0, -142], [106, 0], [-107,
                                                            0], [106, 141], [-107, -142], [-107, 141],
               [106, -142])

    df_calib = pd.read_csv(sub_folder + '/calib/' + current_subject +
                           '_calibration_coords.csv', delimiter='\t')

    fix = df_calib.fix  # subject data
    df_displacement = pd.DataFrame(
        [], columns=['fix_x', 'fix_y', 'x_dis', 'y_dis'])

    gaze_at_fix = []
    xFixation = []
    yFixation = []

    for i in range(len(df_calib)):
        gaze = df_calib.last_gaze[i]  # looping through calibration coordinates
        # string manipulation?, same output as gaze above
        gaze = ast.literal_eval(gaze)

        gaze_x = gaze[0]  # subject data
        gaze_y = gaze[1]  # subject data

        fx = new_fix[i]  # ground truth data

        # taking ground truth fixation points and adding half of screen size
        fix_y = (1) * int(fx[0]) + (880 / 2)
        # taking ground truth fixation points and adding half of screen size
        fix_x = (-1) * int(fx[1]) + (1150 / 2)
        xFixation.append(fix_x)  # ground truth
        yFixation.append(fix_y)  # ground truth

        gaze_at_fix.append(gaze)  # subject data

    #################################
    x_err_up = []
    y_err_up = []
    x_err_low = []
    y_err_low = []
    for i in range(len(gaze_at_fix)):
        fix_x = xFixation[i]  # ground truth
        fix_y = yFixation[i]  # ground truth

        x = gaze_at_fix[i][0]  # subject data
        y = gaze_at_fix[i][1]  # subject

        x_dis = fix_x - x  # ground truth  - subject data
        y_dis = fix_y - y  # ground truth  - subject data

        if x_dis > 0:
            x_err_up.append(x_dis)
            x_err_low.append(0)
        else:
            x_err_up.append(0)
            x_err_low.append(x_dis)
        if y_dis > 0:
            y_err_up.append(y_dis)
            y_err_low.append(0)
        else:
            y_err_up.append(0)
            y_err_low.append(y_dis)

        new_row = pd.DataFrame({'fix_x': [fix_x], 'fix_y': [fix_y], 'x_dis': [
                               x_dis], 'y_dis': [y_dis]}, index=[0])  # saving GT and displacement
        # ground truth x, ground truth y, x displacement, y displacement
        df_displacement = pd.concat(
            [df_displacement, new_row], ignore_index=True)

    x_err = [x_err_low, x_err_up]
    y_err = [y_err_low, y_err_up]
    #ax.errorbar(df_displacement.fix_x, df_displacement.fix_y,yerr=df_displacement.y_dis, xerr=df_displacement.x_dis, fmt='o')
    gaze_x = [int(g[0]) + df_displacement['x_dis'].mean() for g in gaze_at_fix]
    gaze_y = [int(g[1]) + df_displacement['y_dis'].mean()for g in gaze_at_fix]
    y_avg = df_displacement["y_dis"].mean()
    x_avg = df_displacement["x_dis"].mean()

    return x_avg, y_avg  # overall average displacements?


# doesn't finish this function plots raw ET data showing inner and outer
# annulus
def plot_eyetrack(dir_name, subject, date, all_runs):
    outputBadTrials = open(dir_name + '/processed/' + subject + '_' + date + '_session' +
                           session + '_BadTrials.csv', 'a+')  # Save proportion of bad data into csv file
    outputBadTrialsCsv = csv.writer(outputBadTrials)
    outputBadTrialsCsv.writerow(["SID", "Condition", "Total # samples", "Discarded Samples (stim off)",
                                 "Stim on & no blink", "Bad Fixation Samples", "Proportion Bad Fixation Samples"])
    # load up some figures
    fig_all, ax_all = plt.subplots()
    subject_data = pd.ExcelFile(all_runs)

    labels = []
    num_runs = len(subject_data.sheet_names)
    colormap = plt.cm.gist_ncar
    plt.gca().set_color_cycle([colormap(i)
                               for i in np.linspace(0, 0.9, num_runs)])

    for sheet in subject_data.sheet_names:
        df_data = subject_data.parse(sheet)  # subject data
        df_data = df_data[df_data.Blink == 0]  # subject data without blinks
    # !!! Change this back
        df_stim_on = df_data  # subject data
        # subject data with stimuli on
        df_stim_on = df_stim_on[df_stim_on.Stimuli_On == 1]

        #df_stim_on = df_stim_on[df_stim_on.Out_bounds_Stim_On == 0]

        x_avg, y_avg = correct_gaze()  # get average displacements from previous function
        # ax_all.
        try_x = df_stim_on.x + x_avg
        try_y = df_stim_on.y + y_avg / 2
        # ax_all.
        #plt.plot(df_stim_on.x, df_stim_on.y, '.', alpha=0.2, label=sheet)
        plt.plot(try_x, try_y, '.', alpha=0.2, label=sheet)

        labels.append(sheet)

        # Preliminary efforts to weed out bad trials. Proportion of time
        # subject not properly fixating (# bad samples/ # total samples)
        total = len(subject_data.parse(sheet))  # all samples stimuli present
        # discarded samples (stimuli not on)
        samplesDiscarded = len(subject_data.parse(sheet)) - len(df_stim_on)
        # stimulus on and NOT fixating properly
        outsideFix = len(df_data.time[df_data.Out_Bounds_stim_On == 1])
        # proportion of time NOT fixating properly
        pTimeBad = outsideFix / len(df_stim_on)
        outputBadTrialsCsv.writerow(
            [subject, sheet, total, samplesDiscarded, len(df_stim_on), outsideFix, pTimeBad])

    # ax_all
#     plt.xlim([0, 1150])
#     plt.ylim([0, 800])
    plt.ylim([0, 870])
    plt.xlim([0, 1150])
    plt.plot((1150 / 2), (869 / 2), c='yellow', marker='*', markersize=25)
    annulus_Outer = plt.Circle(
        ((1150 / 2), (869 / 2)), 79.25 * 2, color='r', fill=False)  # outer annulua
    annulus_Inner = plt.Circle(
        ((1150 / 2), (869 / 2)), 79.25, color='r', fill=False)  # inner anulus
    plt.gca().add_artist(annulus_Outer)  # plots circle
    plt.gca().add_artist(annulus_Inner)  # plots circle

    plt.gca().invert_yaxis()
    plt.title(subject + ' Eyetrack')
    plt.legend(labels, ncol=1, loc='upper left')
    plt.savefig(dir_name + '/proccessed/' + subject + '_' +
                date + '_session' + session + '_eyePosition.png')


def plot_psychophysical_performance(subject, date, dir_name, num_blocks):
    output = open(dir_name + '/proccessed/' + subject + '_' + date + '_session' +
                  session + '_ContrastThresholds.txt', 'a')  # Save Thresholds into a .txt file
    fig, axs = plt.subplots(2, 3, sharex=True, sharey=True)
    rm_fig, rm_axs = plt.subplots(2, 3, sharex=True, sharey=True)
    fig_result, axs_result = plt.subplots(2, 3, sharex=True, sharey=True)
    fig_cont, axs_cont = plt.subplots(2, 3, sharex=True, sharey=True)
    axs = axs.ravel()
    rm_axs = rm_axs.ravel()
    axs_result = axs_result.ravel()
    axs_cont = axs_cont.ravel()

    df_psy = pd.DataFrame([], columns=[
                          'condition', 'surround_contrast', 'surround', 'annulus', 'threshold_est'])
    EyeData = pd.ExcelFile(dir_name + '/proccessed/' + subject +
                           '_' + date + '_session' + session + '_master_file.xlsx')

    for fn in os.listdir(dir_name):
        if fn.endswith('psydat') == True:
            file_name = fn

            if (int(fn[9:10]) == 1):

                file_read = file(dir_name + '/' + file_name, 'r')
                p = {}  # To hold parameters
                l = file_read.readline()
                # based on file name structure
                # SS_Initials_Condition_date.psydat
                condition = file_name[6:10]
                # selecting sheet based from master excelfile CHECK WHAT IS
                # GOING ON!
                df_eye = EyeData.parse(subject + '_' + condition)
                # remove blink eye movements
                df_eye = df_eye[df_eye.Blink == 0]

                df_broken_fix = df_eye.copy()
                df_broken_fix = df_broken_fix[
                    df_broken_fix.In_Bound == 1]  # LIZ: double check this

                invalid_trials = df_broken_fix[
                    'trial'].tolist()  # removing bad trials?

                if condition[:3] == 'NSV':
                    ax = axs[0]
                    rm_ax = rm_axs[0]
                    ax_r = axs_result[0]
                    ax_c = axs_cont[0]

                elif condition[:3] == 'NSH':
                    ax = axs[3]
                    rm_ax = rm_axs[3]
                    ax_r = axs_result[3]
                    ax_c = axs_cont[3]

                elif condition[:3] == 'PSV':
                    ax = axs[2]
                    rm_ax = rm_axs[2]
                    ax_r = axs_result[2]
                    ax_c = axs_cont[2]

                elif condition[:3] == 'PSH':
                    ax = axs[5]
                    rm_ax = rm_axs[5]
                    ax_r = axs_result[5]
                    ax_c = axs_cont[5]

                elif condition[:3] == 'OSV':
                    ax = axs[1]
                    rm_ax = rm_axs[1]
                    ax_r = axs_result[1]
                    ax_c = axs_cont[1]

                elif condition[:3] == 'OSH':
                    ax = axs[4]
                    rm_ax = rm_axs[4]
                    ax_r = axs_result[4]
                    ax_c = axs_cont[4]
                else:
                    continue

                while l[0] == '#':
                    try:
                        p[l[1:l.find(':') - 1]
                          ] = float(l[l.find(':') + 1:l.find('\n')])

                    # Not all the parameters can be cast as float (the task and the
                    # subject):
                    except:
                        p[l[2:l.find(':') - 1]] = l[l.find(':') +
                                                    1:l.find('\n')]

                    l = file_read.readline()
                # imports psydat file
                data_rec = csv2rec(dir_name + '/' + file_name)
                annulus_target_contrast = data_rec[
                    'annulus_target_contrast'] - p[' annulus_contrast']
                contrast = data_rec[
                    'annulus_target_contrast'] - p[' annulus_contrast']
                correct = data_rec['correct']

                # if need be do np.array(range(1, 81))
                trials = range(1, len(correct) + 1)
                target_cont = data_rec['annulus_target_contrast']

                # remove broken fixation trials here

                rm_contrast = np.copy(contrast)
                rm_contrast = np.asarray(
                    [i for j, i in enumerate(rm_contrast) if j not in invalid_trials])
                rm_correct = np.copy(correct)
                rm_correct = np.asarray(
                    [i for j, i in enumerate(rm_correct) if j not in invalid_trials])

                if num_blocks > 1:
                    for i in range(2, num_blocks + 1):

                        df_eye = EyeData.parse(
                            subject + '_' + fn[6:9] + str(i))
                        df_broken_fix = df_eye.copy()
                        df_broken_fix = df_broken_fix[
                            df_broken_fix.In_Bound == 1]
                        invalid_trials = df_broken_fix['trial'].tolist()

                        to_upload = fn[:9] + str(i) + fn[10:]
                        data_hold = csv2rec(dir_name + '/' + to_upload)
                        annulus_target_contrast_hold = data_hold[
                            'annulus_target_contrast'] - p[' annulus_contrast']

                        append_target_cont = data_hold[
                            'annulus_target_contrast']
                        append_correct = data_hold['correct']
                        append_contrast = data_hold[
                            'annulus_target_contrast'] - p[' annulus_contrast']
                        correct = np.concatenate(
                            (np.array(correct), np.array(append_correct)))
                        contrast = np.concatenate(
                            (np.array(contrast), np.array(append_contrast)))
                        target_cont = np.concatenate(
                            (target_cont, append_target_cont))

                        rm_contrast_hold_append = np.copy(append_contrast)
                        rm_contrast_hold_append = np.asarray(
                            [i for j, i in enumerate(rm_contrast_hold_append) if j not in invalid_trials])
                        rm_contrast = np.concatenate(
                            (rm_contrast, rm_contrast_hold_append))

                        rm_correct_hold_append = np.copy(append_correct)
                        rm_correct_hold_append = np.asarray(
                            [i for j, i in enumerate(rm_correct_hold_append) if j not in invalid_trials])
                        rm_correct = np.concatenate(
                            (rm_correct, rm_correct_hold_append))
                        trials = range(1, len(correct) + 1)

                labels = []
                for trial in correct:
                    if trial == 1:
                        labels.append('correct')
                    else:
                        labels.append('incorrect')

                # !!! Need to add way to remove broken fixation trials here

                # Which staircase to analyze:
                if p['task'] == ' Fixation ':
                    contrast_all = data_rec['fixation_target_contrast']
                elif p['task'] == ' Annulus ':
                    contrast_all = data_rec[
                        'annulus_target_contrast'] - p[' annulus_contrast']

                labelit = ['annulus_off', 'annulus_on']
                if p[' surround_contrast'] % 90 == 0:
                    surround = 'vertical'
                else:
                    surround = 'horizontal'
                if p[' annulus_contrast'] % 90 == 0:
                    annulus = 'vertical'
                else:
                    annulus = 'horizontal'

                if p['SurroundType'] == ' yes ':
                    surround_contrast = (p[' surround_contrast'])
                else:
                    surround_contrast = 0

                # Switch on the two annulus tasks (annulus on vs. annulus off):
            #   for idx_annulus,operator in enumerate(['<','>=']):
                hit_amps = contrast[correct == 1]
                miss_amps = contrast[correct == 0]
                all_amps = np.hstack([hit_amps, miss_amps])
                # Get the data into this form:
                #(stimulus_intensities,n_correct,n_trials)
                stim_intensities = np.unique(all_amps)
                n_correct = [len(np.where(hit_amps == i)[0])
                             for i in stim_intensities]
                n_trials = [len(np.where(all_amps == i)[0])
                            for i in stim_intensities]

                # concatenates values together
                Data = zip(stim_intensities, n_correct, n_trials)
                # Data in the format: for each stimulus intensity the number of trials the subject got corrent
                # (and how many trials they completed at that intensity) is saved

                # have list marked_trials
                rm_hit_amps = rm_contrast[rm_correct == 1]
                rm_miss_amps = rm_contrast[rm_correct == 0]
                rm_all_amps = np.hstack([rm_hit_amps, rm_miss_amps])
                rm_n_correct = [len(np.where(rm_hit_amps == i)[0])
                                for i in stim_intensities]
                rm_n_trials = [len(np.where(rm_all_amps == i)[0])
                               for i in stim_intensities]

                # concatenates values together
                Data = zip(stim_intensities, n_correct, n_trials)
                # Data in the format: for each stimulus intensity the number of trials the subject got correct
                # (and how many trials they completed at that intensity) is saved
                # concatenates values together
                rm_Data = zip(stim_intensities, rm_n_correct, rm_n_trials)

                x = []
                y = []

                rm_x = []
                rm_y = []

            #        for idx,this in enumerate(Data):
                # Take only cases where there were at least 3 observations:
            #    labelit = p['annulus_ori']

                # instead of length
                for idx, this in enumerate(Data):
                    if n_trials >= 3:

                        # Contrast values:
                        # horizontally stacking (a version of cat?)
                        x = np.hstack([x, this[2] * [this[0]]])
                        #% correct:
                        y = np.hstack(
                            [y, this[2] * [this[1] / float(this[2])]])

                initial = np.mean(x), slope
                this_fit, msg = leastsq(err_func, x0=initial, args=(x, y))

                for idx, this in enumerate(rm_Data):
                    if n_trials >= 3:

                        # Contrast values:
                        rm_x = np.hstack([x, this[2] * [this[0]]])
                        #% correct:
                        if float(this[2]) == 0:
                            rm_y = np.hstack([y, this[2] * [this[0]]])
                        else:
                            rm_y = np.hstack(
                                [y, this[2] * [this[1] / float(this[2])]])

                rm_initial = np.mean(rm_x), slope

                rm_this_fit, rm_msg = leastsq(
                    err_func, x0=rm_initial, args=(rm_x, rm_y))

                ax.plot(x, y, 'o')
                x_for_plot = np.linspace(np.min(x), np.max(x), 100)
                ax.plot(x_for_plot, weibull(x_for_plot, this_fit[0],
                                            this_fit[1],
                                            guess,
                                            flake))
                ax.set_title(condition + ' :thresh=%1.2f::slope=%1.2f'
                             % (this_fit[0], this_fit[1]))
                #ax.set_ylabel('Percentage correct')
                #ax.set_xlabel('Target contrast - annulus contrast')

                rm_ax.plot(x, y, 'o')
                rm_x_for_plot = np.linspace(np.min(rm_x), np.max(rm_x), 100)
                rm_ax.plot(rm_x_for_plot, weibull(rm_x_for_plot, this_fit[0],
                                                  rm_this_fit[1],
                                                  guess,
                                                  flake))
                rm_ax.set_title(condition + ' :removed thresh=%1.2f::slope=%1.2f'
                                % (rm_this_fit[0], rm_this_fit[1]))
                #ax.set_ylabel('Percentage correct')
                #ax.set_xlabel('Target contrast - annulus contrast')

                bootstrap_th = []
                bootstrap_slope = []
                keep_x = x
                keep_y = y
                keep_th = this_fit[0] * -1
                for b in xrange(bootstrap_n):
                    b_idx = np.random.randint(0, x.shape[0], x.shape[0])
                    x = keep_x[b_idx]
                    y = keep_y[b_idx]
                    initial = np.mean(x), slope
                    this_fit, msg = leastsq(err_func, x0=initial, args=(x, y))
                    bootstrap_th.append(this_fit[0])
                    bootstrap_slope.append(this_fit[0])
                upper = np.sort(bootstrap_th)[bootstrap_n * 0.975] * -1
                lower = np.sort(bootstrap_th)[bootstrap_n * 0.025] * -1
                # print "Threshold estimate: %s, CI: [%s,%s]"%(keep_th, lower,
                # upper)

                rm_bootstrap_th = []
                rm_bootstrap_slope = []
                rm_keep_x = rm_x
                rm_keep_y = rm_y
                rm_keep_th = rm_this_fit[0] * -1
                for b in xrange(bootstrap_n):
                    b_idx = np.random.randint(0, rm_x.shape[0], rm_x.shape[0])
                    x = rm_keep_x[b_idx]
                    y = rm_keep_y[b_idx]
                    rm_initial = np.mean(rm_x), slope
                    rm_this_fit, rm_msg = leastsq(
                        err_func, x0=rm_initial, args=(rm_x, rm_y))
                    rm_bootstrap_th.append(rm_this_fit[0])
                    rm_bootstrap_slope.append(rm_this_fit[0])
                rm_upper = np.sort(rm_bootstrap_th)[bootstrap_n * 0.975] * -1
                rm_lower = np.sort(rm_bootstrap_th)[bootstrap_n * 0.025] * -1
                # print "Threshold estimate: %s, CI: [%s,%s]"%(keep_th, lower,
                # upper)

                output.write(condition + ' Tresh: %s, CI: [%s, %s]; removed Tresh: %s, CI [%s, %s] \n' % (
                    keep_th, lower, upper, rm_keep_th, rm_lower, rm_upper))
                new_row = pd.DataFrame({'condition': [condition], 'surround': [surround], 'annulus': [
                                       annulus], 'surround_contrast': [surround_contrast], 'threshold_est': [keep_th]})
                df_psy = pd.concat([df_psy, new_row], ignore_index=True)

                trial_history = pd.DataFrame(
                    dict(x=trials, y=correct, labels=labels))  # plots trial history
                #fig1 = sns.lmplot("x", "y", hue="labels", data=trial_history, fit_reg=False)
                #ax_r.plot(np.mean(trial_history.x),np.mean( trial_history.y), '.')
                pcorrect, = ax_r.bar(1, len(trial_history.y[
                                     trial_history.y == 1]) / len(trial_history.y), width=.3, color='g')
                pincorrect, = ax_r.bar(0, len(trial_history.y[
                                       trial_history.y == 0]) / len(trial_history.y), width=.3, color='r')
                ax_r.set_title(condition)
                ax_c.scatter(trial_history.x, target_cont)  # target contrast
                ax_c.set_title(condition)
                ax_r.set_ylim([0, 1])
                ax_r.set_xlim([0, 1.3])
                ax_r.axes.get_xaxis().set_visible(False)
                ax_r.legend([pcorrect, pincorrect], ['correct', 'incorrect'])

    output.close()
    file_stem = subject
    #fig.xlabel('Target contrast - annulus contrast')
    #fig.ylabel('Percentage correct')
    fig.text(0.5, 0.04, 'Target contrast - annulus contrast', ha='center')
    fig.text(0.04, 0.5, 'Percentage correct', va='center', rotation='vertical')
    fig.set_size_inches(12.5, 9.5)
    fig.savefig('%s.png' % (dir_name + '/proccessed/' + subject +
                            '_' + date + '_session' + session + '_FittedThresholdsWeibull'))
    fig.show()

    #fig.xlabel('Target contrast - annulus contrast')
    #fig.ylabel('Percentage correct')
    rm_fig.text(0.5, 0.04, 'Target contrast - annulus contrast', ha='center')
    rm_fig.text(0.04, 0.5, 'Percentage correct',
                va='center', rotation='vertical')
    rm_fig.set_size_inches(12.5, 9.5)
    rm_fig.savefig('%s.png' % (dir_name + '/proccessed/' + subject + '_' +
                               date + '_session' + session + '_RemovedFittedThresholdWeibull'))
    rm_fig.show()

    fig_result.text(0.5, 0.04, 'Correct or Incorrect', ha='center')
    fig_result.text(0.04, 0.5, 'Proportion', va='center', rotation='vertical')
    fig_result.savefig(dir_name + '/proccessed/' + subject + '_' +
                       date + '_session' + session + '_BehavioralPerformance.png')
    fig_result.set_size_inches(12.5, 9.5)
    fig_result.show()

    fig_cont.text(0.5, 0.04, 'trial number', ha='center')  # figure handle
    fig_cont.text(0.04, 0.5, 'Target Contrast',
                  va='center', rotation='vertical')
    fig_cont.savefig(dir_name + '/proccessed/' + subject +
                     '_' + date + '_session' + session + '_TargetContrast.png')
    fig_cont.set_size_inches(12.5, 9.5)
    fig_cont.show()


# What variables are needed for this to run?
# subject
# date
# dir_name


if __name__ == "__main__":
    # Get subject name and folder to analyze:
    # sub_folder = tkFileDialog.askdirectory()

    sub_folder = sys.argv[1]
    current_subject = sys.argv[2]

    date, sep, session = sub_folder.rpartition("_")
    date = date[-8:]

    if not os.path.isdir(sub_folder):
        sys.exit()
    num_blocks = 4

    # Global-ish Variables
    bootstrap_n = 1000

    # Weibull params:
    guess = 0.5  # The guessing rate is 0.5
    flake = 0.99
    slope = 3.5
    plot_psychophysical_performance(
        current_subject, date, sub_folder, num_blocks)  # only uses this function
    all_runs = sub_folder + '/proccessed/' + current_subject + \
        '_' + date + '_session' + session + '_master_file.xlsx'

    #plot_eyetrack('/'+sub_folder+'/proccessed', current_subject, date, all_runs)
    plot_eyetrack(sub_folder, current_subject, date, all_runs)

    print('end all!')

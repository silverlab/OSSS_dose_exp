#import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
#from psychopy import gui
from matplotlib.mlab import csv2rec
import csv
import seaborn as sns
from scipy.optimize import leastsq
#import Tkinter as tk
#import tkFileDialog
import ast
import os


# class Get_initials(tk.Tk):
#     def __init__(self):
#         tk.Tk.__init__(self)
#         self.entry = tk.Entry(self)
#         self.title("Subject Initials")
#         self.button = tk.Button(self, text="Subject Initials:", command=self.on_button)
#         self.button.pack()
#         self.entry.pack()

#     def on_button(self):
#         self.input = self.entry.get()
#         self.quit()


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

    # load up some figures
    fig_all, ax_all = plt.subplots()
    subject_data = pd.ExcelFile(all_runs)

    labels = []
    num_runs = len(subject_data.sheet_names)
    colormap = plt.cm.gist_ncar
    plt.gca().set_color_cycle([colormap(i)
                               for i in np.linspace(0, 0.9, num_runs)])
    for sheet in subject_data.sheet_names:
        df_data = subject_data.parse(sheet)
        df_data = df_data[df_data.Blink == 0]
    # !!! Change this back
        df_stim_on = df_data
        df_stim_on = df_stim_on[df_stim_on.Stimuli_On == 0]
        df_stim_on = df_stim_on[df_stim_on.Out_bounds_Stim_On == 0]

        x_avg, y_avg = correct_gaze()  # get average displacements
        #print(x_avg, y_avg)
        # ax_all.
        try_x = df_stim_on.x + x_avg
        try_y = df_stim_on.y + y_avg / 2
        # ax_all.
        #plt.plot(df_stim_on.x, df_stim_on.y, '.', alpha=0.2, label=sheet)
        plt.plot(try_x, try_y, '.', alpha=0.2, label=sheet)

        labels.append(sheet)

    # ax_all
#     plt.xlim([0, 1150])
#     plt.ylim([0, 800])
    plt.ylim([0, 870])
    plt.xlim([0, 1150])
    plt.plot((1150 / 2), (869 / 2), c='yellow', marker='*', markersize=25)
    annulus_Outer = plt.Circle(
        ((1150 / 2), (869 / 2)), 79.25 * 2, color='r', fill=False)
    annulus_Inner = plt.Circle(
        ((1150 / 2), (869 / 2)), 79.25, color='r', fill=False)
    plt.gca().add_artist(annulus_Outer)
    plt.gca().add_artist(annulus_Inner)

    plt.gca().invert_yaxis()
    plt.title(subject + ' Eyetrack')
    plt.legend(labels, ncol=1, loc='upper left')
    plt.show()


def plot_psychophysical_performance(subject, date, dir_name, num_blocks):

    output = open(dir_name + '/proccessed/' + subject + '_' + date + '_session' +
                  session + '_no_eye_data.txt', 'a')  # Save Thresholds into a .txt file
    fig, axs = plt.subplots(3, 3, sharex=True, sharey=True)
    axs = axs.ravel()
    conditions = ['NS', 'PS', 'OS']

    df_psy = pd.DataFrame([], columns=[
                          'condition', 'surround_contrast', 'surround', 'annulus', 'threshold_est'])
    for cond in conditions:
        if cond == 'NS':
            ax = axs[6]
            ax_index = 0
            # vertical will be 0; horizontal 3

        elif cond == 'OS':
            ax = axs[7]
            ax_index = 1
            # vertical will be 1; horizontal 4

        elif cond == 'PS':
            ax = axs[8]
            ax_index = 2
            # vertical will be 2 horizontal 5

        cond_correct = np.array([])
        cond_contrast = np.array([])
        cond_target_cont = np.array([])
        cond_stim_intensities = np.array([])
        cond_n_correct = np.array([])
        cond_n_trials = np.array([])

        h_correct = np.array([])
        h_contrast = np.array([])
        h_target_cont = np.array([])
        h_stim_intensities = np.array([])
        h_n_correct = np.array([])
        h_n_trials = np.array([])

        v_correct = np.array([])
        v_contrast = np.array([])
        v_target_cont = np.array([])
        v_stim_intensities = np.array([])
        v_n_correct = np.array([])
        v_n_trials = np.array([])

        for fn in os.listdir(dir_name):

            if fn.endswith('psydat') == True:
                if (fn[6:8] == cond):
                    print(fn)
                    if fn[8:9] == 'H':
                        horizontal = 1
                        vertical = 0
                    elif fn[8:9] == 'V':
                        vertical = 1
                        horizontal = 0
                    else:
                        horizontal = np.nan
                        vertical = np.nan

                    file_name = fn
                    file_read = file(dir_name + '/' + file_name, 'r')
                    p = {}  # To hold parameters
                    l = file_read.readline()

                    while l[0] == '#':
                        try:
                            p[l[1:l.find(':') - 1]
                              ] = float(l[l.find(':') + 1:l.find('\n')])

                        # Not all the parameters can be cast as float (the task and the
                        # subject):
                        except:
                            p[l[2:l.find(':') - 1]
                              ] = l[l.find(':') + 1:l.find('\n')]

                        l = file_read.readline()

                    # import the data file
                    data_rec = csv2rec(dir_name + '/' + file_name)
                    annulus_target_contrast = data_rec[
                        'annulus_target_contrast'] - p[' annulus_contrast']
                    contrast = data_rec[
                        'annulus_target_contrast'] - p[' annulus_contrast']
                    correct = data_rec['correct']

                    labels = []
                    for trial in correct:
                        if trial == 1:
                            labels.append('correct')
                        else:
                            labels.append('incorrect')
                    target_cont = data_rec['annulus_target_contrast']

                    cond_correct = np.concatenate((cond_correct, correct))
                    cond_contrast = np.concatenate((cond_contrast, contrast))
                    cond_target_cont = np.concatenate(
                        (cond_target_cont, target_cont))

                    if horizontal == 1:
                        h_correct = np.concatenate((h_correct, correct))
                        h_contrast = np.concatenate((h_contrast, contrast))
                        h_target_cont = np.concatenate(
                            (h_target_cont, target_cont))

                    if vertical == 1:
                        v_correct = np.concatenate((v_correct, correct))
                        v_contrast = np.concatenate((v_contrast, contrast))
                        v_target_cont = np.concatenate(
                            (v_target_cont, target_cont))

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

        hit_amps = cond_contrast[cond_correct == 1]
        miss_amps = cond_contrast[cond_correct == 0]
        all_amps = np.hstack([hit_amps, miss_amps])
        # Get the data into this form:
        #(stimulus_intensities,n_correct,n_trials)
        cond_stim_intensities = np.unique(all_amps)
        cond_n_correct = [len(np.where(hit_amps == i)[0])
                          for i in cond_stim_intensities]
        cond_n_trials = [len(np.where(all_amps == i)[0])
                         for i in cond_stim_intensities]

        hit_amps = h_contrast[h_correct == 1]
        miss_amps = h_contrast[h_correct == 0]
        all_amps = np.hstack([hit_amps, miss_amps])
        # Get the data into this form:
        #(stimulus_intensities,n_correct,n_trials)
        h_stim_intensities = np.unique(all_amps)
        h_n_correct = [len(np.where(hit_amps == i)[0])
                       for i in h_stim_intensities]
        h_n_trials = [len(np.where(all_amps == i)[0])
                      for i in h_stim_intensities]

        hit_amps = v_contrast[v_correct == 1]
        miss_amps = v_contrast[v_correct == 0]
        all_amps = np.hstack([hit_amps, miss_amps])
        # Get the data into this form:
        #(stimulus_intensities,n_correct,n_trials)
        v_stim_intensities = np.unique(all_amps)
        v_n_correct = [len(np.where(hit_amps == i)[0])
                       for i in v_stim_intensities]
        v_n_trials = [len(np.where(all_amps == i)[0])
                      for i in v_stim_intensities]

        #Data = zip(stim_intensities,n_correct,n_trials)
        # Data in the format: for each stimulus intensity the number of trials the subject got corrent
        # (and how many trials they completed at that intensity) is saved

        Data = zip(cond_stim_intensities, cond_n_correct, cond_n_trials)
        hData = zip(h_stim_intensities, h_n_correct, h_n_trials)
        vData = zip(v_stim_intensities, v_n_correct, v_n_trials)

        print(cond_stim_intensities, cond_n_correct, cond_n_trials)
        print(h_stim_intensities, h_n_correct, h_n_trials)
        print(v_stim_intensities, v_n_correct, v_n_trials)

        x = []
        y = []

        hx = []
        hy = []

        vx = []
        vy = []

    #        for idx,this in enumerate(Data):
        # Take only cases where there were at least 3 observations:
    #    labelit = p['annulus_ori']

        for idx, this in enumerate(Data):
            num_trials = this[2]
            if num_trials >= 3:  # n_trials>=3:

                # Contrast values:
                x = np.hstack([x, this[2] * [this[0]]])
                #% correct:
                y = np.hstack([y, this[2] * [this[1] / float(this[2])]])

        initial = np.mean(x), slope
        this_fit, msg = leastsq(err_func, x0=initial, args=(x, y))

        for idx, this in enumerate(hData):
            num_trials = this[2]
            if num_trials >= 3:  # n_trials>=3:

                # Contrast values:
                hx = np.hstack([hx, this[2] * [this[0]]])
                #% correct:
                hy = np.hstack([hy, this[2] * [this[1] / float(this[2])]])

        initial = np.mean(hx), slope

        hthis_fit, hmsg = leastsq(err_func, x0=initial, args=(hx, hy))

        for idx, this in enumerate(vData):
            num_trials = this[2]
            if num_trials >= 3:  # n_trials>=3:

                # Contrast values:
                vx = np.hstack([vx, this[2] * [this[0]]])
                #% correct:
                vy = np.hstack([vy, this[2] * [this[1] / float(this[2])]])

        initial = np.mean(vx), slope
        vthis_fit, vmsg = leastsq(err_func, x0=initial, args=(vx, vy))

        ax.plot(x, y, 'o')
        ax_h = axs[ax_index + 3]
        ax_v = axs[ax_index]
        ax_h.plot(hx, hy, 'o')
        ax_v.plot(vx, vy, 'o')

        x_for_plot = np.linspace(np.min(x), np.max(x), 100)
        ax.plot(x_for_plot, weibull(x_for_plot, this_fit[0],
                                    this_fit[1],
                                    guess,
                                    flake))
        ax.set_title(cond + ' :thresh=%1.2f::slope=%1.2f'
                     % (this_fit[0], this_fit[1]))

        hx_for_plot = np.linspace(np.min(hx), np.max(hx), 100)
        ax_h.plot(hx_for_plot, weibull(hx_for_plot, hthis_fit[0],
                                       hthis_fit[1],
                                       guess,
                                       flake))
        ax_h.set_title(cond + ' horizontal :thresh=%1.2f::slope=%1.2f'
                       % (hthis_fit[0], hthis_fit[1]))

        vx_for_plot = np.linspace(np.min(vx), np.max(vx), 100)
        ax_v.plot(vx_for_plot, weibull(vx_for_plot, vthis_fit[0],
                                       vthis_fit[1],
                                       guess,
                                       flake))
        ax_v.set_title(cond + ' Vertical :thresh=%1.2f::slope=%1.2f'
                       % (vthis_fit[0], vthis_fit[1]))

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

        hbootstrap_th = []
        hbootstrap_slope = []
        hkeep_x = hx
        hkeep_y = hy
        hkeep_th = hthis_fit[0] * -1
        for b in xrange(bootstrap_n):
            b_idx = np.random.randint(0, hx.shape[0], hx.shape[0])
            hx = hkeep_x[b_idx]
            hy = hkeep_y[b_idx]
            hinitial = np.mean(hx), slope
            hthis_fit, msg = leastsq(err_func, x0=initial, args=(hx, hy))
            hbootstrap_th.append(hthis_fit[0])
            hbootstrap_slope.append(hthis_fit[0])
        hupper = np.sort(hbootstrap_th)[bootstrap_n * 0.975] * -1
        hlower = np.sort(hbootstrap_th)[bootstrap_n * 0.025] * -1
        # print "Threshold estimate: %s, CI: [%s,%s]"%(keep_th, lower, upper)
        # print "Threshold estimate: %s, CI: [%s,%s]"%(keep_th, lower, upper)

        vbootstrap_th = []
        vbootstrap_slope = []
        vkeep_x = vx
        vkeep_y = vy
        vkeep_th = vthis_fit[0] * -1
        for b in xrange(bootstrap_n):
            b_idx = np.random.randint(0, vx.shape[0], vx.shape[0])
            vx = vkeep_x[b_idx]
            vy = vkeep_y[b_idx]
            vinitial = np.mean(vx), slope
            vthis_fit, msg = leastsq(err_func, x0=initial, args=(vx, vy))
            vbootstrap_th.append(vthis_fit[0])
            vbootstrap_slope.append(vthis_fit[0])
        vupper = np.sort(vbootstrap_th)[bootstrap_n * 0.975] * -1
        vlower = np.sort(vbootstrap_th)[bootstrap_n * 0.025] * -1

        output.write(
            cond + ' Tresh: %s, CI: [%s, %s];  \n' % (keep_th, lower, upper))
        output.write(
            cond + ' Horizontal Tresh: %s, CI: [%s, %s];  \n' % (hkeep_th, hlower, hupper))
        output.write(
            cond + ' Vertical Tresh: %s, CI: [%s, %s];  \n' % (vkeep_th, vlower, vupper))
        new_row = pd.DataFrame({'condition': [cond], 'surround': [surround], 'annulus': [
                               annulus], 'surround_contrast': [surround_contrast], 'threshold_est': [keep_th]})
        df_psy = pd.concat([df_psy, new_row], ignore_index=True)

    print('end!')
    output.close()
    file_stem = subject
    #fig.xlabel('Target contrast - annulus contrast')
    #fig.ylabel('Percentage correct')
    fig.text(0.5, 0.04, 'Target contrast - annulus contrast', ha='center')
    fig.text(0.04, 0.5, 'Percentage correct', va='center', rotation='vertical')
    fig.set_size_inches(12.5, 9.5)
    fig.savefig('%s.png' % (dir_name + '/proccessed/' +
                            subject + '_' + date + 'combined_threshold_fit'))
    fig.show()

    # display(df_psy)


# What variables are needed for this to run?
# subject
# date
# dir_name

if __name__ == "__main__":
    # Get subject name and folder to analyze:
    sub_folder = sys.argv[1]
    current_subject = sys.argv[2]

    date, sep, session = sub_folder.rpartition("_")
    date = date[-8:]
    #subject_name = Get_initials()
    # subject_name.mainloop()
    if not os.path.isdir(sub_folder):
        #print("{} is not a valid directory!".format(sub_folder))
        sys.exit()

    #current_subject = subject_name.input
    date = "12312017"
    num_blocks = 4

    # Global-ish Variables
    bootstrap_n = 1000

    # Weibull params:
    guess = 0.5  # The guessing rate is 0.5
    flake = 0.99
    slope = 3.5

    plot_psychophysical_performance(
        current_subject, date, sub_folder, num_blocks)

    print('end all!')

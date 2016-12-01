import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from psychopy import gui
from matplotlib.mlab import csv2rec
import csv
import seaborn as sns
from scipy.optimize import leastsq
import Tkinter as tk
import tkFileDialog 


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
        
        

def weib_fit(pars, x):
    thresh,slope = pars
    
    return weibull(x,thresh,slope,guess,flake)
    
def err_func(pars, x, y):
    return y-weib_fit(pars, x)
    
def weibull(x,threshx,slope,guess,flake,threshy=None):

    if threshy is None:
        threshy = 1-(1-guess)*np.exp(-1)
        
    k = (-np.log( (1-threshy)/(1-guess) ))**(1/slope)
    weib = flake - (flake-guess)*np.exp(-(k*x/threshx)**slope)
    return weib 

def plot_psychophysical_performance(subject, date, dir_name, num_blocks):

    output = open(dir_name + '/proccessed/' + subject+'_'+date+'.txt', 'a') # Save Thresholds into a .txt file
    fig, axs = plt.subplots(2,3, sharex=True, sharey=True)
    rm_fig, rm_axs = plt.subplots(2,3, sharex=True, sharey=True)
    fig_result, axs_result = plt.subplots(2, 3, sharex=True, sharey=True)
    fig_cont, axs_cont = plt.subplots(2, 3, sharex=True, sharey=True)
    axs = axs.ravel()
    rm_axs = rm_axs.ravel()
    axs_result = axs_result.ravel()
    axs_cont = axs_cont.ravel()
    
    df_psy = pd.DataFrame([], columns = ['condition','surround_contrast', 'surround', 'annulus', 'threshold_est'])
    EyeData = pd.ExcelFile(dir_name+'/proccessed/'+subject+'_'+dir_name[-8:]+'_master_file.xlsx')
    

    for fn in os.listdir(dir_name):
        if fn.endswith('psydat')==True:
            file_name = fn
            if (int(fn[9:10]) == 1):
            
                file_read = file(dir_name + '/'+ file_name, 'r')
                p={} #To hold parameters
                l = file_read.readline()
                condition = file_name[6:10] # based on file name structure SS_Initials_Condition_date.psydat
                
                df_eye = EyeData.parse(subject+'_'+condition)
                df_broken_fix = df_eye.copy()
                df_broken_fix = df_broken_fix[df_broken_fix.In_Bound == 0] ### LIZ: double check this
                invalid_trials = df_broken_fix['trial'].tolist()
                
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
                    print(condition)
                    continue

                while l[0]=='#':
                    try:
                        p[l[1:l.find(':')-1]]=float(l[l.find(':')+1:l.find('\n')]) 

                    #Not all the parameters can be cast as float (the task and the
                    #subject): 
                    except:
                        p[l[2:l.find(':')-1]]=l[l.find(':')+1:l.find('\n')]

                    l = file_read.readline()
                data_rec = csv2rec(dir_name + '/'+ file_name) # import the data file 
                annulus_target_contrast = data_rec['annulus_target_contrast']-p[' annulus_contrast']
                contrast = data_rec['annulus_target_contrast']-p[' annulus_contrast']
                correct = data_rec['correct']   

                trials = range(1, len(correct)+1) # if need be do np.array(range(1, 81)) 
                target_cont = data_rec['annulus_target_contrast']
                
                # remove broken fixation trials here
            
                rm_annulus_target_contrast = np.copy(annulus_target_contrast) # first copy the list so we don't lose the original data
                rm_annulus_target_contrast = np.asarray([i for j, i in enumerate(rm_annulus_target_contrast) if j not in invalid_trials])
                rm_contrast = np.copy(contrast)
                rm_contrast = np.asarray([i for j, i in enumerate(rm_contrast) if j not in invalid_trials])
                rm_correct = np.copy(correct)
                rm_correct = np.asarray([i for j, i in enumerate(rm_correct) if j not in invalid_trials])
                    
                
                
                if num_blocks > 1:
                    for i in range(2, num_blocks+1):
                        df_eye = EyeData.parse(subject+'_'+fn[6:9] + str(i))
                        df_broken_fix = df_eye.copy()
                        df_broken_fix = df_broken_fix[df_broken_fix.In_Bound == 0] ### LIZ: double check this
                        invalid_trials = df_broken_fix['trial'].tolist()
                        
                        to_upload = fn[:9] + str(i) + fn[10:]
                        data_hold = csv2rec(dir_name + '/'+ to_upload)
                        append_correct = data_hold['correct']
                        append_contrast = data_hold['annulus_target_contrast']
                        correct = np.concatenate((correct, append_correct)
                        contrast = np.concatenate(contrast, append_cont)
                        
                        rm_annulus_target_contrast_hold = np.copy(annulus_target_contrast) # first copy the list so we don't lose the original data
                        rm_annulus_target_contrast_hold = np.asarray([i for j, i in enumerate(rm_annulus_target_contrast) if j not in invalid_trials])
                        rm_contrast_hold = np.copy(append_contrast)
                        rm_contrast_hold = np.asarray([i for j, i in enumerate(rm_contrast) if j not in invalid_trials])
                        rm_contrast = np.concatenate(contrast, rm_contrast_hold)
                        
                        rm_correct_hold = np.copy(append_correct)
                        rm_correct_hold = np.asarray([i for j, i in enumerate(rm_correct) if j not in invalid_trials])
                        rm_correct = np.concatenate(rm_correct, rm_correct_hold)
                        trials = range(1, len(correct)+ 1)

                labels = []
                for trial in correct:
                    if trial == 1:
                        labels.append('correct')
                    else:
                        labels.append('incorrect')
                print(len(correct))
                print(len(trials))
                        
                # !!! Need to add way to remove broken fixation trials here


                #Which staircase to analyze:
                if p['task'] == ' Fixation ':
                    contrast_all = data_rec['fixation_target_contrast']
                elif p['task']== ' Annulus ':
                    contrast_all = data_rec['annulus_target_contrast']-p[' annulus_contrast']

                labelit = ['annulus_off','annulus_on']
                if p[' surround_contrast']%90 == 0 :
                   surround = 'vertical'
                else:
                   surround = 'horizontal'
                if p[' annulus_contrast']%90 == 0 :
                   annulus = 'vertical'
                else:
                   annulus= 'horizontal'

                if p['SurroundType'] == ' yes ':
                   surround_contrast = (p[' surround_contrast'])
                else:
                   surround_contrast = 0


                #Switch on the two annulus tasks (annulus on vs. annulus off):
            #   for idx_annulus,operator in enumerate(['<','>=']):
                hit_amps = contrast[correct==1]
                miss_amps = contrast[correct==0]
                all_amps = np.hstack([hit_amps,miss_amps])
                    #Get the data into this form:
                    #(stimulus_intensities,n_correct,n_trials)
                stim_intensities = np.unique(all_amps)
                n_correct = [len(np.where(hit_amps==i)[0]) for i in stim_intensities]
                n_trials = [len(np.where(all_amps==i)[0]) for i in stim_intensities]

                Data = zip(stim_intensities,n_correct,n_trials) 
                # Data in the format: for each stimulus intensity the number of trials the subject got corrent
                # (and how many trials they completed at that intensity) is saved
                
                # have list marked_trials
                rm_hit_amps = rm_contrast[rm_correct==1]
                rm_miss_amps = rm_contrast[rm_correct==0]
                rm_all_amps = np.hstack([rm_hit_amps, rm_miss_amps])
                rm_n_correct = [len(np.where(rm_hit_amps==i)[0]) for i in stim_intensities]
                rm_n_trials = [len(np.where(rm_all_amps==i)[0]) for i in stim_intensities]
            
                Data = zip(stim_intensities,n_correct,n_trials) 
                # Data in the format: for each stimulus intensity the number of trials the subject got corrent
                # (and how many trials they completed at that intensity) is saved 
                rm_Data = zip(stim_intensities, rm_n_correct, rm_n_trials)
        

                x = []
                y = []
                
                rm_x = []
                rm_y = []

            #        for idx,this in enumerate(Data):
                        #Take only cases where there were at least 3 observations:
            #    labelit = p['annulus_ori'] 


                for idx,this in enumerate(Data):
                    if n_trials>=3:

                    #Contrast values: 
                        x = np.hstack([x,this[2] * [this[0]]])
                            #% correct:
                        y = np.hstack([y,this[2] * [this[1]/float(this[2])]])

                initial = np.mean(x),slope
                this_fit , msg = leastsq(err_func, x0=initial, args=(x,y))
                
                for idx,this in enumerate(rm_Data):
                    if n_trials>=3:

                    #Contrast values: 
                        rm_x = np.hstack([x,this[2] * [this[0]]])
                            #% correct:
                        rm_y = np.hstack([y,this[2] * [this[1]/float(this[2])]])

                rm_initial = np.mean(rm_x),slope
                rm_this_fit , rm_msg = leastsq(err_func, x0=rm_initial, args=(rm_x,rm_y))
            

                ax.plot(x,y,'o')
                x_for_plot = np.linspace(np.min(x),np.max(x),100)
                ax.plot(x_for_plot,weibull(x_for_plot,this_fit[0],
                                               this_fit[1],
                                               guess,
                                               flake))
                ax.set_title(condition +' :thresh=%1.2f::slope=%1.2f'
                                 %(this_fit[0],this_fit[1]))
                #ax.set_ylabel('Percentage correct')
                #ax.set_xlabel('Target contrast - annulus contrast')
                
                rm_ax.plot(x,y,'o')
                rm_x_for_plot = np.linspace(np.min(rm_x),np.max(rm_x),100)
                rm_ax.plot(rm_x_for_plot,weibull(rm_x_for_plot,this_fit[0],
                                               rm_this_fit[1],
                                               guess,
                                               flake))
                rm_ax.set_title(condition +' :removed thresh=%1.2f::slope=%1.2f'
                                 %(rm_this_fit[0],rm_this_fit[1]))
                #ax.set_ylabel('Percentage correct')
                #ax.set_xlabel('Target contrast - annulus contrast')


                bootstrap_th = []
                bootstrap_slope = []
                keep_x = x
                keep_y = y
                keep_th = this_fit[0]*-1
                for b in xrange(bootstrap_n):
                        b_idx = np.random.randint(0,x.shape[0],x.shape[0])
                        x = keep_x[b_idx]
                        y = keep_y[b_idx]
                        initial = np.mean(x),slope
                        this_fit , msg = leastsq(err_func, x0=initial, args=(x,y))
                        bootstrap_th.append(this_fit[0])
                        bootstrap_slope.append(this_fit[0])
                upper = np.sort(bootstrap_th)[bootstrap_n*0.975]*-1
                lower = np.sort(bootstrap_th)[bootstrap_n*0.025]*-1
                #print "Threshold estimate: %s, CI: [%s,%s]"%(keep_th, lower, upper)
                
                
                rm_bootstrap_th = []
                rm_bootstrap_slope = []
                rm_keep_x = rm_x
                rm_keep_y = rm_y
                rm_keep_th = rm_this_fit[0]*-1
                for b in xrange(bootstrap_n):
                        b_idx = np.random.randint(0,rm_x.shape[0],rm_x.shape[0])
                        x = rm_keep_x[b_idx]
                        y = rm_keep_y[b_idx]
                        rm_initial = np.mean(rm_x),slope
                        rm_this_fit , rm_msg = leastsq(err_func, x0=rm_initial, args=(rm_x,rm_y))
                        rm_bootstrap_th.append(rm_this_fit[0])
                        rm_bootstrap_slope.append(rm_this_fit[0])
                rm_upper = np.sort(rm_bootstrap_th)[bootstrap_n*0.975]*-1
                rm_lower = np.sort(rm_bootstrap_th)[bootstrap_n*0.025]*-1
                #print "Threshold estimate: %s, CI: [%s,%s]"%(keep_th, lower, upper)

                output.write(condition + ' Tresh: %s, CI: [%s, %s]; removed Tresh: %s, CI [%s, %s] \n'%(keep_th, lower, upper, rm_keep_th, rm_lower, rm_upper))
                new_row = pd.DataFrame({'condition':[condition], 'surround':[surround], 'annulus': [annulus], 'surround_contrast':[surround_contrast], 'threshold_est':[keep_th]})
                df_psy = pd.concat([df_psy, new_row], ignore_index=True)


              
                trial_history = pd.DataFrame(dict(x=trials, y=correct, labels=labels))
                #fig1 = sns.lmplot("x", "y", hue="labels", data=trial_history, fit_reg=False)
                ax_r.plot(trial_history.x, trial_history.y, '.')
                ax_r.set_title(condition)
                ax_c.scatter(trial_history.x, target_cont)
                ax_c.set_title(condition)
                ax_r.set_ylim([-1, 2])


    print('end!')
    output.close()
    file_stem = subject
    #fig.xlabel('Target contrast - annulus contrast')
    #fig.ylabel('Percentage correct')
    fig.text(0.5, 0.04, 'Target contrast - annulus contrast', ha='center')
    fig.text(0.04, 0.5, 'Percentage correct', va='center', rotation='vertical')
    fig.set_size_inches(12.5, 9.5)
    fig.savefig('%s.png'%(dir_name + '/proccessed/' + subject+'_'+date+ 'threshold_fit'))
    fig.show()
    
        #fig.xlabel('Target contrast - annulus contrast')
    #fig.ylabel('Percentage correct')
    rm_fig.text(0.5, 0.04, 'Target contrast - annulus contrast', ha='center')
    rm_fig.text(0.04, 0.5, 'Percentage correct', va='center', rotation='vertical')
    rm_fig.set_size_inches(12.5, 9.5)
    rm_fig.savefig('%s.png'%(dir_name + '/proccessed/' + subject+'_'+date+ 'removed_threshold_fit'))
    rm_fig.show()

    fig_result.text(0.5, 0.04, 'trial number', ha='center')
    fig_result.text(0.04, 0.5, '1: Correct; 0: Incorrect', va='center', rotation='vertical')
    fig_result.savefig(dir_name + '/proccessed/' + subject+'_'+date+'_trial_history.png')
    fig_result.set_size_inches(12.5, 9.5)
    fig_result.show()

    fig_cont.text(0.5, 0.04, 'trial number', ha='center')
    fig_cont.text(0.04, 0.5, 'Decrement Contrast', va='center', rotation='vertical')
    fig_cont.savefig(dir_name + '/proccessed/' + subject+'_'+date +'_contrast_trial_history.png')
    fig_cont.set_size_inches(12.5, 9.5)
    fig_cont.show()

    #display(df_psy)


# What variables are needed for this to run?
# subject
# date
# dir_name

if __name__ =="__main__":
    ### Get subject name and folder to analyze:
    sub_folder = tkFileDialog.askdirectory()
    print sub_folder
    subject_name = Get_initials()
    subject_name.mainloop()
    
    current_subject = subject_name.input
    date = sub_folder[-8:]
    num_blocks = 1
    
        # Global-ish Variables
    bootstrap_n = 1000

    #Weibull params:
    guess = 0.5 #The guessing rate is 0.5
    flake = 0.99
    slope = 3.5
    
    plot_psychophysical_performance(current_subject, date, sub_folder, num_blocks)
   
   
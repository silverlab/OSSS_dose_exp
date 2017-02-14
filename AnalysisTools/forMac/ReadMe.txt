{\rtf1\ansi\ansicpg1252\cocoartf1404\cocoasubrtf470
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
\margl1440\margr1440\vieww20060\viewh9980\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 Analysis pipeline for OSSS experiment. For mac operating system only. \
Macs have problems with tkinter package and handling GUIs. Code has been modified to run from the command line and all analyses are run from the command line. \
\
1. convertASCtoCSV.py moves all calibration files to a \'93caleb\'94 folder and converts all .asc eye tracking files to a .csv file format\
to call code: \
change directory to where analysis files are being kept.\
call: python convertASCtoCSV.py \'91directory where data is kept\'92 subject#\
e.g. python convertASCtoCSV.py '/Users/aviaizenman/Dropbox/Silver Lab/OSSSdata/04/01192017_11' 04\
\
2. preprocess_eyedata.py converts all .csv files into one merged master excel spreadsheet where each block has its own sheet. \
to call code:\
change directory to where analysis files are being kept.\
call: e.g. python preprocess_eyedata.py \'91directory where data is kept\'92 subject#\
e.g. python preprocess_eyedata.py '/Users/aviaizenman/Dropbox/Silver Lab/OSSSdata04/01192017_11' 04\
\
3. analyze_OSSS_run.py analyzes the eye tracking data and plots psychophysical thresholds and performance. \
to call code: \
change directory to where analysis files are being kept.\
call: e.g. python analyze_OSSS_run.py \'91directory where data is kept\'92 subject#\
e.g. python analyze_OSSS_run.py '/Users/aviaizenman/Dropbox/Silver Lab/OSSSdata/04/01192017_11' 04\
\
N.B. analyze_OSSS_run_no_eye_Mac.py quickly analyzes psychophysical thresholds for the sake of determining a subjects\'92 experimental threshold. Call the same way analyze_OSSS_run.py is called. }
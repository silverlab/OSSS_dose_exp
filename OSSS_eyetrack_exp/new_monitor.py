import csv
import psychopy.monitors.calibTools as T

# Constructs and saves a new monitor to the given pathname based on the
# given photometer data. Photo data file should be in tab delimited form:
# "input level", "grayscale lum", "red gun lum", green gun lum", "blue gun lum"

# Note: When you want to access a monitor saved into a custom path, must
# change the monitorFolder variable inside of the calibTools module, then
# get the monitor using <module>.Monitor(monitorName)

# Set runtime parameters for monitor:
path = './calibration/'     # where monitors will be stored

monitors = {
    'NNL':  # Information for the NNL goggles:
    dict(monitor_name='NNL',  # name of the new monitor
         calib_file='./calibration/NNLGamma_111409_average.txt',  # photometer data
         width=76.2,  # width of the screen (cm)
         distance=120,  # (virtural) distance from the screen (cm)
         size=[800, 600],  # size of the screen (px)
         # We can also save notes to our monitor:
         notes=""" The NNL MR-safegoggles with calibration"""),

    # Just for testing:
    'testMonitor':
    dict(monitor_name='testMonitor',  # name of the new monitor
         calib_file='./calibration/NNLGamma_111409_average.txt',  # photometer data
         width=32,  # width of the screen (cm)
         distance=50,  # (virtural) distance from the screen (cm)
         size=[1280, 1440],  # size of the screen (px)
         # We can also save notes to our monitor:
         notes=""" Rough estimate of parameters on a laptop, just for testing"""),

    'NEWtestMonitor':
    dict(monitor_name='NEWtestMonitor',  # name of the new monitor
         calib_file='./calibration/NNLGamma_111409_average.txt',  # photometer data
         width=36.5,  # width of the screen (cm)
         distance=61.44,  # (virtural) distance from the screen (cm)
         size=[1920, 1024],  # size of the screen (px)
         # We can also save notes to our monitor:
         notes=""" Rough estimate of parameters on a laptop, just for testing"""),

    '582J_multisync': dict(monitor_name='582J_multisync',  # name of the new monitor
                           calib_file='./calibration/582J_multisync_gamma.txt',  # photometer data
                           width=40.8,  # width of the screen (cm)
                           distance=60,  # distance from the screen (cm)
                           size=[800, 600],  # size of the screen (px)
                           # We can also save notes to our monitor:
                           notes=""" This monitor is the LCD in the psychophysical testing room
     582J and supposedly resembles the monitor in the scanner"""),

    #'404_CRT' : dict(monitor_name = '404_CRT', #name of the new monitor
    #    calib_file = './calibration/404_CRT_gamma.txt',
    #    width = 36.5,
    #    distance = 61.44,
    #    size = [1150, 881],
    # notes = """This monitor is the CRT in the Eyetracker room - 404 Minor
    # Addition """),

    '404_CRT_Oct31': dict(monitor_name='404_CRT',  # name of the new monitor
                          calib_file='./calibration/404_CRT_gamma.txt',
                          width=36.5,
                          distance=61.44,
                          size=[1152, 870],
                          notes="""This monitor is the CRT in the Eyetracker room - 404 Minor Addition """)

    #'404_CRT_gray' : dict(monitor_name = '404_CRT_gray', #name of the new monitor
    #    calib_file = './calibration/404_CRT_grayscale.txt',
    #    width = 36.5,
    #    distance = 61.44,
    #    size = [1920, 1440],
    #    notes = """This monitor is the CRT in the Eyetracker room - 404 Minor Addition """)
    #'404_CRT_RGB' : dict(monitor_name = '404_CRT_RGB', #name of the new monitor
    #    calib_file = './calibration/404_CRT_RGB.txt',
    #    width = 36.5,
    #    distance = 61.44,
    #    size = [1920, 1440],
    # notes = """This monitor is the CRT in the Eyetracker room - 404 Minor
    # Addition """)

}

# Make sure to change monitorFolder in this module for custom save location
T.monitorFolder = path

for m in monitors.keys():
    monitor = monitors[m]
    # Initialize our intermediary variables and open the text file
    fileobj = open(monitor['calib_file'], 'rU')
    csv_read = csv.reader(fileobj, dialect=csv.excel_tab)
    print m
    input_levels = []
    lums = {
        'gray': [],
        'R': [],
        'G': [],
        'B': []}

    # Read input levels and luminescence values from file
    for row in csv_read:
        print row
        if m == '582J_multisync':
            input_levels.append(float(row[0]))
            lums['R'].append(float(row[1]))
            lums['G'].append(float(row[2]))
            lums['B'].append(float(row[3]))
        else:
            input_levels.append(float(row[0]))
            lums['gray'].append(float(row[1]))
            lums['R'].append(float(row[2]))
            lums['G'].append(float(row[3]))
            lums['B'].append(float(row[4]))

    # Calculate the gamma grid based on given lums
    gammaGrid = []
    gamma_vals = {'R': [], 'G': [], 'B': []}
    for val in ['R', 'G', 'B']:  # We are not interested in the grayscale value
        calculator = T.GammaCalculator(inputs=input_levels, lums=lums[val])
        gamma_vals[val] = [calculator.a, calculator.b,
                           calculator.gamma]  # changed gammaVal to gamma
        gammaGrid.append(gamma_vals[val])

    # Create the new monitor, set values and save
    newMon = T.Monitor(monitor['monitor_name'],
                       monitor['width'],
                       monitor['distance'])
    newMon.setSizePix(monitor['size'])
    newMon.setNotes(monitor['notes'])
    newMon.setGammaGrid(gammaGrid)
    newMon.setCalibDate()
    newMon.saveMon()

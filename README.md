This software is an all-in-one data syncing and video playback suite, allowing any source of low-level data to be merged 
with an associated video of SPIRIT to view data trends as they happen. 

# Startup
To use the software, clone the repository and run the program using either of the following commands
Run directly using
>> python3 <YOUR_PATH>/ViSync/__main__.py <flags> 
OR 
Install ViSync to your environment via
>> pip install -e <YOUR_PATH>/ViSync
and then
>> python3 -m ViSync <flags>

There are several flag arguments:
- -v **video_path**: A path to where the video lies on your computer
- -c **csv_path**: A path to the low-level csv
- -s **sync_header**: The name of the column of the data being analyzed
- -d **header_row**: The row number at which the headers start at (0 by default)
- -l **loop_duration**: How many seconds before the live video gif resets (5 by default)
- -r **data_sub_sample_rate**: The sample rate (in Hz) of the analyzed data (60 by default)

If video path, csv path, sync header, or header row is not inputted, the user will be prompted to select files from their computer and what header they want from a list. 

# Instructions
To start, drag the red slider and video progress bar until they reach a point where the video and the ball (moving according to the current data) are moving together. Fine adjustments
can be made to the red line by using the arrow keys, and the shift key can be held in tandem with the arrow keys for even finer adjustments. The gif can also be reset anytime by
pressing 'R'. Once the ball and robot are moving together well enough, press the 'Link' button to link the red line and video slider. 

With this, the red line turns to black and can no longer be controlled. The video slider, however, will be controlling the line. The video and data can also be unlinked and relinked for better adjustments

# Further Usage
In addition to the 'Link' button, more buttons exist to help assist with data collection and video playback. The 'Pause' button pauses both the line and video playback, and the footstep buttons can skip to 
Relevant spikes in data may represent things like footsteps on a certain leg. 

# Limitations

This system only works with low level logs at the moment. Support for mocap logs will be added soon

# Contact

Questions? Concerns? Email me at jmaynes@usc.edu for more info

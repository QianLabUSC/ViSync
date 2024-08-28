import os
import pandas as pd
import csv
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *
from PySide6.QtMultimediaWidgets import *
from .videoThread import *
from .ballWidget import *
from bisect import bisect_left

class csvProcess():
    #TODO FILL IN DOCSTRING
    """_summary_
    """
    def __init__(self, csv_path, data_header, subsample_rate=60, header_row = 0):
        self.force_file = csv_path
        self.data_header = data_header

        self.subsample_rate = subsample_rate

        self.header_row = header_row

        self.force_height = []
        self.force_time = []
        self.step_list = []
        self.force_start_index = 0
        self.detection_offset = 5

    def copyForceForces(self):
        """ Returns all low-level leg Z samples(converted to M) in accordance with the freq interval
        """
        with open(self.force_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            data_iterator = 0
            force_height_iterator = 0
            print("Copying data...")
            for row in reader:
                if (force_height_iterator > self.header_row) and (data_iterator > int(1000 / self.subsample_rate)):
                    # chooses Z coords depending on leg chosen
                    data_iterator = 0 
                    #self.force_height.append(float(row[47 + (3 * self.leg_number)]) * 1000)
                    self.force_height.append(float(row[self.data_header]))
                data_iterator += 1
                force_height_iterator += 1
            print("Done.")
            
    def copyForceTime(self):
        """ Returns all low level time samples in accordance with freq interval
        """
        with open(self.force_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            force_time_iterator = 0
            data_iterator = 0
            print("Copying time data...")
            for row in reader:
                if (force_time_iterator > 0) and (data_iterator > int(1000 / self.subsample_rate)):
                    data_iterator = 0
                    self.force_time.append(float(row[0]))
                data_iterator += 1
                force_time_iterator += 1

    def stepChop(self):
        #TODO FILL IN DOCSTRING
        """_summary_
        """
        recent_high = 0
        plateu = False
        for i in range(1, len(self.force_height)):
            # Looks for plateus ever 8k frames. If plateu already detected we don't want it to cancel out of being a plateu with the else 
            if((i % 8000) == 0) and (not plateu):
                # Looks at the low level height 4k frames before, if equal, plateu detected
                if self.force_height[i] == self.force_height[i - 4000]:
                    plateu = True
                else:
                    plateu = False
            # Plateu detected subroutine
            if(plateu):
                # If the low level leg height begins to rise considerably, end of standing and sitting and beginning rising 
                #if(round(self.force_height[i], 4) > (round(self.force_height[i-50] + 10, 4))):
                if(round(self.force_height[i], 4) > (round(self.force_height[i-0.050] + 0.010, 4))):
                    plateu = False
                    recent_high = -0.400
            else:
                # If the height increases, a leg is moving up, updating that height to the recent highest
                if self.force_height[i] > recent_high:
                    recent_high = self.force_height[i]
                # If the leg height starts to dip
                elif self.force_height[i] < recent_high:
                    # The leg dip has to be significant enough 
                    if recent_high > (self.force_height[i] + 0.120):
                        # Adds time of leg movement to list. 
                        recent_high = self.force_height[i]
                        self.step_list.append(round(self.force_time[i] - self.detection_offset))
                
    def barXToY(self, bar_x):
        #TODO FILL IN DOCSTRING
        """_summary_

        Args:
            bar_x (_type_): _description_

        Returns:
            _type_: _description_
        """
        return (self.force_height[bisect_left(self.force_time, bar_x)])

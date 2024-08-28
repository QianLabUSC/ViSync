from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *
from PySide6.QtMultimediaWidgets import *
from pyqtgraph import PlotWidget, plot
import cv2
import time


class GifState():
    #TODO FILL IN DOCSTRING
    """_summary_
    """
    def __init__(self, pixmap, time):
        self.pixmap = pixmap
        self.time = time


class VideoThread(QThread):
    #TODO FILL IN DOCSTRING
    """_summary_
    """
    change_pixmap_signal = Signal(GifState)
    pause_video_received = Signal()
    resume_video_received = Signal()

    def __init__(self, video_file, input_frame, seconds_before_loop, playback_rate = 30):
        super().__init__()
        self._run_flag = True
        self.input_frame = input_frame
        self.latest_input_frame = input_frame
        self.cap = cv2.VideoCapture(video_file)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, input_frame)
        self.playback_rate = playback_rate
        self.seconds_before_loop = seconds_before_loop
        self.thirtyfps_begin = time.time()
        self.pause_pressed = False
        self.reset_flag = False

    def pause_video_received(self):
        #TODO FILL IN DOCSTRING
        """_summary_
        """
        self.pause_pressed = True

    def resume_video_received(self):
        #TODO FILL IN DOCSTRING
        """_summary_
        """
        self.pause_pressed = False

    def reset_gif(self):
        #TODO FILL IN DOCSTRING
        """_summary_
        """
        self.reset_flag = True

    def run(self):
        #TODO FILL IN DOCSTRING
        """_summary_
        """
        while self._run_flag:
            if(self.input_frame != self.latest_input_frame):

                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.input_frame)
                #View frame on pause
                # ret, frame = self.cap.read()
                # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # height, width, channel = frame.shape
                # img = QImage(frame, width, height, QImage.Format_RGB888)
                # pix = QPixmap.fromImage(img)
                # self.change_pixmap_signal.emit(GifState(pix, frames_since_begin / self.cap.get(cv2.CAP_PROP_FPS)))

            self.latest_input_frame = self.input_frame
            if(self.pause_pressed):
                continue
                
            #fps
            
            if(time.time() - self.thirtyfps_begin) < (1.0/self.playback_rate):
                continue

            
            self.thirtyfps_begin = time.time()
            # gif
            # switch to using frames, update methods
            # Number of frames needed to pass before looping back (Gif)
            frames_before_loop = self.seconds_before_loop * self.cap.get(cv2.CAP_PROP_FPS)
            #print(self.input_frame)
            #print(f"Current frame: {self.cap.get(cv2.CAP_PROP_POS_FRAMES)}")
            # How many fames have passed in any given amount of time
            frames_since_begin = (self.cap.get(cv2.CAP_PROP_POS_FRAMES) - self.input_frame)
            # If goes past gif alloted time
            if ((frames_since_begin > frames_before_loop) or (frames_since_begin < 0) or (self.reset_flag) or ((self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.input_frame)
                self.curr_frame = self.input_frame
                frames_since_begin = 0
                self.reset_flag = False
            
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                img = QImage(frame, width, height, QImage.Format_RGB888)
                pix = QPixmap.fromImage(img)
                self.change_pixmap_signal.emit(GifState(pix, frames_since_begin / self.cap.get(cv2.CAP_PROP_FPS)))
            

    def stop(self):
        #TODO FILL IN DOCSTRING
        """_summary_
        """
        self._run_flag = False
        self.wait()
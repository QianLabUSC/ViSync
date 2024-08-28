from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *
from PySide6.QtMultimediaWidgets import *
import pyqtgraph as pg
import cv2
import time
import math
from .videoThread import *
from .ballWidget import *
from .csvProcess import *


class videoGui():
    #TODO FILL IN DOCSTRING
    """_summary_
    """
    def __init__(self, video_path, csv_process, header_name, seconds_before_loop = 5):
        self.csv_process = csv_process
        self.video_fps = 30
        self.input_frame = 0
        self.seconds_before_loop = seconds_before_loop
        self.data_fps = self.csv_process.subsample_rate

        self.video_file = video_path

        self.header_name = header_name

    def inputFrameToGraphXFrame(self, data_type, input_frame):
        #TODO FILL IN DOCSTRING better explain this one
        """Turn convert input frame into an x coordinate

        Args:
            data_type (_type_): _description_
            input_frame (_type_): _description_
        """
        # we know the first x by the first index of time
        # The camera fps should be calculated
        # The Video is 30 frames
        # So we need to get a starting value
        if(data_type == "mocap"):
            data_fps = 120
            graph_x_start = self.csv_process.mocap_time[0]
        elif(data_type == "force"):
            data_fps = 1000
            graph_x_start = self.csv_process.force_time[0]
            #should be like 442.19
        return(int(((1/self.video_fps) * input_frame) * data_fps)) # returns the frame where the input frame    

    def playVideo(self):
        #TODO FILL IN DOCSTRING
        """_summary_
        """
        video_frame = 0
        cap = cv2.VideoCapture(self)
        if (cap.isOpened()== False):
            print("Error playing video...")
        else:
            print("Playing...")
        last_imshow_time = time.time()
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        print(f"fps: {frame_rate}")
        while(cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = cap.read()

            while (time.time() - last_imshow_time)< (1/frame_rate):
                pass
            
            video_frame+=1
            if ret == True:
                # Display the resulting frame
                last_imshow_time = time.time()
                cv2.imshow('Frame', frame)
                # Press Q on keyboard to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
            # Break the loop
            else:
                break

        # When everything done, release
        # the video capture object
        cap.release()

        # Closes all the frames
        cv2.destroyAllWindows()

    def playVideoGif(self):
        #TODO FILL IN DOCSTRING
        """_summary_
        """
        video_frame = 0
        cap = cv2.VideoCapture(self.video_file)
        cap.set(1, self.input_frame)
        if (cap.isOpened()== False):
            print("Error playing video...")
        else:
            print("Playing...")
        last_imshow_time = time.time()
        loop_begin = time.time()
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        print(f"fps: {frame_rate}")
        while(cap.isOpened()):
            # Capture frame-by-frame
            
            if ((time.time() - loop_begin) > self.seconds_before_loop):
                print(f"frame: {self.input_frame}")
                cap.set(1, self.input_frame)
                loop_begin = time.time()
            ret, frame = cap.read()

            while (time.time() - last_imshow_time)< (1/frame_rate):
                pass
            
            video_frame+=1
            if ret == True:
                # Display the resulting frame
                
                last_imshow_time = time.time()
                cv2.imshow('Frame', frame)
                #show_diff = show_time_begin - show_time_end
                # Press Q on keyboard to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
            # Break the loop
            else:
                break
            
        # When everything done, release
        # the video capture object
        cap.release()

        # Closes all the frames
        cv2.destroyAllWindows()

    class mainWindow(QMainWindow):
        #TODO FILL IN DOCSTRING
        """_summary_
        """
        pause_video_send = Signal()
        resume_video_send = Signal()
        reset_gif_send = Signal()
        def __init__(self, csv_process, video_gui):
            super().__init__()
            print("Initializing Window...")
        #Setup csv and video objects
            self.csv_process = csv_process
            self.video_gui = video_gui

            self.pause_pressed = False
        # Truncate input values
            #self.csv_process.returnTruncatedData(self.csv_process.force_height, self.csv_process.force_time, datatype = "force", framerate = 60)

            self.thirty_fps_begin_linemove = time.time()
            self.loop_time = time.time()
        #Line moving 
            self.line_move_index = 0

            #Main setup
            #self.setStyleSheet("background-color: white;")
            self.setWindowTitle("VideoSync")
            self.setMinimumSize(QSize(400,300))
            
            #Plot
            self.graphWidget = pg.PlotWidget()
            #Set background to white
            self.graphWidget.setBackground('#1E1E1E')
            #Set title
            self.graphWidget.setTitle("Low-Level Data ", color="w", size="15pt")
            #Set axis labels
            styles = {"color": "#fff", "font-size": "15px"}
            self.graphWidget.setLabel("left", self.video_gui.header_name, **styles)
            self.graphWidget.setLabel("bottom", "Time (s)", **styles)

            #Add grid
            self.graphWidget.showGrid(x=True, y=True)

            pen = pg.mkPen(color=(255, 255, 255), width = 3)
            self.cursor_pen = pg.mkPen(color = (255,0,0), width = 2)
            self.cursor_pen_link = pg.mkPen(color = (0,0,0), width = 4)
            moving_pen = pg.mkPen(color = (255, 165, 0), width = 1)
            self.graphWidget.plot(self.csv_process.force_time, self.csv_process.force_height, pen=pen)

            #crosshair lines
            self.crosshair_v = pg.InfiniteLine(angle=90, movable=False, pen=moving_pen)
            self.graphWidget.addItem(self.crosshair_v, ignoreBounds=True)
            self.crosshair_cursor = pg.InfiniteLine(pos = 500, angle=90, movable=True, pen=self.cursor_pen)
            #self.crosshair_cursor.sigDragged.connect(self.redlineVideoMove)
            self.graphWidget.setMouseEnabled(y=False)
            self.graphWidget.addItem(self.crosshair_cursor, ignoreBounds=True)
            
            #self.setLineWidth(1)


            #Start video thread
            self.thread = VideoThread(self.video_gui.video_file, self.video_gui.input_frame, self.video_gui.seconds_before_loop, playback_rate = 15)
            self.thread.change_pixmap_signal.connect(self.update_image)
            self.thread.change_pixmap_signal.connect(self.move_crosshair)
            self.thread.start()

            #Resize graph
            #self.graphWidget.setFixedSize(700, 400)  # Adjust the size as needed
            #self.graphWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            
            #Ball Widget Initialization
            self.ballWidget = BallWidget(self.width(), self.height())
            #self.ballWidget.resize(self.height() * (1.0/2) * (16.0/9) * (1.0/4) * (1/2), self.height() * (1.0/2))
            self.ballWidget.resize(10 ,400) 
            #self.ballWidget.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
            #Video initialization
            self.label = QLabel(self)
            #video Control toolbar initialization
            self.video_toolbar = QToolBar()
            # Video Slider setup
            #make a box under it for the orange line path
            self.video_slider = QSlider(Qt.Horizontal)
            self.video_slider.setMinimum(0.0)
            self.video_slider.setMaximum(round(self.thread.cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.thread.cap.get(cv2.CAP_PROP_FPS)))
            #Disable arrow keys controlling slider
            self.video_slider.setFocusPolicy(Qt.NoFocus)
            self.video_slider.valueChanged.connect(self.updateVideoFrame)
            self.video_slider.setToolTip("00:00")

            style = self.style()
            #Pause button setup
            self.pause_icon = QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause)
            self._pause_action = self.video_toolbar.addAction(self.pause_icon, "Pause")
            self._pause_action.setCheckable(True)

            # Make button background stay transparent
            pause_tool_button = self.video_toolbar.widgetForAction(self._pause_action)
            self._pause_action.triggered.connect(self.toggle_pause)
            pause_tool_button.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                }
                QToolButton:checked {
                    background-color: transparent;
                }
                QToolButton:pressed {
                    background-color: transparent;
                }
            """)

            
            #Link button setup
            link_icon = QIcon.fromTheme(QIcon.ThemeIcon.InsertLink)
            self._link_action = self.video_toolbar.addAction(link_icon, "Link")
            self._link_action.triggered.connect(self.toggle_link)
            self._link_action.setCheckable(True)
            self.link_pressed = False
            self.link_tool_button = self.video_toolbar.widgetForAction(self._link_action)
            self.link_tool_button.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                }
                QToolButton:checked {
                    background-color: lightcoral;
                }
                QToolButton:pressed {
                    background-color: transparent;
                }
            """)

            previous_step_icon = QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious)
            self._previous_step_action = self.video_toolbar.addAction(previous_step_icon, "Previous Estimated Footstep")
            self._previous_step_action.triggered.connect(self.previousStep)
            self._previous_tool_button = self.video_toolbar.widgetForAction(self._previous_step_action)
            self._previous_tool_button.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                }
                QToolButton:checked {
                    background-color: transparent;
                }
                QToolButton:pressed {
                    background-color: transparent;
                }
            """)

            self.current_step_viewing = 0
            next_step_icon = QIcon.fromTheme(QIcon.ThemeIcon.GoNext)
            self._next_step_action = self.video_toolbar.addAction(next_step_icon, "Next Estimated Footstep")
            self._next_step_action.triggered.connect(self.nextStep)
            self._next_tool_button = self.video_toolbar.widgetForAction(self._next_step_action)
            self._next_tool_button.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                }
                QToolButton:checked {
                    background-color: transparent;
                }
                QToolButton:pressed {
                    background-color: transparent;
                }
            """)


            # Global message box
            self.messagebox = QLineEdit(self)
            self.messagebox.setReadOnly(True)
            self.messagebox.setMinimumHeight(75)
            self.messagebox.setFocusPolicy(Qt.NoFocus)
            self.messagebox.setFont(QFont('Helvetica Neue', 18))
            self.messagebox.setAlignment(Qt.AlignCenter)
            self.messagebox.setText("Match the video progress bar with the red line, then link")

            
            #Instructions box
            self.instructions_box = QPlainTextEdit(self)
            self.instructions_box.setReadOnly(True)
            #self.instructions_box.resize(1000,600)
            #self.instructions_box.setFixedWidth(600)
            self.instructions_box.setStyleSheet("""
                QPlainTextEdit {
                    background-color: rgb(30, 30, 30);
                    color: rgb(65, 65, 65);
                    font: 14px;
                }
            """)
            self.instructions_box.insertPlainText("Match up the video slider with its appropriate graph position and link \n")
            self.instructions_box.insertPlainText("After linking control video and graph line using the video slider\n \n")
            self.instructions_box.insertPlainText("Controls: \n")
            self.instructions_box.insertPlainText("Reset Gif playback                            R \n")
            self.instructions_box.insertPlainText("Move graph line back                       Left Arrow\n")
            self.instructions_box.insertPlainText("Move graph line forward                  Right Arrow \n")
            self.instructions_box.insertPlainText("Moves graph line back slower          Shift +  Left Arrow\n")
            self.instructions_box.insertPlainText("Moves graph line forward faster      Shift + Right Arrow  \n")
            self.instructions_box.setFrameStyle(QFrame.NoFrame)
            #layout
            #controls
            control_layout = QHBoxLayout()
            control_layout.addWidget(self.video_slider)
            control_layout.addWidget(self.video_toolbar)
            #Add video and controls
            video_controls = QVBoxLayout()
            video_controls.addWidget(self.label)
            video_controls.addLayout(control_layout)
            #Add ball
            video_ball = QHBoxLayout()
            video_ball.addWidget(self.instructions_box, stretch=1)
            
            #video_ball.addStretch()
            video_ball.addLayout(video_controls, stretch=1)
            video_ball.addWidget(self.ballWidget, stretch=1)
            #video_ball.addStretch()
            #Add Message Bar
            message_video_ball = QVBoxLayout()
            message_video_ball.addWidget(self.messagebox)
            message_video_ball.addLayout(video_ball)
            #message_video_ball.addWidget(self.graphWidget)
            #Add Graph
            message_video_ball_graph = QVBoxLayout()
            message_video_ball_graph.addLayout(message_video_ball)
            message_video_ball_graph.addWidget(self.graphWidget)
            

            central_widget = QWidget()
            central_widget.setLayout(message_video_ball_graph)
            self.setCentralWidget(central_widget)
            

            self.pause_video_send.connect(self.thread.pause_video_received)
            self.resume_video_send.connect(self.thread.resume_video_received)
            self.reset_gif_send.connect(self.thread.reset_gif)
            #self.link

            print("Finished Initialization.")

        def getVideoHeightWidth(self, proportion=0.5, window_size=(1080,1920), primary_axis='height', aspect_ratio=16.0/9.0, max_secondary_proportion=0.8):
            #TODO FILL IN DOCSTRING
            """Reduces a video's dimensions when resizing window

            Args:
                proportion (float, optional): _description_. Defaults to 0.5.
                window_size (tuple, optional): _description_. Defaults to (1080,1920).
                primary_axis (str, optional): _description_. Defaults to 'height'.
                aspect_ratio (_type_, optional): _description_. Defaults to 16.0/9.0.
                max_secondary_proportion (float, optional): _description_. Defaults to 0.8.

            Returns:
                _type_: _description_
            """
            if (primary_axis == 'height'):
                primary_axis_index = 0
                secondary_axis_index = 1
            elif (primary_axis ==  'width'):
                primary_axis_index = 1
                secondary_axis_index = 0
            else:
                print('Did not understand axis, defaulting to height')
                primary_axis_index = 0
                secondary_axis_index = 1
            output_size = [0,0]
            # Primary is a proportion of the main window's primary
            output_size[primary_axis_index] = proportion * (window_size[primary_axis_index])
            # Secondary is similarly reduced (primary = width)by or increased (primary = height) by aspect ratio
            output_size[secondary_axis_index] = [aspect_ratio, 1.0/aspect_ratio][primary_axis_index] * output_size[primary_axis_index]
            # If new secondary is more than secondary prop % of the original secondary window size, resize according to the secondary proportion
            if output_size[secondary_axis_index] > max_secondary_proportion * window_size[secondary_axis_index]:
                output_size[secondary_axis_index] = max_secondary_proportion * window_size[secondary_axis_index]
                output_size[primary_axis_index] = [aspect_ratio,1.0/aspect_ratio][secondary_axis_index] * output_size[secondary_axis_index]
            return tuple(output_size)

        def update_image(self, gif_state): 
            #TODO FILL IN DOCSTRING
            """_summary_

            Args:
                gif_state (_type_): _description_
            """
            if(not self.pause_pressed):
                #Prev was 800,
                vid_size = self.getVideoHeightWidth(proportion = 0.8, window_size=(self.height(),self.width()))
                self.label.setPixmap(gif_state.pixmap.scaled(vid_size[0], vid_size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        def move_crosshair(self, gif_state):
            #TODO FILL IN DOCSTRING
            """_summary_

            Args:
                gif_state (_type_): _description_
            """
            if(not self.pause_pressed):
                # Move crosshair
                self.crosshair_v.setPos(self.crosshair_cursor.x() + gif_state.time)

                # Update Ball Position
                self.ballWidget.update_ball_position(self.csv_process.barXToY(self.crosshair_v.x()))

        def pause(self):
            #TODO FILL IN DOCSTRING
            """_summary_
            """
            self.pause_pressed = True
            self._pause_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart))
            self._pause_action.setText("Play")
            self.pause_video_send.emit()
            
        def resume(self):
            #TODO FILL IN DOCSTRING
            """_summary_
            """
            if self.pause_pressed:
                self.pause_pressed = False
                self._pause_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause))
                self._pause_action.setText("Pause")
                self.resume_video_send.emit()

        def nextStep(self):
            #TODO FILL IN DOCSTRING
            """_summary_
            """
            # 8 steps, max is 7
            if(self.link_pressed and self.current_step_viewing < len(self.csv_process.step_list) - 1):
                self.current_step_viewing += 1
                self.crosshair_cursor.setPos(self.csv_process.step_list[self.current_step_viewing])
                link_step_diff = self.csv_process.step_list[self.current_step_viewing] - self.linked_data_time # if step is 400 and link is 500 it will be -100
                self.video_slider.setValue(self.linked_video_pos + link_step_diff)
                self.updateVideoFrame()
                #self.messagebox.setText(f"Step: {self.current_step_viewing}")

        def previousStep(self):
            #TODO FILL IN DOCSTRING
            """_summary_
            """
            # 8 steps, max is 7
            if(self.link_pressed and self.current_step_viewing > 0):
                self.current_step_viewing -= 1
                self.crosshair_cursor.setPos(self.csv_process.step_list[self.current_step_viewing])
                link_step_diff = self.csv_process.step_list[self.current_step_viewing] - self.linked_data_time # if step is 400 and link is 500 it will be -100
                self.video_slider.setValue(self.linked_video_pos + link_step_diff)
                self.updateVideoFrame()
                #self.messagebox.setText(f"Step: {self.current_step_viewing}")

        
        def toggle_pause(self):
            #TODO FILL IN DOCSTRING
            """_summary_
            """
            if self._pause_action.isChecked():
                self.pause()
            else:
                self.resume()

        def keyPressEvent(self, event):
            #TODO FILL IN DOCSTRING
            """_summary_

            Args:
                event (_type_): _description_
            """
            if(not self.link_pressed):
                if event.key() == Qt.Key.Key_Left:
                    if event.modifiers() == Qt.ShiftModifier:
                        if((self.crosshair_cursor.x() - 0.02) >= 0):
                            self.crosshair_cursor.setPos(self.crosshair_cursor.x() - 0.02)
                    else:
                        if((self.crosshair_cursor.x() - 0.2) >= 0):
                            self.crosshair_cursor.setPos(self.crosshair_cursor.x() - 0.2)
                elif event.key() == Qt.Key.Key_Right:
                    if event.modifiers() == Qt.ShiftModifier:
                        self.crosshair_cursor.setPos(self.crosshair_cursor.x() + 0.02)
                    else:
                        self.crosshair_cursor.setPos(self.crosshair_cursor.x() + 0.2)
            if event.key() == Qt.Key.Key_R:
                self.reset_gif_send.emit()


        def toggle_link(self):
            #TODO FILL IN DOCSTRING
            """"
            """
            if self._link_action.isChecked():
                self.link()
            else:
                self.unlink()



        def link(self):
            #TODO FILL IN DOCSTRING
            """_summary_
            """
            # Linked data time is the data time that matches the video time
            self.linked_data_time = self.crosshair_cursor.x()
            self.linked_video_pos = self.video_slider.value()
            self.link_pressed = True
            self._link_action.setText("Unlink")
            self.messagebox.setText(f"Synced. Time difference = {round((self.linked_data_time - self.linked_video_pos), 2)} seconds")
            self.crosshair_cursor.setMovable(False)
            self.crosshair_cursor.setPen(self.cursor_pen_link)
            video_step_list = []
            print("Video steps:")
            for time in self.csv_process.step_list:
                link_step_diff = time - self.linked_data_time # if step is 400 and link is 500 it will be -100
                video_step_time = round(self.linked_video_pos + link_step_diff)
                if(math.floor(video_step_time / 60) < 0):
                    continue
                print(f"{math.floor(video_step_time / 60)}:{str(video_step_time % 60).rjust(2, '0')}  ") #TODO Consider making a helper funtion for MM:SS conversion
          
               

        def unlink(self):
            #TODO FILL IN DOCSTRING
            """_summary_
            """
            self.link_pressed = False
            self._link_action.setText("Link")
            self.messagebox.setText(f"Unsynced.")
            self.crosshair_cursor.setMovable(True)
            self.crosshair_cursor.setPen(self.cursor_pen)

        # Set Video to a frame
        def updateVideoFrame(self):
            #TODO FILL IN DOCSTRING
            """_summary_
            """
            
            self.thread.input_frame = (round(self.video_slider.value() * self.thread.cap.get(cv2.CAP_PROP_FPS)))
            self.video_slider.setToolTip(f"{int(self.video_slider.value() / 60)}:{str(self.video_slider.value() % 60).rjust(2,'0')}")
            if(self.link_pressed):
                self.crosshair_cursor.setPos(self.linked_data_time + (self.video_slider.value() - self.linked_video_pos))


    
        def closeEvent(self,event):
            #TODO FILL IN DOCSTRING
            """_summary_

            Args:
                event (_type_): _description_
            """
            self.thread.stop()
            event.accept()

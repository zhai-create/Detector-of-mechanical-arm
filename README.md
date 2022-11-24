# Detector-of-mechanical-arm

## Introduction
- Start running the program, and the GUI dialog box will pop up. The user is required to input the frame threshold and video path. If the video path entered by the user does not exist, the program will exit automatically after clicking the "OK" button; If the file path exists, click "OK" to continue the program.
- Select ROI area. Use the mouse to frame the ROI area, which represents the area to be detected in the current interface determined by the user. Press the "Enter" key to confirm the ROI area.
- Label the mechanical arm. Press the left mouse button to mark the two endpoints of the mechanical arm, draw a straight line through two points, and then press "Enter" to determine the position of the mechanical arm.
- Press the "Enter" key to start video detection. The upper left corner displays the video frame rate, and the lower part displays the motion status of the mechanical arm detected in the video, including "static", "upward shaking", and "downward shaking".
- If you want to end the detection in advance, you can press the "q" key to end the detection. When the video is played, the robot arm detection will also be ended.
- After video detection, the detected video will be saved in the current folder, and the file name is "out. avi".

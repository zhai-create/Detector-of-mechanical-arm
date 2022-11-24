import cv2 as cv
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import tkinter

class Detector(object):
    def __init__(self):
        self.k1 = 0  # 上一次判断的机械臂斜率
        self.ct = 0  #帧数
        self.ROI = (0,0,0,0) #ROI兴趣区域
        self.fps = 0 #帧率
        self.label_points = [] #标定线对应的端点集合
        self.result = "机械臂静止" #当前判断的运动结果
        self.tolerent = 0.001 #误差容忍度
        self.framegap = 10 #帧数阈值
        self.file_name = ""
        self.x1, self.y1, self.x2, self.y2 = (0,0,0,0) #检测线的两个端点

    def draw_label_line(self, event, x, y, flags, img):
        # 用于绘制标定线
        if event == cv.EVENT_LBUTTONDOWN:  # 左键点击，选择点
            self.label_points.append((x, y)) #每触发一次左键，将标定点向label_points中添加一个
            if len(self.label_points) > 0:
                # 将label_points中的最后一点画出来
                cv.circle(img, self.label_points[-1], 3, (0, 0, 255), -1)
            if len(self.label_points) > 1:
                # 画线
                for i in range(len(self.label_points) - 1):
                    cv.circle(img, self.label_points[i], 3, (0, 0, 255), -1)
                    cv.line(img=img, pt1=self.label_points[i], pt2=self.label_points[i + 1], color=(255, 0, 0), thickness=2)
            cv.imshow('Jiggle detection of mechanical arm', img)
        if event == cv.EVENT_RBUTTONDOWN:  # 右键点击，取消最近一次选择的点
            self.label_points.pop()

    def detect_line(self, img,x,y,w,h):
        #检测机械臂
        gray = cv.cvtColor(np.array(img), cv.COLOR_BGR2GRAY) #将RGB图转换为灰度图
        lines = cv.HoughLines(cv.Canny(gray, 10, 200)[y:y + h, x:x + w], 1, np.pi / 180, 50) #先使用Canny算子寻找边缘，在使用霍夫变换寻找直线
        # cv.imshow("result2", cv.Canny(gray, 10, 200)[y:y + h, x:x + w])
        for line in lines:
            # 沿着左上角的原点，作目标直线的垂线得到长度和角度
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            # 计算检测直线的两端点
            x1 = int(x0 + 60 * (-b)) + x
            y1 = int(y0 + 60 * (a)) + y
            x2 = int(x0 - 60 * (-b)) + x
            y2 = int(y0 - 60 * (a)) + y
            # 计算斜率
            k = (y2 - y1) / (x2 - x1)
            return  k, x1, y1, x2, y2

    def add(self, img, string, position,font_size):
        #添加文字
        font = ImageFont.truetype("font/simsun.ttc", font_size)
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        draw.text(position, string, font=font, fill=(0, 0, 255))
        bk_img = np.array(img_pil)
        return bk_img


    def set_GUI(self):
        #设置GUI的函数
        def GUI_get_text():
            #获取输入框的帧数阈值
            self.framegap = int(accountE.get())

        def GUI_get_text2():
            #获取输入框的文件名
            self.file_name = filenameE.get()

        root = tkinter.Tk()
        root.geometry('300x100')  #改变GUI窗口大小
        root.title("机械臂检测")

        #输入帧数阈值的对话框
        accountL = tkinter.Label(root, text="帧数阈值")  # account标签
        accountL.grid(row=1)
        accountE = tkinter.Entry(root)
        accountE.insert(0, "")
        accountE.grid(row=1, column=1)

        # 文件名的对话框
        filenameL = tkinter.Label(root, text="视频路径")  # account标签
        filenameL.grid(row=2)
        filenameE = tkinter.Entry(root)
        filenameE.insert(0, "")
        filenameE.grid(row=2, column=1)
        frequency = tkinter.Button(root, text='确认', command=lambda: [GUI_get_text(), GUI_get_text2(), root.destroy()])
        frequency.grid(row=3)
        root.mainloop()



    def detect(self): #视频检测主体
        self.set_GUI()  #调用GUI
        cap = cv.VideoCapture(self.file_name)

        # Define the codec and create VideoWriter object
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        out = cv.VideoWriter('output.avi', fourcc, 25, (1000, 500))

        while True:
            success, frame = cap.read() #逐帧读入
            if success:
                frame = cv.resize(frame, (1000, 500)) #改变每一帧的大小，使画面适应于电脑屏幕界面
                if self.ct == 0:
                    # 如果当前是第一帧，则执行框选ROI的操作和标定直线的操作
                    roi = cv.selectROI(windowName="Jiggle detection of mechanical arm", img=frame, showCrosshair=True, fromCenter=False)
                    self.ROI = roi
                    cv.setMouseCallback('Jiggle detection of mechanical arm', self.draw_label_line, frame)
                    cv.waitKey(-1)
                x, y, w, h = self.ROI
                # 绘制ROI矩形
                cv.rectangle(img=frame, pt1=(x, y), pt2=(x + w, y + h), color=(0, 0, 255), thickness=2)
                #绘制标定直线
                if (len(self.label_points) > 1):
                    for i in range(len(self.label_points) - 2, len(self.label_points)):
                        cv.circle(frame, self.label_points[i], 3, (0, 0, 255), -1)  # x ,y 为鼠标点击地方的坐标
                    cv.line(img=frame, pt1=self.label_points[-2], pt2=self.label_points[-1], color=(255, 0, 0), thickness=2)

                k, self.x1, self.y1, self.x2, self.y2 = self.detect_line(frame, x, y, w, h)

                if (self.ct == 0):
                    self.k1 = k

                if (self.ct!=0 and (self.ct%self.framegap) ==0):
                    #如果是第一帧，则不进行晃动或静止的判断，直接赋值为静止
                    #如果当前帧数是framegap的整数倍，则进行运动检测

                    if (k > self.k1+self.tolerent):
                        self.result = "向下晃动"
                    elif (k<self.k1-self.tolerent):
                        self.result = "向上晃动"
                    else:
                        self.result = "机械臂静止"
                    self.k1 = k
                # if (self.ct == 0):
                #     #如果是第一帧，则只进行机械臂检测，不进行晃动判断
                #    self.k1, self.x1, self.y1, self.x2, self.y2 = self.detect_line(frame, x, y, w, h)
                cv.line(frame, (self.x1, self.y1), (self.x2, self.y2), (0, 0, 255), 1)  #绘制检测出的直线
                if (self.result == "机械臂静止"):
                    frame = self.add(frame, self.result, (200, 380), font_size=30) # 为当前帧添加运动检测结果
                else:
                    frame = self.add(frame, self.result, (50, 380), font_size=30)  # 为当前帧添加运动检测结果

                self.fps = cap.get(cv.CAP_PROP_FPS)
                frame = self.add(frame, "FPS:" + str(int(self.fps)), (0, 0), font_size=30) #为当前帧添加帧率
                out.write(frame)
                cv.namedWindow('Jiggle detection of mechanical arm', 0)
                cv.imshow('Jiggle detection of mechanical arm', frame)
                # key = cv.waitKey(int(1000/25)) & 0xFF
                key = cv.waitKey(5) & 0xFF
                # key = cv.waitKey(5)
                if key == ord('q'):
                    print('手动停止')
                    break
                self.ct += 1
            else:
                print(self.file_name)
                print('播放完成')
                break
        cap.release()
        out.release()
        cv.destroyAllWindows()

if __name__=="__main__":
    detector = Detector()
    detector.detect()


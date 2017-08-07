#coding=utf-8
import numpy as np
import cv2
import RPi.GPIO as GPIO
import time
import threading
import signal  
import atexit
import random


#绿色区域
global LG
global UG
LG =np.array([12,0,0])
UG =np.array([72,124,164])
'''
步进电机类
'''
class stepperMotor(object):

    time=0.000002                           #1/2脉冲时间
    def __init__(self,DIR1,STEP1,EN1,DIR2,STEP2,EN2,SERVO_PIN):
        self.flag=0
        self.dir1=DIR1
        self.step1=STEP1
        self.en1=EN1
        self.dir2=DIR2
        self.step2=STEP2
        self.en2=EN2
        self.C_servo=servo(SERVO_PIN)
        output=[self.dir1,self.step1,self.en1,self.dir2,self.step2,self.en2]
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(output,GPIO.OUT)
        

    def x_add(self,data):
        T=(data)*1000
        GPIO.output(self.en1,GPIO.LOW)
        GPIO.output(self.en2,GPIO.LOW)
        GPIO.output(self.dir1,GPIO.HIGH)
        GPIO.output(self.dir2,GPIO.HIGH)
        for i in range(0,int(T)):
            GPIO.output(self.step1,GPIO.HIGH)
            GPIO.output(self.step2,GPIO.HIGH)
            time.sleep(self.time)
            GPIO.output(self.step1,GPIO.LOW)
            GPIO.output(self.step2,GPIO.LOW)
            time.sleep(self.time)
        GPIO.output(self.en1,GPIO.HIGH)
        GPIO.output(self.dir1,GPIO.LOW)
        GPIO.output(self.step1,GPIO.LOW)

        GPIO.output(self.en2,GPIO.HIGH)
        GPIO.output(self.dir2,GPIO.LOW)
        GPIO.output(self.step2,GPIO.LOW)

    def y_add(self,data):
        T=(data)*1000
        GPIO.output(self.en1,GPIO.LOW)
        GPIO.output(self.en2,GPIO.LOW)
        GPIO.output(self.dir1,GPIO.HIGH)
        GPIO.output(self.dir2,GPIO.LOW)
        for i in range(0,int(T)):
            GPIO.output(self.step1,GPIO.HIGH)
            GPIO.output(self.step2,GPIO.HIGH)
            time.sleep(self.time)
            GPIO.output(self.step1,GPIO.LOW)
            GPIO.output(self.step2,GPIO.LOW)
            time.sleep(self.time)
        GPIO.output(self.en1,GPIO.HIGH)
        GPIO.output(self.dir1,GPIO.LOW)
        GPIO.output(self.step1,GPIO.LOW)

        GPIO.output(self.en2,GPIO.HIGH)
        GPIO.output(self.dir2,GPIO.LOW)
        GPIO.output(self.step2,GPIO.LOW)

    def x_reduce(self,data):
        T=(data)*1000
        GPIO.output(self.en1,GPIO.LOW)
        GPIO.output(self.en2,GPIO.LOW)
        GPIO.output(self.dir1,GPIO.LOW)
        GPIO.output(self.dir2,GPIO.LOW)
        for i in range(0,int(T)):
            GPIO.output(self.step1,GPIO.HIGH)
            GPIO.output(self.step2,GPIO.HIGH)
            time.sleep(self.time)
            GPIO.output(self.step1,GPIO.LOW)
            GPIO.output(self.step2,GPIO.LOW)
            time.sleep(self.time)
        GPIO.output(self.en1,GPIO.HIGH)
        GPIO.output(self.dir1,GPIO.LOW)
        GPIO.output(self.step1,GPIO.LOW)

        GPIO.output(self.en2,GPIO.HIGH)
        GPIO.output(self.dir2,GPIO.LOW)
        GPIO.output(self.step2,GPIO.LOW)

    def y_reduce(self,data):
        T=(data)*1000
        GPIO.output(self.en1,GPIO.LOW)
        GPIO.output(self.en2,GPIO.LOW)
        GPIO.output(self.dir1,GPIO.LOW)
        GPIO.output(self.dir2,GPIO.HIGH)
        for i in range(0,int(T)):
            GPIO.output(self.step1,GPIO.HIGH)
            GPIO.output(self.step2,GPIO.HIGH)
            time.sleep(self.time)
            GPIO.output(self.step1,GPIO.LOW)
            GPIO.output(self.step2,GPIO.LOW)
            time.sleep(self.time)
        GPIO.output(self.en1,GPIO.HIGH)
        GPIO.output(self.dir1,GPIO.LOW)
        GPIO.output(self.step1,GPIO.LOW)

        GPIO.output(self.en2,GPIO.HIGH)
        GPIO.output(self.dir2,GPIO.LOW)
        GPIO.output(self.step2,GPIO.LOW)

    def init(self):
        self.y_add(0.5)
        time.sleep(1)
        self.x_reduce(0.5)
        time.sleep(1)
        self.x_reduce(11)
        time.sleep(1)


    def play(self,y,x):
        self.x_add(x+3)
        self.y_add(y)
        if self.flag==0:
            self.C_servo.set(34)
            self.flag=1
        else:
            self.C_servo.set(90)
            self.flag=0
        self.x_reduce(x+3)
        self.y_reduce(y)
        

class servo(object):

    def __init__(self,pin):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(pin,GPIO.OUT) 
        self.p = GPIO.PWM(pin,50)                   #50HZ  
        self.p.start(0)
        self.set(90)

    def set(self,angle):
        self.p.ChangeDutyCycle(2.5+10*angle/180)    #设置转动角度  
        time.sleep(2)                               #等待2s周期结束  
        self.p.ChangeDutyCycle(0)                   #归零信号  


'''
五子棋类
'''
class Gobang(object):
    chessBlue=[]
    chess=[]
    Prepare1=[]
    Prepare=[]
    rule=[]
    countBlue0=0
    countBlue1=0
    Random=False
    
    def getMouseColor(self,event,x,y,flags,param):
        global LG
        global UG
        if event==cv2.EVENT_LBUTTONDOWN:
            hG=hsv_img[x,y][0]
            sG=hsv_img[x,y][1]
            vG=hsv_img[x,y][2]
            LG=np.array([hG-30,sG-90,vG-90])
            UG=np.array([hG+30,sG+90,vG+90])
            print("LG:",LG,"\nUG:",UG)
            print("hG:",hG,"sG:",sG,"vG:",vG)
        return 0
    def __init__(self):
        self.checkerboard_init()#初始化数据
        #self.arm=extraman(37,35,33,40,38,36,31)  #DIR1,STEP1,EN1,DIR2,STEP2,EN2,SERVO_PIN
        self.arm=stepperMotor(37,35,33,40,38,36,31) 	#DIR1(37),STEP1(35),EN1(33),DIR2,STEP2,EN2,SERVO_PIN0
    def add_green(self,x,y):
        self.chess[x][y]=2
        self.arm.play(x,y)
        #print("add_green",x,y)

    def checkerboard_init(self):
        self.chessBlue=[([0]*9)for i in range(9)]
        self.chess=[([0]*9)for i in range(9)]
        self.Prepare1=[([0]*9)for i in range(9)]
        self.Prepare=[([0]*9)for i in range(9)]
        self.t=0
        #print("checkerboard_init")

    def chess_board(self):
        cv2.namedWindow('src_img')
        #蓝色区域
        hVal2=111
        sVal2=157
        vVal2=127
        global hsv_img      
        video_cap=cv2.VideoCapture(0)
        
        while(video_cap.isOpened()):
            ret_data,src_img=video_cap.read()                                   #获取摄像头图像
            src_img=cv2.resize(src_img,(0,0),fx=0.4,fy=0.4)
            hsv_img= cv2.cvtColor(src_img,cv2.COLOR_BGR2HSV)                     #转化成HSV图像
            #查找绿色部分，定位棋盘
            #print(LG,UG)
            green_mask=cv2.inRange(hsv_img,LG,UG)                               #查找绿色部分
            ret,binary=cv2.threshold(green_mask,50,255,cv2.THRESH_BINARY)       #图像二值化
            contours,hierarchy=cv2.findContours(binary,cv2.RETR_TREE,\
                                        cv2.CHAIN_APPROX_SIMPLE)                #查找轮廓
            contours_poly=contours
            for i in range(0,len(contours)-1):
                contours_poly[i]=cv2.approxPolyDP(contours[i],25,True)          #轮廓近似

            if len(contours_poly)>0:
                if len(contours_poly)>1:
                    i=len(contours_poly)-1

                    '''
                    查找最大面积的轮廓，并将该轮廓放在第一位
                    '''
                    while(i):
                        if cv2.contourArea(contours_poly[i])>cv2.contourArea(contours_poly[i-1]):
                            temp=contours_poly[i-1]
                            contours_poly[i-1]=contours_poly[i]
                            contours_poly[i]=temp
                        i=i-1

                if(len(contours_poly[0])==4):
                    poly=contours_poly[0]
                    cbPoint=[]

                    '''
                    从轮廓中找出4个坐标点
                    '''
                    if (poly[0][0][0]+poly[0][0][1])<(poly[1][0][0]+poly[1][0][1]):
                        cbPoint.insert(0,(poly[0][0][0],poly[0][0][1]))
                        cbPoint.insert(1,(poly[1][0][0],poly[1][0][1]))
                        cbPoint.insert(2,(poly[2][0][0],poly[2][0][1]))
                        cbPoint.insert(3,(poly[3][0][0],poly[3][0][1]))
                    else:
                        cbPoint.insert(0,(poly[1][0][0],poly[1][0][1]))
                        cbPoint.insert(1,(poly[2][0][0],poly[2][0][1]))
                        cbPoint.insert(2,(poly[3][0][0],poly[3][0][1]))
                        cbPoint.insert(3,(poly[0][0][0],poly[0][0][1]))

                    '''
                    确定变换后的坐标轴
                    '''
                    cbPoint2=[]
                    cbPoint2.insert(0,[0,0])
                    cbPoint2.insert(1,[0,300])
                    cbPoint2.insert(2,[300,300])
                    cbPoint2.insert(3,[300,0])
                    cbPointTemp=[]
                    cbPointTemp.insert(0,[cbPoint[0][0],cbPoint[0][1]])
                    cbPointTemp.insert(1,[cbPoint[1][0],cbPoint[1][1]])
                    cbPointTemp.insert(2,[cbPoint[2][0],cbPoint[2][1]])
                    cbPointTemp.insert(3,[cbPoint[3][0],cbPoint[3][1]])
                    cbPointA=np.float32(cbPointTemp)
                    cbPointB=np.float32(cbPoint2)
                
                    '''
                    变换图形
                    '''
                    perspective=cv2.getPerspectiveTransform(cbPointA,cbPointB)
                    self.perspective_img=cv2.warpPerspective(src_img,perspective,(300,300))             #变换透视
                    self.perspective_img=cv2.medianBlur(self.perspective_img,9)                         #低通滤波平滑图像，防止干扰
                    perspective_hsv_img=cv2.cvtColor(self.perspective_img,cv2.COLOR_BGR2HSV)            #转换成HSV模型
                

                    '''
                    寻找棋盘坐标点
                    '''
                    self.cblPoint12=[]
                    self.cblPoint23=[]
                    self.cblPoint34=[]
                    self.cblPoint41=[]
                    for i in range(0,9):
                        l12x=cbPoint2[0][0]+((cbPoint2[1][0]-cbPoint2[0][0])/10)*(1+i)
                        l12y=cbPoint2[0][1]+((cbPoint2[1][1]-cbPoint2[0][1])/10)*(1+i)
                        self.cblPoint12.insert(i,(int(l12x),int(l12y)))
                        l23x=cbPoint2[1][0]+((cbPoint2[2][0]-cbPoint2[1][0])/10)*(1+i)
                        l23y=cbPoint2[1][1]+((cbPoint2[2][1]-cbPoint2[1][1])/10)*(1+i)
                        self.cblPoint23.insert(i,(int(l23x),int(l23y)))
                        l34x=cbPoint2[3][0]+((cbPoint2[2][0]-cbPoint2[3][0])/10)*(1+i)
                        l34y=cbPoint2[3][1]+((cbPoint2[2][1]-cbPoint2[3][1])/10)*(1+i)
                        self.cblPoint34.insert(i,(int(l34x),int(l34y)))
                        l41x=cbPoint2[0][0]+((cbPoint2[3][0]-cbPoint2[0][0])/10)*(1+i)
                        l41y=cbPoint2[0][1]+((cbPoint2[3][1]-cbPoint2[0][1])/10)*(1+i)
                        self.cblPoint41.insert(i,(int(l41x),int(l41y)))
                        cv2.line(self.perspective_img,
                                 self.cblPoint12[i],self.cblPoint34[i],(0,0,255),2,8)
                        cv2.line(self.perspective_img,
                                 self.cblPoint23[i],self.cblPoint41[i],(0,0,255),2,8)

                    '''
                    寻找所有坐标轴交叉点的上颜色是否有蓝色
                    '''
                    for i in range(0,9):
                        data=perspective_hsv_img[self.cblPoint12[i][1]]
                        for j in range(0,9):
                            h=data[self.cblPoint41[j][0]][0]
                            s=data[self.cblPoint41[j][0]][1]
                            v=data[self.cblPoint41[j][0]][2]
                            if h>(hVal2-20)and h<(hVal2+20)\
                                and s>(sVal2-60)and s<(sVal2+60)\
                                and v>(vVal2-60)and v<(vVal2+60):
                                self.chessBlue[i][j]=1
                                self.chess[i][j]=1
                            else:
                                self.chessBlue[i][j]=0
                    self.chessAI()

                    cv2.imshow("self.perspective_img",self.perspective_img)

                cv2.imshow("src_img",src_img)
                cv2.setMouseCallback('src_img',self.getMouseColor)
                cv2.imshow("green_mask",green_mask)
            if cv2.waitKey(1) & (0xFF)==ord('9'):
                break

    def chessAI(self):
        adjust=0
        '''
        判断是否有五子相连的情况
        '''
        i=0;
        while(i<9 and adjust==0):
            j=0
            while(j<9 and adjust==0):
                if(self.chess[i][j]==2)and(adjust==0):
                    if i>5:
                        A=0
                    else:
                        A=(i+4<9)and(self.chess[i+1][j]==2)and(self.chess[i+2][j]==2)and(self.chess[i+3][j]==2)and(self.chess[i+4][j]==2)
                    if j>5:
                        B=0
                    else:
                        B=(i+4<9)and(self.chess[i][j+1]==2)and(self.chess[i][j+2]==2)and(self.chess[i][j+3]==2)and(self.chess[i][j+4]==2)
                    if i>5 or j>5:
                        C=0
                    else:
                        C=(i+4<9)and(j+4<9)and(self.chess[i+1][j+1]==2)and(self.chess[i+2][j+2]==2)and(self.chess[i+3][j+3]==2)and(self.chess[i+4][j+4]==2)
                    if i>5 or j<4:
                        D=0
                    else:
                        D=(i+4<9)and(j-4>=0)and(self.chess[i+1][j-1]==2)and(self.chess[i+2][j-2]==2)and(self.chess[i+3][j-3]==2)and(self.chess[i+4][j-4]==2)
                    if(A or B or C or D):
                        #do something
                        print(("G_win"))
                        adjust=1

                if (self.chessBlue[i][j]==1):
                    if i>5:
                        A=0
                    else:
                        A=(i+4<9)and(self.chess[i+1][j]==1)and(self.chess[i+2][j]==1)and(self.chess[i+3][j]==1)and(self.chess[i+4][j]==1)
                    if j>5:
                        B=0
                    else:
                        B=(i+4<9)and(self.chess[i][j+1]==1)and(self.chess[i][j+2]==1)and(self.chess[i][j+3]==1)and(self.chess[i][j+4]==1)
                    if i>5 or j>5:
                        C=0
                    else:
                        C=(i+4<9)and(j+4<9)and(self.chess[i+1][j+1]==1)and(self.chess[i+2][j+2]==1)and(self.chess[i+3][j+3]==1)and(self.chess[i+4][j+4]==1)
                    if i>5 or j<4:
                        D=0
                    else:
                        D=(i+4<9)and(j-4>=0)and(self.chess[i+1][j-1]==1)and(self.chess[i+2][j-2]==1)and(self.chess[i+3][j-3]==1)and(self.chess[i+4][j-4]==1)
                    if(A or B or C or D):
                        #do something
                        print("B_win")
                        adjust=1
                j=j+1
            i=i+1
            
        self.countBlue1=0                       #蓝色棋子数量初始化值为0        
        for i in range(0,9):
            for j in range(0,9):                #遍历棋盘，获取蓝色棋子数量
                if(self.chessBlue[i][j]==1):
                    self.countBlue1=self.countBlue1+1
      
        if self.countBlue1==0:                  #如果没有蓝色棋子,棋盘初始化
            if(self.t>8):
                self.countBlue0=0
                self.checkerboard_init()
            self.t=self.t+1

        elif(self.countBlue1-self.countBlue0==1)and(adjust==0):
            for i in range(0,9):
                for j in range(0,9):
                    self.Prepare[i][j]=0        #清空计分
            
            c0=[1,1,1,1,3] #4-5
            self.chessDecisionGreen(c0,950)
            self.chessDecisionBlue(c0,900)
            c1=[1,1,1,3,1] #3-5
            self.chessDecisionGreen(c1,950)
            self.chessDecisionBlue(c1,900)
            c2=[3,1,1,1,0] #3-4
            c2a=[3,1,1,1,0,2] 
            c3=[2,1,1,1,3,0]
            self.chessDecisionGreen(c2,540)
            self.chessDecisionGreen(c2a,540)
            self.chessDecisionGreen(c3,40)
            self.chessDecisionBlue(c2,560)
            self.chessDecisionBlue(c2a,545)
            self.chessDecisionBlue(c3,50)

            c4=[1,1,3,1,1] #2-5
            self.chessDecisionGreen(c4,950)
            self.chessDecisionBlue(c4,900)

            c5=[0,1,1,3,1,0]#2-4
            c6=[2,1,1,3,1,3]
            c7=[0,1,1,3,1,2]
            self.chessDecisionGreen(c5,500)
            self.chessDecisionGreen(c6,40)
            self.chessDecisionGreen(c7,70)
            self.chessDecisionBlue(c5,500)
            self.chessDecisionBlue(c6,40)
            self.chessDecisionBlue(c7,70)

            c8=[0,3,1,1,0]#2-3
            c8a=[3,1,1,0,0]
            c9=[2,1,1,3,0]
            self.chessDecisionGreen(c8,80)
            self.chessDecisionGreen(c8a,30)
            self.chessDecisionGreen(c9,10)
            self.chessDecisionBlue(c8,80)
            self.chessDecisionBlue(c8a,30)
            self.chessDecisionBlue(c9,10)
            c10=[0,1,3,1,0] #1-3
            c11=[2,1,3,1,0]
            self.chessDecisionGreen(c10,35)
            self.chessDecisionGreen(c11,10)
            self.chessDecisionBlue(c10,30)
            self.chessDecisionBlue(c11,10)

            c12=[0,3,3,1,0] #1-2
            c13=[0,0,3,1,2]
            self.chessDecisionGreen(c12,3)
            self.chessDecisionGreen(c13,2)
            self.chessDecisionBlue(c12,2)
            self.chessDecisionBlue(c13,1)

            c14=[0,1,3,3,1] #1-2-4
            c15=[0,1,0,1,3,0]
            self.chessDecisionGreen(c14,14)
            self.chessDecisionGreen(c15,14)
            self.chessDecisionBlue(c14,17)
            self.chessDecisionBlue(c15,17)

            c16=[0,1,1,0,3,0] #2-2-4
            self.chessDecisionGreen(c16,20)
            self.chessDecisionBlue(c16,20)

            c17=[0,1,1,0,3,1] #2-2-5
            c17a=[0,1,1,3,0,1] #2-3-5
            self.chessDecisionGreen(c17,20)
            self.chessDecisionGreen(c17,20)
            self.chessDecisionBlue(c17,20)
            self.chessDecisionBlue(c17,20)
            c18=[1,1,1,0,3] #3-3-5
            self.chessDecisionGreen(c18,13)
            self.chessDecisionBlue(c18,13)
            #self.chessDecisionBlue2x()
            #print("prepare:",self.Prepare)
            max=x=y=0
            for i in range(0,9):
                for j in range(0,9):
                    if(self.Prepare[i][j]>max):
                        max=self.Prepare[i][j]
            for i in range(0,9):
                for j in range(0,9):
                    if(self.Prepare[i][j]==max):
                        if((i-4)**2+(j-4)**2 < (x-4)**2+(y-4)**2 ):
                            x=i;y=j
                        if((i-4)**2+(j-4)**2 == (x-4)**2+(y-4)**2 ):
                            if(random.randint(0,2)==1):
                                x=i;y=j
            
            self.add_green(x,y)
            self.countBlue0=self.countBlue1

        #创建一个矩形，来让我们在图片上写文字，参数依次定义了文字类型，高，宽，字体厚度等
        font = cv2.FONT_HERSHEY_SIMPLEX
        for i in range(0,9):
            for j in range(0,9):       
                if(self.chess[i][j]==2):
                    cv2.circle(self.perspective_img,(self.cblPoint41[j][0],\
                                                     self.cblPoint12[i][1]),15,(255,255,0),-1)
                if(self.chessBlue[i][j]==1):
                    cv2.circle(self.perspective_img,(self.cblPoint41[j][0],\
                                                     self.cblPoint12[i][1]),15,(255,0,0),-1)
                if(self.Prepare[i][j]!=0):
                    cv2.putText(self.perspective_img,str(self.Prepare[i][j]),\
                            (self.cblPoint41[j][0]-8,self.cblPoint12[i][1]+8),\
                            font, 0.5,(0,0,0),2)  

    def chessDecisionBlue(self,a,Count):
        Num=len(a)
        for i in range(0,9):
            for j in range(0,9-Num+1):
                l=j
                for k in range(0,Num):
                    if ((a[k]==0)and(self.chess[i][l]==0))or\
                        ((a[k]==1)and(self.chess[i][l]==1))or\
                        ((a[k]==2)and(self.chess[i][l]==2))or\
                        ((a[k]==3)and(self.chess[i][l]==0)):
                        if (k==Num-1):
                            for m in range(0,Num):
                                if a[m]==3:
                                    self.Prepare[i][j+m]=self.Prepare[i][j+m]+Count
                        l=l+1
                    else:
                        break

                l=j
                k=Num-1
                while(k>=0):
                    if((a[k]==0)and(self.chess[i][l]==0))or\
                    ((a[k]==1)and(self.chess[i][l]==1))or\
                    ((a[k]==2)and(self.chess[i][l]==2))or\
                    ((a[k]==3)and(self.chess[i][l]==0)):
                        if k==0:
                            for m in range(0,Num):
                                if (a[m]==3):
                                    self.Prepare[i][j+(Num-1-m)]=self.Prepare[i][j+(Num-1-m)]+Count
                        l=l+1
                    else:
                        break
                    k=k-1


                l=j
                for k in range(0,Num):
                    if((a[k]==0)and(self.chess[l][i]==0))or\
                    ((a[k]==1)and(self.chess[l][i]==1))or\
                    ((a[k]==2)and(self.chess[l][i]==2))or\
                    ((a[k]==3)and(self.chess[l][i]==0)):
                        if k==Num-1:
                            for m in range(0,Num):
                                if (a[m]==3):
                                    self.Prepare[j+m][i]=self.Prepare[j+m][i]+Count
                        l=l+1
                    else:
                        break

                l=j
                k=Num-1
                while(k>=0):
                    if((a[k]==0)and(self.chess[l][i]==0))or\
                    ((a[k]==1)and(self.chess[l][i]==1))or\
                    ((a[k]==2)and(self.chess[l][i]==2))or\
                    ((a[k]==3)and(self.chess[l][i]==0)):
                        if k==0:
                            for m in range(0,Num):
                                if (a[m]==3):
                                    self.Prepare[j +(Num-1-m)][i]=self.Prepare[j +(Num-1-m)][i]+Count
                        l=l+1
                    else:
                        break
                    k=k-1
        for i in range(0,9-Num+1):
            for j in range(0,9-Num+1):
                l=j
                n=i
                for k in range(0,Num):
                    if((a[k]==0)and(self.chess[n][l]==0))or\
                    ((a[k]==1)and(self.chess[n][l]==1))or\
                    ((a[k]==2)and(self.chess[n][l]==2))or\
                    ((a[k]==3)and(self.chess[n][l]==0)):
                        if(k==Num-1):
                            for m in range(0,Num):
                                if(a[m]==3):
                                    self.Prepare[i+m][j+m]=self.Prepare[i+m][j+m]+Count
                        l=l+1
                        n=n+1
                    else:
                        break

                l=j
                n=i
                k=Num-1
                while(k>=0):
                    if((a[k]==0)and(self.chess[n][l]==0))or\
                    ((a[k]==1)and(self.chess[n][l]==1))or\
                    ((a[k]==2)and(self.chess[n][l]==2))or\
                    ((a[k]==3)and(self.chess[n][l]==0)):
                        if k==0:
                            for m in range(0,Num):
                                if a[m]==3:
                                    self.Prepare[i+(Num-1-m)][j+(Num-1-m)]=self.Prepare[i+(Num-1-m)][j+(Num-1-m)]+Count
                        l=l+1
                        n=n+1
                    else:
                        break
                    k=k-1
        i=8
        while(i>=Num-1):
            for j in range(0,9-Num+1):
                l=j
                n=i
                for k in range(0,Num):
                    if((a[k]==0)and(self.chess[n][l]==0))or\
                    ((a[k]==1)and(self.chess[n][l]==1))or\
                    ((a[k]==2)and(self.chess[n][l]==2))or\
                    ((a[k]==3)and(self.chess[n][l]==0)):
                        if(k==Num-1):
                            for m in range(0,Num):
                                if(a[m]==3):
                                    self.Prepare[i-m][j+m]=self.Prepare[i-m][j+m]+Count
                        l=l+1
                        n=n-1
                    else:
                        break

                l=j
                n=i
                k=Num-1
                while(k>=0):
                    if((a[k]==0)and(self.chess[n][l]==0))or\
                    ((a[k]==1)and(self.chess[n][l]==1))or\
                    ((a[k]==2)and(self.chess[n][l]==2))or\
                    ((a[k]==3)and(self.chess[n][l]==0)):
                        if k==0:
                            for m in range(0,Num):
                                if a[m]==3:
                                    self.Prepare[i-(Num-1-m)][j+(Num-1-m)]=self.Prepare[i-(Num-1-m)][j+(Num-1-m)]+Count
                        l=l+1
                        n=n-1
                    else:
                        break
                    k=k-1
            i=i-1

    def chessDecisionGreen(self,a,Count):
        Num=len(a)
        for i in range(0,9):
            for j in range(0,9-Num+1):
                l=j
                for k in range(0,Num):
                    if ((a[k]==0)and(self.chess[i][l]==0))or\
                        ((a[k]==1)and(self.chess[i][l]==2))or\
                        ((a[k]==2)and(self.chess[i][l]==1))or\
                        ((a[k]==3)and(self.chess[i][l]==0)):
                        if (k==Num-1):
                            for m in range(0,Num):
                                if a[m]==3:
                                    self.Prepare[i][j+m]=self.Prepare[i][j+m]+Count
                        l=l+1
                    else:
                        break

                l=j
                k=Num-1
                while(k>=0):
                    if((a[k]==0)and(self.chess[i][l]==0))or\
                    ((a[k]==1)and(self.chess[i][l]==2))or\
                    ((a[k]==2)and(self.chess[i][l]==1))or\
                    ((a[k]==3)and(self.chess[i][l]==0)):
                        if k==0:
                            for m in range(0,Num):
                                if (a[m]==3):
                                    self.Prepare[i][j+(Num-1-m)]=self.Prepare[i][j+(Num-1-m)]+Count
                        l=l+1
                    else:
                        break
                    k=k-1


                l=j
                for k in range(0,Num):
                    if((a[k]==0)and(self.chess[l][i]==0))or\
                    ((a[k]==1)and(self.chess[l][i]==2))or\
                    ((a[k]==2)and(self.chess[l][i]==1))or\
                    ((a[k]==3)and(self.chess[l][i]==0)):
                        if k==Num-1:
                            for m in range(0,Num):
                                if (a[m]==3):
                                    self.Prepare[j+m][i]=self.Prepare[j+m][i]+Count
                        l=l+1
                    else:
                        break

                l=j
                k=Num-1
                while(k>=0):
                    if((a[k]==0)and(self.chess[l][i]==0))or\
                    ((a[k]==1)and(self.chess[l][i]==2))or\
                    ((a[k]==2)and(self.chess[l][i]==1))or\
                    ((a[k]==3)and(self.chess[l][i]==0)):
                        if k==0:
                            for m in range(0,Num):
                                if (a[m]==3):
                                    self.Prepare[j +(Num-1-m)][i]=self.Prepare[j +(Num-1-m)][i]+Count
                        l=l+1
                    else:
                        break
                    k=k-1
        for i in range(0,9-Num+1):
            for j in range(0,9-Num+1):
                l=j
                n=i
                for k in range(0,Num):
                    if((a[k]==0)and(self.chess[n][l]==0))or\
                    ((a[k]==1)and(self.chess[n][l]==2))or\
                    ((a[k]==2)and(self.chess[n][l]==1))or\
                    ((a[k]==3)and(self.chess[n][l]==0)):
                        if(k==Num-1):
                            for m in range(0,Num):
                                if(a[m]==3):
                                    self.Prepare[i+m][j+m]=self.Prepare[i+m][j+m]+Count
                        l=l+1
                        n=n+1
                    else:
                        break

                l=j
                n=i
                k=Num-1
                while(k>=0):
                    if((a[k]==0)and(self.chess[n][l]==0))or\
                    ((a[k]==1)and(self.chess[n][l]==2))or\
                    ((a[k]==2)and(self.chess[n][l]==1))or\
                    ((a[k]==3)and(self.chess[n][l]==0)):
                        if k==0:
                            for m in range(0,Num):
                                if a[m]==3:
                                    self.Prepare[i+(Num-1-m)][j+(Num-1-m)]=self.Prepare[i+(Num-1-m)][j+(Num-1-m)]+Count
                        l=l+1
                        n=n+1
                    else:
                        break
                    k=k-1
        i=8
        while(i>=Num-1):
            for j in range(0,9-Num+1):
                l=j
                n=i
                for k in range(0,Num):
                    if((a[k]==0)and(self.chess[n][l]==0))or\
                    ((a[k]==1)and(self.chess[n][l]==2))or\
                    ((a[k]==2)and(self.chess[n][l]==1))or\
                    ((a[k]==3)and(self.chess[n][l]==0)):
                        if(k==Num-1):
                            for m in range(0,Num):
                                if(a[m]==3):
                                    self.Prepare[i-m][j+m]=self.Prepare[i-m][j+m]+Count
                        l=l+1
                        n=n-1
                    else:
                        break

                l=j
                n=i
                k=Num-1
                while(k>=0):
                    if((a[k]==0)and(self.chess[n][l]==0))or\
                    ((a[k]==1)and(self.chess[n][l]==2))or\
                    ((a[k]==2)and(self.chess[n][l]==1))or\
                    ((a[k]==3)and(self.chess[n][l]==0)):
                        if k==0:
                            for m in range(0,Num):
                                if a[m]==3:
                                    self.Prepare[i-(Num-1-m)][j+(Num-1-m)]=self.Prepare[i-(Num-1-m)][j+(Num-1-m)]+Count
                        l=l+1
                        n=n-1
                    else:
                        break
                    k=k-1
            i=i-1

    def chessDecisionBlue2x(self):
        for k in range(0,9):
            for l in range(0,9):
                if (self.chessBlue[k][l]==1):
                    if ((k+2<9)and(l+1<9)and(l-1>=0)and\
                        (self.chessBlue[k+1][l+1]==1)and(self.chessBlue[k+1][l-1]==1)and\
                        (self.chessBlue[k+2][l]!=1)and(self.chess[k+2][l]!=2)):
                        self.Prepare[k+2][l]=self.Prepare[k+2][l]+25
                    if ((k+2<9)and(l+1<9)and(l-1>=0)and\
                        (self.chessBlue[k+1][l+1]==1)and(self.chessBlue[k+2][l]==1)and\
                        (self.chessBlue[k+1][l-1]!=1)and(self.chess[k+1][l-1]!=2)):
                        self.Prepare[k+1][l-1]=self.Prepare[k+1][l-1]+25
                    if ((k+2<9)and(l+1<9)and(l-1>=0)and\
                        (self.chessBlue[k+2][l]==1)and(self.chessBlue[k+1][l-1]==1)and\
                        (self.chessBlue[k+1][l+1]!=1)and(self.chess[k+1][l+1]!=2)):
                        self.Prepare[k+1][l+1]=self.Prepare[k+1][l+1]+25
                    if ((k+1<9)and(k-1>=0)and(l+2<9)and\
                        (self.chessBlue[k+1][l+1]==1)and(self.chessBlue[k][l+2]==1)and\
                        (self.chessBlue[k-1][l+1]!=1)and(self.chess[k-1][l+1]!=2)):
                        self.Prepare[k-1][l+1]=self.Prepare[k-1][l+1]+25

                    if ((k+2<9)and(l+1<9)and(l-1>=0)and\
                        (self.chessBlue[k+1][l+1]==1)and(self.chessBlue[k+1][l-1]==1)and(self.chessBlue[k+2][l]==1)):
                        if ((k+4<9)and(l-4>=0)and\
                            (self.chessBlue[k+2][l-2]==1)and(self.chess[k+3][l-3]!=2)and\
                            (self.chess[k+4][l-4]!=2)and(self.chessBlue[k+3][l-1]!=1)and(self.chess[k+3][l-1]!=2)):
                            self.Prepare[k+3][l-1]=self.Prepare[k+3][l-1]+15

                        if ((k+4<9)and(l+4<9)and\
                            (self.chessBlue[k+2][l+2]==1)and(self.chess[k+3][l+3]!=2)and\
                            (self.chess[k+4][l+4]!=2)and(self.chessBlue[k+3][l+1]!=1)and(self.chess[k+3][l+1]!=2)):
                            self.Prepare[k+3][l+1]=self.Prepare[k+3][l+1]+15
                    
                        if ((k-4>=0)and(l+4<9)and\
                            (self.chessBlue[k-2][l+2]==1)and(self.chess[k-3][l+3]!=2)and\
                            (self.chess[k-4][l+4]!=2)and(self.chessBlue[k-3][l+1]!=1)and(self.chess[k-3][l+1]!=2)):
                            self.Prepare[k-3][l+1]+self.Prepare[k-3][l+1]+15
                            
                        if ((k-4>=0)and(l-4>=0)and\
                            (self.chessBlue[k-2][l-2]==1)and(self.chess[k-3][l-3]!=2)and\
                            (self.chess[k-4][l-4]!=2)and(self.chessBlue[k-3][l-1]!=1)and(self.chess[k-3][l-1]!=2)):
                            self.Prepare[k-3][l-1]=self.Prepare[k-3][l-1]+15

G=Gobang()
G.arm.init()
G.chess_board()

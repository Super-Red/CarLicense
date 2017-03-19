'''
Project Name: BOT_Class(Object_Oriented_Program) 
Author: Red_Chan
Finished: Sat Nov 26 18:57:12 2016
Contact: fswccgh@126.com
What's new: Seal into a class, can store the password
            Everytime the thread stop, total time will be refreshed.
            Instructions are beautified to be more adorable.
'''

import requests
from tkinter import *
import re 
import io
from PIL import Image, ImageTk
import threading
import time
import json
import os
import subprocess

class Bot(object):

    def __init__(self, username="", password="", interval=60):  
        self._username = username
        self._passsword = password      
        self.session = requests.Session()
        self.root = Tk()
        self.root.title("BOT")
        self.root.geometry("400x300+500+200")
        self.root.resizable(False,False)
        self.canvas = Canvas(self.root, width=400, height=300)
        # 0,1,2 used for login entrys; 3,4,5 used for time-showing labels
        self.textVariableList = [StringVar() for i in range(6)]
        self.buildBasicLayout()
        self.quitFlag = [False, ]
        self.button = []
        self.interval = interval 
        self.canvas.pack()
        self.root.mainloop()       
    
    def buildBasicLayout(self):
        '''
        build the basic GUI
        includes 3 label and 3 entry for users to key in login datas
        And one label to give instructions
        And two original buttons to login and reset
        '''
        Label(self.root, text="账号: ", font="Monaco 15").place(x=30, y=10)
        Label(self.root, text="密码: ", font="Monaco 15").place(x=30, y=40)
        Label(self.root, text="验证码: ", font="Monaco 15").place(x=30, y=70)
        self.checkCodeImage = Image.open(io.BytesIO(self.session.get(self.getCheckCodeSrc()).content))
        self.checkCodeImage = ImageTk.PhotoImage(self.checkCodeImage)
        Label(self.root, image=self.checkCodeImage).place(x=200, y=70)
        self.usernameEntry = Entry(width=20, textvariable=self.textVariableList[0])
        self.passwordEntry = Entry(width=20, textvariable=self.textVariableList[1])
        self.checkCodeEntry = Entry(width=10, textvariable=self.textVariableList[2])
        self.textVariableList[0].set(self._username)
        self.textVariableList[1].set(self._passsword)
        self.usernameEntry.place(x=100, y=10)
        self.passwordEntry.place(x=100, y=40)
        self.checkCodeEntry.place(x=100, y=70)  
        self.passwordEntry["show"] = "*"
        self.instructionText = self.canvas.create_text(200, 120,font="Monaco 15",text="请登陆",fill='black')
        self.buildButtons()

    def buildButtons(self):
        '''
        build TWO buttons
        Button1 used for upload the data users key in and post to log in
        Button2 used for resetting the data if key in something wrong 
        '''
        Button(text=" 登 录   ", command=self.submit).place(x=300,y=10)
        Button(text=" 重 置   ", command=self.reset).place(x=300,y=40)

    def reset(self):
        '''
        -*-Button Method-*-
        Reset the environment the make the next submit available
        '''
        for value, variable in enumerate(self.textVariableList):
            if value in (0, 1, 2):
                variable.set("")
        self.changeInstruction("-*-*-*-*-*-      请重新登录      -*-*-*-*-*-")

    def submit(self):
        '''
        -*-Button Method-*-
        post all data users key in to login
        if success to login, show the further information
        '''
        userData = {}
        userData["UserName"] = self.usernameEntry.get()
        userData["Pwd"] = self.passwordEntry.get()
        userData["VerifyCode"] = self.checkCodeEntry.get()
        userData["loginType"] = 1
        self.session.post("http://www.jppt.com.cn/gzpt/index/shopLogin", data=userData)
        r = self.session.get("http://www.jppt.com.cn/gzpt/")
        if "退出登录" not in r.text :
            self.changeInstruction("-*-*-*-*-*-   登录失败～请重置    -*-*-*-*-*-")
        else:
            for entry in [self.usernameEntry, self.passwordEntry, self.checkCodeEntry]:
                entry["state"] = "readonly"
            self.changeInstruction("-*-*-*-*-*-   登录成功,请开始挂机  -*-*-*-*-*-")
            self.showTotalTime()

    def showTotalTime(self):
        '''
        Can only be accessed when login successfully
        Show more information and create two more Buttons
        Button1: start button, to start the essential bot function
        Button2: stop button, to stop the thread
        '''
        Label(self.root, font="Monaco 15", textvariable=self.textVariableList[3]).place(x=100,y=150)
        Label(self.root, font="Monaco 15", textvariable=self.textVariableList[4]).place(x=100,y=180)
        Label(self.root, font="Monaco 15", textvariable=self.textVariableList[5]).place(x=100,y=210)
        self.refreshTime()
        startButton = Button(text="  挂 机   ",command=self.startThread)
        startButton.place(x=100,y=256)
        self.button.append(startButton)
        stopButton = Button(text="  停 止   ",command=self.stopThread, state='disabled')
        stopButton.place(x=200,y=256)
        self.button.append(stopButton)

    def stopThread(self):
        '''
        -*-Button Method-*-
        stop the thread through changing the flag
        also reset the environment to make the next startThread available
        '''
        self.quitFlag[0] = True
        self.button[0]["state"] = "normal"
        self.button[1]["state"] = "disabled"
        time.sleep(3)
        if not self.thread1.is_alive():
            self.changeInstruction("-*-*-*-*-*-已停止挂机，可重新'挂机'-*-*-*-*-*-")
            self.refreshTime()
        else:
            self.changeInstruction("-*-*-*-*-*-   停止失败,仍在挂机   -*-*-*-*-*-")
        self.thread1.join()

    def startThread(self):
        '''
        -*-Button Method-*-
        start a new thread the run the reflash function
        '''
        self.quitFlag[0] = False
        self.button[0]["state"] = "disabled"
        self.button[1]["state"] = "normal"
        # the method in self.thread1 is self.startTrain
        self.thread1 = threading.Thread(target=self.startTrain)
        self.thread1.start() 

    def startTrain(self):
        '''
        -*-Thread Method-*-
        return the dynamic time from the Internet
        '''
        self.session.post("http://www.jppt.com.cn/gzpt/admin/train/startTrain/")
        self.changeInstruction("-*-*-*-*-*-       已在挂机       -*-*-*-*-*-")
        second = 0
        while not self.quitFlag[0]:
            if second%self.interval == 0:
                r = self.session.post("http://www.jppt.com.cn/gzpt/admin/train/calculateOnLoad")
                second = int(json.loads(r.text)[0]['currentTrained'])
                self.changeInstruction("-*-*-*-*-*-     已挂机:{0}分钟    -*-*-*-*-*-".format(second//60))
            mytime = "".join([str(second//60), "分", str(second-60*(second//60)), "秒"])
            self.textVariableList[5].set("本次培训时间:      " + mytime)
            # if mytime == "15分0秒":
            #     result = self.resultOfRandomCal()
            #     self.session.post("http://www.jppt.com.cn/gzpt/admin/train/randomCompute?result="+result)
            time.sleep(1)
            second += 1

#############################################################################################################################

    def getCheckCodeSrc(self):
        # return the checkcode Image
        r = self.session.get("http://www.jppt.com.cn/gzpt/index/newLogin")
        srcList = re.findall(r'src="(.+?)"', r.text)
        checkCodeSrc = ''.join(["http://www.jppt.com.cn", [i for i in srcList if "getImage" in i][0]])
        return checkCodeSrc

    def changeInstruction(self, str):
        # change the instruction text in canvas
        self.canvas.itemconfig(self.instructionText, text=str)
        print(str)

    def refreshTime(self):
        # refresh the time when the thead start and end!
        r = self.session.get("http://www.jppt.com.cn/gzpt/")
        totalMins = re.findall(r"当前科目理论：<span>(.+?)</span>", r.text)[0]
        todayMins = re.findall(r"当日完成学时：<span>(.+?)</span>", r.text)[0]
        self.textVariableList[3].set("当前科目理论:      " + str(totalMins))
        self.textVariableList[4].set("当日完成学时:      " + str(todayMins))
        self.textVariableList[5].set("本次培训时间:      ")

    def resultOfRandomCal(self):
        #To auto recognize the code.(not available right now)
        currentTime = time.strftime("%a %b %d %Y %H:%M:%S ") + "GMT+0800 (CST)"
        imageUrl = "http://www.jppt.com.cn/gzpt/admin/getRandCheck?" + "%20".join((currentTime).split(" "))
        randomCalImage = Image.open(io.BytesIO(session.get(imageUrl).content))
        clearImage = randomCalImage.point(lambda x: 0 if x<143 else 255)
        image.save(os.path.abspath("cache.png"))
        subprocess.call(["tesseract", newFilePath, "output"])
        # 打开文件读取结果  
        with open(os.path.abspath("output.txt"), 'r') as file:
            randomEquation = file.read()
        os.remove(os.path.abspath("cache.png"))
        os.remove(os.path.abspath("output.txt"))
        result = eval(randomEquation)
        return str(result)

test = Bot("350524199303180096", "641852")
print ("All Done!")



'''
Project Name: A BOT
Author: Red_Chan
Finished: Sat Nov 26 00:21:09 2016
Contact: fswccgh@126.com
'''

from tkinter import *
import requests
import re
from PIL import Image, ImageTk
import io
import time
import threading
import json
import subprocess
import os

def getCheckCode(session):
    # return the checkcode url
    r = session.get("http://www.jppt.com.cn/gzpt/index/newLogin")
    srcList = re.findall(r'src="(.+?)"', r.text)
    checkCodeSrc = ''.join(["http://www.jppt.com.cn", [i for i in srcList if "getImage" in i][0]])
    return checkCodeSrc

def builtGUI(checkCodeImage, session):
    '''
    build the basic GUI, build TWO buttons and one calls 'submit' METHOD, 
    the other one calls 'reset' METHOD
    '''
    root = Tk()
    root.title("BOT")
    root.geometry("400x300+500+200")
    canvas = Canvas(root, width=400, height=300)
    root.resizable(False,False)
    Label(text="账号: ", font="Monaco 15").place(x=30, y=10)
    Label(text="密码: ", font="Monaco 15").place(x=30, y=40)
    Label(text="验证码: ", font="Monaco 15").place(x=30, y=70)
    textVariableList = [StringVar(), StringVar(), StringVar()]
    usernameEntry = Entry(width=20, textvariable=textVariableList[0])
    passwordEntry = Entry(width=20, textvariable=textVariableList[1])
    checkCodeEntry = Entry(width=10, textvariable=textVariableList[2])
    usernameEntry.place(x=100, y=10)
    passwordEntry.place(x=100, y=40)
    checkCodeEntry.place(x=100, y=70)
    passwordEntry["show"] = "*" 
    codeImage = ImageTk.PhotoImage(checkCodeImage)
    print(codeImage)
    Label(root, image=codeImage).place(x=200, y=70)
    loginStatus = canvas.create_text(200, 120,font="Monaco 15",text="请登陆",fill='black')
    Button(text=" 登 录   ", command=lambda:submit\
        (session, usernameEntry, passwordEntry, checkCodeEntry, root, canvas, loginStatus)).place(x=300,y=10)
    Button(text=" 重 置   ", command=lambda: reset(textVariableList, canvas, loginStatus)).place(x=300,y=40)

    canvas.pack()
    root.mainloop()

def submit(session, e1, e2, e3, root, canvas, loginStatus):
    '''
    Called by Button Submit (登录)
    Receive the data users key in and post to login
    If successfully log in, show the further information with 'showTotalTime' METHOD
    '''
    userData = {}
    userData["UserName"] = e1.get()
    userData["Pwd"] = e2.get()
    userData["VerifyCode"] = e3.get()
    userData["loginType"] = 1
    r = session.post("http://www.jppt.com.cn/gzpt/index/shopLogin", data=userData)
    r = session.get("http://www.jppt.com.cn/gzpt/")
    if "退出登录" not in r.text :
        canvas.itemconfig(loginStatus, text="登录失败～请重置")
    else:
        e1['state'] = 'readonly'
        e2['state'] = 'readonly'
        e3['state'] = 'readonly'
        canvas.itemconfig(loginStatus, text="登录成功～请开始挂机")
        showTotalTime(session, root, canvas, loginStatus)

def reset(textVariableList, canvas, loginStatus):
    '''
    Called by Button Reset
    Allow users to reset information they key in
    Useful when users failed the first try to log in
    '''
    for i in textVariableList:
        i.set("")
    canvas.itemconfig(loginStatus, text="重新登录")

def showTotalTime(session, root, canvas, loginStatus):
    '''
    Called by submit METHOD
    Can only be accessed when login successfully
    Show the total time formation and further bulid two more buttons including "Start" and "Exit"
    Button "Start" calls the startThread METHOD to create a new thread
    Button "Exit" calls the exit METHOD to stop the last thread
    '''
    r = session.get("http://www.jppt.com.cn/gzpt/")
    totalMins = re.findall(r"当前科目理论：<span>(.+?)</span>", r.text)[0]
    todayMins = re.findall(r"当日完成学时：<span>(.+?)</span>", r.text)[0]
    Label(root, font="Monaco 15", text="当前科目理论:     {time}".format(time=totalMins)).place(x=100,y=150)
    Label(root, font="Monaco 15", text="当日完成学时:     {time}".format(time=todayMins)).place(x=100,y=180)
    quitFlag = [False, ]
    button = []
    getButton = Button(text="  挂 机   ",command=lambda:startThread(session, root, canvas, quitFlag, button, loginStatus))
    getButton.place(x=100,y=256)
    button.append(getButton)
    quitButton = Button(text="  停 止   ",command=(lambda:exit('hello', quitFlag, button, canvas, loginStatus)), state='disabled')
    quitButton.place(x=200,y=256)
    button.append(quitButton)

def startThread(session, root, canvas, quitFlag, button, loginStatus):
    """
    Called by the Button 'Start'
    Create a new thread called getThread (in fact I can create the thread early so that I don't have to global it)
    The new thread executes some tasks which are collected into a METHOD called stareTrain
    """
    global getThread
    quitFlag[0] = False
    button[0]['state']='disabled'
    button[1]['state']='normal'
    getThread = threading.Thread(target=startTrain,args=(session, root, quitFlag, canvas, loginStatus))
    getThread.start()

def startTrain(session, root, quitFlag, canvas, loginStatus):
    '''
    Execute the new thread 
    To return the dynamic time botted
    Recognize the checkcode if show up (will be available soon)
    '''
    global currentTime
    r = session.post("http://www.jppt.com.cn/gzpt/admin/train/startTrain/")
    Label(root, font="Monaco 15", text="本次培训时间:").place(x=100,y=210)
    currentTime = canvas.create_text(260, 223,font="Monaco 15",text="",fill='black')
    canvas.itemconfig(loginStatus, text="已在挂机")
    while not quitFlag[0]:
        r = session.post("http://www.jppt.com.cn/gzpt/admin/train/calculateOnLoad")
        second = int(json.loads(r.text)[0]['currentTrained'])
        mytime = "".join([str(second//60), "分", str(second-60*(second//60)), "秒"])
        canvas.itemconfig(currentTime, text="{time}".format(time=mytime))
        # if mytime == "15分0秒":
        #     result = resultOfRandomCal(session)
        #     session.post("http://www.jppt.com.cn/gzpt/admin/train/randomCompute?result={result}".format(result=result))
        print (mytime)
        time.sleep(2)

def resultOfRandomCal(session):
    '''
    To auto recognize the code.(not available right now)
    '''
    imageUrl = "http://www.jppt.com.cn/gzpt/admin/getRandCheck?" + "%20".join((time.strftime("%a %b %d %Y %H:%M:%S ") + "GMT+0800 (CST)").split(" "))
    randomCalImage = Image.open(io.BytesIO(session.get(imageUrl).content))
    clearImage = randomCalImage.point(lambda x: 0 if x<143 else 255)
    image.save(os.path.abspath("cache.png"))
    subprocess.call(["tesseract", newFilePath, "output"])
    # 打开文件读取结果  
    with open(os.path.abspath("output.txt"), 'r') as F:
        randomEquation = F.read()
    
    os.remove(os.path.abspath("cache.png"))
    os.remove(os.path.abspath("output.txt"))
    result = eval(randomEquation)
    return imageUrl

def exit(s1, quitFlag, button, canvas, loginStatus):
    '''
    Called by the button "Exit"
    Stop the 'Start' Thread and reset the environment to make the next 'Start' available
    '''
    quitFlag[0] = True
    button[0]['state']='normal'
    button[1]['state']='disabled'
    time.sleep(3)
    if (not getThread.is_alive()):
        canvas.itemconfig(loginStatus, text="已停止挂机，可重新'挂机'")
        print("You have successfully quit the programe\nRestart it if you wanna use it again")
        canvas.itemconfig(currentTime, text="")
    else : 
        canvas.itemconfig(loginStatus, text="停止失败，仍在挂机")
        print("Something goes wrong!")
    getThread.join()

data = {"id": "350524199303180096",
        "password": "641852"}

# session = requests.Session()
# checkCodeImage = Image.open(io.BytesIO(session.get(getCheckCode(session)).content))
# builtGUI(checkCodeImage, session)

print("done!")





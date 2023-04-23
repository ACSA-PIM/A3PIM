import  time
from tsjPython.tsjCommonFunc import *
import curses
from curses import wrapper
import multiprocessing as mp
barTotalNum=dict()
barCurrentNum=dict()
barStartTime=dict()
barBeforeTime=dict()
barName=set()


def is_positive(value):
    value = int(value)
    if value < 0:
        return False
    return True

def time2String(timeNum):
    if timeNum < 60:
        return "{:.2f}".format(timeNum)
    elif timeNum < 3600:
        timeNum=int(timeNum)
        minutes=timeNum//60
        secends=timeNum%60
        return "{:0>2d}:{:0>2d}".format(minutes,secends)
    else:
        timeNum=int(timeNum)
        hour=timeNum//3600
        minutes=(timeNum-hour*3600)//60
        secends=timeNum%60
        return "{:0>2d}:{:0>2d}:{:0>2d}".format(hour,minutes,secends)

def barString(name,current=0,total=-1):
    global barBeforeTime,barName,barStartTime,barTotalNum
    retSting=""
    if name not in barName:
        if is_positive(total):
            barName.add(name)
            barBeforeTime[name]=time.time()
            barStartTime[name]=time.time()
            barTotalNum[name]=total
            barCurrentNum[name]=0
        return "bar is ready……"
    elif is_positive(current):       
        total=barTotalNum[name]
        if total<current:
            current=total
        lastTime=time.time()-barBeforeTime[name]
        if current > barCurrentNum[name]:
            lastTime=lastTime/(current-barCurrentNum[name])
            barCurrentNum[name]=current
            barBeforeTime[name]=time.time()
        else:
            current=barCurrentNum[name]
        pastTime=time.time()-barStartTime[name]
        if current > 0:
            restTime=pastTime/current*(total-current)
        else:
            restTime=0   
        retSting+="[{}:{:3d}%] > |".format(format(name," <10"),int(100*current/total))  #█
        space='█'
        spaceNum=int(format(100*current/total,'0>2.0f'))
        leftNum=100-spaceNum
        retSting=retSting.ljust(spaceNum+len(retSting),space)
        retSting=retSting.ljust(leftNum+len(retSting),' ')
        retSting+="| {} [{}<{}, {} s/it]".format(str(current)+"/"+str(total),time2String(pastTime),time2String(restTime),time2String(pastTime/(current+1)))
    return retSting 

def display_info(str, x, y, colorpair=2):
    '''''使用指定的colorpair显示文字'''  
    global stdscr
    stdscr.clrtoeol()
    try:
        stdscr.addstr(y, x,str, curses.color_pair(colorpair))
    except curses.error:
        # stdscr.addstr(y, x,"pls wider your windows to show Bar!!!", curses.color_pair(colorpair))
        pass
    stdscr.refresh()

def set_win():
    '''''控制台设置'''
    global stdscr
    #使用颜色首先需要调用这个方法
    curses.start_color()
    #文字和背景色设置，设置了两个color pair，分别为1和2
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    #关闭屏幕回显
    curses.noecho()
    #输入时不需要回车确认
    curses.cbreak()
    #设置nodelay，使得控制台可以以非阻塞的方式接受控制台输入，超时1秒
    stdscr.nodelay(1)

def unset_win():
    '''控制台重置'''
    global stdstr
    #恢复控制台默认设置（若不恢复，会导致即使程序结束退出了，控制台仍然是没有回显的）
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    #结束窗口
    curses.endwin()

def clearBarInfo():
    barTotalNum.clear()
    barCurrentNum.clear()
    barStartTime.clear()
    barBeforeTime.clear()
    barName.clear()

def multBarCore(stdscr,Msg,ProcessNum,total,sendPipe,receivePipe,pList):
    set_win()
    # set total num
    totalNum=0
    totalSum=0
    for ProcessID in range(ProcessNum):    
        totalNum+=1 
        totalSum+=total[ProcessID]
        display_info(barString(ProcessID,0,total[ProcessID]),0,ProcessID+1,1)
    display_info(barString("Sum",0,totalSum),0,totalNum+1,3)
    #close parent sendPipe
    for ProcessID , sendID in sendPipe.items():
        sendID.close()

    remainReceive=1
    whileTimes=0
    currentTmp=dict()
    while remainReceive:
        for p in pList:
            if p.exception:
                error, traceback = p.exception
                clearBarInfo()
                unset_win()
                print("p.exception:")
                print(traceback)
                raise TypeError(traceback)
        childProcessNum=len(mp.active_children())
        if childProcessNum==0:
            break
        whileTimes+=1
        display_info("childProcessNum/remainBarNum: "+str(childProcessNum)+"/"+str(len(receivePipe))+" "+Msg+" check time: "+str(whileTimes),0,0,2)
        remainReceive=0
        deleteReceivePipeID=[] 
        for ProcessID , receiveID in receivePipe.items():
            if barTotalNum[ProcessID]>0:
                if receiveID.poll():
                    try:
                        msg=receiveID.recv()
                    except Exception  as e:
                        clearBarInfo()
                        unset_win()
                        raise TypeError("e={} ProcessID={} barTotalNum[ProcessID]={} currentTmp[ProcessID]={}".format(e,ProcessID,barTotalNum[ProcessID],currentTmp[ProcessID]))
                        print("{} {} {}".format(e,ProcessID,barTotalNum[ProcessID]))
                        msg=0
                    if isinstance(msg,int):
                        display_info(barString(ProcessID,msg),0,ProcessID+1,1)
                        if(msg>=barTotalNum[ProcessID]):
                            deleteReceivePipeID.append(ProcessID)
                            currentTmp[ProcessID]=barTotalNum[ProcessID]
                        else:
                            currentTmp[ProcessID]=msg
                    else:
                        clearBarInfo()
                        unset_win()
                        raise TypeError("ProcessID={} sub process msg={}\nbarTotalNum[ProcessID]={} currentTmp[ProcessID]={}".format(ProcessID,msg,barTotalNum[ProcessID],currentTmp[ProcessID]))
                else:
                    display_info(barString(ProcessID,0),0,ProcessID+1,1)
                remainReceive=1
            else:
                deleteReceivePipeID.append(ProcessID)
        tmpCurrentSum=0
        for ProcessID , eachCurrent in currentTmp.items():
            tmpCurrentSum+=eachCurrent
        display_info(barString("Sum",tmpCurrentSum),0,totalNum+1,3)
        display_info("",0,totalNum+2,3)
        for ProcessID in deleteReceivePipeID:
            del receivePipe[ProcessID]
        time.sleep(0.2)
    clearBarInfo()
    

def multBar(Msg,ProcessNum,total,sendPipe,receivePipe,pList,stdscrInput):
    global stdscr
    stdscr= stdscrInput
    processBeginTime=time.time()
    unset_win()
    yellowPrint("\n\r{} : start multiple Processes at: {}".format(Msg,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    wrapper(multBarCore,Msg,ProcessNum,total,sendPipe,receivePipe,pList)  
    passPrint("{} : wait {} to finish multiple Processes at: {}".format(Msg,time2String(int(time.time()-processBeginTime)),time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))

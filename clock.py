#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading, signal, time, sys, socket

import ST7789V
from PIL import Image,ImageDraw,ImageFont
import PIL.ImageOps

import WS2812 
from rpi_ws281x import Adafruit_NeoPixel, Color

import RPi.GPIO as GPIO

import datetime
import os

MODE_PIN = 26
LEFT_PIN = 22
RIGHT_PIN =  17

dig7=[ 0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f, 0x00, 0x01, 0x02, 0x04,0x08,0x10,0x20,0x40]

digdot = [ [ 0x00,0x3e,0x51,0x49,0x45,0x3e ], [ 0x00,0x00,0x42,0x7f,0x40,0x00],[0x00,0x42,0x61,0x51,0x49,0x46],[0x00,0x21,0x41,0x45,0x4b,0x31], [0x00,0x18,0x14,0x12,0x7f,0x10], [0x00,0x27,0x45,0x45,0x45,0x39], [0x00,0x3c,0x4a,0x49,0x49,0x30],[0x00,0x01,0x71,0x09,0x05,0x03],[0x00,0x36,0x49,0x49,0x49,0x36], [0x00,0x06,0x49,0x49,0x29,0x1e]]



#dir = "/home/pi/Clock"
#numpicdir = dir + "/numpic/A/"

print("1. LCD init")
BlackLightLev =8 
lcd = ST7789V.LCD1in14(BlackLightLev)
lcd.Init()
lcd.clearAll()

print("2. Set RGB Color")
rgb = WS2812.WS2812()

CL = {'White':[40,40,40], 'Red':[40,0,0], 'Green':[0,255,0], 'Blue':[0,0,40], 'Yellow':[255,255,0], 'Cyan':[0,255,255], 'Purple':[255,0,255], 'Black':[0,0,0]}
rgbColor = [CL['Red'],CL['Red'],CL['Red'],CL['Red'],CL['Red'],CL['Red']]
RGBday = CL["Blue"]

lastdigit = [-1,-1,-1,-1,-1,-1]
day2 = 0

# rgb.Close()
rgb.SetRGB(rgbColor)

# gpios = GPIOCFG.GPIOCFG()


def signal_handler(sig, frame):
    GPIO.cleanup()
    print("I've been killed")
    sys.exit(0)

def drawDot(drawim, x,y,w, s):
    if (s==1):
         ff=oncol
    else:
         ff=offcol
    shape = [(x,y),(x+w,y+w)]
    drawim.ellipse(shape, fill= ff, outline="black") 
    

def ShowDigitDot(l,n):
    h=10
    w=20
    x=10
    y=40
    if (lastdigit[l] != n):
       im = Image.new("RGB", (135,240), backcol)
       drawim = ImageDraw.Draw(im)
       for j in range(6):
          for i in range(8):
              drawDot(drawim,x+j*w,y+i*w,w,(digdot[n][j]>>i)&0x1 )
       lcd.ShowImage(l, im)
       lastdigit[l] = n

def ShowDigitTxt(l, n):
    x=0
    y=-20
    if (lastdigit[l] != n):
       im = Image.new("RGB", (135,240), backcol)
       drawim = ImageDraw.Draw(im)
       font1 = ImageFont.truetype(('Font.ttc'), 250)
       drawim.text((x,y), str(n), font = font1, fill=oncol)
       lcd.ShowImage(l, im)
       lastdigit[l] = n


def drawSegment(drawim, x,y, orient, ll, hh, s):
    if (orient==0):
        pt=[(x,y),(x+hh,y+hh), (x+ll-hh,y+hh), (x+ll, y) , (x+ll-hh,y-hh), (x+hh, y-hh), (x,y)]
    else:
        pt=[(x,y),(x+hh,y+hh), (x+hh,y+ll-hh), (x, y+ll) , (x-hh,y+ll-hh), (x-hh, y+hh), (x,y)]
    if  (s==1): 
        ff=oncol
    else:
        ff=offcol
    drawim.polygon(pt, fill=ff, outline="black")

def ShowDigit7(l, n):
    w=90
    h=10     
    x=20
    y=20
    if (lastdigit[l] != n):
       im = Image.new("RGB", (135,240), backcol)
       drawim = ImageDraw.Draw(im)
       drawSegment(drawim,x,y,0,w,h,(dig7[n]>>0)&0x1) 
       drawSegment(drawim,x+w,y,1,w,h,(dig7[n]>>1)&0x1) 
       drawSegment(drawim,x+w,y+w,1,w,h,(dig7[n]>>2)&0x1) 
       drawSegment(drawim,x,y+w*2,0,w,h,(dig7[n]>>3)&0x1) 
       drawSegment(drawim,x,y+w,1,w,h,(dig7[n]>>4)&0x1) 
       drawSegment(drawim,x,y,1,w,h,(dig7[n]>>5)&0x1) 
       drawSegment(drawim,x,y+w,0,w,h,(dig7[n]>>6)&0x1) 
       lcd.ShowImage(l, im)
#       print("Digit ",l," num ",n)
       lastdigit[l] = n

def ClearLCD(l):
    im = Image.new("RGB", (135,240), backcol)
    lcd.ShowImage(l, im)

def ClearLCDAll():
    im = Image.new("RGB", (135,240), backcol)
    for i in range(5):
        lcd.ShowImage(i, im)

def ShowDate(l):
    font1 = ImageFont.truetype(('Font.ttc'), 100)
    font2 = ImageFont.truetype(('Font.ttc'), 60)
    W,H = (135,240)
    im = Image.new("RGB", (W,H), backcol)
    drawim = ImageDraw.Draw(im)
    weekday = datetime.datetime.now().strftime('%a')
    w,h = drawim.textsize(weekday, font=font2)
    drawim.text(((W-w)/2,5),weekday,font=font2,fill=oncol)
    y=h+10
    day = str(datetime.datetime.now().day)
    w,h  = drawim.textsize(day, font=font1)
    drawim.text(((W-w)/2,y),day,font=font1,fill=oncol)
    y=y+h+5
    month = datetime.datetime.now().strftime('%b')
    w,h = drawim.textsize(month, font=font2)
    drawim.text(((W-w)/2,y),month,font=font2,fill=oncol) 
    lcd.ShowImage(l,im)

def ShowColon(l, t):
    im = Image.new("RGB", (135,240), backcol)
    drawim = ImageDraw.Draw(im)
    fillcol = oncol
#    if (t > 400000):
#        fillcol = oncol
    drawim.ellipse((50,50,80,80), fill= fillcol) 
    drawim.ellipse((50,150,80,180), fill= fillcol) 
    lcd.ShowImage(l, im)

def ShowHost(l):
    font2 = ImageFont.truetype(('Font.ttc'), 40)
    W,H = (135,240)
    im = Image.new("RGB", (135,240), backcol)
    drawim = ImageDraw.Draw(im)
    fillcol = oncol
    hostname=socket.gethostname()
    w,h = drawim.textsize(hostname, font=font2)
    drawim.text(((W-w)/2,100),hostname,font=font2,fill=oncol) 
    lcd.ShowImage(l,im)


def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

def ShowIP(l):
    font2 = ImageFont.truetype(('Font.ttc'), 40)
    W,H = (135,240)
    im = Image.new("RGB", (135,240), backcol)
    drawim = ImageDraw.Draw(im)
    fillcol = oncol
    IP=get_ip()
    IP_split = IP.split(".")
    w,h = drawim.textsize(IP_split[0], font=font2)
    drawim.text(((W-w)/2,10),IP_split[0],font=font2,fill=oncol) 
    w,h = drawim.textsize(IP_split[1], font=font2)
    drawim.text(((W-w)/2,50),IP_split[1],font=font2,fill=oncol) 
    w,h = drawim.textsize(IP_split[2], font=font2)
    drawim.text(((W-w)/2,90),IP_split[2],font=font2,fill=oncol) 
    w,h = drawim.textsize(IP_split[3], font=font2)
    drawim.text(((W-w)/2,130),IP_split[3],font=font2,fill=oncol) 
    lcd.ShowImage(l,im)

def DispInfo():
    ShowDate(0)
    ShowHost(1)
    ShowIP(2)


def DispTime():
    global day2
    hour = datetime.datetime.now().hour
    minutes =  datetime.datetime.now().minute
    microsec = datetime.datetime.now().microsecond
    day = datetime.datetime.now().day

    hr1 = hour % 10
    hr2 = hour // 10
    min1 = minutes % 10
    min2 = minutes // 10

    if DispType==1:
        ShowDigit7(0, hr2)
        ShowDigit7(1, hr1)
        ShowDigit7(3, min2)
        ShowDigit7(4, min1)
    elif DispType==2:
        ShowDigitDot(0, hr2)
        ShowDigitDot(1, hr1)
        ShowDigitDot(3, min2)
        ShowDigitDot(4, min1)
    elif DispType==3:
        ShowDigitTxt(0, hr2)
        ShowDigitTxt(1, hr1)
        ShowDigitTxt(3, min2)
        ShowDigitTxt(4, min1)
    
    ShowColon(2, microsec)
    if (day != day2):
       ShowDate(5)
       day2=day

def mode_button_callback(channel):
    global DispType, lastdigit, day2
    print("mode button pressed")
    DispType+=1
    if DispType==4:
       DispType = 0
    lcd.clearAll()
    lastdigit = [-1,-1,-1,-1,-1,-1]
    day2 = 0
    UpdateDisp()

def left_button_callback(channel):
    global oncolday, offcolday, lastdigit, day2, oncol, offcol, coloursel
    coloursel+=1
    if coloursel > 4:
       coloursel = 1
    if  coloursel == 1:
       oncolday = "#80c0ff" # Blue
       offcolday = "#3a2f0b"
       RGBday = CL["Blue"]
    elif coloursel == 2:
       oncolday = "#e00000" # Red
       offcolday = "#3a2f0b"
       RGBday = CL["Red"]
    elif coloursel == 3:
       oncolday = "#00e000" # Green
       offcolday = "#3a2f0b"
       RGBday = CL["Green"]
    elif coloursel == 4:
       oncolday = "#e0e0e0" # White
       offcolday = "#3a2f0b"
       RGBday = CL["White"]
    oncol = oncolday
    offcol = offcolday
    lastdigit = [-1,-1,-1,-1,-1,-1]
    day2 = 0
    UpdateDisp()
    rgb.SetRGBall(RGBday)
    print("left button pressed")

def right_button_callback(channel):
    global oncol, offcol, lastdigit, day2
    oncol = "#80c0ff"
    offcol = "#3a2f0b"
    lastdigit = [-1,-1,-1,-1,-1,-1]
    day2 = 0
    DispTime()
    print("right button pressed")

def UpdateDisp():
    if DispType == 0:
        DispInfo()
    else:
        DispTime()

oncol = "#80c0ff"
offcol = "#3a2f0b"
#backcol = "#202080"

#oncol = "#c00000"
#offcol = "#201010"

coloursel = 1
offcolday = offcol
oncolday = oncol
backcol = "#000000"
ClearLCDAll()

DispType = 0
oncol = "#ee00ee"
offcol = "#3a2f0b"

UpdateDisp()
time.sleep(10)
DispType=1


GPIO.setmode(GPIO.BCM)
GPIO.setup(MODE_PIN, GPIO.IN)
GPIO.setup(LEFT_PIN, GPIO.IN)
GPIO.setup(RIGHT_PIN, GPIO.IN)

GPIO.add_event_detect(MODE_PIN, GPIO.RISING, callback=mode_button_callback, bouncetime=500)
GPIO.add_event_detect(LEFT_PIN, GPIO.RISING, callback=left_button_callback, bouncetime=500)
GPIO.add_event_detect(RIGHT_PIN, GPIO.RISING, callback=right_button_callback, bouncetime=500)


signal.signal(signal.SIGINT, signal_handler)

#for i in range(10,18):
#for l in range(6):
#     ShowDigit(l,8)
#     time.sleep(0.5) 

cc=0

while(1):
    hour = datetime.datetime.now().hour
    if (hour < 8):
      if (cc!=1):
       oncol = "#c00000"
       offcol = "#201010"
#       rgbColor = [CL['Black'],CL['Black'],CL['Black'],CL['Black'],CL['Black'],CL['Black']]
       lastdigit = [-1,-1,-1,-1,-1,-1]
       day2 = 0
       rgb.SetRGBall("Black")
       lcd.SetLcdBlackLight(2)
       cc=1
    elif (hour<22):
      if (cc!=2):
       oncol = oncolday
       offcol = offcolday
#       rgbColor = [CL['Blue'],CL['Blue'],CL['Blue'],CL['Blue'],CL['Blue'],CL['Blue']]
       lastdigit = [-1,-1,-1,-1,-1,-1]
       day2 = 0
       lcd.SetLcdBlackLight(8)
       rgb.SetRGBall(RGBday)
       cc=2
    else:
      if (cc!=3):
       oncol = "#e00000"
       offcol = "#3a2f0b"
       rgbColor = [CL['Red'],CL['Red'],CL['Red'],CL['Red'],CL['Red'],CL['Red']]
       lastdigit = [-1,-1,-1,-1,-1,-1]
       day2 = 0
       lcd.SetLcdBlackLight(6)
       rgb.SetRGB(rgbColor)
       cc=3

    UpdateDisp()
    time.sleep(20)


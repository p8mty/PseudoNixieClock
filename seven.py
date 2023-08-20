#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading, signal, time

import ST7789V
from PIL import Image,ImageDraw,ImageFont
import PIL.ImageOps

import WS2812 
from rpi_ws281x import Adafruit_NeoPixel, Color

#import GPIOCFG
import datetime
import os

dig7=[ 0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f, 0x00, 0x01, 0x02, 0x04,0x08,0x10,0x20,0x40]

dir = "/home/pi/LCD-Clock-A-Code/rpi"

numpicdir = dir + "/numpic/A/"

print("1. LCD init")
BlackLightLev =8 
lcd = ST7789V.LCD1in14(BlackLightLev)
lcd.Init()
lcd.clearAll()

print("2. Set RGB Color")
rgb = WS2812.WS2812()

CL = {'White':[40,40,40], 'Red':[40,0,0], 'Green':[0,255,0], 'Blue':[0,0,40], 'Yellow':[255,255,0], 'Cyan':[0,255,255], 'Purple':[255,0,255], 'Black':[0,0,0]}
rgbColor = [CL['Red'],CL['Red'],CL['Red'],CL['Red'],CL['Red'],CL['Red']]

lastdigit = [-1,-1,-1,-1,-1,-1]
day2 = 0

# rgb.Close()
rgb.SetRGB(rgbColor)

# gpios = GPIOCFG.GPIOCFG()

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

def ShowDigit(l, n):
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

    ShowDigit(0, hr2)
    ShowDigit(1, hr1)
    ShowDigit(3, min2)
    ShowDigit(4, min1)
    
    ShowColon(2, microsec)
    if (day != day2):
       ShowDate(5)
       day2=day


oncol = "#80c0ff"
offcol = "#3a2f0b"
#backcol = "#202080"

oncol = "#c00000"
offcol = "#201010"
backcol = "#000000"

#for i in range(10,18):
#for l in range(6):
#     ShowDigit(l,8)
#     time.sleep(0.5) 

ShowDigit(0,10)
time.sleep(0.5)
ShowDigit(1,10)
time.sleep(0.5)
ClearLCD(2)
time.sleep(0.5)
ShowDigit(3,10)
time.sleep(0.5)
ShowDigit(4,10)
time.sleep(0.5)
ClearLCD(5)

time.sleep(0.5)

cc=0

while(1):
    hour = datetime.datetime.now().hour
    if (hour < 8):
      if (cc!=1):
       oncol = "#c00000"
       offcol = "#201010"
       rgbColor = [CL['Black'],CL['Black'],CL['Black'],CL['Black'],CL['Black'],CL['Black']]
       lastdigit = [-1,-1,-1,-1,-1,-1]
       day2 = 0
       rgb.SetRGB(rgbColor)
       lcd.SetLcdBlackLight(2)
       cc=1
    elif (hour<22):
      if (cc!=2):
       oncol = "#80c0ff"
       offcol = "#3a2f0b"
       rgbColor = [CL['Blue'],CL['Blue'],CL['Blue'],CL['Blue'],CL['Blue'],CL['Blue']]
       lastdigit = [-1,-1,-1,-1,-1,-1]
       day2 = 0
       lcd.SetLcdBlackLight(8)
       rgb.SetRGB(rgbColor)
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

    DispTime()
    time.sleep(20)


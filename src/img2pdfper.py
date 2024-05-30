#!/usr/bin/python
# (C) 2011, 2012 University of Kaiserslautern 
# 
# You may not use this file except under the terms of the accompanying license.
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License. You may
# obtain a copy of the License at http:#www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# Project: Decapod
# Section: genpdf module 
# File: img2pdfper
# Purpose: run the genpdf on a set of test images
# Creator: Hasan S. M. Al-Khaffaf (hasan@iupr.com)
# Reviewer: 
# Primary Repository: 
# Web Sites: www.iupr.com




from builtins import str
from builtins import range
from past.utils import old_div
from ocrodir import *
from optparse import OptionParser 
import sys
import glob
import subprocess
from inspect import currentframe
import time
from reportlab.pdfgen import canvas
import os 
import datetime
from reportlab.lib.pagesizes import A4
from PIL import Image, ImageDraw

def createImageList(opt):
    imageFormats = [".jpg", ".tif", ".tiff", ".png", ".bmp"] #FIXME: add more image file types supported by Ocropus
#    __imageFormatLine__ = currentframe().f_back.f_lineno
    listFiltered = []
    list = glob.glob(opt.srcDirectory + "*.*") 
    
    if opt.verbose == 1:
        print("[info] Filtering input images:\n")
        print("[info] supported image types", imageFormats)
        print("[info] want to support a new image type? Add it into imageFormats list") # at line %i"%(int(__imageFormatLine__))
        
    #filter the list by removing non-images
    for i in list:
        foundFlag = 0
        # filter out non images
        for j in imageFormats:
            str = i[len(i)-len(j):]
            if j == (i[len(i)-len(j):]).lower():
                foundFlag = 1;
        if foundFlag == 1:
            listFiltered.append(i) 
    listFiltered.sort()
    return listFiltered
    
    
def stripExt(name):
    nameNoExt = name[0:len(name)-4]
    return nameNoExt


def genPDF4ImageList(fileList, opt):
    booksDirList = []
    batchBegin = time.time()
    for i in fileList: # generate PDF for the image i
        nameNoExt = stripExt(i)
        for j in list(str(opt.pdfType)): # generate PDF type j
            booksDirList.append([j, i, nameNoExt+"t" + j])
            cmd = ["./decapod-genpdf.py", "-t", j, "-b", i, "-d", (nameNoExt+"t" + j + ""), "-p", (nameNoExt + "[t" + j + "]" + ".pdf"), '-r', "%s"%opt.dpi, "-v", "2", "-W", "%s"%opt.pageWidth, "-H", "%s"%opt.pageHeight, "-B", "%s"%opt.bitdepth]
            if opt.verbose == 1:
                print("************** Now executing genpdf with image:", i, "\nCommand: ", cmd ," ************")
            begTime = time.time()
            retCode = subprocess.call(cmd)
            if retCode != 0:
                print("[warn] decapod-genpdf did not work as expected")
            endTime = time.time()
            if opt.verbose == 1:
                print("Duration to run genpdf pipeline for image %s= %i sec."% (i, endTime - begTime))
    batchEnd = time.time()
    if opt.verbose == 1:
        print("Duration to run genpdf pipeline for list of images %s= %i:%i:%i  (h:m:s)"% (fileList, old_div((batchEnd - batchBegin),(60*60)), old_div((batchEnd - batchBegin),60), (batchEnd - batchBegin)%60))
    return booksDirList

def generateCoverPage(c, dateNowStr, timeNowStr, height):
    c.setFont("Helvetica", 30)
    c.drawString(80, height-200, "Decapod Nightly Run - A Report")
    c.setFont("Helvetica", 15)
    c.drawString(100, 200, "Date: " + dateNowStr)
    c.drawString(100, 180, "Time: " + timeNowStr)
    if os.path.isfile("./FBinformatik.png"):
        c.drawImage("./FBinformatik.png", 20, 81)
    if os.path.isfile("./decapod.jpg"):
        c.drawImage("./decapod.jpg", 200, 100, preserveAspectRatio=True, width=150)
    c.showPage()
    return

def loadLineBB(ccs):
    return
    
def loadTokenID(tokenIDs):
    return

def setImage(im):
    width, height = im.size
    for i in range(width-1):
        for j in range(height-1):
            im.putpixel((i,j), (0,0,0))
    return im

def loadTokenImage(tokFileName, bookDir, opt):
#    tokenFileName = bookDir + "/tokens/" + "%08i.png"%int(tokNum)
    im = Image.open(tokFileName)
    if opt.verbose == 1:
        print((tokFileName,"\n"))
    return im
                   
def loadLineImage(line, opt):
#    lineFileName = pageDir + "%02i"%int(page.number) + "%04h"%int(line.) + "%08i.png"%int(num)
    im = Image.open(line.image)
#    im = Image.open(line.csegFile)
    if opt.verbose==1:
        print((line.image,"\n"))
    return im

def findBBox(image):
    xsize, ysize = image.size
    i=0
    j=0
    x1= xsize
    y1= ysize
    x2=-1
    y2=-1
    while j<ysize:
        i=0
        while i<xsize:
            r,g,b = image.getpixel((i,j))
            if r == 0:
#                print "x=%i, y=%i, r = %s"% (i, j, image.getpixel((i,j))) 
                if i < x1:
                    x1 = i
                if j < y1:
                    y1 = j
                if i > x2:
                    x2 = i
                if j > y2:
                    y2 = j
            i += 1
        j += 1
    return (x1, y1, x2, y2)
    
def MSE(tokImage, charImage, bbx, opt):
    xx1, yy1, xx2, yy2 = bbx # bbx for a char from charImage that match tokImage
    x1 = int(xx1)
    y1 = int(yy1)
    x2 = int(xx2)
    y2 = int(yy2)
    width, height = tokImage.size
    xsize = x2 - x1 #+ 1
    ysize = y2 - y1 #+ 1
    bb = findBBox(tokImage)
#    tokImage.putpixel((bb[0], bb[1]), (255,0,0))
#    tokImage.putpixel((bb[2], bb[3]), (255,0,0))
#    tokImage.show()
#    bb = tokImage.getbbox()
    if opt.verbose == 1:
        print("token bb = %s"%(bb,))
        print("char bb= %s"%(bbx,))
    bbTemp = [bb[0], bb[1], bb[2]+1, bb[3]+1]
    tokImageCrop = tokImage.crop(bbTemp)
##    tokImageCrop.save("/home/hasan/Desktop/tokImageCrop.png")
#    tokImageCrop.show()
    tokImageCropScaled = tokImageCrop.resize((xsize, ysize), Image.NEAREST)# Resizing the CC rather than the whole image
##    tokImageCropScaled.save("/home/hasan/Desktop/tokImageCropScaled.png")
    tokImageCropScaledPix = tokImageCropScaled.load() 
#    charImage = charImage.transpose(Image.FLIP_TOP_BOTTOM)
    charImagePix = charImage.load()
    charW, charH = charImage.size
##    charImage.putpixel((x1,(charH - y1 - 1)), (0,128,0))
##    charImage.putpixel((x2,(charH - y2 - 1)), (0,128,0))
   
#    tokImageCropScaled.show() #last test
#    print "tokImage.size=%s"%((tokImage.size),)
##    charImageCrop = charImage.crop([x1, charH-y2, x2, charH-y1])
##    charImageCrop.save("/home/hasan/Desktop/charImageCrop.png")
##    charImage.show()
#    print "charImage.size=%s"%((charImage.size),)
    
    if opt.verbose == 1:
        print("tokImage.size=%s"%((tokImage.size),))
        print("tokImageCrop.size=%s"%((tokImageCrop.size),))
        print("tokImageCropScaled.size=%s"%((tokImageCropScaled.size),))
        print("charImage.size=%s\n"%((charImage.size),))
#    print  "xsize=%i"%xsize
#    print  "ysize=%i"%ysize
##    tokCopy = tokImageCropScaled.copy()
##    tokCopy = setImage(tokCopy)  
            
    xcpt = 0
    mse = 0.0
    xt = 0 # Token x coord
    yt = 0 # Token y coord
    y1flip = charH-y2
    y2flip = charH-y1-1
    while  y1flip <= y2flip:
        x1 = int(xx1)
        xt = 0
        while x1 < x2:
            try:
#                print (xt, " ", yt, "[", tokImageCropScaledPix[xt,yt], "]")
#                print (x1, " ", y1, "[", charImagePix[x1,y1], "]")
##                tokImageCropScaled.putpixel((xt,yt), (255,0,0))
##                tokImageCropScaled.save("/home/hasan/Desktop/tokImageCropScaled.png")
##                charImage.putpixel((x1,y1flip), (255,0,0))
##                charImage.save("/home/hasan/Desktop/charImage.png")
               
                r1, g1, b1 = tokImageCropScaledPix[xt,yt]
                r2, g2, b2 = charImagePix[x1,y1flip]
##                if r1 != r2: 
##                    tokCopy.putpixel((xt,yt), (255,255,255))
##                else:
##                    tokCopy.putpixel((xt,yt), (0,0,0))
                mse += (r1 - r2) * (r1 - r2)
#                print "x=%i, y=%i, tokImage.getpixel((x,y)=%i, charImage.getpixel((x,y)=%i"%(x1, y1, r1, r2)
                xt = xt + 1
                x1 = x1 + 1
            except: #FIXME: Correct by specify the cause of the exception
                xt = xt + 1
                x1 = x1 + 1
                xcpt += 1
#                print "exception\n"                
#                pass
        yt = yt + 1
        y1flip = y1flip + 1
        if xcpt != 0:   
            print("except= %i"%xcpt)
##    tokCopy.save("/home/hasan/Desktop/tok-org-diff.png")
    return (old_div(mse,((1.0 * xsize)*ysize)))
    
def getPerformance(b, opt):
    psnr = 0.0
    accMSE = 0.0
    mse = 0.0
#    print b.tokens
    for i in range(len(b.pages)):
        for j in range(len(b.pages[i].lines)):
            k = b.pages[i].lines[j]
                #bb = loadLineBB(k.ccs) # load BB for each char in the line into `bb` list
            if opt.verbose == 1:
                print("k.ccs=%s\n"%k.ccs)
                #tID = loadTokenID(k.tokenIDs) # load token ID into `tID` list
                print("k.tokenIDs=%s\n"%k.tokenIDs)
            charImage = loadLineImage(k, opt)
            z=0
            for t in k.tokenIDs: # calculate performance using t (/tokens/`t`.png) matrix and its corresponding original image (.cseg.png) matrix
                tokImage = loadTokenImage(b.tokens[t], b.bookDir, opt)
                mse = MSE(tokImage, charImage, k.ccs[z], opt)
##                print "mse = %s"%mse
                accMSE += mse
                z += 1
    print("***************")
    print("accMSE=%s"%(accMSE)) 
    print("***************")
#    psnr = 20.0 * log10(255.0/sqrt(accMSE))        
    return accMSE
        
def calculateImg2PDFPerformance(booksDirList, fileList, opt):
    if len(fileList) == 0:
        print("warn: No images to process.\nExiting.")
        return
    path = os.path.dirname(fileList[0]) # get the working folder name  
    dateTimeNow = datetime.datetime.now()
    dateNowStr = str(dateTimeNow.year) + "-" + "%02i"%dateTimeNow.month + "-" + "%02i"%dateTimeNow.day 
    timeNowStr = "%02i"%dateTimeNow.hour + ":" + "%02i"%dateTimeNow.minute
    dateTimeNowStr = dateNowStr + '[' + timeNowStr + ']'
    
    c = canvas.Canvas((path + '/' + "Report:" + dateTimeNowStr + ".pdf"), bottomup=1) #Create a canvas i.e. a PDF file
    width, height = A4
    c.setAuthor("Hasan S. M. Al-Khaffaf (hasan@iupr.com)")
    c.setTitle("Decapod Nightly Run")
    generateCoverPage(c, dateNowStr, timeNowStr, height)

    pos= 50 # put some space for the top margin 
    c.drawString(20, height - pos, "Image")
    c.drawString(450, height - pos, "MSE")
    c.drawString(525, height - pos, "PDF")
    pos = pos + 30
    for i in booksDirList:
        if i[0] == '4' or i[0] == '3':
            b =  Book(i[2])
            PSNR = getPerformance(b, opt)
        else:
            PSNR = -1
        c.drawString(20, height - pos, i[1])
        c.drawString(450, height - pos, str(int(PSNR)))
        c.drawString(525, height - pos, i[0])
        pos = pos + 30
        if pos > height-50: # if end-of-page then create new page
            c.showPage()
            pos= 50
            c.drawString(20, height - pos, "Image")
            c.drawString(450, height - pos, "MSE")
            c.drawString(525, height - pos, "PDF")
            pos = pos + 30
   
    c.showPage()
    c.save()
    return
    
    
def main(sysargv):
    parser = OptionParser()
    parser.add_option("-d", "--directory", default="", dest="srcDirectory", 
        type="string", help="Directory name for the source images. The '/' will be added (if not there)")
    parser.add_option("-t", "--type", default=1, dest="pdfType", type="int", 
        help="type of the output PDF file [1..4]. Can use more than one type simultaneously")
    parser.add_option("-r", "--resolution", default=300, dest="dpi", type="int", 
        help="resolution (default 300dpi)")
    parser.add_option("-v", "--verbose", default=0, dest="verbose", type="int", 
        help="verbose type: 0 (silent) or 1 (detailed)")
    parser.add_option("-W", "--width", default=21.0, dest="pageWidth",
        type="float", help="page width of the generated PDF file (in [cm])")
    parser.add_option("-H", "--height", default=29.7, dest="pageHeight",
        type="float", help="page height of the generated PDF file (in [cm])")
    parser.add_option("-B", "--bitdepth", default=0, dest="bitdepth",  
        help="Color bit depth of the output file")
    
    (opt, args) = parser.parse_args()
    
    if opt.srcDirectory == '':
        print("Error: directory name for the source images is missing.\nPlease supply the directory name using the '-d' option")
        exit(1)
    if opt.srcDirectory[len(opt.srcDirectory)-1] != '/':
        opt.srcDirectory = opt.srcDirectory + '/'
   
    fileList = createImageList(opt)
    booksDirList =  genPDF4ImageList(fileList, opt)
    calculateImg2PDFPerformance(booksDirList, fileList, opt)
    
    print("img2pdfper: End-of-Program")
    
    
    
if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)

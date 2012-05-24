#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) 2010 University of Kaiserslautern 
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
# File: ocrodir
# Purpose: "Parse" OCRopus output directory
# Responsible: Joost van Beusekom (joost@iupr.org)
# Reviewer: Michael
# Primary Repository: 
# Web Sites: www.iupr.com

import os, glob, string, sys, time, getopt, commands, math, numpy, datetime, platform, tempfile
import codecs
from numpy import *

# needed to read unicode text files
def readFile(fn):
    try:
        f = codecs.open(fn, encoding="utf-8")
        tmp=[]
        for line in f:
            #print line
            for i in range(len(line)):
                tmp.append(line[i])
        f.close()
        return tmp;
    except UnicodeDecodeError:
        print "[err] Error reading file ", fn
        return []
    except IOError:
        print "[warn] file could not be opened: ",fn
        return []

#reads locations of where each image belongs on page (bounding box)
def readBoxFile(fn):
    if os.path.exists(fn)== False:
        print "[warn] file could not be opened: ",fn
        return []
    f    = file(fn, "r")
    data = [line.split() for line in f]
    f.close()
    coords = zeros([len(data),4],int)
    for i in range(len(data)):
        coords[i,0] = int(data[i][0]) # x0
        coords[i,1] = int(data[i][1]) # y0
        coords[i,2] = int(data[i][2]) # x1
        coords[i,3] = int(data[i][3]) # y1
    return coords


#reads shift File containing pairs of parameters tx, ty for each cc
def readShiftFile(fn):
    if os.path.exists(fn)== False:
        print "[warn] file could not be opened: ",fn
        return []
    f    = file(fn, "r")
    data = [line.split() for line in f]
    f.close()
    coords = zeros([len(data),4],int)
    for i in range(len(data)):
        coords[i,0] = int(data[i][0]) # x0
        coords[i,1] = int(data[i][1]) # y0
    return coords



#reads the output from binned clustering
def readTokenIDFile(fn):
    if os.path.exists(fn) == False:
        print "[warn] file could not be opened: ",fn
        return []
    f    = file(fn, "r")
    data = [line.split() for line in f]
    f.close()
    tID = zeros([len(data)],int)
    for i in range(len(data)):
        tID[i] = int(data[i][0])
    return tID

#================= BOOK CLASS ===============
#== Object that represents the book structure ==
class Book:
    
    # default constructor
    def __init__(self):
        self.bookDir  = "" # path of the book directory
        self.pageSize = [21.0,29.7] # paper size in cm
        self.tokenDir = "" # token directory
        self.tokens   = {} # token [ID, file name]
        self.fontDir  = "" # path to the ttf font files
        self.fonts    = {} # fonts [ID, font file name]

    # ocrodir path is given to constructor; directory tree is parsed automatically
    def __init__(self, path):
        self.bookDir  = path
        self.pageSize = [21.0,29.7] # paper size in cm
        self.tokenDir = path+"/tokens/" 
        self.tokens   = {} # token[ID] = file name
        self.fontDir  = path+"/fonts/" # path to the ttf font files
        self.fonts    = {} # fonts [ID, font file name]
        self.update()
    
    # parse directory tree
    def update(self):
        # get line image list
        self.pages = []
        fileList = os.listdir(self.bookDir) 
        # filelist is unsorted, that's why pages need to be sorted afterwards
        for f in fileList:
            if(len(f)==8 and f[len(f)-4:len(f)] == ".png"): # FIXME joost,
                if(os.path.exists(self.bookDir+"/"+f.split(".")[0])): #whitespace page check
                    p = Page(self.bookDir+"/"+f)
                    self.pages.append(p)
        self.sortPages()
        self.readTokens()
        self.readFonts()
    
    # sort pages
    def sortPages(self):
        oldMinPage = -1
        for i in range(len(self.pages)):
            minLine = 10000
            minIndex = -1
            for j in range(len(self.pages)):
                if (self.pages[j].number < minLine and self.pages[j].number > oldMinPage):
                    minLine = self.pages[j].number
                    minIndex = j
            if minIndex == -1:
                print("[err] Book::sortPages: Error sorting the page!")
                break
            p = self.pages[minIndex]
            self.pages[minIndex]=self.pages[i]
            self.pages[i]=p
            oldMinPage = minLine
    
    # read token dir in book structure to book object
    def readTokens(self):
        # check if token path exists; (may be missing if clustering fails)
        if (os.path.exists(self.tokenDir) == False):
            print("[warn] No token directory found in %s" %(self.bookDir))
            return;
        fileList = os.listdir(self.tokenDir)
        for f in fileList:
            if(f.split(".")[0]):
                #self.tokens.append([int(f[0:len(f)-4]), self.tokenDir+f])
                self.tokens[int(f[0:len(f)-4])] = self.tokenDir+f
                
    # read font dir in book structure to book object
    def readFonts(self):
        # check if token path exists; (may be missing if clustering fails)
        if (os.path.exists(self.fontDir) == False):
            print("[warn] No font directory found in %s" %(self.bookDir))
            return;
        fileList = os.listdir(self.fontDir)
        for f in fileList:
            if(f.split(".")[0] and f[len(f)-4:len(f)]==".ttf"):
                #self.tokens.append([int(f[0:len(f)-4]), self.tokenDir+f])
                self.fonts[int(f[4:len(f)-4])] = self.fontDir+f
    
    # print the book information to stdout
    def output(self):
        print("bookDir         = %s" %(self.bookDir))
        print("Number of pages = %d" %(len(self.pages)))
        for i in range(len(self.pages)):
            print("Page %d" %(i))
            self.pages[i].output()
    
    def getTokens(self):
        return tokens
    
    def checkTokenable(self):
        for page in self.pages:
            if (page.checkTokenable() == False or
                len(self.tokens) <= 0):
                return False;
        return True;
    
    def checkTokenPresence(self):
        return (len(self.tokens)>0)
        
    def checkFontPresence(self):
        return (len(self.fonts)>0)




#================= PAGE CLASS ===============

# child of book object, each book has n pages. Corresponds to OCRopus book structure
class Page:
    # default constructor
    def __init__(self):
        self.number   = -1 # page number
        self.image    = "" # original image file name
        self.binImage = "" # binarized image file name
        self.pageDir  = "" # path containing the page information
        self.lineBoxs = "" # file containing the page to line segm. information
        self.linesPos = [] # position of lines
        self.lines    = [] # list of lines

    # constructor with file name, e.g. bookDIR/0001.png
    def __init__(self, imgFN):
        # filename given
        if ((imgFN[len(imgFN)-4:len(imgFN)]).lower()==".png"): # FIXME joost,
            self.image    = imgFN # original image file name
            self.number   = int(imgFN[len(imgFN)-8:len(imgFN)-4]) # FIXME joost,
            self.binImage = imgFN[0:len(imgFN)-4]+".bin.png" # FIXME joost,
            self.lineBoxs = imgFN[0:len(imgFN)-4]+".pseg.txt" # FIXME joost,
            self.pageDir  = imgFN[0:len(imgFN)-4]+"/" # FIXME joost,
            self.update()
        # output error message
        else:
            print("[err] Page::fromOcroDir: Error: expected PNG file as input!")
            return
    
    # print page information to std out
    def output(self):
        print("  image      = %s" %(self.image))
        print("  binImage   = %s" %(self.binImage))
        print("  pageNumber = %d" %(self.number))
        print("  num. lines = %d" %(len(self.lines)))
        print("  pageDir    = %s" %(self.pageDir))
        for i in range(len(self.lines)):
            print("    Line %d" %(i))
#            self.lines[i].output()#Hasan: commented this line

    # read the page information from the directory structure
    def update(self):
        # get line image list
        if(not os.path.exists(self.pageDir)):
            return #ocropus does not genereate dir for whitespace page
        self.lines = []
        self.linesPos = readBoxFile(self.lineBoxs)
        fileList = os.listdir(self.pageDir)
        for f in fileList:
            if(len(f) == 10 and f[len(f)-4:len(f)] == ".png"): # FIXME joost,
                l = Line(self.pageDir + f)
                self.lines.append(l)
        self.sortLines()


    # sort lines
    def sortLines(self):
        oldMinLine = -1
        for i in range(len(self.lines)):
            minLine = 1000000000000
            minIndex = -1
            for j in range(len(self.lines)):
                if (self.lines[j].number < minLine and self.lines[j].number > oldMinLine):
                    minLine = self.lines[j].number
                    minIndex = j
            if minIndex == -1:
                print("Book::sortPages: Error sorting the lines!") # FIXME joost,
                break
            p = self.lines[minIndex]
            self.lines[minIndex]=self.lines[i]
            self.lines[i]=p
            oldMinLine = minLine
    
    # verify if the page is tokenable
    def checkTokenable(self):
        for line in self.lines:
            if (line.checkTokenable() == False):
                return False;
        return True;

    # verify if the page if fontable
    def checkFontable(self):
        for line in self.lines:
            if (line.checkFontable() == False):
                return False;
        return True;





#================= LINE CLASS ===============

#child of page, every page contains x lines. Corresponds to OCRopus structure
class Line:
    def __init__(self):
        self.number   = -1 # page number
        self.image    = "" # original image file name
        self.ccs      = [] # connected components
        self.txtAll   = [] # text in text line
        self.txt      = [] # text of the characters (removing spaces etc. from txt)
        self.tokenIDs = [] # token IDs in line
        self.tokenFile= "" # tokenID File
        self.bboxFile = "" # file name of connected component
        self.textFile = "" # name of the file containing the line text
        self.csegFile = "" # name of the file containing the line image
        self.fontIDs  = [] # font IDs for single characters
        self.fontFile = "" # font File containing information for each character in line what font to use
        self.shiftFile= "" # file containing the shift information for each text-line
        self.baseLineY= 0  # relative height of the baseline
        self.fontHeight= 50 # default font height for 12 pts in 300dpi = 50 px
        self.words    = [] # list of strings
        self.wordPos  = [] # list of quadruples of word bounding boxes
        self.wordFont = [] # font ID to be used to render the word (only available for fontable books)
        
        
    # constructor with file name, e.g. bookDIR/0001/0001.png
    def __init__(self, imgFN):
        # filename given
        if ((imgFN[len(imgFN)-4:len(imgFN)]).lower()==".png"):
            self.image    = imgFN # original image file name
            #self.number   = toHex(imgFN[len(imgFN)-10:len(imgFN)-4])
            self.number   = int((imgFN[len(imgFN)-10:len(imgFN)-4]),16) # FIXME joost,
            self.textFile = imgFN[0:len(imgFN)-4]+".txt"
            self.tokenFile= imgFN[0:len(imgFN)-4]+".tokID.txt" # text in text line # FIXME joost, might change to tokID
            self.bboxFile = imgFN[0:len(imgFN)-4]+".cseg.txt"
            self.csegFile = imgFN[0:len(imgFN)-4]+".cseg.png"
            self.fontFile = imgFN[0:len(imgFN)-4]+".fontID.txt"
            self.shiftFile= imgFN[0:len(imgFN)-4]+".shifts.txt"
            self.baseLineY= 0  # relative height of the baseline
            self.fontHeight= 50 # default font height for 12 pts in 300dpi = 50 px
            self.update()
        # output error message
        else:
            print("Page::fromOcroDir: Error: expected PNG file as input!")
            return
    
    # print page information to std out
    def output(self):
        print("====================")
        print("    image      = %s" %(self.image))
        print("    page number= %x" %(self.number))
        print("    text       = %s" %(self.txt))
        print("    num. bboxs = %d" %(len(self.ccs)))
        print("    num. tokIDs= %d" %(len(self.tokenIDs)))
        print("    bboxFile   = %s" %(self.bboxFile))
        print("    fontFile   = %s" %(self.fontFile))
        print("    shiftFile  = %s" %(self.shiftFile))
        print("    words      = %s" %(self.words))
        print("--------------------")


    # update position of connected components with shift corrections
    def updateCC(self):
        if(os.path.exists(self.image)):
            shifts = readShiftFile(self.shiftFile)
            if len(shifts)==0: return #IF NO SHIFT FILE FOR LINE THEN DO NOTHING
            if (len(shifts) != len(self.ccs)-1):
                print("[warn] Line::updateCC: Warning: number of ccs and number of shifts do not match!")
                return
            for i in range(len(shifts)):
                self.ccs[i,0] += shifts[i,0]
                self.ccs[i,1] += shifts[i,1]
                self.ccs[i,2] += shifts[i,0]
                self.ccs[i,3] += shifts[i,1]
    
    # compute the relative y position of the base line
    def updateBaseLine(self):
        y0 = []
        baseLineChars = ['a','b','c','d','e','f','h','i','k','l','m','n','o','r','s','t','u','v','w','x','z',
                         'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                         '1','2','3','4','5','6','7','8','9','0']
        for i in range(len(self.txt)):
            found = False
            for blChr in baseLineChars:
                if(blChr in self.txt[i]):
                    found = True
                    break
            if found==True:
                y0.append(self.ccs[i,1])
        self.baseLineY = median(y0)
     
    # generate self.txt containing no whitespaces (' ','\n')
    def updateTXT(self):
        self.txt=[]
        for i in range(len(self.txtAll)):
            if (self.txtAll[i] != ' ' and
                self.txtAll[i] != '\n'):
                  self.txt.append(self.txtAll[i])
    
    
    # compute the font size in pixels from the characters in the text-line
    def updateFontHeight(self):
        aChrH = [] # heights of ascender characters
        dChrH = [] # heights of descender characters
        xChrH = [] # heights of xheight characters
        AscenderChars = ['b','d','f','h','k','l','t','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                         '1','2','3','4','5','6','7','8','9','0']
        DescenderChars = ['g','j','p','q','y']
        XHeightChars = ['a','c','e','m','n','o','r','s','u','v','w','x','z']
        for i in range(len(self.txt)):
            found = False
            # check if self.txt[i] is an ascender character
            for c in AscenderChars:
                if(c in self.txt[i]):
                    found = True
                    break
            if found==True:
                aChrH.append(self.ccs[i,3])
                continue
            # check if self.txt[i] is an descender character
            for c in DescenderChars:
                if(c in self.txt[i]):
                    found = True
                    break
            if found==True:
                dChrH.append(self.ccs[i,1])
                continue
                # check if self.txt[i] is an descender character
                
            for c in XHeightChars:
                if(c in self.txt[i]):
                    found = True
                    break
            if found==True:
                xChrH.append(self.ccs[i,3])
                continue
        # avoid crash when no ascender or descender was found
        # if no ascender or descender was found take twice the current line height as font height
        if len(aChrH) == 0 and len(dChrH)==0:
            self.fontHeight = median(xChrH)*1.5
        # if either an ascender or a descender was wound use 1.5 x size as lineHeight
        if len(aChrH) == 0 and len(dChrH)>0:
            print self.ccs, shape(self.ccs), shape(self.ccs)[1]
            self.fontHeight = median(xChrH)*1.5
        if len(aChrH) > 0 and len(dChrH)==0:
            self.fontHeight = median(xChrH)*1.5
        if len(aChrH) > 0 and len(dChrH)>0:
            self.fontHeight = median(aChrH) - median(dChrH)
	#self.fontHeight = self.fontHeight*0.95
    
    # segment the string into words and generate font information on word level
    def updateWords(self):
        self.words   = [] # list of strings
        self.wordPos = [] # list of quadruples of word bounding boxes
        self.wordFont= [] # font IDs to render the words (only available in fontable mode)
        startIndex = 0
        endIndex   = len(self.txtAll)
        nextSepIndex = startIndex+1;
        numSpaces = 0
        while(startIndex<endIndex):
            while (nextSepIndex < endIndex and
                  self.txtAll[nextSepIndex] != ' ' and
                  self.txtAll[nextSepIndex] != '\n'):
                  nextSepIndex = nextSepIndex+1
            word = ""
            for k in range(startIndex,nextSepIndex):
                word = word + self.txtAll[k]
            pos = [min(self.ccs[startIndex-numSpaces:nextSepIndex-numSpaces,0]),
                   min(self.ccs[startIndex-numSpaces:nextSepIndex-numSpaces,1]),
                   max(self.ccs[startIndex-numSpaces:nextSepIndex-numSpaces,2]),
                   max(self.ccs[startIndex-numSpaces:nextSepIndex-numSpaces,3])]
            font = median(self.fontIDs[startIndex-numSpaces:nextSepIndex-numSpaces])
            numSpaces = numSpaces + 1
            startIndex = nextSepIndex+1
            nextSepIndex = startIndex+1
            self.words.append(word)
            self.wordPos.append(pos)
            self.wordFont.append(font)
    
    # read the page information from the directory structure
    def update(self):
        # read text from file
        self.txtAll   = readFile(self.textFile)
        self.ccs      = readBoxFile(self.bboxFile)
        self.tokenIDs = readTokenIDFile(self.tokenFile)
        self.fontIDs  = readTokenIDFile(self.fontFile)
        self.updateCC();
        if self.checkTextable() == True:
            self.updateTXT();
            self.updateWords();
            self.updateFontHeight()
            self.updateBaseLine()
            print("[info] relative y0 position of the base-line = %g" %(self.baseLineY))



    # checks if the font information is complete
    def checkFontable(self):
        return (os.path.exists(self.image) and 
                os.path.exists(self.textFile) and
                os.path.exists(self.fontFile) and
                os.path.exists(self.bboxFile) and
                os.path.exists(self.csegFile))

    # checks if the line information is complete
    def checkTokenable(self):
        return (os.path.exists(self.image) and 
                os.path.exists(self.textFile) and
                os.path.exists(self.tokenFile) and
                os.path.exists(self.bboxFile) and
                os.path.exists(self.csegFile))

    # checks if the text information is complete
    def checkTextable(self):
        return (os.path.exists(self.image) and 
                os.path.exists(self.textFile) and
                os.path.exists(self.bboxFile) and
                os.path.exists(self.csegFile))
		



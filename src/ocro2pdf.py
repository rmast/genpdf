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
# File: ocro2pdf
# Purpose: Convert OCROpus directory to PDF file
# Responsible: Joost van Beusekom (joost@iupr.org)
# Reviewer: 
# Primary Repository: 
# Web Sites: www.iupr.org, www.dfki.de

import os, glob, string, sys, time, getopt, commands, math, numpy, datetime, platform, tempfile
from ocrodir import *
import codecs
from numpy import *
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.units import inch
from cStringIO import StringIO # "cStringIO" is faster, but if you need to subclass, use "StringIO" 

# global variables:
verbose     = 0         # output debugging information
dpi         = 200       # resolution of the ouput images in the pdf


# ========= ImagePDF =========

def convert2ImagePDF(bookDir,pdfFileName,b,pdf):
    global verbose
    # aspect/ratio of the pdf page to be generated
    ar = float(b.pageSize[0])/float(b.pageSize[1])
    # generate PDF
    for i in range(len(b.pages)):
        if(verbose>0):
            print("Processing page %d" %(b.pages[i].number))
        img = Image.open(b.pages[i].image)
        # width and height of the document image in pixels
        W = float(img.size[0])
        H = float(img.size[1])
        # fit document image to PDF page maximizing the displayed area
        if(W/H > ar):
            width = float(b.pageSize[0]) # width of the page in cm
            height= width/(W/H) # height od the page in cm
            if(verbose > 2):
                print(W/H, ar, width, height)
            pdf.drawInlineImage(img, 0,0,width*cm,height*cm) # use inline as each page is used only once
        if(W/H <= ar):
            height= float(b.pageSize[1])
            width = height/(W/H)
            if(verbose > 2):
                print(W/H, ar, width, height)
            pdf.drawInlineImage(img, 0,0,width*cm,height*cm) # use inline as each page is used only once
        
        pdf.showPage() # finish PDF page
    pdf.save() # save PDF to sile


# ========= Image with underlaid Text PDF =========

def convert2ImageTextPDF(bookDir,pdfFileName,b,pdf):
    global dpi
    # aspect/ratio of the pdf page to be generated
    ar = float(b.pageSize[0])/float(b.pageSize[1])
    for i in range(len(b.pages)):
        if(verbose > 0):
            print("Processing page %d" %(b.pages[i].number))
        # put image
        img = Image.open(b.pages[i].image)
        # width and height of the document image in pixel
        W = float(img.size[0])
        H = float(img.size[1])
        # fit document image to PDF page maximizing the displayed area
        factor = 0.0
        if(W/H > ar):
            width = float(b.pageSize[0]) # width of the page in cm
            height= width/(W/H)
            factor = b.pageSize[0]/W

        if(W/H <= ar):
            height= float(b.pageSize[1])
            width = height/(W/H)
            factor = b.pageSize[1]/H
        resizeW = (1.0/2.54)*width*dpi # width of the image after resizing
        resizeH = (1.0/2.54)*height*dpi # height of the image after resizing 
        if(verbose > 1):
            print("Size before %d x %d and after %d x %d" %(W,H,resizeW,resizeH))
            
        # put text
        # change text color to white
        pdf.setFillColorRGB(1.0,1.0,1.0)
        for j in range(len(b.pages[i].lines)): # j is the object of each line in book class
            numSpaces = 0;
            if (not b.pages[i].lines[j].checkTextable()):
                continue
            
            
            startIndex = 0
            endIndex   = len(b.pages[i].lines[j].txt)
            nextSepIndex = startIndex+1;
            while(startIndex<endIndex):
                while (nextSepIndex < endIndex and
                      b.pages[i].lines[j].txt[nextSepIndex] != ' ' and
                      b.pages[i].lines[j].txt[nextSepIndex] != '\n'):
                      nextSepIndex = nextSepIndex+1
                word = ""
                for k in range(startIndex,nextSepIndex):
                    word = word + b.pages[i].lines[j].txt[k]
                wordPos = b.pages[i].linesPos[j] + b.pages[i].lines[j].ccs[startIndex-numSpaces]
                if(verbose > 3):
                    print ccPos
                
                pdf.drawString(wordPos[0]*factor*cm, 
                                wordPos[1]*factor*cm, word)
                numSpaces = numSpaces + 1
                startIndex = nextSepIndex+1
                nextSepIndex = startIndex+1
            # what follows is the old code that puts each character as a single string
            # this posed some issues when searching for words
            #for k in range(len(b.pages[i].lines[j].txt)):
                #if (b.pages[i].lines[j].txt[k]==unicode(' ') or 
                    #b.pages[i].lines[j].txt[k]==unicode('\n')):
                    #numSpaces += 1
                    #continue
                #pdf.setFont("Helvetica", 10)
                #ccPos = b.pages[i].linesPos[j] + b.pages[i].lines[j].ccs[k-numSpaces]
                #if(verbose > 3):
                    #print ccPos
                
                #pdf.drawString(ccPos[0]*factor*cm, 
                               #ccPos[1]*factor*cm, b.pages[i].lines[j].txt[k])
        
        # put image over the text
        pdf.drawInlineImage(img.resize((int(round(resizeW)),int(round(resizeH)))), 0,0,width*cm,height*cm) # use inline as each page is used only once
        pdf.showPage() # finish PDF page
    pdf.save() # save PDF to file
            



# ========= Image with underlaid Text and tokenized image PDF =========
# FIXME joost, add underlaid text to pdf
def convert2TokenPDF(bookDir,pdfFileName,b,pdf):
    global dpi
    # aspect/ratio of the pdf page to be generated
    ar = float(b.pageSize[0])/float(b.pageSize[1])
    tokens=[]
    for i in range(len(b.pages)):
        if(verbose > 1):
            print("Processing page %d" %(b.pages[i].number))
        # put image
        img = Image.open(b.pages[i].image)
        
        # width and height of the document image in pixel
        W = float(img.size[0])
        H = float(img.size[1])
        # fit document image to PDF page maximizing the displayed area
        factor = 0.0
        if(W/H > ar):
            width = float(b.pageSize[0]) # width of the PDF page in cms
            height= width/(W/H)
            factor = b.pageSize[0]/W
        if(W/H <= ar):
            height= float(b.pageSize[1])
            width = height/(W/H)
            factor = b.pageSize[1]/H
        resizeW = (1.0/2.54)*width*dpi # width of the image after resizing
        resizeH = (1.0/2.54)*height*dpi # height of the image after resizing
        #print("Size before %d x %d and after %d x %d" %(W,H,resizeW,resizeH))
        
        # put text
        pdf.setFillColorRGB(1.0,1.0,1.0)
        #print "length of lines",len(b.pages[i].lines)
        for j in range(len(b.pages[i].lines)): # iterate through all pages
            if(b.pages[i].lines[j].checkTokenable() == False or
               b.pages[i].lines[j].checkTextable() == False): continue
            numSpaces = 0;
            # first: put text
            startIndex = 0
            endIndex   = len(b.pages[i].lines[j].txt)
            nextSepIndex = startIndex+1;
            while(startIndex<endIndex):
                while (nextSepIndex < endIndex and
                      b.pages[i].lines[j].txt[nextSepIndex] != ' ' and
                      b.pages[i].lines[j].txt[nextSepIndex] != '\n'):
                      nextSepIndex = nextSepIndex+1
                word = ""
                for k in range(startIndex,nextSepIndex):
                    word = word + b.pages[i].lines[j].txt[k]
                wordPos = b.pages[i].linesPos[j] + b.pages[i].lines[j].ccs[startIndex-numSpaces]
                if(verbose > 3):
                    print ccPos
                
                pdf.drawString(wordPos[0]*factor*cm, 
                                wordPos[1]*factor*cm, word)
                numSpaces = numSpaces + 1
                startIndex = nextSepIndex+1
                nextSepIndex = startIndex+1
            # second: put tokens
            for k in range(len(b.pages[i].lines[j].tokenIDs)): 
                #check if token is already present
                tokenIndex = -1;
                tokenIndex = b.pages[i].lines[j].tokenIDs[k]
                # FIXME joost,comment XO yO ccPOS
                X0 = b.pages[i].linesPos[j,0]+b.pages[i].lines[j].ccs[k,0]
                Y0 = H-(b.pages[i].linesPos[j,1]+b.pages[i].lines[j].ccs[k,1])
                ccPos = b.pages[i].linesPos[j] + b.pages[i].lines[j].ccs[k]

                # width and height of cc in PDF units
                ccWidth = factor*(b.pages[i].lines[j].ccs[k,2]-b.pages[i].lines[j].ccs[k,0])
                ccHeight= factor*(b.pages[i].lines[j].ccs[k,3]-b.pages[i].lines[j].ccs[k,1])
                
                ccW = (1.0/2.54)*ccWidth*dpi*0.5
                ccH = (1.0/2.54)*ccHeight*dpi*0.5
                #pdf.drawString(ccPos[0]*factor*cm, 
                               #ccPos[1]*factor*cm, b.pages[i].lines[j].txt[k])
                if(ccW >= 1 and ccH >= 1):
                    f = b.tokens[tokenIndex]
                    img = Image.open(f)
                    pdf.drawInlineImage(img, 
                                ccPos[0]*factor*cm,ccPos[1]*factor*cm,
                                ccWidth*cm,ccHeight*cm)
                
        pdf.showPage() # finish PDF page
    pdf.save() # save PDF to file



  # FIXME joost, reintergrate this code
        # put text
        # change text color to white
        #pdf.setFillColorRGB(1.0,1.0,1.0)
        #for j in range(len(b.pages[i].lines)):
            #numSpaces = 0;
            #for k in range(len(b.pages[i].lines[j].txt)):
                #if (b.pages[i].lines[j].txt[k]==unicode(' ')):
                    #numSpaces += 1
                    #continue
                #pdf.setFont("Helvetica", 10)
                ##print "linePos: ", b.pages[i].linesPos[j]
                ##print "ccsPos: ",b.pages[i].lines[j].ccs[k-numSpaces]
                ##print "\"",b.pages[i].lines[j].txt[k-numSpaces],"\""
                #ccPos = b.pages[i].linesPos[j] + b.pages[i].lines[j].ccs[k-numSpaces]
                #print ccPos
                
                #pdf.drawString(ccPos[0]*factor*cm, 
                               #ccPos[1]*factor*cm, b.pages[i].lines[j].txt[k])
        
        ## put image over the text
        #pdf.drawInlineImage(img.resize((resizeW,resizeH)), 0,0,width*cm,height*cm) # use inline as each page is used only once
        #pdf.showPage() # finish PDF page
    #pdf.save() # save PDF to sile


# read args, opts and process
def main(sysargv):
    # make global variables available
    global verbose 
    global dpi
    pdfOutputType = 1
    bookDir = ""
    pdfFileName  = ""
    pageWidth  = 21.0; # default page width, DIN A4
    pageHeight = 29.7; # default page height, DIN A4
    # parse command line options
    if len(sysargv) == 1:
        usage(sysargv[0])
        sys.exit(0)    
    try:
        optlist, args = getopt.getopt(sysargv[1:], 'ht:d:p:W:H:v:r:', ['help','type=','dir=','pdf=','width=','height=','verbose=','resolution='])
        #print(optlist, args)
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in optlist:
        if o in ("-h", "--help"):
            usage(sysargv[0])
            sys.exit(0)
        if o in ("-t", "--type"):
            pdfOutputType = int(a)
        if o in ("-W", "--width"):
            pageWidth = float(a)
        if o in ("-H", "--height"):
            pageHeight = float(a)
        if o in ("-d", "--dir"):
            bookDir = a
        if o in ("-p", "--pdf"):
            pdfFileName = a
        if o in ("-v", "--verbose"):
            verbose = int(a)
        if o in ("-r", "--resolution"):
            dpi = int(a)

    
    # read ocrodir book directory
    if (len(bookDir)>0 and bookDir[len(bookDir)-1]!='/'):
        bookDir = bookDir+'/'
    b = Book(bookDir)
    if(verbose>2):
        b.output()
    b.pageSize[0] = pageWidth
    b.pageSize[1] = pageHeight
    
    # generate PDF canvas with correct pagesize
    pdf = canvas.Canvas(pdfFileName,pagesize=(b.pageSize[0]/2.54*72.0,b.pageSize[1]/2.54*72.0))
    pdf.setAuthor("DECAPOD GenPDF")
    pdf.setTitle("Generated PDF")

    # read data file    
    if(pdfOutputType == 1):
        convert2ImagePDF(bookDir,pdfFileName,b,pdf)

    if(pdfOutputType == 2):
        convert2ImageTextPDF(bookDir,pdfFileName,b,pdf)

    if(pdfOutputType == 3):
        if(b.checkTokenPresence() == 1):
            convert2TokenPDF(bookDir,pdfFileName,b,pdf)
        else:
            print("[warn] No tokens found! Book structure is not tokenable. Switching to type 2 mode!")
            convert2ImageTextPDF(bookDir,pdfFileName,b,pdf)
    


# print help information
def usage(progName):
    print "\n%s [OPTIONS] -dir ocroDir -pdf out.pdf\n\n"\
          "   -d, --dir          Ocropus Directory to be converted\n"\
          "   -p, --pdf          PDF File that will be generated\n"\
          " Options:\n"\
          "   -h, --help:        print this help\n"\
          "   -v, --verbose:     verbose level [0,1,2,3]\n"\
          "   -t, --type:        type of the PDF to be generates:\n"\
          "                          1: image only [default]\n"\
          "                          2: recognized text overlaid with image\n"\
          "                          3: tokenized\n"\
          "   -W, --width:       width of the PDF page [in cm] [default = 21.0]:\n"\
          "   -H, --height:      height of the PDF page [in cm] [default = 29.7]:\n"\
          "   -r, --resolution:  resolution of the images in the PDF [default = 200dpi]\n"\


if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)










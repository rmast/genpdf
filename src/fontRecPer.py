#!/usr/bin/python
# (C) 2012 University of Kaiserslautern 
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
# File: fontRecPer.py
# Purpose: Extract glyph info from reconstructed TTF file and compute performance matrices between the original and the reconstructed font.
# Creator: Hasan S. M. Al-Khaffaf (hasan@iupr.com)
# Reviewer: 
# Primary Repository: 
# Web Sites: www.iupr.com




from builtins import chr
from builtins import str
from builtins import range
from past.utils import old_div
from ocrodir import *
import fontforge
from optparse import OptionParser 
from PIL import Image, ImageDraw
#from pdfrw import PdfReader

def fontAnalysis():
#    x = PdfReader("/home/hasan/Desktop/ClearScan/book[t1][ClearScan].pdf")
##    x = PdfReader("/home/hasan/1-5-1[t4].pdf")
#    print "Pagecount= %i "% (len(x.Root.Pages))
#    print "Kids[0] ", x.Root.Pages.Kids[0]
#    return 
    
    print("Testing fontforge")
    fontforge.setPrefs("PreferPotrace", 1)
    fontforge.setPrefs("AutotraceAsk", "-O 0.5 -u 1 -t 1")
    font = fontforge.open("/home/hasan/Desktop/ClearScan/fnt179.cff")
    for i in font.glyphs():
        print("encoding %s"% chr(i.encoding))
#        if i.encoding >=0x30 and i.encoding <= 0x80:
        i.export("/home/hasan/Desktop/ClearScan/chr/"+chr(i.encoding)+".png")
#        print font.ndEncodingSlot()
    return 
    glyphA = font["C"]
    foreground = glyphA.foreground
    for i in range(len(foreground)):
#        print "background[%i] = %s"%(i, glyphA.background,)
        print("foreground[%i] = %s"%(i, foreground[i],))
        print("len(foreground[%i]) = %s"%(i, len(foreground[i])))
        print("foreground[%i].closed = %s"%(i, str(foreground[i].closed==True)))
        print("foreground[%i].spiro = %s\n"%(i, str(foreground[i].spiro)))
        print("foreground[%i].spiro[0] = %s\n"%(i, str(foreground[i].spiro[0])))
        glyphA.export("/home/hasan/Desktop/C.png")
#        spiro = foreground[i].spiro[0]
#        spiro = (spiro[0]+1,spiro[1], spiro[2], spiro[3])
#        foreground[i]= foreground[i]
#        print "foreground[%i].spiro[0] = %s\n"%(i, str(foreground[i].spiro[0]))
#    contour = fontforge.contour()
#    glyphA.autoTrace()
#    glyphA.simplify(0.1, ("ignoreextrema", "ignoreslopes", "nearlyhvlines", "forcelines", "setstarttoextremum"))
#    glyphB = font["B"]
#    glyphB.simplify(0.1, ("ignoreextrema", "ignoreslopes", "nearlyhvlines", "forcelines", "setstarttoextremum"))
    font.save("/home/hasan/Desktop/font01.ttf")
    
#########################################################3
    x = PdfReader("/home/hasan/ClearScan/book[t1][ClearScan].pdf")
    print("Pagecount= %i "% (len(x.Root.Pages)))
    print("Kids[0] ", x.Root.Pages.Kids[0])
    return 

def initFontForge():
    fontforge.setPrefs("PreferPotrace", 1)
    fontforge.setPrefs("AutotraceAsk", "-O 0.5 -u 1 -t 1")
    return

def loadFont(fontName):
    if os.path.isfile(fontName):
        return fontforge.open(fontName)
    else:
        print("[fatal Error]: The file '%s' does not exist or is not a file"%fontName)
        return None

def loadGlyphs(font):
    allchars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    glyphDict = {}
    encoding = []
    for i in font.glyphs():
#        print i.encoding
        if len(str(i.encoding)) == 2:
            encoding.append(i.encoding)
    for i in allchars:
#        if ord(i) in encoding:
        if i in font:
            print(i)
            glyph = font[i]
            glyphDict[i] = glyph
    return glyphDict

def rasterizeGlyphs(glyphDict, bookPath, fontFolder):
#    global capLetters
#    global smallLetters 
    ofontPath = bookPath + fontFolder
    if not os.path.exists(ofontPath):
        os.makedirs(ofontPath)
#    capLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#    smallLetters = "abcdefghijklmnopqrstuvwxyz"
#    digits = "0123456789"
#    allchars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    glyphNameDict = {}
    for i in list(glyphDict.keys()):
        glyphFileName = ofontPath+i+".png"
        print(glyphFileName)
        glyphDict[i].export(glyphFileName)
        if not os.path.isfile(glyphFileName):
            del glyphDict[i]
        glyphNameDict[i] = glyphFileName
    return glyphNameDict

def loadRastGlyphs(glyphNameDict):
    glyphImageDict = {}
    for i in list(glyphNameDict.keys()):
#        print i
        image = Image.open(glyphNameDict[i])
        glyphImageDict[i] = image
    return glyphImageDict

def loadRastGlyphs1(glyphNameDict):
    glyphImageDict = {}
    for i in list(glyphNameDict.keys()):
#        print i
        image = Image.open(glyphNameDict[i])
        glyphImageDict[i] = image.convert("RGB")
    return glyphImageDict

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
            r = image.getpixel((i,j))
            if r >= 128:
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
    return (x1, y1, x2+1, y2+1)


def cropAndResize(oImage, rImage):
    obbx = findBBox(oImage)
    rbbx = findBBox(rImage)

#    oImage.putpixel((obbx[0], obbx[1]), (128))
#    oImage.putpixel((obbx[2], obbx[3]), (128))
                    
#    rImage.putpixel((rbbx[0], rbbx[1]), (128))
#    rImage.putpixel((rbbx[2], rbbx[3]), (128))
    
#    oImage.show()
#    rImage.show()

    oImageCroped = oImage.crop(obbx)
    rImageCroped = rImage.crop(rbbx)

#    oImageCroped.show()
#    rImageCroped.show()

    oWidth, oHeight = oImageCroped.size
    rWidth, rHeight = rImageCroped.size
    if oWidth * oHeight > rWidth * rHeight:
        rImageCropedResized = rImageCroped.resize((oWidth, oHeight))
        oImageCropedResized = oImageCroped
    else:
        oImageCropedResized = oImageCroped.resize((rWidth, rHeight))
        rImageCropedResized = rImageCroped
    oWidth, oHeight = oImageCropedResized.size
    rWidth, rHeight = rImageCropedResized.size
    
    return (oImageCropedResized, rImageCropedResized)

def performance(oImageCR, rImageCR):
    oWidth, oHeight = oImageCR.size
    sum = 0
    for i in range(oWidth-1):
        for j in range(oHeight-1):
            op = oImageCR.getpixel((i,j))
            rp = rImageCR.getpixel((i,j))
            sum += (op - rp) * (op - rp)
    return old_div(sum, (oWidth * oHeight))

def reconstructedFontPerformanceIndex(oGlyphImageDict, rGlyphImageDict):
    performanceIndexDict = {}
    for i in list(oGlyphImageDict.keys()):
        if i in list(rGlyphImageDict.keys()):
            (oGlyphImageDict[i], rGlyphImageDict[i]) = cropAndResize(oGlyphImageDict[i], rGlyphImageDict[i])
            performanceIndexDict[i] = performance(oGlyphImageDict[i], rGlyphImageDict[i])
    return performanceIndexDict
    
def getPerformanceT4(performanceIndexDict, b, opt):
    psnr = 0.0
    accMSE = 0.0
    performanceIndexDictKeys  = list(performanceIndexDict.keys())
    mse = 0.0
#    print b.tokens
    for i in range(len(b.pages)):
        for j in range(len(b.pages[i].lines)):
            print("processing page %i, line %i"%(i,j))
            k = b.pages[i].lines[j]
                #bb = loadLineBB(k.ccs) # load BB for each char in the line into `bb` list
            if opt.verbose == 1:
                print("k.ccs= %s\n"%k.ccs)
                #tID = loadTokenID(k.tokenIDs) # load token ID into `tID` list
                print("k.txt= %s\n"%k.txt)
                print("k.tokenIDs= %s\n"%k.tokenIDs)
            #charImage = loadLineImage(k, opt)
#            z=0
            if k.ccs != []:
                for t in k.txt: # calculate performance using t (/tokens/`t`.png) matrix and its corresponding original image (.cseg.png) matrix
                    char = ord(t)
                    char = str(t)
                    if char in performanceIndexDictKeys:
                        mse = performanceIndexDict[char] #FIXME
                        accMSE += mse
                print("mse= %i"% mse)
#                z += 1
    print("***************")
    print("accMSE= %i"%(accMSE)) 
    print("***************")
#    psnr = 20.0 * log10(255.0/sqrt(accMSE))        
    return accMSE


def setImage(im):
    width, height = im.size
    for i in range(width-1):
        for j in range(height-1):
            im.putpixel((i,j), 0)
    return im


def loadLineImage(line, opt):
#    lineFileName = pageDir + "%02i"%int(page.number) + "%04h"%int(line.) + "%08i.png"%int(num)
    im = Image.open(line.image)
#    im = Image.open(line.csegFile)
    if opt.verbose==1:
        print((line.image,"\n"))
    return im

def findBBox1(image):
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
            if r <= 128:
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
    bb = findBBox1(tokImage)
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
    if opt.verbose ==1:
        print("tokImageCrop.mode, tokImageCrop.histogram", tokImageCrop.mode, tokImageCrop.histogram())
#    tokImageCropScaled.save("/home/hasan/Desktop/tokImageCropScaled.png")
    tokImageCropScaledPix = tokImageCropScaled.load() 
#    charImage = charImage.transpose(Image.FLIP_TOP_BOTTOM)
    charImagePix = charImage.load()
    charW, charH = charImage.size
# beginn uncomment    
##    charImage.putpixel((x1,(charH - y1 - 1)), (0,128,0))
##    charImage.putpixel((x2,(charH - y2 - 1)), (0,128,0))
   
#    tokImageCropScaled.show() #last test
#    print "tokImage.size=%s"%((tokImage.size),)
#    charImageCrop = charImage.crop([x1, charH-y2, x2, charH-y1])
    if opt.verbose == 1:
        print("charImageCrop.mode, charImageCrop.histogram", charImageCrop.mode, charImageCrop.histogram())
#    charImageCrop.save("/home/hasan/Desktop/charImageCrop.png")
#    charImage.show()
#    print "charImage.size=%s"%((charImage.size),)
# end uncomemnt    
    if opt.verbose == 1:
        print("tokImage.size=%s"%((tokImage.size),))
        print("tokImageCrop.size=%s"%((tokImageCrop.size),))
        print("tokImageCropScaled.size=%s"%((tokImageCropScaled.size),))
        print("charImage.size=%s\n"%((charImage.size),))
#    print  "xsize=%i"%xsize
#    print  "ysize=%i"%ysize
#    tokCopy = tokImageCropScaled.copy()
#    tokCopy = setImage(tokCopy)  
            
    xcpt = 0
    match=0
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
#                if r1 != r2: 
#                    tokCopy.putpixel((xt,yt), (0,0,0))
##                    xcpt += 1
#                else:
#                    tokCopy.putpixel((xt,yt), (255,255,255))
#                    match +=1
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
        print("[error] except#= %i, match#=%i"%(xcpt,match))
#    tokCopy.save("/home/hasan/Desktop/tok-org-diff.png")
    return (old_div(mse,((1.0 * xsize)*ysize)))
    
def getPerformance(oGlyphImageDict, b, opt):
    psnr = 0.0
    accMSE = 0.0
    mse = 0.0
    
    Llen = 58
    w = 0
    Achar = 47*54
    Evalue = 64*64
    LinperPage = 40
    oGlyphImageDictKeys = list(oGlyphImageDict.keys())
#    print b.tokens
    for i in range(len(b.pages)):
        print("%i: line/page= %i"%(i,len(b.pages[i].lines))) 
        for j in range(len(b.pages[i].lines)):
            k = b.pages[i].lines[j]
                #bb = loadLineBB(k.ccs) # load BB for each char in the line into `bb` list
#            if opt.verbose == 1:
            print("processing page %i, line %i"%(i,j))
            charImage = loadLineImage(k, opt)
            z=0
            if k.checkTextable():
                for t in k.txt: # calculate performance using t (/tokens/`t`.png) matrix and its corresponding original image (.cseg.png) matrix
    ###                tokImage = loadTokenImage(b.tokens[t], b.bookDir, opt)
                    if t in oGlyphImageDictKeys:
                        tokImage = oGlyphImageDict[t]
                        mse = MSE(tokImage, charImage, k.ccs[z], opt)
    ##                print "mse = %s"%mse
                        accMSE += mse
                        z += 1
            else:
#                for i in oGlyphImageDictKeys:
#                    size = oGlyphImageDict[i].size
                accMSE +=  Llen * w * (Achar) * (Evalue) # NumCharperLine * (0.25*sizeOfLetter_a) * (255-0)*(255-0)
        if i != 0 and i != len(b.pages)-1: # adding penalty to all missing lines of pages except 1st and last page
            if len(b.pages[i].lines) < LinperPage:
                accMSE += abs(LinperPage - len(b.pages[i].lines)) * Llen * w * (Achar) * (Evalue)
    
    print("***************")
    print("accMSE=%i"%(accMSE)) 
    print("***************")
#    psnr = 20.0 * log10(255.0/sqrt(accMSE))        
    return accMSE

#######################################################################
#def getPerformanceT4(oGlyphImageDict, b, opt):
#    psnr = 0.0
#    accMSE = 0.0
#    performanceIndexDictKeys  = performanceIndexDict.keys()
##    mse = 0.0
##    print b.tokens
#    for i in range(len(b.pages)):
#        for j in range(len(b.pages[i].lines)):
#            k = b.pages[i].lines[j]
#                #bb = loadLineBB(k.ccs) # load BB for each char in the line into `bb` list
#            if opt.verbose == 1:
#                print("k.ccs= %s\n"%k.ccs)
#                #tID = loadTokenID(k.tokenIDs) # load token ID into `tID` list
#                print("k.txt= %s\n"%k.txt)
#                print("k.tokenIDs= %s\n"%k.tokenIDs)
#            #charImage = loadLineImage(k, opt)
##            z=0
#            if k.ccs != []:
#                for t in k.txt: # calculate performance using t (/tokens/`t`.png) matrix and its corresponding original image (.cseg.png) matrix
#                    char = ord(t)
#                    char = str(t)
#                    if char in performanceIndexDictKeys:
#                        accMSE += performanceIndexDict[char] #FIXME
##                z += 1
#    print("***************")
#    print("accMSE= %i"%(accMSE)) 
#    print("***************")
##    psnr = 20.0 * log10(255.0/sqrt(accMSE))        
#    return accMSE
#############################################################################

def main():
#    fontAnalysis()
#    return 

    parser = OptionParser()
    parser.add_option("-d", "--directory", default="", dest="book", 
        type="string", help="Directory name for the book structure. The '/' will be added (if not there)")
    parser.add_option("-o", "--original", default=None, dest="ofont", type="string", 
        help="name of original font file (.ttf)")
    parser.add_option("-r", "--reconstructed", default=None, dest="rfont", type="string", 
        help="name of reconstructed font file (.ttf)")
    parser.add_option("-v", "--verbose", default=0, dest="verbose", type="int", 
        help="verbose type: 0 (silent) or 1 (detailed)")
    (opt, args) = parser.parse_args()
    if opt.book == "" or opt.ofont =="" or opt.rfont=="":
        print("Usage: ./fontRecPer.py -d bookDir/ -o font_name.ttf [-r font_name.ttf]")
        print("       if -r option is ommited, the bookDir/ is assumed to hold the book info of the reconstructed font in raster format")
        return 
    
    if opt.book[len(opt.book)-1] != '/':
        opt.book = opt.book + '/'
        
#    if os.path.isdir(opt.rfont):
#        rFontList = glob.glob(opt.rfont)
#    else:
#        rFontList = []

    print("Loading book structure ->")
    book = Book(opt.book) # Load the book structure
    print("<- Book structure loaded")
    
    initFontForge()
    ofont = loadFont(opt.ofont)
    if opt.rfont:
        rfont = loadFont(opt.rfont)
    else:
        rfont = None
    
    if ofont:
        oGlyphDict = loadGlyphs(ofont)
        if rfont:
            rGlyphDict = loadGlyphs(rfont)
        
        oGlyphNameDict = rasterizeGlyphs(oGlyphDict, opt.book, "ofont/")
        if rfont:
            rGlyphNameDict = rasterizeGlyphs(rGlyphDict, opt.book, "rfont/")
        
        if rfont:
            oGlyphImageDict = loadRastGlyphs(oGlyphNameDict)
            rGlyphImageDict = loadRastGlyphs(rGlyphNameDict)
        else:
            oGlyphImageDict = loadRastGlyphs1(oGlyphNameDict)
            
        if rfont:
            performanceIndexDict = reconstructedFontPerformanceIndex(oGlyphImageDict, rGlyphImageDict)
        if rfont:
            performance = getPerformanceT4(performanceIndexDict, book, opt)
        else:
            performance = getPerformance(oGlyphImageDict, book, opt)
    print("End-of-Program: fontRecper.py")
    return performance
    
if __name__ == "__main__":
    main()

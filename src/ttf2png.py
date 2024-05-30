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
# File: ttf2png.py
# Purpose: Create a database of glyphs from TTF file. The glyphs belongs to one font will be stored in a folder name f0000\, f0001\, etc and 
#            the files in the form a.png, b.png, etc
# Creator: Hasan S. M. Al-Khaffaf (hasan@iupr.com)
# Reviewer: 
# Primary Repository: 
# Web Sites: www.iupr.com



from builtins import chr
from builtins import str
from builtins import range
import fontforge
import glob, os
from optparse import OptionParser 
from PIL import Image
import json

#import numpy
#import scipy
#from scipy import ndimage


def loadFont(fontName):
    if os.path.isfile(fontName):
        return fontforge.open(fontName)
    else:
        print("[fatal Error]: The file '%s' does not exist or is not a file"% fontName)
        return None


def findContour(imageName):
    im = Image.open(imageName)
    im_contour = im.copy()
    imLoad = im.load()
#    print (0,0, im.getpixel((0,0)))
    for jj in range(im.size[1]-2): # Hasan: FIXME: contour pixels at image boundary is not handled well.
        for ii in range(im.size[0]-2):
            i = ii+1
            j = jj+1 
            if (imLoad[i,j]<=127) and (imLoad[i-1,j-1]>127 or imLoad[i-1,j]>127 or imLoad[i-1,j+1]>127 or imLoad[i,j-1]>127 or imLoad[i,j+1]>127 or imLoad[i+1,j-1]>127 or imLoad[i+1,j]>127 or imLoad[i+1,j+1]>127):
                im_contour.putpixel((i,j), 0)
            else:
                im_contour.putpixel((i,j), 255)
    im_contour.save(imageName)
    return im_contour


def createFontList(dir):
    imageFormats = [".ttf", ".pfb"] #FIXME: add more font file types supported by FontForge
    listFiltered = []
    list1 = glob.glob(dir + "*.*") 
    list1.sort()
    #filter the list by removing non-fonts
    for i in list1:
        foundFlag = 0
        # filter out non-fonts
        for j in imageFormats:
            if j == (i[len(i)-len(j):]).lower():
                foundFlag = 1
        if foundFlag == 1:
            listFiltered.append(i) 
    return listFiltered

def createFontDict(inDir, outDir, ext):
    fontList = createFontList(inDir)
    fontDict = {}
    c = 0
    for i in fontList:
        fontDict[c] = [i, outDir + '/' + chr(c) + '/']
        c += 1
    return fontDict

def createFontGlyphsFiles1(fontDict, outDir, ext, verbose, crop, candidateChar = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"):
    for i in list(fontDict.keys()):
        fontName = fontDict[i][0]
        glyphPath = outDir + "f%04d/"%i 
        font = loadFont(fontName)
        glyphsDict = {}
        for j in candidateChar:
            if not j in font:
                if verbose >0:
                    print("warn: '%s' is not in font '%s'"%(j, fontName))
                continue
            if verbose > 0:
                print("Processing char %s=%d"%(j,ord(j)))
            glyph = font[j]
            if not os.path.isdir(glyphPath):
                os.makedirs(glyphPath)
            fullPath = glyphPath + j + '.' + ext
            glyph.export(fullPath)
            if ext in ["bmp", "png"]:
                image = Image.open(fullPath)
                if crop:
                    bbx = findBBox(image)
                    image = image.crop(bbx)
                    image.save(fullPath)
                glyphsDict[j] = [fullPath, image]
        fontDict[i].append(glyphsDict)
    return fontDict
   
def createFontGlyphsFiles2(fontDict, outDir, ext, verbose, crop, candidateChar = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"):
    glyphsDic = {}
    for i in candidateChar:
        glyphPath = outDir + "%s/"%i
        if not os.path.isdir(glyphPath):
            os.makedirs(glyphPath)
        glyphsDic[i] = glyphPath
       
    for i in list(fontDict.keys()):
        fontName = fontDict[i][0]
#        glyphPath = outDir + "f%04d/"%i 
        font = loadFont(fontName)
#        glyphPathsList = []
        glyphsDict = {}
        for j in candidateChar:
            if not j in font:
                if verbose >0:
                    print("warn: '%s' is not in font '%s'"%(j, fontName))
                continue
            if verbose > 0:
                print("Processing char %s=%d"%(j,ord(j)))
            glyph = font[j]
#            if not os.path.isdir(glyphPath):
#                os.makedirs(glyphPath)
            fullPath = glyphsDic[j] + "%04d"%i + '.' + ext
            glyph.export(fullPath)
            if ext in ["bmp", "png"]:
                image = Image.open(fullPath)
                if crop:
                    bbx = findBBox(image)
                    image = image.crop(bbx)
                    image.save(fullPath)
                glyphsDict[j] = [fullPath, image]
        fontDict[i].append(glyphsDict)
    return fontDict
   
def getMaxDimOfAllGlyphs(fontDict):
    """ This function checks all glyphs and return the maximum width and the maximum height in the set of glyphs"""
    sizesList = []
    for i in list(fontDict.keys()):
#        print fontDict[i][2].values()
        sizesList += [x[1].size for x in list(fontDict[i][2].values())]
    maxv = [0,0]
    for i in sizesList:
        if i[0] > maxv[0]:
            maxv[0] = i[0]
        if i[1] > maxv[1]:
            maxv[1] = i[1]
    return maxv

# The 'maxSize' function is taken from: http://mail.python.org/pipermail/image-sig/2006-January/003724.html
def maxSize(image, maxSize, method = 3):
    """ im = maxSize(im, (maxSizeX, maxSizeY), method = Image.BICUBIC)

    Resizes a PIL image to a maximum size specified while maintaining
    the aspect ratio of the image. Similar to Image.thumbnail(), but allows
    usage of different resizing methods and does NOT modify the image in place."""

    imAspect = float(image.size[0])/float(image.size[1])
    outAspect = float(maxSize[0])/float(maxSize[1])

    if imAspect >= outAspect:
        #set to maxWidth x maxWidth/imAspect
        return image.resize((maxSize[0], int((float(maxSize[0])/imAspect) + 0.5)), method)
    else:
        #set to maxHeight*imAspect x maxHeight
        return image.resize((int((float(maxSize[1])*imAspect) + 0.5), maxSize[1]), method)
    
def resizeAllGlyphstoMax(fontDict, maxv, scale, filterStr, contourFlag):
    if filterStr == 'NEAREST':
        filterr = Image.NEAREST
    elif filterStr == 'BILINEAR':
        filterr = Image.BILINEAR
    elif filterStr == 'BICUBIC':
        filterr = Image.BICUBIC
    elif filterStr == 'ANTIALIAS':
        filterr = Image.ANTIALIAS
    for i in list(fontDict.keys()):
        for j in list(fontDict[i][2].keys()):
#            fontDict[i][2][j][1] = fontDict[i][2][j][1].resize(maxv, filterr) # resizing and stretching
            if scale:
                image = maxSize(fontDict[i][2][j][1], maxv, filterr)
            else:
                image = fontDict[i][2][j][1]
#            fontDict[i][2][j][1].thumbnail(maxv, filterr)
            image2 = Image.new("L", maxv, 255)
            pos = (maxv[0]-image.size[0]-(maxv[0] - image.size[0])//2, maxv[1]-image.size[1]-(maxv[1]-image.size[1]-(maxv[1] - image.size[1])//2)) # center the glyph horizontally and vertically inside the canvas
            if pos[0] < 0 or pos[1] < 0:
                print("Error: negative coordinates are not allowed ",pos)
            image2.paste(image, pos)
            fontDict[i][2][j][1] = image2
            fontDict[i][2][j][1].save(fontDict[i][2][j][0])
            if contourFlag:
                findContour(fontDict[i][2][j][0])
    return

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

def saveAsJSON(fontDict, outDir):
    dic ={}
    for i in list(fontDict.keys()):
        dic[i] = fontDict[i][0]
    str1 = json.dumps(dic)
    f = open(outDir + "train.json", 'w')
    f.write(str1 + '\n')
    f.close()
    return 

def saveAsTXT1(fontDict, outDir, candidateChar = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"):
    f = open(outDir + "train1.txt", 'w')
    for i in candidateChar:
        for j in list(fontDict.keys()):
            if i in fontDict[j][2]:
                f.write(str(j))
                f.write(";")
                f.write(fontDict[j][2][i][0])
                f.write("\n")
    f.close()
    return 

def saveAsTXT2(fontDict, outDir, candidateChar = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"):
    f = open(outDir + "train2.txt", 'w')
    for i in candidateChar:
        for j in list(fontDict.keys()):
            if i in fontDict[j][2]:
                f.write(str(ord(i)))
                f.write(";")
                f.write(fontDict[j][2][i][0])
                f.write("\n")
    f.close()
    return 

def main():
    parser = OptionParser()
    parser.add_option("-d", "--directory", default="", dest="inDir", 
        type="string", help="Directory name for the ttf font files. The '/' will be added (if not there)")
    parser.add_option("-o", "--output", default="", dest="outDir", type="string", 
        help="Directory name for the output files. The '/' will be added (if not there)")
    parser.add_option("-f", "--format", default="png", dest="format", type="string", 
        help="Format type: PNG (default), BMP, EPS, PDF, SVG")
    parser.add_option("-t", "--filter", default="ANTIALIAS", dest="filter", type="string", 
        help="Filter type: NEAREST, BILINEAR, BICUBIC, ANTIALIAS (default)")
    parser.add_option("-c", "--crop", default=False, dest="crop",  
        help="Crop to the glyph's bounding box", action="store_true")
    parser.add_option("-r", "--resize", default=False, dest="resize", 
        help="Scale all images to one size (the largest width and height of glyphs)", action="store_true")
    parser.add_option("-s", "--scale", default=False, dest="scale", 
        help="Scale the glyphs inside the images to fit within the image canvas", action="store_true")
    parser.add_option("-S", "--size", default=-1, dest="size", type="int", 
        help="Force the use of specified square canvas (size*size). The glyphs will be scaled to fit the canvas)")
    parser.add_option("-m", "--mode", default=1, dest="mode", 
        type="int", help="Type of directory structure. 1: All font glyphs' in separate folder (default). 2: Every class letter in its own folder")
    parser.add_option("-u", "--contour", default=False, dest="contour", 
        help="Apply morphological filter to keep only glyph contours (boundaries)", action="store_true")
    parser.add_option("-v", "--verbose", default=0, dest="verbose", type="int", 
        help="Verbose mode: 0 (silent) or 1 (detailed)")
    (opt, args) = parser.parse_args()
    if opt.inDir == "" or opt.outDir =="":
        print("Usage: ./ttf2png.py [-f png|bmp|eps|pdf|svg] [-t NEAREST|BILINEAR|BICUBIC|ANTIALIAS] [-S size] [-c] [-s] [-r] [-v] -d fontsDir/ -o glyphsDir/")
        print("PS:The precedence of c, s, r is: crop followed by scale and finally resize.")
        return 
    
    if opt.inDir[len(opt.inDir)-1] != '/':
        opt.inDir = opt.inDir + '/'
    if opt.outDir[len(opt.outDir)-1] != '/':
        opt.outDir = opt.outDir + '/'
    
    if not os.path.isdir(opt.inDir):
        print("Error: '%s' should be an existent directory"% opt.inDir)
        exit(3)
    if not os.path.isdir(opt.outDir):
        os.makedirs(opt.outDir) 
    opt.format = opt.format.lower()
    opt.filter = opt.filter.upper()
    
    if opt.format in ['eps', 'svg', 'pdf'] and (opt.resize or opt.crop or opt.scale):
        print("Info: Using vector format (%s), hence the three parameters -r -c -s will be ignored [if provided]."%opt.format)

    fontDict = createFontDict(opt.inDir, opt.outDir, opt.format)
    if fontDict == {}:
        print("Error: the input font directory is empty")
        exit(3)
    if opt.mode == 1:
        fontDict = createFontGlyphsFiles1(fontDict, opt.outDir, opt.format, opt.verbose, opt.crop)
    else:
        fontDict = createFontGlyphsFiles2(fontDict, opt.outDir, opt.format, opt.verbose, opt.crop)
        
    if opt.format in ['bmp', 'png', 'eps', 'svg', 'pdf']: 
        if opt.resize or opt.scale:
            if opt.size == -1:
                maxv = getMaxDimOfAllGlyphs(fontDict)
                maxval = max(maxv[0], maxv[1])
                if opt.verbose > 0:
                    print("Max width & height:", maxv)
                    print("Images width & height will be set to %i*%i"%(maxval, maxval))
                maxv = [maxval, maxval]
            else:
                maxv = [opt.size, opt.size]
            resizeAllGlyphstoMax(fontDict, maxv, opt.scale, opt.filter, opt.contour)
    else:
        print("Error: '%s' Unsupported file format."% opt.format)
    saveAsJSON(fontDict, opt.outDir)
    if opt.mode == 1:
        saveAsTXT1(fontDict, opt.outDir) # All font glyphs are saved in one folder
    else:
        saveAsTXT2(fontDict, opt.outDir) # Every character class has its own folder
        
    print("End-of-Program: ttf2png.py")
    return 
    
if __name__ == "__main__":
    main()

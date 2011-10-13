#!/usr/bin/python
# (C) 2011 University of Kaiserslautern 
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
# Responsible: Hasan S. M. Al-Khaffaf (hasan@iupr.com)
# Reviewer: 
# Primary Repository: 
# Web Sites: www.iupr.com


from optparse import OptionParser 
import sys
import glob
import subprocess
from inspect import currentframe
import time

def createImageList(opt):
    imageFormats = [".jpg", ".tif", ".tiff", ".png", ".bmp"] #FIXME: add more image file types supported by Ocropus
#    __imageFormatLine__ = currentframe().f_back.f_lineno
    listFiltered = []
    list = glob.glob(opt.srcDirectory + "*.*") 
    
    if opt.verbose == 1:
        print "[info] Filtering input images:\n"
        print "[info] supported image types", imageFormats
        print "[info] want to support a new image type? Add it into imageFormats list" # at line %i"%(int(__imageFormatLine__))
        
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
    return listFiltered
    
    
def stripExt(name):
    nameNoExt = name[0:len(name)-4]
    return nameNoExt


def genPDF4ImageList(fileList, opt):
    batchBegin = time.time()
    for i in fileList: # generate PDF for the image i
        nameNoExt = stripExt(i)
        for j in list(str(opt.pdfType)): # generate PDF type j
            cmd = ["./decapod-genpdf.py", "-t", j, "-b", i, "-d", (nameNoExt+"t" + j + ""), "-p", (nameNoExt + "[t" + j + "]" + ".pdf"), "-v", "2"]
            if opt.verbose == 1:
                print "************** Now executing genpdf with image:", i, "\nCommand: ", cmd ," ************"
            begTime = time.time()
            retCode = subprocess.call(cmd)
            if retCode != 0:
                print "[warn] decapod-genpdf did not work as expected"
            endTime = time.time()
            if opt.verbose == 1:
                print "Duration to run genpdf pipeline for image %s= %i sec."% (i, endTime - begTime)
    batchEnd = time.time()
    if opt.verbose == 1:
        print "Duration to run genpdf pipeline for list of images %s= %i:%i:%i  (h:m:s)"% (fileList, (batchEnd - batchBegin)/(60*60), (batchEnd - batchBegin)/60, (batchEnd - batchBegin)%60)

        
def calculateImg2PDFPerformance():
    
    return

    
    
def main(sysargv):
    parser = OptionParser()
    parser.add_option("-d", "--directory", default="", dest="srcDirectory", 
        type="string", help="Directory name for the source images. The '/' will be added (if not there)")
    parser.add_option("-t", "--type", default=1, dest="pdfType", type="int", 
        help="type of the output PDF file [1..4]. Can use more than one type simultaneously")
    parser.add_option("-v", "--verbose", default=0, dest="verbose", type="int", 
        help="verbose type: 0 (silent) or 1 (detailed)")
    (opt, args) = parser.parse_args()
    
    if opt.srcDirectory == '':
        print("Error: directory name for the source images is missing.\nPlease supply the directory name using the '-d' option")
        exit(1)
    if opt.srcDirectory[len(opt.srcDirectory)-1] != '/':
	opt.srcDirectory = opt.srcDirectory + '/'
   
    fileList = createImageList(opt)
    genPDF4ImageList(fileList, opt)
    calculateImg2PDFPerformance()
    
    print("img2pdfper: End-of-Program")
    
    
    
if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)

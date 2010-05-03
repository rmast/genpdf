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
from multiprocessing import Process, Queue, Pool
import shlex, subprocess

# global variables:
verbose     = 0         # output debugging information
dpi         = 200       # resolution of the ouput images in the pdf
tempLogDir  = "testOutput/"

# ========= ImagePDF =========




# read args, opts and process
def main(sysargv):
    # make global variables available
    global verbose 
    global dpi
    pageWidth  = 21.0; # default page width, DIN A4
    pageHeight = 29.7; # default page height, DIN A4
    # parse command line options
    if len(sysargv) == 1:
        usage(sysargv[0])
        sys.exit(0)    
    try:
        optlist, args = getopt.getopt(sysargv[1:], 'hd:l:', ['help','dir=','log='])
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
        if o in ("-d", "--dir"):
            testSetDir = a
        if o in ("-l", "--log"):
            pdfFileName = a
        if o in ("-v", "--verbose"):
            verbose = int(a)
        if o in ("-r", "--resolution"):
            dpi = int(a)

    testSet = readTestSet(testSetDir)

    #print "============="
    #print testSet
    #print "============="

    smallSet = testSet[1:3]

    errors, total = runTest(testSet)
    
    if(len(errors)==0):
        print("===== SUCCESS! ====")
        print("  all %d tests went through!" %(total))
    else:
        print("===== ERROR REPORT ====")
        print("exit code\tPDF type\timage\ttempDir")
        for i in errors:
            print("%d       \t%d      \t%s\t%s" %(i[0],i[1],i[2],i[3]))
    
    
    
            
        
        
def readTestSet(testSetDir):
    fileNames = []
    print testSetDir
    for root, dirs, files in os.walk(testSetDir):
        #print "=== 0 ==="
        #print root
        #print "=== 1 ==="
        #print dirs
        #print "=== 2 ==="
        #print files
        for name in files:
            #print name, name[len(name)-3:len(name)]
            if (name.find("_") < 0 and name[len(name)-3:len(name)]=="jpg"):
                fileNames.append(root+"/"+name)
    return fileNames
    
    
def executeCmd(fn, tempDir, tempLogDir, t):
    global verbose
    bn    = fn[fn.rfind("/"):len(fn)]
    pdfFN = tempDir + bn[0:len(bn)-3] + "pdf"
    logFN = tempLogDir + bn[0:len(bn)-3] + "log"
    # remove the generated DIR as decapod-genpdf will create it
    os.rmdir(tempDir)
    cmd_genpdf = "decapod-genpdf.py -b %s -d %s -p %s -t %s > %s" %(fn,tempDir,pdfFN,t,logFN)
    #cmd_genpdf = "decapod-genpdf.py"
    #args_genpdf = "-b %s -d %s -p %s -t %s " %(fn,tempDir,pdfFN,t,logFN)
    if verbose>=1:
        print(cmd_genpdf)
    #pID = os.popen(cmd_genpdf)
    #print "===== pID ====="
    #print pID
    args = shlex.split(cmd_genpdf)
    retcode = subprocess.call(args)
    return retcode,t,fn,tempDir


def runTest(testSet):
    global tempLogDir
    q = []
    processes=Pool()
    
    totalTests = 0
    types = [1,2,3]
    for t in types:
        print "========== Running test for type %d ==========" %(t)
        for test in testSet:
            totalTests += 1
            print "    === Image %s ===" %(test)
            tempDir=tempfile.mkdtemp()+"/";
            q.append(processes.apply_async(executeCmd,(test, tempDir, tempLogDir, t)))
    
  
    processes.close()
    processes.join()
    
    #results=zeros([4],int) # TOT, HPS corr., VPS corr.
    errors=[]
    #print(q)
    for i in q:
        print(i)
        data=i.get()
        #print data
        if(data[0]!=0):
            errors.append(data)
    return errors, totalTests



# print help information
def usage(progName):
    print "\n%s [OPTIONS] -dir ocroDir -pdf out.pdf\n\n"\
          "   -d, --dir          directory of the Oulu dataset\n"\
          "   -l, --log          log file containing the report\n"\
          " Options:\n"\
          "   -h, --help:        print this help\n"\
          "   -v, --verbose:     verbose level [0,1,2,3]\n"


if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)










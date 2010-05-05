#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import getopt

import shlex, subprocess, tempfile

def main(sysargv):
    
#if o in ("-h", "--help"):
#if o in ("-t", "--type"):
#if o in ("-W", "--width"):
#if o in ("-H", "--height"):
#if o in ("-d", "--dir"):
#if o in ("-p", "--pdf"):
#if o in ("-v", "--verbose"):
#if o in ("-r", "--resolution"):
#if o in ("-b", "--book"):
#if o in ("-e","--eps"):
#if o in ("-s","--reps"):
#if o in ("-R","--remerge"):
#if o in ("-C","--enforceCSEG"):
#if o in ("-S","--seg2bbox"):
    fn     = "../data/test-image.jpg"
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    print "========== Running test 01 ==========" 
    retNoOpt  = subprocess.call(["./decapod-genpdf.py"])
    print "========== Running test 02 ==========" 
    retHelp   = subprocess.call(["./decapod-genpdf.py","-h"])
    print "========== Running test 03 ==========" 
    retWrgFn  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"fn"])
    os.rmdir(tmpDir)
    print "========== Running test 04 ==========" 
    retMinOpt = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,fn])
    print "========== Running test 05 ==========" 
    retExDir  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,fn])
    
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    print "========== Running test 06 ==========" 
    retWH     = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","1","-H","1",fn])

    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    print "========== Running test 07 ==========" 
    retNegWH  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","-1","-H","-1",fn])
    
    print "========== REPORT =========="
    print "Test  is  exp.      details"
    print "01    [%d] [0]  testing w/o option" %(retNoOpt)
    print "02    [%d] [0]  testing -h option" %(retHelp)
    print "03    [%d] [2]  testing with wrong file name options" %(retWrgFn)
    print "04    [%d] [0]  testing with minimal options" %(retMinOpt)
    print "05    [%d] [1]  testing with existing book directory" %(retExDir)
    print "06    [%d] [0]  testing with different width and height directory" %(retWH)
    print "07    [%d] [1]  testing with negative width and height directory" %(retNegWH)

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)


 

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import getopt

import shlex, subprocess, tempfile

def main(sysargv):
    
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
    
    
    print "========== Running test 06 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retWH     = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","1","-H","1",fn])

    
    print "========== Running test 07 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retNegWH  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","-1","-H","-1",fn])
    
    
    print "========== Running test 08 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retquadWH  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","10.0","-H","10.0",fn])
    
    print "========== Running test 09 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retasyWH1  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","100.0","-H","10.0",fn])
    
    print "========== Running test 10 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retasyWH2  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","10.0","-H","100.0",fn])
    
    print "========== Running test 11 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retNegRes  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-r","-300","-t","2",fn])
    
    print "========== Running test 12 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retZeroRes  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-r","0","-t","2",fn])
    
    print "========== Running test 13 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retSmallRes  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-r","10","-t","2",fn])
    
    print "========== Running test 14 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retHighRes  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-r","600","-t","2",fn])
    
    print "========== Running test 15 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retType3  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-r","300","-t","3",fn])
    
    print "========== Running test 16 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retBook  = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-b",fn])

    print "========== Running test 17 ==========" 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    retMultiple = subprocess.call(["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,fn,fn,fn])

    
    print "========== REPORT =========="
    print "Test  is  exp.      details"
    print "01    [%d] [0]  testing w/o option" %(retNoOpt)
    print "02    [%d] [0]  testing -h option" %(retHelp)
    print "03    [%d] [2]  testing with wrong file name options" %(retWrgFn)
    print "04    [%d] [0]  testing with minimal options" %(retMinOpt)
    print "05    [%d] [1]  testing with existing book directory" %(retExDir)
    print "06    [%d] [0]  testing with different width and height" %(retWH)
    print "07    [%d] [1]  testing with negative width and height" %(retNegWH)
    print "08    [%d] [0]  testing with quadratic page size" %(retquadWH)
    print "09    [%d] [0]  testing with very wide page width" %(retasyWH1)
    print "10    [%d] [0]  testing with very heigh page height" %(retasyWH2)
    print "11    [%d] [0]  testing with negative resolution" %(retNegRes)
    print "12    [%d] [0]  testing with zero resolution" %(retZeroRes)
    print "13    [%d] [0]  testing with small resolution (10dpi)" %(retSmallRes)
    print "14    [%d] [0]  testing with high resolution (600dpi)" %(retHighRes)
    print "15    [%d] [0]  testing with type 3 as output" %(retType3)
    print "16    [%d] [0]  testing with -b bookFile as input" %(retBook)
    print "17    [%d] [0]  testing with multiple input files" %(retMultiple)

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)


 

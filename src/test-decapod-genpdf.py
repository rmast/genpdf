#!/usr/bin/env python
# -*- coding: utf-8 -*-

from builtins import range
import os
import sys
import time
import getopt

import shlex, subprocess, tempfile

def main(sysargv):
    
    testDes = [] # descriptions of the tests
    testOut = [] # retur values of the tests
    testExp = [] # expected return values of the tests
    testCmd = [] # commands for calling the tests
    
    
    fn     = "../data/test-image.jpg"
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    print("========== Running test 01 ==========") 
    cmd = ["./decapod-genpdf.py"]
    ret = subprocess.call(cmd)
    testDes.append("Testing w/o options. Should return help message.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd)
    
    print("========== Running test 02 ==========") 
    cmd = ["./decapod-genpdf.py","-h"]
    ret = subprocess.call(cmd)
    testDes.append("Testing -h option. Should return help message.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd)
    
    print("========== Running test 03 ==========") 
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"fn"]
    ret = subprocess.call(cmd)
    testDes.append("Testing with wrong file name options.")
    testOut.append(ret)
    testExp.append(2)
    testCmd.append(cmd)
    os.rmdir(tmpDir)    
    
    print("========== Running test 04 ==========") 
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with minimal options.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 
    
    print("========== Running test 05 ==========") 
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with existing book directory.")
    testOut.append(ret)
    testExp.append(1)
    testCmd.append(cmd) 
    
    print("========== Running test 06 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","1","-H","1",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with different width and height.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 
    
    print("========== Running test 07 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","-1","-H","-1",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with negative width and height.")
    testOut.append(ret)
    testExp.append(1)
    testCmd.append(cmd) 
    
    print("========== Running test 08 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","10.0","-H","10.0",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with quadratic page size.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 
    
    print("========== Running test 09 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","100.0","-H","10.0",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with very wide page width.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 

    print("========== Running test 10 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-W","10.0","-H","100.0",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with very high page height.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 

    print("========== Running test 11 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-r","-300","-t","2",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with negative resolution.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 
    
    print("========== Running test 12 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-r","0","-t","2",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with zero resolution.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 
    
    print("========== Running test 13 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-r","10","-t","2",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with small resolution (10 dpi).")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 
    
    print("========== Running test 14 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-r","600","-t","2",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with high resolution (600 dpi).")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 
    
    print("========== Running test 15 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-r","300","-t","3",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with PDF output type 3.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 
    
    print("========== Running test 16 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,"-b",fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with -b bookFile as input.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 

    print("========== Running test 17 ==========") 
    tmpDir = tempfile.mkdtemp()+"/"
    os.rmdir(tmpDir)
    outFn  = tmpDir + "out.pdf"
    cmd = ["./decapod-genpdf.py","-d",tmpDir,"-p",outFn,fn,fn,fn]
    ret = subprocess.call(cmd)
    testDes.append("Testing with multiple input files.")
    testOut.append(ret)
    testExp.append(0)
    testCmd.append(cmd) 
    
    print("========== REPORT ==========")
    print("Test\tis  exp.      details")
    for i in range(len(testDes)):
        print("%d\t[%d] [%d] %s" %(i+1,testOut[i],testExp[i],testDes[i]))
    print("========== ERRORS ==========")
    print("Test\tis  exp.      details     command")
    for i in range(len(testDes)):
        if (testOut[i] != testExp[i]):
            print("%d\t[%d] [%d] %s\t%s" %(i+1,testOut[i],testExp[i],testDes[i],testCmd[i]))

    #print "01    [%d] [0]  testing w/o option" %(retNoOpt)
    #print "02    [%d] [0]  testing -h option" %(retHelp)
    #print "03    [%d] [2]  testing with wrong file name options" %(retWrgFn)
    #print "04    [%d] [0]  testing with minimal options" %(retMinOpt)
    #print "05    [%d] [1]  testing with existing book directory" %(retExDir)
    #print "06    [%d] [0]  testing with different width and height" %(retWH)
    #print "07    [%d] [1]  testing with negative width and height" %(retNegWH)
    #print "08    [%d] [0]  testing with quadratic page size" %(retquadWH)
    #print "09    [%d] [0]  testing with very wide page width" %(retasyWH1)
    #print "10    [%d] [0]  testing with very heigh page height" %(retasyWH2)
    #print "11    [%d] [0]  testing with negative resolution" %(retNegRes)
    #print "12    [%d] [0]  testing with zero resolution" %(retZeroRes)
    #print "13    [%d] [0]  testing with small resolution (10dpi)" %(retSmallRes)
    #print "14    [%d] [0]  testing with high resolution (600dpi)" %(retHighRes)
    #print "15    [%d] [0]  testing with type 3 as output" %(retType3)
    #print "16    [%d] [0]  testing with -b bookFile as input" %(retBook)
    #print "17    [%d] [0]  testing with multiple input files" %(retMultiple)

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)


 

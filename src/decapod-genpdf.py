#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import getopt
import shlex, subprocess

msg = '\nusage: python runPipeLine.py input file in pdf form \n\nworks iff "." only appears prior ext\nntake an input file and run ocropus clustering genPdf'

def main(sysargv):
    clustercommand = [] # command called for token clustering
    pdfgencommand = []  # command called for PDF generation
    bookFileName = ""   # multipage TIFF file for which the PDF is generated
    verbose = 1         # output debuging information
    pdfOutputType = 1   # default PDF type: image only
    pdfFileName = ""    # filename of the resultine PDF
    # parse command line options
    if len(sysargv) == 1:
        usage(sysargv[0])
        sys.exit(0)        
    try:
        optlist, args = getopt.getopt(sysargv[1:], 'hb:t:d:p:W:H:e:s:RCSv:r:', ['help','book=','type=','dir=','pdf=','width=','height=',"eps=","reps","remerge","enforceCSEG","seg2bbox",'verbose=','resolution='])
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
            pdfgencommand.append(" -t %d " % (pdfOutputType))
        if o in ("-W", "--width"):
            pageWidth = float(a)
            if (pageWidth < 0):
                print("[Error]: pageWidth %f < 0!" %(pageWidth))
                sys.exit(1)
            pdfgencommand.append(" -W %f " % (pageWidth))
        if o in ("-H", "--height"):
            pageHeight = float(a)
            if (pageHeight < 0):
                print("[Error]: pageHeight %f < 0!" %(pageHeight))
                sys.exit(1)
            pdfgencommand.append(" -H %f " % (pageHeight))
        if o in ("-d", "--dir"):
            bookDir = a
            # add "/" to bookDir if necessary
            if (len(bookDir)>0 and bookDir[len(bookDir)-1]!='/'):
                bookDir = bookDir+'/'
            if os.path.exists(bookDir)==True:
                print("[Error]: bookDir \"%s\" does already exist! Please choose another directory!" %(bookDir))
                sys.exit(1)
            pdfgencommand.append(" -d %s " % (bookDir))
            clustercommand.append(" -b %s " % (bookDir))
        if o in ("-p", "--pdf"):
            pdfFileName = a
            pdfgencommand.append(" -p %s " % (pdfFileName))
        if o in ("-v", "--verbose"):
            verbose = int(a)
            clustercommand.append(" -v %d " % (verbose))
            pdfgencommand.append(" -v %d " % (verbose))
        if o in ("-r", "--resolution"):
            dpi = int(a)
            pdfgencommand.append(" -r %d " (dpi))
        if o in ("-b", "--book"):
            bookFileName = a
        if o in ("-e","--eps"):
            eps = int(a)
            clustercommand.append(" -e %d " % (eps) )
        if o in ("-s","--reps"):
            reps = float(a)
            clustercommand.append( " -r %f " % (reps))
        if o in ("-R","--remerge"):
            clustercommand.append(" -R ")
        if o in ("-C","--enforceCSEG"):
            clustercommand.append(" -C ")
        if o in ("-S","--seg2bbox"):
            clustercommand.append(" -S ")  

    outputLog = str(bookFileName)+"-log"
    # if no bookFileName is given use all the arg images as input
    if bookFileName=="":
        for arg in args:
            bookFileName += arg + " "
    
    if (bookFileName=="" or pdfFileName=="" or bookDir==""):
        print("[Error]: bookFilename, pdfFileName or bookDir not defined! (\"%s\", \"%s\", \"%s\")" %(bookFileName, pdfFileName,bookDir))
        sys.exit(1)

    out = open(outputLog, 'w')
    #Deprecated: old ocropus commands
    #book2pages = "ocropus book2pages %s %s" % (bookDir,bookFileName)
    #pages2lines = "ocropus pages2lines %s" % (bookDir)
    #lines2fsts = "ocropus lines2fsts %s" % (bookDir)
    #fsts2text = "ocropus fsts2text %s" % (bookDir)
    
    # Corresponding ocropy commands.
    book2pages = "ocropus-binarize -o %s %s" % (bookDir,bookFileName)
    pages2lines = "ocropus-pseg %s/????.png" % (bookDir) 
    lines2fsts = "ocropus-linerec %s/????/??????.png" % (bookDir)
  
    #prep clustering statement
    clustercommand = "binned-inter %s" % ("".join(clustercommand))
    if(pdfOutputType == 2):
        clustercommand = "binned-inter -b %s -v %d -J" % (bookDir,verbose) 

    #prep pdf gen statement
    pdfcommand = "ocro2pdf.py %s" % ("".join(pdfgencommand))

    if verbose>1:
        print "genBook command: %s" %(book2pages)
        print "pseg    command: %s" %(pages2lines)
        print "fsts    command: %s" %(lines2fsts)
        print "cluster command:","".join(clustercommand)
        print "pdf     command:","".join(pdfgencommand)

    start = time.time()

    #run ocropus pipeline
    if verbose>1:
        print "running ocropus pipeline"
    
    cmd = shlex.split(book2pages)
    retCode = subprocess.call(cmd)
    if (retCode != 0):
        print "[error] generating book structure did not work as expected! (%s)" %(book2pages)
        sys.exit(2) #unknown error
    #os.system(book2pages)
    
    if(pdfOutputType > 1):
        cmd = shlex.split(pages2lines)
        retCode = subprocess.call(cmd)
        if (retCode != 0):
            print "[error] page segmentation did not work as expected! (%s)" %(pages2lines)
        sys.exit(2) #unknown error
        #os.system(pages2lines)

        cmd = shlex.split(lines2fsts)
        retCode = subprocess.call(cmd)
        if (retCode != 0):
            print "[error] line recognition did not work as expected! (%s)" %(lines2fsts)
        #os.system(lines2fsts)

        #os.system(fsts2text)

    endOCROPUS = time.time()
    if verbose>1:
        print >> out, "Time elapsed OCROPUS= ", endOCROPUS - start, "seconds"

    #run clustering
    if(pdfOutputType==2 or pdfOutputType==3):
        if verbose>1:
            print "running clustering"
        cmd = shlex.split(clustercommand)
        retCode = subprocess.call(cmd)
        if (retCode != 0):
            print "[error] clustering did not work as expected! (%s)" %(clustercommand)
        #os.system(clustercommand)

    endClustering = time.time()
    if verbose>1:
        print >> out, "Time elapsed clustering= ",endClustering - endOCROPUS, "seconds"

    #run pdf gen
    if verbose>1:
        print "generating pdf"
    
    cmd = shlex.split(pdfcommand)
    retCode = subprocess.call(cmd)
    if (retCode != 0):
        print "[error] PDF generation did not work as expected! (%s)" %(pdfcommand)
    #os.system(pdfcommand)
    
    endGenPDF = time.time()
    if verbose>1:
        print >> out, "Time elapsed pdfGen= ",endGenPDF - endClustering, "seconds"
        print >> out, "total time elapsed =",endGenPDF - start,"seconds"


def usage(progName):
    print "\n%s [OPTIONS]\n\n"\
	      "   -b  --book         name of multipage tiff file\n"\
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
          "   -R --remerge       remerge token clusters [default = false] \n"\
          "   -S, --seg2bbox     suppresses generating files necessary to generate PDF \n"\
          "   -C, --enforceCSEG  characters can only match if there CSEG labels are equal \n"\
          "   -e, --eps          matching threshold [default=7] \n"\
          "   -s, --reps         matching threshold [default=.07] \n"\


if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)


 

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import time
import getopt
import shlex, subprocess
import glob

msg = '\nusage: python runPipeLine.py input file in pdf form \n\nworks iff "." only appears prior ext\nntake an input file and run ocropus clustering genPdf'

def main(sysargv):
    clustercommand = ["binned-inter"] # command called for token clustering
    pdfgencommand = ["ocro2pdf.py"]   # command called for PDF generation
    book2pages = ["ocropus-binarize"] # command called for generating the book Dir and binarization
    bookFileName = ""   # multipage TIFF file for which the PDF is generated
    verbose = 2         # output debuging information
    pdfOutputType = 1   # default PDF type: image only
    pdfFileName = ""    # filename of the resultine PDF
    dpi=300             # default resolution
    verbose=0           # default: be not verbose at all
    # parse command line options
    if len(sysargv) == 1:
        usage(sysargv[0])
        sys.exit(0)        
    try:
        optlist, args = getopt.getopt(sysargv[1:], 'hb:t:d:p:W:H:e:s:RCSv:r:', ['help','book=','type=','dir=','pdf=','width=','height=',"eps=","reps","remerge","enforceCSEG","seg2bbox",'verbose=','resolution='])
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
            pdfgencommand.append("-t")
            pdfgencommand.append("%d" %(pdfOutputType))
        if o in ("-W", "--width"):
            pageWidth = float(a)
            if (pageWidth < 0):
                print("[Error]: pageWidth %f < 0!" %(pageWidth))
                sys.exit(1)
            pdfgencommand.append("-W")
            pdfgencommand.append("%f" %(pageWidth))
        if o in ("-H", "--height"):
            pageHeight = float(a)
            if (pageHeight < 0):
                print("[Error]: pageHeight %f < 0!" %(pageHeight))
                sys.exit(1)
            pdfgencommand.append("-H")
            pdfgencommand.append("%f" %(pageHeight))
        if o in ("-d", "--dir"):
            bookDir = a
            # add "/" to bookDir if necessary
            if (len(bookDir)>0 and bookDir[len(bookDir)-1]!='/'):
                bookDir = bookDir+'/'
            if os.path.exists(bookDir)==True:
                print("[Error]: bookDir \"%s\" does already exist! Please choose another directory!" %(bookDir))
                sys.exit(1)
            pdfgencommand.append("-d")
            pdfgencommand.append("%s" %(bookDir))
            clustercommand.append("-b")
            clustercommand.append("%s" %(bookDir))
        if o in ("-p", "--pdf"):
            pdfFileName = a
            pdfgencommand.append("-p")
            pdfgencommand.append("%s" %(pdfFileName))
        if o in ("-v", "--verbose"):
            verbose = int(a)
            clustercommand.append("-v")
            clustercommand.append("%d" %(verbose))
            pdfgencommand.append("-v")
            pdfgencommand.append("%d" %(verbose))
        if o in ("-r", "--resolution"):
            dpi = int(a)
            if (dpi==0):
                print("[Warn]: Resolution set to zero! Changed to 300 dpi!")
                dpi=300
            if (dpi<0):
                dpi = abs(dpi)
                print("[Warn]: Resolution set to < 0! Changed to %d dpi!" %(dpi))
            if (dpi>600):
                dpi = abs(dpi)
                print("[Warn]: Resolution set to > 600! Processing will be slow and may crash! Use a lower resolution!")
            pdfgencommand.append("-r")
            pdfgencommand.append("%d" %(dpi))
        if o in ("-b", "--book"):
            book2pages.append("-o")
            book2pages.append("%s" %(a))
        #FIXME: Micheal: we should hide these parameters as far as possible
        if o in ("-e","--eps"):
            eps = int(a)
            clustercommand.append("-e")
            clustercommand.append("%d" %(eps))
        if o in ("-s","--reps"):
            reps = float(a)
            clustercommand.append("-r")
            clustercommand.append("%f" %(reps))
        if o in ("-R","--remerge"):
            clustercommand.append("-R")
        if o in ("-C","--enforceCSEG"):
            clustercommand.append("-C")
        if o in ("-S","--seg2bbox"):
            clustercommand.append("-S")  

    ## ===== PREPARE COMMANDS ===== ##
    # if no bookFileName is given use all the arg images as input
    if len(book2pages)==1:
        book2pages = args
        book2pages.insert(0,"ocropus-binarize")  # insert command string
        book2pages.insert(1,"-o")                # insert output option string
        book2pages.insert(2,"%s" %(bookDir))

    if(pdfOutputType == 2):
        clustercommand = ["binned-inter","-b","%s" %(bookDir),"-v","%d" %(verbose),"-J"]

    if verbose>1:
        print "[Info]: genBook command: %s" %(book2pages)
        print "[Info]: cluster command: %s" %(clustercommand)
        print "[Info]: pdf     command: %s" %(pdfgencommand)

    start = time.time()

    if (len(book2pages)<3 or pdfFileName=="" or bookDir==""):
        print("[Error]: bookFilename, pdfFileName or bookDir not defined! (\"%s\", \"%s\", \"%s\")" %(bookFileName, pdfFileName,bookDir))
        sys.exit(2)

    ## ===== EXECUTE COMMANDS ===== ##
    #run ocropus pipeline
    if verbose>1:
        print "[Info]: running ocropus pipeline"
    
    # run ocropus binarization to generate the book Dir
    retCode = subprocess.call(book2pages)
    if (retCode != 0):
        print "[Error] generating book structure did not work as expected! (%s)" %(book2pages)
        sys.exit(2) #unknown error
    
    endBin = time.time()
    if verbose>1:
        print "[Info]: time used by binarization: %d sec" %(endBin - start)

    if(pdfOutputType > 1):
        fileList = glob.glob("%s/????.png" %(bookDir))
        cmd = fileList
        cmd.insert(0,"ocropus-pseg")
        retCode = subprocess.call(cmd)
        if (retCode != 0):
            print "[Error] page segmentation did not work as expected! (%s)" %(cmd)
            sys.exit(2) #unknown error

        endPSeg = time.time()
        if verbose>1:
            print "[Info]: time used by page segmentation: %d sec" %(endPSeg - endBin)

        fileList = glob.glob("%s/????/??????.png" %(bookDir))
        cmd = fileList
        cmd.insert(0,"ocropus-linerec")
        retCode = subprocess.call(cmd)
        if (retCode != 0):
            print "[Error] line recognition did not work as expected! (%s)" %(cmd)
            sys.exit(2) #unknown error
        
        endRecog = time.time()
        if verbose>1:
            print "[Info]: time used by text recognizer: %d sec" %(endRecog-endPSeg)


    endOCROPUS = time.time()
    if verbose>1:
        print "[Info]: time used by OCRopus: %d sec" %(endOCROPUS - start)

    #run clustering
    if(pdfOutputType==2 or pdfOutputType==3):
        if verbose>1:
            print "[Info]: running clustering"
        #cmd = shlex.split(clustercommand)
        retCode = subprocess.call(clustercommand)
        if (retCode != 0):
            print "[Error]: clustering did not work as expected! (%s)" %(clustercommand)
        #os.system(clustercommand)

    endClustering = time.time()
    if verbose>1:
        print "[Info]: time used by clustering: %d sec" %(endClustering - endOCROPUS)

    #run pdf gen
    if verbose>1:
        print "[Info]: generating pdf"
    
    retCode = subprocess.call(pdfgencommand)
    if (retCode != 0):
        print "[Error] PDF generation did not work as expected! (%s)" %(pdfgencommand)
        sys.exit(2)
    
    endGenPDF = time.time()
    if verbose>1:
        print "[Info]: time used by pdf generation: %d sec" %(endGenPDF - endClustering)
        print "[Info]: time used for whole process: %d sec" %(endGenPDF - start)

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


 

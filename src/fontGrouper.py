#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (C) 2011-2012 University of Kaiserslautern 
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
# File: fontGrouper.py
# Purpose: reconstruct document font(s)
# Responsible: 
# Reviewer (01-Aug-2011 onward): Hasan S. M. Al-Khaffaf (hasan@iupr.com)
# Primary Repository: 
# Web Site: www.iupr.com

from ocrodir import *
from numpy import *
#from numpy.numarray import *
from pylab import *
from PIL import Image
import fontforge
import psMat
import sys
#import matplotlib.pyplot as plt
#from ocropy import binnednn,ocrobook
import PIL
import copy
from optparse import OptionParser
import os
from datetime import datetime
from inspect import currentframe #Hasan: Added this line


class CandidateFont():
    '''class to hold tokenSet that has been grouped into a CandidateFont'''
    
    def __init__(self,tokenSet,candidateFontID):
        '''tokenSet is a list of ints representing tokens'''
        self.tokenSet = copy.copy(tokenSet)
        self.candidateFontID = candidateFontID
        self.goalSet = set()
        self.hasSet = []
        self.needSet = []
        #static set of 52 letters the algorithm is searching for

    def addToTokenSet(self,tID):
        self.tokenSet.append(tID)
    def genGoalSet(self):
        '''returns list of ascii chars a-z & A-Z'''
        if len(self.goalSet) > 0: return
        self.goalList = []
        A=65
        Z=90
        a=97
        z=122
        for x in range(A,Z+1):
            self.goalList.append( chr(x) )
        for x in range(a,z+1):
            self.goalList.append( chr(x) )
        self.goalSet = set(self.goalList)
    def genHasSet(self):
        self.hasSet = []
        for t in self.tokenSet:
            self.hasSet.append(labels[t])
        self.hasSet = set(self.hasSet)
    def addToHasSet(self,tokenID):
        self.hasSet.add(labels[tokenID])
    def genNeedSet(self):
        self.needSet = self.goalSet.difference(self.hasSet)
        
    
    

class Token():
    '''class to hold information about each token'''
    def __init__(self,coordsN=None,foundPageN=None,foundLineN=None,tokenIDN=None):
        '''creates first entry of a token found in document'''
        self.coords = [(coordsN)] #x0 y0 x1 y1
        self.foundPage = []
        self.foundLine = []
        self.foundPage.append(foundPageN)
        self.foundLine.append(foundLineN)
        self.tokenID = tokenIDN
        self.count = 1
        self.fontClass = -1
        self.assignedFontClass = -1
        self.confidenceAF = -1
        self.averageH = -1
        self.averageW = -1
        self.fontClassScore = zeros(options.numFontClasses)
        self.backDeltaList = []
        self.forwardDeltaList = []
    def addOccurrence(self,coordsN,foundPageN,foundLineN):
        '''adds another occurrence of same tokenID found in document to class token'''
        self.coords.append(coordsN)
        self.foundPage.append(foundPageN)
        self.foundLine.append(foundLineN)
        self.count += 1
    def hasFontClass(self):
        if self.fontClass > -1: 
            return True
        else: return False
    def hasAssignedFontClass(self):
        if self.assignedFontClass > -1: return True
        else: return False
    def findAverageWandH(self):
        cumH = 0
        cumW = 0
        for x0,y0,x1,y1 in self.coords:
            cumH += (y1 - y0)
            cumW += (x1 - x0)
        self.averageH = cumH / len(self.coords)
        self.averageW = cumW / len(self.coords)
    def fontClassScoreUpdate(self,update):
        self.fontClassScore += update
        if sum(self.fontClassScore) <= 0: return #no assigned font class without representation
        self.assignedFontClass = self.fontClassScore.argmax()
        self.confidenceAF = self.fontClassScore[self.assignedFontClass]
    def setBackwardNeighbor(self,back,instance):
        "find distance between back, which is a token, and instance, which is an instance of this tokenID - reject if distance too far"
        bx0,by0,bx1,by1 = back.coords[0]
        sx0,sy0,sx1,sy1 = instance.coords[0]
        #thresh check for space if the back x1 is further then the size of instance then reject
        if (bx1 + ((sx1 - sx0)/1.5)) < sx0: 
            #print "rejected as neighbor"
            return
        delta = sx0 - bx1
        self.backDeltaList.append(delta)
    def setForwardNeighbor(self,forward,instance):
        "find distance between forward, which is a token, and instance, which is an instance of this tokenID - reject if distance too far"
        fx0,fy0,fx1,fy1 = forward.coords[0]
        sx0,sy0,sx1,sy1 = instance.coords[0]
        #thresh check for space if the forward x1 is further then the size of instance then reject
        if (sx1 + ((sx1 - sx0)/1.5)) < fx0: 
            #print "rejected as neighbor"
            return
        delta = fx0 - sx1
        self.forwardDeltaList.append(delta)
    def avgForwardDelta(self):
        if len(self.forwardDeltaList) == 0: return None
        return sum(self.forwardDeltaList)/float(len(self.forwardDeltaList))
    def avgBackDelta(self):
        if len(self.backDeltaList) == 0: return None
        return sum(self.backDeltaList)/float(len(self.backDeltaList))        


def eucl(a,b):
    return sqrt(sum((a-b)**2))

def normalize (a):
    return a/norm(a)



class KmeansClassifier:
    '''used to classify unfonted tokens, currently only used as NN classifier'''
    def __init__(self):
        self.vs = []
        self.cs = []
        self.k = 1
        self.c = array(()) # array of prototypes
        self.cl = array(()) # array of class labels for c
    def train(self,v,c):
        self.vs.append(v)
        self.cs.append(c)
    def simpleClassify(self,v):
        minARG = argmin([eucl(x,v) for x in self.vs])
        return self.cs[minARG],eucl(self.vs[minARG],v)
    def train_done(self):
        self.c = kmeans(array(self.vs),self.k)
        # count class labels for all prototypes
        d = zeros((self.k,len(unique(self.cs))))
        #print d.shape
        #print len(self.vs)
        for i in range(len(self.vs)):
            #print argmin([eucl(self.vs[i],x) for x in self.c])
            #print self.cs[i]
            d[argmin([eucl(self.vs[i],x) for x in self.c]), self.cs[i]] += 1
        # determine most likely class for each prototype
        self.cl = argmax(d,1)
    def classify(self,v):
        # return class label of nearest prototype
        minArg = self.cl[argmin([eucl(v,x) for x in self.c])]
        return minArg,self.cl[minArg]
#    def visualize(self):
#        global dim
#        for i in range(len(self.c)):
#            subplot(ceil(sqrt(len(self.c))),ceil(sqrt(len(self.c))),i+1)
#            imshow(255-self.c[i].reshape(dim))
#            gray()
#       show()

def kmeans(data,k):
    from pylab import *
    from math import *
    from numpy import *
    from time import *
    from numpy.linalg import norm
    dim = (1024)
    # get k different initial random prototypes (c)
    c = data[ numpy.random.permutation(len(data))[:k] ]
    b = zeros(len(data))
    for i in range(100):
        b_old = b
        b = zeros(len(data))
        # calc cluster belongings of each data point
        for i in range(len(data)):
            b[i] = argmin([eucl(data[i],x) for x in c])
        # calc new cluster means
        for i in range(len(c)):
            cm = data[b==i]
            if len(cm) > 0:
                c[i] = mean(cm,0)
            else:
                # Set empty cluster centers to zero
                c[i] = zeros(prod(dim))
        if alltrue(b == b_old):
            break
    # remove "zero-cluster centers" before returning
    return c[array([not alltrue(x==zeros(prod(dim))) for x in c])]


# log timestamped message to file & stdout
def logMsg(f, msg):
  '''outputs message to file (f) and to stdout.'''
  ts = "[%s] " % (datetime.now().strftime("%Y/%m/%d %I:%M%p"),)
  out = ts + str(msg)
  print >> f, (out)
  if options.verbose >=1: print (out)

  # flush file output buffer immediately
  f.flush()
  os.fsync(f.fileno())





##########################################################
'''evaluate performance: this code is only useful when evaluating fontGroupers performance on data with three fonts, spread out amongst three pages'''
##########################################################
'''
@purpose: group font: 
@input ocropus book structure
@output font file
@author Michael P. Cutter cutter@iupr.com

@methods: graph cut algorithom, linkExploration 
'''
##########################################################

def evaluateClusterCRIME3(fontList):
    ''' HACKED TOGETHER JUST FOR crimeStory3font-book'''
    fontOne=0
    fontTwo=0
    fontThree=0
    
    for i in range(len(b.pages)):
        for j in range(len(b.pages[i].lines)):
            if(b.pages[i].lines[j].checkTokenable() == False): 
                print "bad line"
                continue
            for t in range(len(b.pages[i].lines[j].tokenIDs)):
                if b.pages[i].lines[j].tokenIDs[t] in fontList:
                    #hard coded known borders, lines of each font
                    if (i <= 1): 
                        fontOne+=1
                    elif(i >= 2 and i <= 5 ) :
                        fontTwo+=1
                    elif(i >= 6):
                        fontThree+=1
    print "fontone",fontOne,"percent",fontOne/float(0.000000001+fontOne+fontTwo+fontThree)
    print "fontTwo",fontTwo,"percent",fontTwo/float(0.000000001+fontOne+fontTwo+fontThree)
    print "fontThree",fontThree,"percent",fontThree/float(0.000000001+fontOne+fontTwo+fontThree)

    
def evaluateCRIME3_assignedREP(tokenList,f):
    ''' HACKED TOGETHER JUST FOR crimeStory3font-book'''
    falsePositive=0
    truePositive=0
    falseNegative=0
    trueNegative=0
    unlabeled=0
    seenList = []
    for t in tokenList:
        if t.tokenID in seenList: continue
        assignedFontClass = allTokens[t.tokenID].assignedFontClass
        fontClass = allTokens[t.tokenID].fontClass
        if assignedFontClass == 0 or fontClass == 0:
            #hard coded known borders, lines of each font
            if (t.foundPage[0] <= 1): 
                truePositive+=1
            else:
                falsePositive +=1 # over shattered
        elif assignedFontClass == 1 or fontClass == 1:
            #hard coded known borders, lines of each font
            if (t.foundPage[0] >= 2 and t.foundPage[0] <= 5): 
                truePositive+=1
            else:
                falsePositive +=1 # over shattered
        elif assignedFontClass == 2 or fontClass == 2:
            #hard coded known borders, lines of each font
            if (t.foundPage[0] >= 6): 
                truePositive+=1
            else:
                falsePositive +=1 # over shattered
        else:
            unlabeled+=1
        seenList.append(t.tokenID)
    logMsg(f, "percision "+ str(truePositive / float(falsePositive+truePositive+.00001)))
    logMsg(f,"unlabeled %"+ str(unlabeled / float(len(tokenList))))	
    logMsg(f,"num unlabeled %"+ str(unlabeled))


##############################################################################################
#Greedy Graph Segmentation
##############################################################################################

def linkExplore(allTokens):
    '''Main function for technique to find optimal set of tokens to group together into a candidate font'''
    canidates = {}
    epoc = 0
    numSwaps = options.numSwaps
    goalSet = set(makeLargeGoalList())
    fontList,foundSet = greedyStart()
    lastFoundSet = set()
    while( not goalSet.issuperset(foundSet) ):
        if options.verbose >= 1: 
            print "epoc= %i"%epoc
        if epoc == 0:
            if options.sparse:
                canidates = exploreSPARSE(fontList,goalSet.difference(foundSet))
            else:
                canidates = explore(fontList,goalSet.difference(foundSet))
        else:
            if options.sparse:
                canidates = exploreSPARSE(secondDepthList,goalSet.difference(foundSet))
            else: 
                canidates = explore(secondDepthList,goalSet.difference(foundSet))
        foundSet = selectBest( canidates, goalSet.difference(foundSet), fontList , foundSet, allTokens)
        secondDepthList = secondDepth(canidates,foundSet) 
        if lastFoundSet == len(foundSet) or epoc >= 100:
            break
        else:
            lastFoundSetLen = len(foundSet)
        epoc+=1
    for i in range(numSwaps):
        fontList = swapWeakLinks(fontList)
    return set(fontList)


def specificCharSearch(letter,tokenID,fontList):
    '''only finds relation core for same char-class inputs'''
    if letter == labels[tokenID]:
        return findRelationScore(tokenID,fontList)
    else: return 0 
    

def swapWeakLinks(fontList):
    '''Tries swapping a random token for one that results in a higher LinkScore'''
    global labels
    minThresh = 5
    newFontList = []
    fontList =  numpy.random.permutation(fontList)
    for tokenID in fontList:
        if findRelationScore(tokenID,fontList) < minThresh:
            bestMatch = argmax([specificCharSearch(labels[tokenID],x,fontList) for x in b.tokens.keys()])
            newFontList.append(bestMatch)
            #print "swapping a weaklink"
        else: newFontList.append(tokenID)
    return newFontList
            
            

def secondDepth(canidates,foundSet):
    '''explore canidates for possible 2nd depth matches'''
    secondDepthList = []
    for Tid,x in canidates.keys():
        if labels[x] not in foundSet:
            #print labels[x],x,labels[Tid],Tid
            secondDepthList.append(x)
    return secondDepthList
            
def makeLargeGoalList():
    '''returns ascii cars plus punct marks because ocr could mislabel'''
    goalList = []
    first = 33
    z = 122
    for x in range(first,z+1):
        goalList.append( chr(x) )	
    return goalList

def makeGoalList():
    '''returns list of ascii chars a-z & A-Z'''
    goalList = []
    A=65
    Z=90
    a=97
    z=122
    for x in range(A,Z+1):
        goalList.append( chr(x) )
    for x in range(a,z+1):
        goalList.append( chr(x) )
    return goalList




def findRelationScore(canidateTokenID,fontList):
    ''' finds the sum over all the token co-occurence edge weights between a token and group of tokens '''
    score = 0
    for tokenID in fontList:
        if options.sparse: score += n[tokenID].count(canidateTokenID)
        else: score += n[(tokenID,canidateTokenID)]
    return score

def greedyStart():
    ''' Inits a candidate font by selecting the token with the most frequent occurences, not already in any candidate font'''
    fontList = []
    foundList = []
    for tID,count in tokenCounts: #tokenCounts is sorted
        if tID not in masterFontList:
            foundList.append(ord(labels[tID]))
            fontList.append(tID)
            return fontList, set(foundList)
            
def initWordSet(startingPoint):
    '''temporay init at the most pop token, will be automated soon'''
    fontList = []
    foundList = []
    fontList.append(startingPoint)
    foundList.append(ord(labels[startingPoint]))
    return fontList, set(foundList)
            
def initSet():
    '''loads an entire starting setence as referance point'''
    fontList = []
    foundList = []
    for c in b.pages[1].lines[24].txt:
        foundList.append(c)
    for tID in b.pages[1].lines[24].tokenIDs:
        if tID not in fontList and labels(tID): fontList.append(tID)
    return fontList, set(foundList)
            


def explore(fontList,goalSet):
    ''' explore all nodes connected that are of the class that has not been found yet'''
    canidates = {}
    for tID in fontList: 
        for x in b.tokens.keys():
            #print "inEXPORE",tID,x,labels[x]
            if (labels[x] in goalSet) and (n[tID,x] > 0): #Hasan: There is a run-time error on this line with some images 
                canidates[(tID,x)] = int(n[tID,x])
    return canidates

#the sparse function is to be called when the matrix data structure consumes too much memory
def exploreSPARSE(fontList,goalSet):
    ''' explore all nodes connected that are of the class that has not been found yet'''
    print "start: exploreSPARSE()"
    print "fontList=",fontList
    canidates = {}
    for tID in fontList: 
        for x in b.tokens.keys():
            #print "inEXPORE",tID,x,labels[x],n[tID,x]
            #sys.exit(2)
            count = int(n[tID].count(x))
            if (labels[x] in goalSet) and (count > 0):
                #print "adding", labels[x]
                canidates[(tID,x)] = count
            if options.verbose >= 2:
                print "explore token# = %i "%x
    return canidates

def selectBest(canidates,goalSet,fontList,foundSet,allTokens):
    '''heuristic used to select the best token from a set of candidates to become a part of the candidate reconstructed font'''
    for char in goalSet:
        currMax = 0
        currMaxCount = 0
        maxIDs = -1
        foundFlag = False
        #print char
        for Tid,x in canidates.keys():
            #print labels[Tid],char
            if labels[x] == char and x not in fontList and labels[x] not in foundSet and findRelationScore(x,fontList) > currMax and x not in masterFontList:
                #if allTokens[x].count < currMaxCount: continue
                foundFlag = True
                currMax = findRelationScore(x,fontList) #canidates[(Tid,x)]
                currMaxCount = allTokens[x].count
                newFontID = x
        if foundFlag: 
            fontList.append(newFontID)
            foundSet.add(labels[newFontID])
    return foundSet


##############################################################################################
#create token co-occurence graph
##############################################################################################

def purgeSpace(line):
    '''removes spaces from line of text'''
    returnLine = []
    for c in line:
        if c==unicode(' ') or c ==unicode('\n'):
            continue
        returnLine.append(c)
    return returnLine

def purgeNewLine(line):
    '''removes newline chars from a line of text'''
    returnLine = []
    for c in line:
        if c ==unicode('\n') or ord(c) == 10:
            continue
        returnLine.append(c)
    return returnLine

def fillOutSentenceMatrix():
    '''creates a token co-occurence graph based sentence level co-occurance'''
    for i in range(len(b.pages)):
        for j in range(len(b.pages[i].lines)):
            if(b.pages[i].lines[j].checkTokenable() == False): 
                print "bad line"
                continue
            if len(b.pages[i].lines[j].tokenIDs) != len(b.pages[i].lines[j].txt):
                #print "not the same"
                b.pages[i].lines[j].txt = purgeSpace(b.pages[i].lines[j].txt)
                if len(b.pages[i].lines[j].tokenIDs) != len(b.pages[i].lines[j].txt):
                    sys.exit(5)
            for k in range(len(b.pages[i].lines[j].tokenIDs)):
                tokenID = b.pages[i].lines[j].tokenIDs[k]
                labels[tokenID] = b.pages[i].lines[j].txt[k]
                #print "was added to labels",tokenID
                for d in range(len(b.pages[i].lines[j].tokenIDs)):
                    n[(tokenID,b.pages[i].lines[j].tokenIDs[d])]+=1


def addToArray(inSameWordList):
    '''adds all tokens in the same word list to each other respective entry in the co-occurence matrix, n'''
    for tID in range(len(inSameWordList)):
        for tID2 in range(len(inSameWordList)):
            if tID == tID2: continue
            #print "inSameWord",inSameWordList[tID],inSameWordList[tID2]
            if options.sparse: n[inSameWordList[tID]].append(inSameWordList[tID2])
            else: n[(inSameWordList[tID],inSameWordList[tID2])]+=1
            

def fillOutWordMatrix():
    '''creates a token co-occurence graph based word level co-occurance'''
    if options.sparse: #if sparse is selected then add adjacent edges
        for t in b.tokens.keys():
            n[t] = []
    for i in range(len(b.pages)):
        for j in range(len(b.pages[i].lines)):
            if(b.pages[i].lines[j].checkTokenable() == False): 
                print "[info] bad line (untokenable line)"
                continue
            spaceCount = 0
            inSameWordList = []
            b.pages[i].lines[j].txt = purgeNewLine(b.pages[i].lines[j].txt)
            #print "newPAge",spaceCount
            for k in range(len(b.pages[i].lines[j].txt)):
                c = b.pages[i].lines[j].txt[k]
                #print c
                
                if c.isspace() or ord(c) == 10 or unicode('\n') == c:
                    #print "in term",c,"isspace",ord(c)
                    spaceCount+=1
                    addToArray(inSameWordList)
                    inSameWordList = []
                    continue
                
                #print "space count",spaceCount,"char is",ord(b.pages[i].lines[j].txt[k])
                inSameWordList.append(b.pages[i].lines[j].tokenIDs[k-spaceCount])
                #print b.pages[i].lines[j].tokenIDs[k-spaceCount],"k", b.pages[i].lines[j].txt[k]
                #sif b.pages[i].lines[j].tokenIDs[k-spaceCount] == 7967: sys.exit(3)
                labels[b.pages[i].lines[j].tokenIDs[k-spaceCount]] = b.pages[i].lines[j].txt[k]
            addToArray(inSameWordList) #end of line, assume this means end of word
            # FIXME add case for words extended over multiple lines



#########################################################################################
#token counts	
#########################################################################################


def readInTokenCounts(fn):
    '''reads in token count file, although this is only useful if you just want to graph the frequency, since this functionality is duplicated by other methods'''
    global tokenCounts
    tokenCountsH = {}
    if os.path.exists(fn) == False:
        print "Warning: file could not be opened: ",fn
        return []
    f    = file(fn, "r")
    data = [line.strip().split("\t") for line in f]
    for d in data:
        tID,count = d
        tokenCountsH[tID] = int(count)

    items = [(v, k) for k, v in tokenCountsH.items()]
    items.sort()
    items.reverse()             # so largest is first
    tokenCounts = [(int(k), int(v)) for v, k in items]

def displayTokenCounts(fn):
    '''print function for tokenCounts'''
    print tokenCounts[0]
    print tokenCounts[len(tokenCounts)-1]
    tokenNames = [(int(k)) for v, k in tokenCounts]
    tokenVal = [(int(v)) for v, k in tokenCounts]
    print tokenNames[0]
    print tokenVal[0]
    print len(tokenNames)
    print sum(tokenNames[:100]),"all",(sum(tokenNames))
    #plt.plot(tokenNames[:168])
    #plt.xlabel("token ID")
    #plt.ylabel("token density")
    #plt.suptitle("Token density distribution")
    #show()
    sys.exit()



########################################################################################
#gen fontID file for OCRopus extended book structure
#########################################################################################

def outputFontIDfile(tokenList):
    "outputs a cooresponding font group ID for each token if no font group ID exisits '0' is outputted"
    #transferTokenListToAllTokens(tokenList)
    for i in range(len(b.pages)):
        pageDir = b.pages[i].pageDir
        for j in range(len(b.pages[i].lines)):
            if(b.pages[i].lines[j].checkTokenable() == False): 
                print "bad line"
                continue
            #open file for writting
            lineName = b.pages[i].lines[j].tokenFile.split(".tokID.txt")[0]
            lineName = lineName[lineName.rfind("/")+1:]
            f = open(pageDir+"/"+lineName+".fontID.txt","w")  
            outString = ""
            for tokenID in b.pages[i].lines[j].tokenIDs:
                fontClass = allTokens[tokenID].fontClass
                #if no fontclass is set then use assigned
                if fontClass == -1: fontClass = allTokens[tokenID].assignedFontClass
                #if no assigned is known then output ?
                if fontClass == -1: fontClass = 0 # the class is unknown but it is better to print something then nothing"?"
                outString=str(fontClass)+"\n"
                f.writelines(outString)
            f.close()

def transferTokenListToAllTokens(tokenList):
    '''transfers font class information from chronological list to allTokenHash'''
    for tL in tokenList:
        allTokens[tL.tokenID].fontClass = tL.fontClass
        allTokens[tL.tokenID].assignedFontClass = tL.assignedFontClass


def printOutTXT(FONT):
    '''uses fontforges sample output methods to test font for readability'''
    allTheTXT=""
    for i in range(len(b.pages)):
        if (i <= 1 and FONT.fontname!="Untitled1"):
            continue
        if (i >=2 and i<=5 and FONT.fontname!="Untitled2"):
            continue
        if (i >=6 and FONT.fontname!="Untitled3"):
            continue
        for j in range(len(b.pages[i].lines)):
            if(b.pages[i].lines[j].checkTokenable() == False): 
                print "bad line"
                continue
            for c in b.pages[i].lines[j].txt:
                allTheTXT += c
            allTheTXT+="\n"
    fontforge.printSetup("pdf-file","test.pdf") 
    #FONT.printSample(  "fontsample" ,12,"l","test.pdf")
    print allTheTXT
    #FONT.printSample(  "fontdisplay" ,24,allTheTXT,"fontdisplay.pdf"+str(FONT.fontname))
    FONT.printSample(  "fontsample" ,9,allTheTXT,str(FONT.fontname+"test.pdf"))
    FONT.printSample(  "fontsample" ,24,"hello worldp","forPaper"+str(FONT.fontname))
    print FONT.fontname
    #sys.exit(0)

def visualizeFontLocation(tokenList,i):
    '''debug function to see distribution of font locations'''
    for t in tokenList:
        if t.fontClass == i:
            print "token of font:",i,"found on page:",t.foundPage,"line:",t.foundLine

def fillAllTokens():
    '''fills allTokens hash by parsing OCRopus extended book structure'''
    global allTokens
    global tokenCounts
    foundBefore = []
    for i in range(len(b.pages)):
        for j in range(len(b.pages[i].lines)): # iterate through all pages
            for k in range(len(b.pages[i].lines[j].tokenIDs)):
                coords = 0
                tokenID = b.pages[i].lines[j].tokenIDs[k]
                x0 = b.pages[i].lines[j].ccs[k,0]
                y0 = b.pages[i].lines[j].ccs[k,1]
                x1 = b.pages[i].lines[j].ccs[k,2]
                y1 = b.pages[i].lines[j].ccs[k,3]
                coords = x0,y0,x1,y1
                #print coords
                #print b.pages[i].lines[j].ccs[1,]
                #sys.exit(1)
                #token = self,coords,foundPage,foundLine,charClass,tokenID)
                if tokenID not in foundBefore:
                    allTokens[tokenID] = Token(coords,i,j, tokenID)
                    foundBefore.append(tokenID)
                else:
                    allTokens[tokenID].addOccurrence(coords,i,j)
    tokenCountsH = {}
    for t in allTokens.values(): tokenCountsH[t.tokenID] = t.count
    items = [(v, k) for k, v in tokenCountsH.items()]
    items.sort()
    items.reverse()             # so largest is first
    tokenCounts = [(int(k), int(v)) for v, k in items]
                    
def addToTokenList(tokenList):
    '''fills chronological list of tokens by parsing OCRopus extended book structure'''
    for i in range(len(b.pages)):
        for j in range(len(b.pages[i].lines)): # iterate through all pages
            for k in range(len(b.pages[i].lines[j].tokenIDs)):
                coords = 0
                tokenID = b.pages[i].lines[j].tokenIDs[k]
                x0 = b.pages[i].lines[j].ccs[k,0]
                y0 = b.pages[i].lines[j].ccs[k,1]
                x1 = b.pages[i].lines[j].ccs[k,2]
                y1 = b.pages[i].lines[j].ccs[k,3]
                coords = x0,y0,x1,y1
                tokenList.append( Token(coords,i,j, tokenID) )


def transferClasses(fontList,tokenList,i):
    '''quick and dirty hack to transfer info from one list to anfalsePositiveother in order to evaluate alg'''
    for t in tokenList:
        if t.tokenID in fontList:
            t.fontClass = i
            allTokens[t.tokenID].fontClass = i

#########################################################################################
#font class labeling by proximity
#########################################################################################



def insureBoundary(tokenList,k,i):
    '''smoothing function to ensure that the same area is looked at when in boundary condition'''
    length = len(tokenList)
    if length < (k * 2): return 0,0
    neg = i-k
    pos = i+k
    if neg < 0:
        return 0,pos-neg #neg will be a negative number so it is addition
    if pos > (length-1):
        return i-((length-1)-neg),length-1
    return neg,pos


def labelNeighborhood(tokenList):
    '''this function checks each token in the chronological token list to see if it has a font class,
    if it doesn't the token is based to labelViaNeighbor'''
    k = options.k # searchDistance = ?
    for i in range(len(tokenList)): #linearListOfCharacters
        if not allTokens[tokenList[i].tokenID].hasFontClass():
            labelViaNeighbor(tokenList,i)

def labelViaNeighbor(tokenList,i):
    '''this function assigns font cluster IDs to instances of tokens (letters)
    based on proximity to tokens which are members of candidate fonts.
    the label assigned to the letter is an 'assigned' label and does not affect the labels of adjacent letters'''
    weightPositive = 1
    weightAssigned = .1 #not used currently
    fontClassScore = zeros(options.numFontClasses)

    pos,neg = insureBoundary(tokenList,options.k,i)
    for j in range(pos,neg+1):
        if j == i: continue
        if allTokens[tokenList[j].tokenID].hasFontClass:
            for c in range(0,options.numFontClasses):
                if tokenList[j].fontClass == c:
                    #decaying weight given for numbers further from 'known' data point
                    fontClassScore[c]+=1*weightPositive*(1/float(abs(i-j)+1))
                #if tokenList[j].assignedFontClass == c:
                    #fontClassScore[c]+=1*weightAssigned
    allTokens[tokenList[i].tokenID].fontClassScoreUpdate(fontClassScore)			

######################################################################################
#Below functions use fontforge and token bitmaps to convert a list of tokens into a reconstructed font
######################################################################################


def padWithPil(imName):
    '''pad by adding a boarder of white space around character image prior to tracing'''
    #motivation: prevent residual artifacts from being introduced in reconstructed font
    from PIL import Image
    im = Image.open(imName)
    w,h = im.size
    new = Image.new(im.mode,(w+2,h+2),"white")
    new.paste(im,(1,1))
    newName = imName[len(imName)-4:]+"TEMP.png"
    new.save(newName)
    return newName

def makeFont(fontList,i):
    '''makeFont is the first version; it has been replaced by makeLessSupervisedFont, it is left here only as a reference'''
    #uses fontforge and psMat to convert token images into usable fonts
    #make a font from list
    FONT=fontforge.font() #
    #open known font
    font = fontforge.open("DejaVuSans.sfd") #the module font
    
    for Tid in fontList:
        print labels[Tid]
        try:
            c = FONT.createChar(ord(labels[Tid]))      #generate a new char #int represents unicode position
            tempImageFileName = padWithPil(b.tokens[Tid])		
            c.importOutlines(tempImageFileName)         #load outline
            os.remove(tempImageFileName)
            #on 64bit ubuntu this does not work as expected...
            c.autoTrace()   #trace	
            xminR,yminR, xmaxR,ymaxR = c.boundingBox()
            #K stands for known	
            xminK,yminK, xmaxK,ymaxK = font[ord(labels[Tid])].boundingBox()
#fontforge.unicodeFromName(chr(labels[Tid])
            xScale = (xmaxK - xminK) / float((xmaxR - xminR) )
            yScale = (ymaxK - yminK) / float((ymaxR - yminR) )
            #if xScale > 1: xScale = (xmaxR - xminR) / float((xmaxK - xminK) )
            #if yScale > 1: yScale = (ymaxR - yminR)/ float( (ymaxK - yminK) )
            scaler = psMat.scale(xScale,yScale)
            c.transform(scaler)
            #print "before transform",xminR,yminR, xmaxR,ymaxR
            #print "after",c.boundingBox()
            #print "goal",font["a"].boundingBox()
            #next translate max
            xminR,yminR, xmaxR,ymaxR = c.boundingBox()
            xmaxTranslate = xmaxK - xmaxR
            #if xmaxTranslate < 0: xmaxTranslate = xmaxR - xmaxK
            ymaxTranslate = ymaxK - ymaxR
            #if ymaxTranslate < 0: ymaxTranslate = ymaxR - ymaxK
            translatemax = psMat.translate(xmaxTranslate,ymaxTranslate)
            c.transform(translatemax)
            #set borders to match template
            c.width = font[str(labels[Tid])].width
            c.vwidth = font[str(labels[Tid])].vwidth
            
            
            
            
            c.right_side_bearing = font[str(labels[Tid])].right_side_bearing
            c.left_side_bearing = font[str(labels[Tid])].left_side_bearing
            #print "before translate max",xminR,yminR, xmaxR,ymaxR
            #print "after",c.boundingBox()
            #print "goal",font["a"].boundingBox()
            # next translate min
            '''
            xminTranslate = xminK - xminR
            yminTranslate = yminK - yminK
            translatemin = psMat.translate(xminTranslate,yminTranslate)
            c.transform(translatemin)
            print "before translate min",xminR,yminR, xmaxR,ymaxR
            print "after",c.boundingBox()
            print "goal",font["a"].boundingBox()
            '''
            c.autoTrace()
            #c.autoWidth( ) #does not work...	#Guesses at reasonable horizontal advance widths for the selected glyphs
            #c.autoInstr()	#Generates TrueType instructisons for all selected glyphs
            #c.autoHint()	#Generates PostScript hints for all selected glyphs.
            #print c.isWorthOutputting()
        except TypeError:
            continue
    #print "xmean",mean(xDeltaList)
    #print "ymean",mean(yDeltaList)
    #print std(xDeltaList)
    #print std(yDeltaList)
    #sys.exit(1)
    #printOutTXT(FONT)
    FONT.ascent = font.ascent
    FONT.descent = font.descent
    print "font",font.hasvmetrics,"dsf",font.xHeight,font.uwidth,font.ascent,font.descent
    print "FONT",FONT.hasvmetrics,"dsf",FONT.xHeight,FONT.uwidth,FONT.ascent,FONT.descent
    
    FONT.fontname=options.bookDir                 #Give the new font a name
    FONT.save(options.fontName+str(i)+".sfd") 

def makeLessSupervisedFont(fontList,i):
    '''takes a fontList as input and outputs a font.ttf file into the OCRopus extended book structure'''
    #uses fontforge and psMat to convert token images into usable fonts
    #make a font from list
#    fontforge.setPrefs("AutotraceArgs","-u 20")#Hasan: Added this line
    FONT=fontforge.font()
    fontforge.setPrefs("PreferPotrace", 1) # Hasan: added this line: Setting Potrace as the prefered boundray tracer
    fontforge.setPrefs("AutotraceAsk", "-O 0.5 -u 1 -t 1") # Hasan: added this line: Setting the parameters of the tracing library

    #open known font
    font = fontforge.open("DejaVuSans.sfd") 
    #the information from the module font is used in the following way:
    #to compute baseline percentage 
    #font is a known font that is used to model baseline proportion for characters of same class
    avgXscaleList = []
    avgYscaleList = []
    minYlist = []
    for Tid in fontList:
        if options.verbose >=2: print "making a font for character class",labels[Tid]
        try:
            c = FONT.createChar(ord(labels[Tid]))      #generate a new char #int represents unicode position
#            if (labels[Tid] == 'A' or labels[Tid] == 'a'): #Hasan: 'if' Added for debug purpose
#                print("<<<",labels[Tid],">>>")
            tempImageFileName = padWithPil(b.tokens[Tid])       
            c.importOutlines(tempImageFileName)         #load outline
            os.remove(tempImageFileName)
            #on 64bit ubuntu 'c.autotrace()' does not work as expected...
            c.autoTrace()   #trace  
            xminR,yminR, xmaxR,ymaxR = c.boundingBox()
            fH = ymaxR - yminR
            fW = xmaxR - xminR
            cH = allTokens[Tid].averageH 
            cW = allTokens[Tid].averageW
            if options.verbose >= 2: print "font",fH,fW,"char",cH,cW
            if (fW == 0 or fH == 0): # Hasan: added this 'if' statement
                print "Error: division by zero in makeLessSupervisedFont(), function call at line %i\n Possibly invalid bounding box info\n Pleae make sure autotrace and potrace libraries are installed"% currentframe().f_back.f_lineno
                raise(-1)
            avgXscaleList.append(cW/float(fW))
            avgYscaleList.append(fH/float(fH))
            scaler = psMat.scale(cW/float(fW),cH/float(fH))
            if options.verbose >= 2: print "scaler:",scaler
            c.transform(scaler)            
            
            xminR,yminR, xmaxR,ymaxR = c.boundingBox()
            #K stands for known 
            translatemax = psMat.translate((-1*xminR),(-1*yminR)) #place character on orgin (0,0)
            c.transform(translatemax)

            #next yscale translate
            xminR,yminR,xmaxR,ymaxR = c.boundingBox()
            if options.verbose >=3: print c.boundingBox()
            xminK,yminK, xmaxK,ymaxK = font[ord(labels[Tid])].boundingBox()
            baselineProp = yminK / (ymaxK-yminK)
            if options.verbose >=3: print baselineProp
            yscaleAmount = baselineProp * ymaxR
            if options.verbose >=3: print yscaleAmount
            translatemax = psMat.translate(0,yscaleAmount)
            c.transform(translatemax) #makes the size relative to cseg bbox
            #next xscale translate to pad the image
            xminR,yminR,xmaxR,ymaxR = c.boundingBox() #Hasan: BB in em units ?!?!
            xlength = xmaxR - xminR
            guessXpad = xlength/7
            translatemax = psMat.translate(guessXpad,0)
            c.transform(translatemax)

            # wrong way to do it
            xminR,yminR, xmaxR,ymaxR = c.boundingBox()
            #K stands for known 
            translatemax = psMat.translate((-1*xminR),0) 
            c.transform(translatemax)   #place character on orgin (0,0)
            
            xminR,yminR,xmaxR,ymaxR = c.boundingBox()
            xlength = xmaxR - xminR
            #add backpadding
            #if allTokens[Tid].avgBackDelta() is None:
            #if int(xlength/6)<3 or int(xlength/6)>5:
                #backPad=4
            #else:
                #backPad = int(xlength/6)
            backPad = 2    
            #else:
            #    backPad =  allTokens[Tid].avgBackDelta()/2
            translatemax = psMat.translate((backPad),0) #shift by backpad
            c.transform(translatemax)             
            
            xminR,yminR,xmaxR,ymaxR = c.boundingBox()
            xlength = xmaxR - xminR
            #if allTokens[Tid].avgForwardDelta() is None:
            #if int(xlength/6) < 3:
                #c.width= int(xmaxR + 3)
            #else:
                #c.width = int(xmaxR + xlength/6)
            c.width = c.width= int(xmaxR + 2)
            #else:
            #     c.width = xmaxR + allTokens[Tid].avgForwardDelta()/2
            
            minYlist.append(yminR)
            if options.verbose >= 2:
                print "backDelta",allTokens[Tid].avgBackDelta(),"forwardDelta",allTokens[Tid].avgForwardDelta()
                #c.vwidth = font[str(labels[Tid])].vwidth
                print  "c.right_side_bearing",c.right_side_bearing
                print "font[str(labels[Tid])].right_side_bearing",font[str(labels[Tid])].right_side_bearing
                #c.right_side_bearing = font[str(labels[Tid])].right_side_bearing
                print "c.left_side_bearing",c.left_side_bearing
                print " font[str(labels[Tid])].left_side_bearing", font[str(labels[Tid])].left_side_bearing
          # c.left_side_bearing = font[str(labels[Tid])].left_side_bearing
            
            #JUST A TRY DELETEME
            c.vwidth = 8.0
            c.right_side_bearing = abs(xminR)
            c.left_side_bearing = abs(xminR)
            
            
            #print c.isWorthOutputting()
        except TypeError:
            continue
    
    #everythign must be selected for the autos below to work
    #FONT.selection.select(("ranges",None),"a","z")
    #FONT.autoWidth(1 ) #does not work...   #Guesses at reasonable horizontal advance widths for the selected glyphs
    #c.autoInstr()  #Generates TrueType instructisons for all selected glyphs
    #c.autoHint()   #Generates PostScript hints for all selected glyphs.
    #xminR,yminR,xmaxR,ymaxR = font["p"].boundingBox()
    FONT.ascent = FONT.capHeight+(FONT.xHeight/10)
    if options.verbose >=2: print FONT.descent
    FONT.descent = int(.45 *  FONT.capHeight) #FONT.descent = int(min(minYlist)+(-.1)*FONT.xHeight) #causes fontforge to crash int(yminR+(1/6)*yminR)
    #print "font",font.hasvmetrics,"dsf",font.xHeight,font.uwidth,font.ascent,font.descent
    if options.verbose >=2: print "FONT",FONT.hasvmetrics,FONT.xHeight,FONT.uwidth,FONT.ascent,FONT.descent,FONT.upos,"capheight",FONT.capHeight,"xheight",FONT.xHeight
    #font.selection.select(("ranges",None)," "," ")
    avgXscale = (sum(avgXscaleList)/float(len(avgXscaleList)))
    avgYscale = (sum(avgYscaleList)/float(len(avgYscaleList)))
    
    #hard coded space character, FIXME this should be changed in the future
    font.selection.select(32)
    font.copy()
    FONT.selection.select(32)
    #FONT.selection.select(("ranges",None)," "," ")
    FONT.paste()
    FONT[32].width = font[32].width * avgXscale
    
    #hard coded '.' character, FIXME this should be changed in the future
    font.selection.select(46)
    font.copy()
    FONT.selection.select(46)
    FONT.paste()
    scaler = psMat.scale(avgXscale,avgXscale)
    FONT[46].transform(scaler)
    xminR,yminR, xmaxR,ymaxR = FONT[46].boundingBox()
    #K stands for known 
    translatemax = psMat.translate((-1*xminR),(-1*yminR)) #place character on orgin (0,0)
    FONT[46].transform(translatemax)

    #next yscale translate
    xminR,yminR,xmaxR,ymaxR = FONT[46].boundingBox()
    xminK,yminK, xmaxK,ymaxK = font[46].boundingBox()
    baselineProp = yminK / (ymaxK-yminK)
    yscaleAmount = baselineProp * ymaxR
    translatemax = psMat.translate(0,yscaleAmount)
    FONT[46].transform(translatemax)
    #next xscale translate to pad the image
    xminR,yminR,xmaxR,ymaxR = FONT[46].boundingBox()
    xlength = xmaxR - xminR
    guessXpad = xlength/6
    translatemax = psMat.translate(guessXpad,0)
    FONT[46].transform(translatemax)
    #set borders to match template
    FONT[46].width = xlength + xlength/3
    
    FONT.fontname=options.fontName +str( ("%.2d" % (i)) )  #Give the new font a name
    if options.verbose >= 2: print options.bookDir+"/fonts/"+options.fontName+str( ("%.2d" % (i)) )+".sfd"

    if not os.path.exists(options.bookDir+"/fonts"):
        os.makedirs(options.bookDir+"/fonts")

    FONT.save(options.bookDir+"/fonts/"+options.fontName+str( ("%.2d" % (i)) )+".sfd")
    FONT.generate(options.bookDir+"/fonts/"+options.fontName+str( ("%.2d" % (i)) )+".ttf")


#################################################################################################
#Dealing with unfonted tokens (tokens that are not part of a candidate font
#################################################################################################

def resize_character(ichar,nr=32,nc=32,borg=0,ifilter=Image.BICUBIC):
    '''this function uses PIL to resize an image of a character to 1024 vector'''
    import numpy.numarray
    from numpy.numarray import ones, zeros, array, where, shape , nd_image, arange, sum
    ichar = numpy.numarray.array(ichar,typecode=float)
    r = float(len(ichar))
    c = float(len(ichar[0]))
    richar = zeros((nr,nc))
    dr = nr - r
    dc = nc - c 
    if dr>=0 and dc >=0:
        dr = ceil(dr/2)
        dc = ceil(dc/2)
        richar[dr:dr+r,dc:dc+c] = ichar*255
    else:
#        print 'c=', c # Hasan: added this line
#        print 'r=', r # Hasan: added this line
        c = int (c) # Hasan: added this line
        r = int (r) # Hasan: added this line
        im = PIL.Image.new('L',(c,r))
        ichar.shape = c*r
        im.putdata(ichar*255)
        ichar.shape = r,c
        if r>=c:
            nnr = nr
            nnc = c*nnr/r	
        else:
            nnc = nc
            nnr = r*nnc/c
        nnr = ceil(nnr)
        nnc = ceil(nnc)
        nnc = int(nnc) # Hasan: added this line
        nnr = int(nnr) # Hasan: added this line
        rim = im.resize((nnc,nnr),ifilter)	#  Image.NEAREST , Image.BILINEAR , Image.BICUBIC , Image.ANTIALIAS
        _ichar = array(rim.getdata())
        _ichar = numpy.numarray.array(_ichar,typecode=float)
        _ichar.shape = nnr,nnc
        if borg==0:
            x,y = where(_ichar>=83) #magic binary constent
            _ichar = _ichar*0
            _ichar[x,y] = 255

        dr = nr - nnr
        dc = nc - nnc 
        dr = ceil(dr/2.0)
        dc = ceil(dc/2.0)
        
        richar[dr:dr+nnr,dc:dc+nnc] = _ichar
    rI = copy.deepcopy(richar)
    richar.shape = nr*nc
    return richar,rI

def getResizeSerial(tokenID):
    '''this function takes as input a tokenID and returns 1024 resized vector of the tokens prototype image'''
    import numpy.numarray
    from numpy.numarray import ones, zeros, array, where, shape , nd_image, arange, sum
    image = PIL.Image.open(b.tokens[tokenID])
    image_array = array(image.getdata())
    [columns,rows] = image.size
    image_array.shape = (rows,columns,3)
    image_array = numpy.numarray.array(image_array,typecode=int)
    image_array = image_array[:,:,0]
    serial, _ = resize_character(image_array)
    return serial


def makeKMEANS(fontList,allTokens):
    '''this function creates a nearest neighbor classifier for a candidate font'''
    kmeansC = KmeansClassifier()
    for tID in fontList:
        serial = getResizeSerial(tID) #loads a serial vector of the image resized
        kmeansC.train(serial,ord(labels[tID]))
    return kmeansC


def findOrphans(tokenList,kmeansList,f):
    '''this function assigns a font class to unfonted tokens if the tokens prototype image is within a threshold (e) of an image in a candidate font based on Euclidean distance '''
    minScoreThresh = options.e
    match=0
    notMatch=0
    for token in tokenList:
        repToken = allTokens[token.tokenID] #the rep token represents all the instances of this token
        if not repToken.hasAssignedFontClass() and not repToken.hasFontClass():
            minScore = minScoreThresh
            serial = getResizeSerial(token.tokenID)
            minsCharClass = 255
            for k in range(len(kmeansList)):
                charClass,score = kmeansList[k].simpleClassify(serial)
                if score < minScore: 
                    repToken.assignedFontClass = k
                    minScore = score
                    minsCharClass = charClass
            if minsCharClass == 255: continue
            if chr(minsCharClass) == labels[token.tokenID]: match+=1
            else: 
                notMatch+=1
                #print chr(minsCharClass),"not equal to",labels[token.tokenID]
                #if minScore == minScoreThresh: addToFont(tokenID,fontList)
    if options.verbose >= 1:
        print "match ratio",match/float(notMatch+match+.000000001),"match",match,"notMatch",notMatch
        logMsg(f, "match ratio "+str(match/float(notMatch+match+.000000001))+" match: "+str(match)+" notMatch: "+str(notMatch))

#add tokens to candidate fonts that were missed because they were not co-occur in words e.g I
def adoptOrphans(CandidateFont):
    '''input == candidateFont object; decides to adopts tokens with assigned token classes same as candidate font and needed'''
    global masterFontList
    global allTokens
    consideringScore = {}
    consideringToken = {}
    for c in CandidateFont.needSet:
        consideringScore[c] = 0
    for token in allTokens.values():
        if token.assignedFontClass == CandidateFont.candidateFontID:
            if token.tokenID not in masterFontList:
              if labels[token.tokenID] in CandidateFont.needSet:
                  if token.confidenceAF >consideringScore[labels[token.tokenID]]:
                      consideringScore[labels[token.tokenID]] = token.confidenceAF
                      consideringToken[labels[token.tokenID]] = token.tokenID                
    for tID in consideringToken.values():
        #complete all steps necessary to add tokenID to candidate font
        CandidateFont.addToHasSet(tID)
        CandidateFont.addToTokenSet(tID)
        masterFontList.append(tID)
        allTokens[tID].fontClass = CandidateFont.candidateFontID
    #print "need",CandidateFont.needSet
    #print "has",CandidateFont.hasSet
    #print "goal",CandidateFont.goalSet
      
#def addToFont(tokenID,fontList):
    #findRelationScore(canidateTokenID,fontList)
        
#################################################################################################
#Helpful utility functions
#################################################################################################

def computeAllAverages():
    '''finds the average W and H of the letters represented by a token'''
    for token in allTokens.values():
        token.findAverageWandH()
        #print "avgs H,W",token.averageH,token.averageW

def printFontListAverages(fontList):
    '''prints the average W and H of the letters represented by a token'''
    for tID in fontList:
        print "avgs H,W",allTokens[tID].averageH,allTokens[tID].averageW

def findBackandForwardDelta(tokenList,fontList):
    '''finds the average of the amount of space between a token and its adjacent letters'''
    for index in range(len(tokenList)):
        tokenI = tokenList[index].tokenID 
        if tokenI in fontList:
            if index!= 0: 
                allTokens[tokenI].setBackwardNeighbor(tokenList[index-1],tokenList[index])
            if index != len(tokenList)-1:
                allTokens[tokenI].setForwardNeighbor(tokenList[index+1],tokenList[index])



#########################################################################################
#main logic	
#########################################################################################

def reconstructFonts(f):
    ''' main method: f = output file to log msg to \n 
	calls implementation of greedy graph parition algorithm 
	searches 'n' token-graph data structure for specified number candidate fonts
	calls 'makelesssuperverised font', which calls fontforge to add parameters to candidate fonts 
	for each reconstructed font, a .ttf file is outputted to the extended-ocropus-book-structure
	calls implementation of font cluster identification	
	for each line in the extended-ocropus-book-structure a fontID string is outputted
    '''
    tokenList = []
    kmeansList = []
    listOfCandidateFonts = []
    for i in range(options.numFontClasses):
        logMsg(f, "##############################\n now operating on font cluster:::"+str(i)+":::\n")
        fontList = linkExplore(allTokens)
        masterFontList.extend(fontList)
        #print "current masterFontList",masterFontList
        #print fontList
        fontList = list(fontList)
        listOfCandidateFonts.append(CandidateFont(fontList,i))
        listOfCandidateFonts[i].genGoalSet() #static set of 52 letters the algorithm is searching for
        listOfCandidateFonts[i].genHasSet()
        listOfCandidateFonts[i].genNeedSet()
        logMsg(f, "fontList: %s" % (str(fontList),))

        addToTokenList(tokenList) #tokenList contains each character in order and their tokenID
  
        #transferTokenListToAllTokens(tokenList)

        transferClasses(fontList,tokenList,i)	
        labelNeighborhood(tokenList) #uses the chronological tokenList to assign font groups 

        adoptOrphans(listOfCandidateFonts[i]) #uses assigned font group score to adopt needed tokens to candidate font
        fontList = listOfCandidateFonts[i].tokenSet
        
        transferClasses(fontList,tokenList,i)
        labelNeighborhood(tokenList)
#        print "font list", fontList  #Hasan: this line is added
#        print 'all Tokens', allTokens #Hasan: this line is added
        kmeansList.append(makeKMEANS(fontList,allTokens))
        visualizeFontLocation(tokenList,i) # Hasan: uncommented
        findBackandForwardDelta(tokenList,fontList)
        makeLessSupervisedFont(fontList,i) # invokes fontforge by using ccseg.txt information to add metrics and vectors to font
    if options.verbose >=1: print "all candidates formed, assigning remainder"
    #visualizeFontLocation(tokenList,1)
    if options.evaluate: 
        for cF in listOfCandidateFonts:
            evaluateClusterCRIME3(cF.tokenSet)
    findOrphans(tokenList,kmeansList,f) #uses the shape to assign font groups to unfonted tokens
    if options.verbose >=1: print "runing labelNeighborhood with k=500"
    options.k = 500
    labelNeighborhood(tokenList)
    if options.evaluate: evaluateCRIME3_assignedREP(tokenList,f)
    outputFontIDfile(tokenList) #outputs file: for each tokenIDline what font to print each token in


def main():
    #parse usr options
    parser = OptionParser()
    parser.add_option("-d", "--book", dest="bookDir",
                  help="bookname of OCR bookstructure [EXTENDED]")
    parser.add_option("-n", "--numFontClasses",default=1,
                  dest="numFontClasses", type="int", help="the number of fontClasses")
    parser.add_option("-k", "--numNearestNeighbors", default=1,type="int",
                  dest="k",help="the number of neighbors to shatter")
    parser.add_option("-s", "--numSwaps", default=3,
                  dest="numSwaps",type="int",help="the number of time to try swapping for stronger connected tokens")
    parser.add_option("-e", "--errorThresh",default=42**2,
                  dest="e",type="int",help="the threshold for allowing match when computing eucliden distance")
    parser.add_option("-E", "--evaluate",action="store_true",
                  dest="evaluate",help="use evaluate option only if target data matches evaluate function")                  
    parser.add_option("-v", "--verbose",default=1,
                  dest="verbose",type="int",help="this value affects how much output will be displayed")                  
    parser.add_option("-f","--fontName",default="font",dest="fontName",help="name of the font")
    parser.add_option("-o","--outputLog",default="genericName",dest="o",help="name of log file")
    parser.add_option("-S","--sparse",default= False, dest="sparse",help="use slower datastructure, that uses much less memory",  action="store_true") 

    global options
    (options, args) = parser.parse_args()
    if options.bookDir is None:
        print "[ERROR] must set ocropus extended book directory path with -d option"
        exit(2)
#    if options.verbose >= 1:
#        print "Book Dir= %s"%options.bookDir
#        print "e= %i"%options.e
#        print "k= %i"%options.k
#        print "Number of font classes= %i"%options.numFontClasses
    outputFile = "output_"+str(options.o)+"errorThresh"+str(options.e)+"K"+str(options.k)+"NUMCLASSES"+str(options.numFontClasses)+"numSwaps"+str(options.numSwaps)
    f = open(outputFile, 'w')
    logMsg(f, "GGS: Greedy Graph Segmentation")
    logMsg(f, "Output file: %s" % (outputFile,))
    logMsg(f, "==================================================================")
    logMsg(f, "numFontClusters : %f" % (float(options.numFontClasses),))
    logMsg(f, "Error thresh: %f" % (float(options.e),))
    logMsg(f, "fontname: %s" % (str(options.fontName),))
    logMsg(f, "bookdir: %s" % (str(options.bookDir),))
    logMsg(f, "==================================================================")


    #init book structure
    global b
    global tokenCounts
    tokenCounts = []
    print "starts reading book structure-->"
    b = Book(options.bookDir)
    print "<--ends reading book structure....\n"
    print "Number of tokens in b.token= %i"% len(b.tokens)
    #readInTokenCounts(options.bookDir+"/tokenCounts.txt")
    global n
    
#    if options.sparse == False and len(b.tokens) > 20000: #Hasan: avoiding program crash due to large memory allocation for 'n' array
#        print "[warn] fontGrouper requires huge memory size to process the current book."
#        print "  [info] Switching from 2d array to sparse hash-map instead."
#        print "    [warn] sparse hash map is slow and execution time could take hours [depends on book size]."
#        print "      [tip] to speed up the process, use -s option to set numSwaps to 1 instead of the requested [or default] value of %i" % options.numSwaps
#        options.sparse = True
        
    if options.sparse: 
        n = {}
        print "[info] Using sparse hashmap for co-occurance matrix (requires less memory, but slow)"
    else: 
        if b.tokens == {}:
            print "[fatal error] No tokens were found in the book structure."
            print "   [info] pages2lines stage could be the source of this error."
            exit(2)
        try:
            n=zeros((max(b.tokens)+1,max(b.tokens)+1))
            print "[info] Using 2d array for co-occurance matrix (fast in execution)"
        except:
            print "[warn] Not enough memory. fontGrouper requires huge memory size to process the current book."
            print "  [info] Switching from 2d array to sparse hash-map instead."
            print "    [warn] sparse hash map is slow and execution time could take hours [depends on book size]."
            print "      [tip] to speed up the process, use -s option to set numSwaps to 1 instead of the requested [or default] value of %i" % options.numSwaps
            options.sparse = True
            n = {}
            
    #here is where we change it to a sparse hashmap pointing to lists
    
    global labels
    global masterFontList
    masterFontList = []
    labels = {}
    #fill out n with coaccurance count of tokens on each line
    fillOutWordMatrix()
    #findMaxNode()
    #fillOutSentenceMatrix()
  

    global allTokens
    allTokens = {}
    fillAllTokens()
    computeAllAverages()
    reconstructFonts(f)


if __name__ == "__main__":
    main()







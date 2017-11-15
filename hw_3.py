import re
import os
import copy
import math
import sys
import random
#flags
MCAP = 1
Perceptrons = 1
stopint = 1
#set variable
#MCAP
rate = 1.5
rlist = [0.3,0.5,0.9,1.5,2]
loop = 20
#Perceptrons
ratePlist = [0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.3,1.5,2]
loopPlist = [10,20]
# rateP = 1.5
# loopP = 2

hamset = []
spamset = []
stopset = []
numham = 0 
numspam = 0

def delStop(wordset,stopset):
    indi = 0
    wordsettemp = copy.copy(wordset)
    for words in wordset:
        for word in stopset:
            if words == word:
                wordsettemp.remove(words)
    return wordsettemp
#Ignore punctuation & special characters ,normalize words by converting them to lower case, converting plural words to singular
def getword(SString):
    mailwords = re.split(r'\W*', SString)
    #if len(word) > 12 it's very likely that this is not a meaningful word so ignore it  
    lowwords =[word.lower() for word in mailwords if(len(word) > 2 and len(word) < 12 and word.isalpha())]
    slow = []
    #converting plural words to singular
    for word in lowwords:
        if word[-1] == 's':
            #print(word[:-1])
            slow.append(word[:-1])
        else:
            #print(word)
            slow.append(word)
    return slow

def getSample(path,numham,numspam,terms):
    i = 0
    sample = [[0 for col in range(len(terms)+2)] for row in range(numham + numspam)]
    pathDir =  os.listdir(path + 'ham/')
    for allDir in pathDir:
        f = open(path + 'ham/'+ allDir)
        s=f.read()
        wordlisttemp = []
        wordlisttemp = getword(s)
        sample[i]=[0]*(len(terms)+2)
        for word in wordlisttemp:
            if word in terms:
                sample[i][terms.index(word)+1]+=1
        sample[i][0] = 1
        sample[i][len(terms)+1] = 1
        i = i+1
    pathDir =  os.listdir(path+'spam/')
    for allDir in pathDir:
        f = open(path + 'spam/' + allDir)
        s=f.read()
        wordlisttemp = []
        wordlisttemp = getword(s)
        sample[i]=[0]*(len(terms)+2)
        for word in wordlisttemp:
            if word in terms:
                sample[i][terms.index(word)+1]+=1
        sample[i][0] = 1
        sample[i][len(terms)+1] = 0
        i = i+1
    return sample
def training ( path ,stopset,flag):
    samclass = []
    wordlist = []
    wordset = []
    wordVec = []
    indiword = 0
    num = 0
    pathDir =  os.listdir(path)
    for allDir in pathDir:
        num+=1
        f = open(path +allDir)
        s=f.read()
        wordlisttemp = []
        wordlisttemp = getword(s)
        wordlist.extend(wordlisttemp)
    wordset = list(set(wordlist))
    if flag is 0:
        return wordset,num
    else:#deled stop words
        wordset = delStop(wordset,stopset)
        return wordset,num

if __name__ == '__main__': 

    fp = open("results.txt", "a")
    f = open('stopWords.txt')
    s=f.read()
    wordlist = []
    wordlist = getword(s)
    stopset = list(set(wordlist))
    hamset,numham = training('train'+'/ham/',stopset,stopint) 
    spamset,numspam = training('train'+'/spam/',stopset,stopint)
#======================test ==========================
    terms = []
    tempspam = []
    tempham = [] 
    tempspam = copy.copy(spamset)
    tempham = copy.copy(hamset)
    tempspam.extend(tempham)
    terms = list(set(tempspam))#all words set
    #   Data    matrix  of  size    m   x   (n+2)
    sampleTrain = [[0 for col in range(len(terms)+2)] for row in range(numham + numspam)]
    sampleTrain = getSample('train/',numham,numspam,terms)
    SUMTrain = numham + numspam
    i = 0
    pathDir =  os.listdir('test/ham/')
    for allDir in pathDir:
        i = i + 1
    numhamT = i 
    i = 0 
    pathDir =  os.listdir('test/spam/')
    for allDir in pathDir:
        i = i +1
    numspamT = i
    SUMTest = numhamT + numspamT
    sampleTest = [[0 for col in range(len(terms)+2)] for row in range(numhamT + numspamT)]
    sampleTest = getSample('test/',numhamT,numspamT,terms)

    if MCAP is 1:
        for r in rlist:
            print '========traininng use MCAP========'
            print >> fp, '========traininng use MCAP========'
            Pr = [0]*(numham + numspam)
            dw = [0]*(len(terms)+1)
            he = 0 
            w= [0]*(len(terms)+1)
            # rate = 1.5
            # r = 0.3
            # loop = 20
            for i in range(0,loop): 
                for x in range(0,SUMTrain):
                    he = 0
                    for y in range(1,len(terms)+1):
                        he = he + w[y]*sampleTrain[x][y]
                    if w[0] + he > 700:
                        Pr[x] = 1
                    else:
                        Pr[x] = math.exp(w[0] + he)/(1 + math.exp(w[0] + he))
                for i in range(0,(len(terms)+1)):
                    for j in range(0,SUMTrain):
                        dw[i] = dw[i] + sampleTrain[j][i] * (sampleTrain[j][len(terms)+1] - Pr[j])

                for i in range(0,(len(terms)+1)):
                    w[i] = w[i] + rate * (dw[i] - r *w[i])
            print '========testing use MCAP========'
            print >> fp, '========testing use MCAP========'
            testham = 0
            testspam = 0
            Pr = [0]*(numhamT + numspamT)
            for x in range(0,numhamT):
                he = 0
                for y in range(1,len(terms)+1):
                    he = he + w[y]*sampleTest[x][y]
                if w[0] + he > 700:
                    Pr[x] = 1
                else:
                    Pr[x] = math.exp(w[0] + he)/(1 + math.exp(w[0] + he))
                if Pr[x] > 0.5:
                    testham = testham + 1
            for x in range(numhamT,SUMTest):
                he = 0
                for y in range(1,len(terms)+1):
                    he = he + w[y]*sampleTest[x][y]
                if w[0] + he > 700:
                    Pr[x] = 1
                else:
                    Pr[x] = math.exp(w[0] + he)/(1 + math.exp(w[0] + he))
                if Pr[x] < 0.5:
                    testspam = testspam + 1
            if stopint is 1:
                print 'stopwords removed'
                print >> fp, 'stopwords removed'
            else:
                print 'stopwords not removed'
                print >> fp, 'stopwords not removed'
            print 'learning rate = ' ,rate
            print >> fp, 'learning rate = ',rate

            print 'r = ' ,r
            print >> fp, 'r = ' ,r

            print 'iterations = ' + str(loop)
            print >> fp, 'iterations = ' + str(loop)

            print 'MCAP accuracy rate:' + str(float(testspam + testham)/float(SUMTest))
            print >> fp, 'MCAP accuracy rate:' + str(float(testspam + testham)/float(SUMTest))

            print '************************'
            print >> fp, '************************'

    if Perceptrons is 1:
        # rateP = 1.5
        # loopP = 2
        for x in ratePlist:
            for y in loopPlist:
                rateP = x
                loopP = y

                print '========traininng use Perceptrons========'
                print >> fp, '========traininng use Perceptrons========'
                Pr = [0]*(numham + numspam)
                dw = [0]*(len(terms)+1)
                wP= [0]*(len(terms)+1)
                # rateP = 1.5
                # loopP = 20
                for i in range(0,loopP):
                    for i in range(0,SUMTrain):
                        judge = 0
                        for j in range(0,(len(terms)+1)):
                            judge = judge + wP[j]*sampleTrain[i][j]
                        if judge > 0:
                            Pr[i] = 1
                        else:
                            Pr[i] = 0
                    for i in range(0,(len(terms)+1)):
                        for j in range(0,SUMTrain):
                            dw[i] = dw[i] + sampleTrain[j][i] * (sampleTrain[j][len(terms)+1] - Pr[j])

                    for i in range(0,(len(terms)+1)):
                        wP[i] = wP[i] + rateP * (dw[i] - wP[i])
                print '========testing use Perceptrons========'
                print >>fp , '========testing use Perceptrons========'
                judge = 0 
                testham = 0
                testspam = 0   
                for i in range(0,numhamT):
                    for j in range(0,(len(terms)+1)):
                        judge = judge + wP[j]*sampleTest[i][j]
                    if judge > 0:
                        testham = testham + 1
                    judge = 0
                for i in range(numhamT,SUMTest):
                    for j in range(0,(len(terms)+1)):
                        judge = judge + wP[j]*sampleTest[i][j]
                    if judge < 0:
                        testspam = testspam + 1
                    judge = 0
                if stopint is 1:
                    print 'stopwords removed'
                    print >>fp , 'stopwords removed'
                else:
                    print 'stopwords not removed'
                    print >>fp ,'stopwords not removed'
                print 'learning rate = ' + str(rateP)
                print >>fp ,'learning rate = ' + str(rateP)
                print 'iterations = ' + str(loopP)
                print >>fp ,'iterations = ' + str(loopP)
                print 'Perceptrons accuracy rate:' + str(float(testspam + testham)/float(SUMTest))
                print >>fp ,'Perceptrons accuracy rate:' + str(float(testspam + testham)/float(SUMTest))
    fp.close()
    
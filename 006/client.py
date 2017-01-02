#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import re
import xmlrpc.client
import datetime

groupSeparator="Moses::ContextScope::GroupSeparator"
recordSeparator="Moses::ContextScope::RecordSeparator"

#######################################################

def scoreOrderFromFVals(fvals):

    results=[]

    parts=fvals.strip().split()

    feature=None
    size=0

    for part in parts:
        if part.endswith("="):
            if feature != None:
                results.append("{}{}".format(feature,size))
            feature=part
            size=0

        else:
            size += 1

    if feature != None:
        results.append("{}{}".format(feature,size))

    return results

#######################################################

def scoreSlice(scores, scoreOrder, featureName):

    start=0

    for featureInfo in scoreOrder:

        name,size = featureInfo.split("=")
        
        if name==featureName:
            return start, start+int(size)
        else:
            start += 1

    raise LookupError("Feature {} was requested, but was not found in {}".format(featureName, scoreOrder))

#######################################################

def topts(topts, source, featureName):

    results={}

    for topt in topts:
        start=topt["start"]
        end=topt["end"]+1
        source_phrase=" ".join(source[start:end])
        target_phrase=topt["phrase"]
        scores=topt["scores"]
#        scoreStart, scoreEnd = scoreSlice(scores, scoreOrder, featureName)
#        print(scoreStart)
#        print(scoreEnd)
        scores=topt["labelledScores"][featureName][0]
        print("{} ||| {} ||| {}".format(source_phrase, target_phrase, " ".join([str(score) for score in scores])))
        
        

#######################################################

url = "http://localhost:8090/RPC2"
proxy = xmlrpc.client.ServerProxy(url)

texts=["je vous achète un chat"]

positive={
          texts[0]:"chat     ||| kitty ||| 2 2 2 2\nje vous achète ||| I would like to buy you ||| 1 1 1 1\n",
         }

negative={
          texts[0]:"un ||| a ||| 1000000000000000000 1000 1000 1000\n",
         }


for text in texts:


    params = {
              "text":text,
              "topt":"true",
              "add-score-breakdown":"true",
              "nbest":1,
             }

    result = proxy.translate(params)

    for key,value in result.items():
        
        if key=='text':
            value = re.sub(r"UNK\S+", "<unk>", result['text'])

#        print("{}\t{}".format(key,value))
#        print()

#    scoreOrder=scoreOrderFromFVals(result["nbest"][0]["fvals"])

#    print("Score order:", end="\t")
#    print(scoreOrder)

    source_words=text.split()
    topts(result["topt"], source_words, "TranslationModel2")


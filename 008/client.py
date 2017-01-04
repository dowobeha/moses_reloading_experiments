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

def topts(topts, source, featureName):

    result=""

    for topt in topts:
        start=topt["start"]
        end=topt["end"]+1
        source_phrase=" ".join(source[start:end])
        target_phrase=topt["phrase"]
#        scores=topt["scores"]
#        scoreStart, scoreEnd = scoreSlice(scores, scoreOrder, featureName)
#        print(scoreStart)
#        print(scoreEnd)
        scores=topt["labelledScores"][featureName][0]
        result += "{} ||| {} ||| {}\n".format(source_phrase, target_phrase, " ".join([str(score) for score in scores]))
        
    return result
        

#######################################################

static_moses = xmlrpc.client.ServerProxy("http://localhost:8090/RPC2")
dynamic_moses = xmlrpc.client.ServerProxy("http://localhost:8091/RPC2")

texts=["je vous achète un chat"]

positive="chat ||| kitty ||| 1000000000 1000000000 1000000000 100000000"


for text in texts:

    source_words=text.split()

    static_moses_result = static_moses.translate({"text":text, "topt":"true"})
    print(re.sub(r"UNK\S+", "<unk>", static_moses_result['text']))
    print()

    dynamic_pt=topts(static_moses_result["topt"], source_words, "TranslationModel2")
    print("dynamic_pt=\"{}\"".format(dynamic_pt))
    print()

    dynamic_pt=dynamic_pt+positive
    print("dynamic_pt=\"{}\"".format(dynamic_pt))
    print()

    contextScope = "TranslationModel0" + recordSeparator + dynamic_pt
    print("contextScope=\"{}\"".format(contextScope))
    print()

    dynamic_moses_result = dynamic_moses.translate({"text":text, "topt":"true","context-scope":contextScope})
    print(re.sub(r"UNK\S+", "<unk>", dynamic_moses_result['text']))
    print()

    actual_dynamic_pt=topts(dynamic_moses_result["topt"], source_words, "TranslationModel0")
    print("actual_dynamic_pt=\"{}\"".format(actual_dynamic_pt))
    print()


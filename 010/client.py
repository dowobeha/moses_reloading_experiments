#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import re
import xmlrpc.client
import datetime
from collections import defaultdict

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

class LMdict:

    def __init__(self, lm_string):
        self.LM = defaultdict(dict)
        for line in lm_string.split("\n"):
#            if line.strip() and not "\\" in line:
            if "\t" in line:
                entry = line.split("\t")
                if len(entry) == 3:
                    left_coef = float(entry[0])
                    ngram = entry[1]
                    right_coef = float(entry[2])
                    self.LM[len(ngram.split())][ngram] = (float(left_coef), float(right_coef))
                elif len(entry) == 2:
                    try:
                        left_coef = float(entry[0])
                        ngram = entry[1]
                        self.LM[len(ngram.split())][ngram] = (float(left_coef), None)
                    except ValueError:
                        ngram = entry[0]
                        right_coef = float(entry[1])
                        self.LM[len(ngram.split())][ngram] = (None, float(right_coef))
                else:
                    print("Unexpected LM entry: {}".format(line))

    def get_nlist(self):
        return sorted(self.LM.keys())

    def update(self, update_string):
        pass #TODO: get ngrams from update string and update coefficients

    def toString(self):

        def _xstr(value):
            if value == None:
                return ""
            return str(value)

        ret = "\n\\data\\\n"
        for key in sorted(self.LM.keys()):
            ret+="ngram {}={}\n".format(key, len(self.LM[key]))
        for key in sorted(self.LM.keys()):
            ret+="\n\\{}-grams:\n".format(key)
            for ngram in sorted(self.LM[key].keys()):
                entry = self.LM[key][ngram]
                left_coef = entry[0]
                right_coef = entry[1]
                ret+="{}\t{}\t{}".format(_xstr(left_coef), ngram, _xstr(right_coef)).strip()+"\n"
        ret+="\n\\end\\\n"
        return ret
         

#######################################################


static_moses = xmlrpc.client.ServerProxy("http://localhost:8090/RPC2")
dynamic_moses = xmlrpc.client.ServerProxy("http://localhost:8091/RPC2")

texts=["je vous achète un chat"]

#positive="chat ||| kitty ||| 1000000000 1000000000 1000000000 100000000"

with open("static.lm","r") as lm:
    lm_string = lm.read()

dynamic_lm = LMdict(lm_string)

print("lm_string=\"{}\"".format(lm_string))
print()
print("dynamic_lm=\"{}\"".format(dynamic_lm.toString()))

for text in texts:

    source_words=text.split()

    static_moses_result = static_moses.translate({"text":text, "topt":"true"})
    print(re.sub(r"UNK\S+", "<unk>", static_moses_result['text']))
    print()

    dynamic_pt=topts(static_moses_result["topt"], source_words, "TranslationModel2")
    print("dynamic_pt=\"{}\"".format(dynamic_pt))
    print()

#    dynamic_pt=dynamic_pt+positive
#    print("dynamic_pt=\"{}\"".format(dynamic_pt))
#    print()

    contextScope = "TranslationModel0" + recordSeparator + dynamic_pt + groupSeparator + "LM0" + recordSeparator + dynamic_lm.toString()
#    contextScope = "TranslationModel0" + recordSeparator + dynamic_pt + groupSeparator + "LM0" + recordSeparator + lm_string
    print("contextScope=\"{}\"".format(contextScope))
    print()

    dynamic_moses_result = dynamic_moses.translate({"text":text, "topt":"true","context-scope":contextScope})
    print(re.sub(r"UNK\S+", "<unk>", dynamic_moses_result['text']))
    print()

    actual_dynamic_pt=topts(dynamic_moses_result["topt"], source_words, "TranslationModel0")
    print("actual_dynamic_pt=\"{}\"".format(actual_dynamic_pt))
    print()


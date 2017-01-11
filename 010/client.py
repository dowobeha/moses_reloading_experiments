#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
from nltk.util import ngrams
import sys
import re
import xmlrpc.client
import datetime
import math
import subprocess
from collections import defaultdict as dd
import cProfile as profile

#######################################################
# Globals

groupSeparator="Moses::ContextScope::GroupSeparator"
recordSeparator="Moses::ContextScope::RecordSeparator"

languages=["fr","de"]

sources = {'de':u"ich kaufe sie eine katze", 'fr':u"je vous achète un chat"}

static_ports = {'de':8081, 'fr':8082}
dynamic_ports = {'de':8083, 'fr':8084}

dynamic_pts = {}
dynamic_lm = None

def defaultLambda():
    return -1

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

#class LMdict:
#
#    def __init__(self, lm_string):
#        self.LM = defaultdict(dict)
#        for line in lm_string.split("\n"):
##            if line.strip() and not "\\" in line:
#            if "\t" in line:
#                entry = line.split("\t")
#                if len(entry) == 3:
#                    left_coef = float(entry[0])
#                    ngram = entry[1]
#                    right_coef = float(entry[2])
#                    self.LM[len(ngram.split())][ngram] = (float(left_coef), float(right_coef))
#                elif len(entry) == 2:
#                    try:
#                        left_coef = float(entry[0])
#                        ngram = entry[1]
#                        self.LM[len(ngram.split())][ngram] = (float(left_coef), None)
#                    except ValueError:
#                        ngram = entry[0]
#                        right_coef = float(entry[1])
#                        self.LM[len(ngram.split())][ngram] = (None, float(right_coef))
#                else:
#                    print("Unexpected LM entry: {}".format(line))
#
#    def get_nlist(self):
#        return sorted(self.LM.keys())
#
#    def update(self, update_string):
#        pass #TODO: get ngrams from update string and update coefficients
#
#    def toString(self):
#
#        def _xstr(value):
#            if value == None:
#                return ""
#            return str(value)
#
#        ret = "\\data\\\n"
#        for key in sorted(self.LM.keys()):
#            ret+="ngram {}={}\n".format(key, len(self.LM[key]))
#        for key in sorted(self.LM.keys()):
#            ret+="\n{}-grams:\n".format(key)
#            for ngram in sorted(self.LM[key].keys()):
#                entry = self.LM[key][ngram]
#                left_coef = entry[0]
#                right_coef = entry[1]
#                ret+="{}\t{}\t{}".format(_xstr(left_coef), ngram, _xstr(right_coef)).strip()+"\n"
#            
#        return ret

#######################################################

#def moses(port, src_language, tgt_language, text, iteration):
def static_moses(port, text):
    url = "http://localhost:{}/RPC2".format(port)
    proxy = xmlrpc.client.ServerProxy(url)
    params = {
        "text":text,
#        "align":"true",
#        "add-score-breakdown":"true",
#        "sg":"true",
        "topt":"true"
    }
    return proxy.translate(params)
#    result = proxy.translate(params)
#    for key, value in result.items():
#        if key != "text":
#        if key != "text" and key != 'nbest':
#            print(key + "\t" + str(value) + "\n")
#    totalScore = result['nbest'][0]['totalScore']
#    kenLMscore = result['nbest'][0]['scores']['LM0'][0][0]
#    updatedLMscore = result['nbest'][0]['scores']['LM1'][0][0]
#    result = re.sub(r"UNK(\S+)", r"\1", result['text'])
#    ter = '%.3f' % pyter.ter(result, ref)
#    ter="N/A"
#    print("Iteration {}, {}-{}:\t{}\ttotal={}\tLM0={}\tLM1={}".format(iteration, src_language, tgt_language, result, totalScore, kenLMscore, updatedLMscore))
#    return "<s> " + result + " </s>"

#######################################################

def dynamic_moses(port, text, contextScope):
    url = "http://localhost:{}/RPC2".format(port)
    proxy = xmlrpc.client.ServerProxy(url)
    params = {
        "text":text,
        "topt":"true",
        "contextScope":contextScope
    }
    return proxy.translate(params)

#######################################################

def unique_ngrams(translations, i, max_n):
    """ extracts all n-grams up to length max_n that are not present in source i """
    ngrams_in_this_source = set()
    for n in range(1, max_n+1):
        for ngram in ngrams(translations[i].split(), n):
            if "<s>" not in ngram and "</s>" not in ngram:
                ngrams_in_this_source.add(ngram)

    ngrams_not_in_this_source = set()
    for n in range(1, max_n+1):
 #       print(sources)
        for j, source in enumerate(translations):
#            print("{}\t{}".format(l,source))
            if j != i:
                for ngram in ngrams(source.split(), n):
                    if ngram not in ngrams_in_this_source and "<s>" not in ngram and "</s>" not in ngram:
#                        print("{} is not in source {}".format(ngram, language))
                        ngrams_not_in_this_source.add(ngram)

    return ngrams_not_in_this_source

#######################################################

def gamma(xk, max_n):
    """ extracts all n-grams up to length n """
    multiset = dd(int)
    for n in range(1, max_n+1):
        grams = ngrams(xk.split(), n)
        for gram in grams:
            multiset[gram] += 1
    return multiset

#######################################################

def get_updates(sources, ngram_order):
    """ gets the updates """
    updates = []
    K = len(sources) # number of languages
    average = dd(float)
    gammas = []

    # average sparse vectors
    for i, xk in enumerate(sources):
        gammas.append(gamma(xk, ngram_order))
        for ngram, count in gammas[i].items():
            average[ngram] += count / K

    # great updates
    for i, xk in enumerate(sources):
        updates.append(dd(float))
        for ngram, value in average.items():
            updates[i][ngram] = -1 * (gammas[i][ngram] - value)

#    print('UPDATES = {}'.format(updates))
    return [dict(x) for x in updates]

#######################################################

#def writeTM(i, ngrams, max_order):
def writePT(src_lang, result):
    pt = topts(result["topt"], 
                sources[src_lang].split(), 
                "TranslationModel2",
                )

    dynamic_pts[src_lang] = pt

    pt_filename = ".pt".format(src_lang)
    with open(pt_filename, 'w') as pt_file:
        pt_file.write(pt)
    print("{} written...".format(pt_filename))
#    tm_file = open("dd_tm{}".format(i), 'w')
#
#    for order in range(1, max_order+1):
#
#        ngram_list = [ngram for ngram in ngrams if len(ngram)==order];
#        print('NGRAMS = {}'.format(ngrams))
#        print('NGRAM_LIST = {}'.format(ngram_list))
#
#        for ngram in sorted(ngram_list):
#            tm_file.write(" ".join(ngram) + "\n")
#
#    tm_file.close()

#######################################################

def writeLM(i, Lambdas, max_order):
    lm_filename = "{}.lm.arpa".format(languages[i])
    lm_file = open(lm_filename, 'w')

    lm_file.write("\n\\data\\\n")
    for order in range(1, max_order+1):
        count=len([(ngram,value) for ngram, value in Lambdas[i].items() if (len(ngram)==order)])
        if order==1:
            count += 1
        lm_file.write("ngram {}={}\n".format(order, count))
    for order in range(1, max_order+1):
        lm_file.write("\n\\{}-grams:\n".format(order))
        ngram_list = [(ngram, value) for ngram, value in Lambdas[i].items() if len(ngram)==order];
        if order==1:
            unk=(('<unk>',), -5)
            ngram_list.append(unk)
        for ngram, value in sorted(ngram_list):
            if ngram==('<unk>',):
                lm_file.write("{}\t{}\n".format(value, "<unk>"))
            elif ngram==('<s>',):
                lm_file.write("{}\t{}\t{}\n".format("-99", "<s>", "-99"))
            elif Lambdas[i][ngram] < 0:
                if (order < max_order):
                    lm_file.write("{}\t{}\t{}\n".format(Lambdas[i][ngram], " ".join(ngram), "-99"))
                else:
                    lm_file.write("{}\t{}\n".format(Lambdas[i][ngram], " ".join(ngram)))
            elif Lambdas[i][ngram] >= 0:
                if (order < max_order):
                    lm_file.write("{}\t{}\t{}\n".format("0", " ".join(ngram), "-99"))
                else:
                    lm_file.write("{}\t{}\n".format("0", " ".join(ngram)))
    lm_file.write("\n\\end\\\n")
    lm_file.close()
    with open(lm_filename) as lm_file:
        dynamic_lm = lm_file.read()
    print("{} written...".format(lm_filename))

#######################################################i

#def dualDecomposition(iterations=2000, eta=0.1, max_order=1):
#    translations=[]
#    for language in languages:
#        translation=moses(ports[language], language, "english", sources[language], 0)
#        translations.append(translation)
#
#    for i in range(0, len(translations)):
#        writeTM(i, unique_ngrams(translations, i, max_order), max_order)
#
#    # 
#    Lambdas = [dd(defaultLambda) for _ in translations]
#
#    for t in range(iterations):
#        for i, update in enumerate(get_updates(translations, max_order)):
##            print('UPDATE = {}'.format(update))
#            for ngram, value in update.items():
#                Lambdas[i][ngram] += eta * value
#        #TODO: pick one n-gram and print out lambda value to see if it changes over time
##            print("lambda[0]['a cat'] = {}".format(Lambdas[0][('a cat',)]))
##            print("lambda[1]['a cat'] = {}".format(Lambdas[1][('a cat',)]))
#            writeLM(i, Lambdas, max_order)
#
#        translations = []
#        for language in languages:
#            translation = moses(dd_ports[language], language, "english", sources[language], t+1)
#            translations.append(translation)
#
#        if len(set(translations)) == 1:
#            # CONVERGED
#            pass

#######################################################


#static_moses = xmlrpc.client.ServerProxy("http://localhost:8090/RPC2")
#dynamic_moses = xmlrpc.client.ServerProxy("http://localhost:8091/RPC2")

#texts=["je vous achète un chat"]

#positive="chat ||| kitty ||| 1000000000 1000000000 1000000000 100000000"

#with open("static.lm","r") as lm:
#    lm_string = lm.read()

#dynamic_lm = LMdict(lm_string)

#print("lm_string=\"{}\"".format(lm_string))
#print()
#print("dynamic_lm=\"{}\"".format(dynamic_lm.toString()))

#for text in texts:
def dualDecomposition(iters=10, eta=0.1, max_order=3):

    dynamic_pts = {}

    translations = []
    for src_lang in languages:

        result = static_moses(static_ports[src_lang], 
                                sources[src_lang],
                                )

        translation = re.sub(r"UNK\S+", "<unk>", result['text'])
        print(translation)
        translations.append(translation)

        writePT(src_lang, result)
#        pt = topts(result["topt"], 
#                    sources[src_lang].split(), 
#                    "TranslationModel2",
#                    )
#
#        dynamic_pts[src_lang] = pt
#
#        pt_filename = ".pt".format(src_lang)
#        with open(pt_filename, 'w') as pt_file:
#            pt_file.write(pt)
#        print("{} written...".format(pt_filename))

    Lambdas = [dd(defaultLambda)] * len(translations)

    for i in range(iterations):
        for translation, update in enumerate(get_updates(translations, max_order)):
            for ngram, value in update.items():
                Lambdas[translation][ngram] += eta * value 

            writeLM(translation, 
                    Lambdas, 
                    max_order,
                    )

        translations = []
        for src_lang in languages:

            contextScope = "TranslationModel" + recordSeparator + dynamic_pts[src_lang] \
                            + groupSeparator \
                            + "LM0" + recordSeparator + dynamic_lm

            result = dynamic_moses(dynamic_ports[src_lang], 
                                    sources[src_lang], 
                                    contextScope)

            translation = re.sub(r"UNK\S+", "<unk>", result['text'])
            print(translation)
            translations.append(translation)

            writePT(src_lang, result)
#            pt = topts(result["topt"], 
#                        sources[src_lang].split(), 
#                        "TranslationModel2",
#                        )
#
#            dynamic_pts[src_lang] = pt
#
#            pt_filename = ".pt".format(src_lang)
#            with open(pt_filename, 'w') as pt_file:
#                pt_file.write(pt)
#            print("{} written...".format(pt_filename))

        if len(set(translations)) == 1:
            # CONVERGED
            pass



#    static_moses_result = static_moses.translate({"text":src_text, "topt":"true"})
#    print(re.sub(r"UNK\S+", "<unk>", static_moses_result['text']))
#    print()
#
#    dynamic_pt=topts(static_moses_result["topt"], source_words, "TranslationModel2")
#    print("dynamic_pt=\"{}\"".format(dynamic_pt))
#    print()
#
##    dynamic_pt=dynamic_pt+positive
##    print("dynamic_pt=\"{}\"".format(dynamic_pt))
##    print()
#
#    contextScope = "TranslationModel0" + recordSeparator + dynamic_pt + groupSeparator + "LM0" + recordSeparator + dynamic_lm.toString()
#    print("contextScope=\"{}\"".format(contextScope))
#    print()
#
#    dynamic_moses_result = dynamic_moses.translate({"text":text, "topt":"true","context-scope":contextScope})
#    print(re.sub(r"UNK\S+", "<unk>", dynamic_moses_result['text']))
#    print()
#
#    actual_dynamic_pt=topts(dynamic_moses_result["topt"], source_words, "TranslationModel0")
#    print("actual_dynamic_pt=\"{}\"".format(actual_dynamic_pt))
#    print()

if __name__ == '__main__':
#    profile.runctx("dualDecomposition()", locals(), globals())
    dualDecomposition()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from nltk.util import ngrams
import re
import xmlrpc.client
from collections import defaultdict as dd

#######################################################
# Globals

languages=["de", "fr"]

sources = {languages[0]:u"ich kaufe sie eine katze", 
            languages[1]:u"je vous achète un chat",
            }

static_ports = {languages[0]:8081, 
                languages[1]:8082,
                }

dynamic_ports = {languages[0]:8083, 
                    languages[1]:8084,
                    }

groupSeparator="Moses::ContextScope::GroupSeparator"

recordSeparator="Moses::ContextScope::RecordSeparator"

staticPTstem = "StaticPT"

dynamicPTstem = "DynamicPT"

dynamicLMstem = "DynamicLM"

dynamic_PTs = {languages[0]:None,
                languages[1]:None,
                }

dynamic_LM = None

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
        scores=topt["labelledScores"][featureName][0]
        result += "{} ||| {} ||| {}\n".format(source_phrase, target_phrase, " ".join([str(score) for score in scores]))
        
    return result
        
#######################################################

def static_moses(port, text):
    url = "http://localhost:{}/RPC2".format(port)
    proxy = xmlrpc.client.ServerProxy(url)
    params = {
        "text":text,
        "topt":"true",
    }
    return proxy.translate(params)

#######################################################

def dynamic_moses(port, text, contextScope):
    url = "http://localhost:{}/RPC2".format(port)
    proxy = xmlrpc.client.ServerProxy(url)
    params = {
        "text":text,
        "topt":"true",
        "contextScope":contextScope,
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
        for j, source in enumerate(translations):
            if j != i:
                for ngram in ngrams(source.split(), n):
                    if ngram not in ngrams_in_this_source and "<s>" not in ngram and "</s>" not in ngram:
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

    return [dict(x) for x in updates]

#######################################################

def writePT(src_lang, result, PTname):
    pt = topts(result["topt"], 
                sources[src_lang].split(), 
                PTname,
                )

    global dynamic_PTs
    dynamic_PTs[src_lang] = pt

    pt_filename = "_{}.pt".format(PTname)
    with open(pt_filename, 'w') as pt_file:
        pt_file.write(pt)
    print("{} written...".format(pt_filename))

#######################################################

# TODO: Modify to write one string to file instead of line by line.
#       Are there buffer concerns if modified in such a way? 
# TODO: Eliminate need for lang_index parameter.

def writeLM(i, Lambdas, max_order, LMname):
    lm_filename = "_{}.lm".format(LMname)
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
        global dynamic_LM
        dynamic_LM = lm_file.read()

    print("{} written...".format(lm_filename))

#######################################################i

def dualDecomposition(iters=10, eta=0.1, max_order=3):

    translations = []
    for lang_index, src_lang in enumerate(languages):

        result = static_moses(static_ports[src_lang], 
                                sources[src_lang],
                                )

        translation = re.sub(r"UNK\S+", "<unk>", result['text'])
        print(translation)
        translations.append(translation)

        PTname = staticPTstem + str(lang_index)

        writePT(src_lang, 
                result,
                PTname,
                )

    Lambdas = [dd(defaultLambda)] * len(translations)

    for i in range(iters):
        for lang_index, update in enumerate(get_updates(translations, max_order)):
            for ngram, value in update.items():
                Lambdas[lang_index][ngram] += eta * value 

            LMname = dynamicLMstem + str(lang_index)

            # TODO: Remove lang_index parameter once method is modifed.
            writeLM(lang_index, 
                    Lambdas, 
                    max_order,
                    LMname,
                    )

        translations = []
        for lang_index, src_lang in enumerate(languages):

            print("dynamic_PTs[{}]=\n\"{}\"".format(src_lang, dynamic_PTs[src_lang]))
            print("dynamic_LM=\n\"{}\"".format(dynamic_LM))

            contextScope = "TranslationModel" + recordSeparator + dynamic_PTs[src_lang] \
                            + groupSeparator \
                            + "LM0" + recordSeparator + dynamic_LM

            result = dynamic_moses(dynamic_ports[src_lang], 
                                    sources[src_lang], 
                                    contextScope,
                                    )

            translation = re.sub(r"UNK\S+", "<unk>", result['text'])
            print(translation)
            translations.append(translation)

            PTname = dynamicPTstem + str(lang_index)

            writePT(src_lang, 
                    result,
                    PTname
                    )

        if len(set(translations)) == 1:
            # CONVERGED
            pass



if __name__ == '__main__':
    dualDecomposition()

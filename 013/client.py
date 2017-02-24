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

static_ports = {languages[0]:8080, 
                languages[1]:8081,
                }

dynamic_ports = {languages[0]:8090, 
                    languages[1]:8091,
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
#def topts(topts, source, featureName, Lambdas):

#    print("\ntopts =\n{}".format(topts))

    result=""

    for topt in topts:
        start=topt["start"]
        end=topt["end"]+1
        source_phrase=" ".join(source[start:end])
        target_phrase=topt["phrase"]
        scores=topt["labelledScores"][featureName][0]
#        scores = [score + Lambdas[target_phrase] for score in scores]
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

#    print("contextScope=\n\"{}\"".format(contextScope))

    url = "http://localhost:{}/RPC2".format(port)

#    print(url)

    proxy = xmlrpc.client.ServerProxy(url)
    params = {
        "text":text,
        "topt":"true",
        "context-scope":contextScope,
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
#    return multiset
    return dict(multiset)   #WAB

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
#            updates[i][ngram] = -1 * (gammas[i][ngram] - value)
            try:                                                        #WAB
                updates[i][ngram] = -1 * (gammas[i][ngram] - value)     #WAB
            except KeyError:                                            #WAB
                pass                                                    #WAB

    print("\ngammas={}".format(gammas))
    print("\naverage={}".format(average))
    print("\nupdates={}".format(updates))
    return [dict(x) for x in updates]

#######################################################

def writePT(src_lang, result, PTname):
#def writePT(src_lang, Lambdas, result, PTname):
    pt = topts(result["topt"], 
                sources[src_lang].split(), 
                PTname,
#                Lambdas,
                )

#    print("{} = \n{}".format(PTname, pt))

    global dynamic_PTs
    dynamic_PTs[src_lang] = pt

    pt_filename = "_{}.pt".format(PTname)
    with open(pt_filename, 'w') as pt_file:
        pt_file.write(pt)
    print("\n{} written...".format(pt_filename))

#######################################################

# TODO: Modify to write one string to file instead of line by line.
#       Are there buffer concerns if modified in such a way? 
# TODO: Eliminate need for lang_index parameter.

def writeLM(Lambdas, max_order, LMname):
    lm_filename = "_{}.lm".format(LMname)
    lm_file = open(lm_filename, 'w')

    lm_file.write("\n\\data\\\n")
    for order in range(1, max_order+1):
#        count=len([(ngram,value) for ngram, value in Lambdas[i].items() if (len(ngram)==order)])
        count=len([(ngram,value) for ngram, value in Lambdas.items() if (len(ngram)==order)])
        if order==1:
            count += 3
        lm_file.write("ngram {}={}\n".format(order, count))
    for order in range(1, max_order+1):
        lm_file.write("\n\\{}-grams:\n".format(order))
#        ngram_list = [(ngram, value) for ngram, value in Lambdas[i].items() if len(ngram)==order];
        ngram_list = [(ngram, value) for ngram, value in Lambdas.items() if len(ngram)==order];
        if order==1:
            unk=(('<unk>',), -5)
            ngram_list.append(unk)
            starttag=(('<s>',), -99)
            ngram_list.append(starttag)
            endtag=(('</s>',),-0)
            ngram_list.append(endtag)
        for ngram, value in sorted(ngram_list):
            if ngram==('<unk>',):
                lm_file.write("{}\t{}\n".format(value, "<unk>"))
            elif ngram==('<s>',):
                lm_file.write("{}\t{}\t{}\n".format("-99", "<s>", "-99"))
            elif ngram==('</s>',):
                lm_file.write("{}\t{}\t{}\n".format("-0", "</s>", "-0"))
#            elif Lambdas[i][ngram] < 0:
            elif Lambdas[ngram] < 0:
                if (order < max_order):
#                    lm_file.write("{}\t{}\t{}\n".format(Lambdas[i][ngram], " ".join(ngram), "-99"))
                    lm_file.write("{}\t{}\t{}\n".format(Lambdas[ngram], " ".join(ngram), "-99"))
                else:
#                    lm_file.write("{}\t{}\n".format(Lambdas[i][ngram], " ".join(ngram)))
                    lm_file.write("{}\t{}\n".format(Lambdas[ngram], " ".join(ngram)))
#            elif Lambdas[i][ngram] >= 0:
            elif Lambdas[ngram] >= 0:
                if (order < max_order):
                    lm_file.write("{}\t{}\t{}\n".format("0", " ".join(ngram), "-99"))
                else:
                    lm_file.write("{}\t{}\n".format("0", " ".join(ngram)))
    lm_file.write("\n\\end\\\n")
    lm_file.close()

    with open(lm_filename) as lm_file:
        global dynamic_LM
        dynamic_LM = lm_file.read()

    print("\n{} written...".format(lm_filename))

#######################################################i

def dualDecomposition(iters=2000, eta=0.1, max_order=3):

    translations = []
    for lang_index, src_lang in enumerate(languages):

        result = static_moses(static_ports[src_lang], 
                                sources[src_lang],
                                )

        translation = "<s> " + re.sub(r"UNK\S+", "<unk>", result['text']) + " </s>"
        print("\nlanguage={} translation={}".format(src_lang, translation))
        translations.append(translation)

        PTname = staticPTstem + str(lang_index)

        writePT(src_lang, 
                result,
                PTname,
                )

#    Lambdas = [dd(defaultLambda)] * len(translations)
    Lambdas = dd(defaultLambda)

    for i in range(iters):
#        for lang_index, update in enumerate(get_updates(translations, max_order)):
        print("\ntranslations={}".format(translations))
        for update in get_updates(translations, max_order):
            #TODO: Should update be enumerated, and the update for each language 
            # is used to update the PT for the other language.  So, updates from the 
            # translation from de source updates the fr PT and vice versa?
            for ngram, value in update.items():
#                print("ngram={}\tvalue={}".format(ngram, value))
#                Lambdas[lang_index][ngram] += eta * value 
#                print("\nngram = {}\neta = {}\tvalue = {}\nproduct = {}".format(ngram, eta, value, (eta*value)))
                Lambdas[ngram] += eta * value 

#        PTname = staticPTstem + str(lang_index)

#        writePT(src_lang, 
#                result,
#                PTname,
#                )
#            LMname = dynamicLMstem + str(lang_index)

            # TODO: Remove lang_index parameter once method is modifed.
#            writeLM(lang_index, 
#                    Lambdas, 
        writeLM(Lambdas, 
                max_order,
#                    LMname,
                dynamicLMstem,
                )

        print("\nLambdas = \n{}".format(Lambdas))
        print("\ndynamic_LM = \n{}".format(dynamic_LM))

        translations = []
        for lang_index, src_lang in enumerate(languages):

#            print("dynamic_PTs[{}]=\n\"{}\"".format(src_lang, dynamic_PTs[src_lang]))

            PTname = dynamicPTstem + str(lang_index)
            LMname = dynamicLMstem + str(lang_index)

            contextScope = PTname + recordSeparator + dynamic_PTs[src_lang] \
                            + groupSeparator \
                            + LMname + recordSeparator + dynamic_LM

            result = dynamic_moses(dynamic_ports[src_lang], 
                                    sources[src_lang], 
                                    contextScope,
                                    )

            translation = "<s> " + re.sub(r"UNK\S+", "<unk>", result['text']) + " </s>"
            print("\nlanguage={} translation={}".format(src_lang, translation))
            translations.append(translation)

            PTname = dynamicPTstem + str(lang_index)

            writePT(src_lang, 
                    result,
                    PTname
                    )

#            for lang in languages:
#                print("\n{} pt=\n{}\n".format(lang, dynamic_PTs[lang]))
#            print("\nlm=\n{}\n".format(dynamic_LM))

        if len(set(translations)) == 1:
            # CONVERGED
            print("\nTranslations converged - exiting")
            exit()



if __name__ == '__main__':
    dualDecomposition()

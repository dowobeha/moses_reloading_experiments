#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from nltk.util import ngrams
import re
import xmlrpc.client
from collections import defaultdict as dd

#######################################################
# Globals

langs=["de", "fr",]

sources = [u"ich kaufe sie eine katze", u"je vous achète un chat",]
            
static_ports = [8080, 8081,]

reloading_ports = [8090, 8091,]

reloading_PTs = [None, None,]

reloading_LMs = [None, None,]

groupSeparator="Moses::ContextScope::GroupSeparator"

recordSeparator="Moses::ContextScope::RecordSeparator"

def defaultLambda():
    return -1

#######################################################

def clean_translation(trans):
    trans = re.sub(r"\|\d+-\d+\| +", r"", trans)
    trans = re.sub(r"UNK\S+", "<unk>", trans)
    trans = "<s> " + trans + " </s>"
    return trans

#######################################################

def topts(topts, source, featureName):

    result=""

    for topt in topts:
        start=topt["start"]
        end=topt["end"]+1
        source_phrase=" ".join(source[start:end])
        target_phrase=topt["phrase"]
        scores=topt["labelledScores"][featureName][0]
        result += "{} ||| {} ||| {}\n".format(source_phrase, 
                                            target_phrase, 
                                            " ".join([str(score) for score in scores]),
                                            )
       
    return result
        
#######################################################

def static_moses(port, text):
    url = "http://localhost:{}/RPC2".format(port)
    proxy = xmlrpc.client.ServerProxy(url)
    params = {
        "text":text,
        "topt":"true",
        "align":"true",
        "word-align":"true",
    }
    return proxy.translate(params)

#######################################################

def reloading_moses(port, text, contextScope):

    url = "http://localhost:{}/RPC2".format(port)

    proxy = xmlrpc.client.ServerProxy(url)
    params = {
        "text":text,
        "topt":"true",
        "align":"true",
        "word-align":"true",
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

# TODO: make sure that the OOV key appears in the french sentence
def handleOOV(oov, lang_index):
    for i in range(len(langs)):
        if i == lang_index:
            continue
        ltt_name = "static.{}.ltt".format(i)
        with open(ltt_name) as ltt:
            for line in ltt.read().split("\n"):
                if len(line.split()) > 0 and oov == line.split()[1]:
                    key = line.split()[0]
                    for entry in reloading_PTs[i].split("\n"):
                        entry = [s.strip() for s in entry.split("|||")]
                        if entry[0] == key:
                            # TODO: maybe new entry coeffs should be scaled by the prob in the ltt
                            new_entry = "{} ||| {} ||| {}\n".format(oov, entry[1], entry[2])
                            reloading_PTs[lang_index] += new_entry

#######################################################

def writePT(lang_index, result, prev_pt):
    pt_name = "reloading.{}.pt".format(lang_index)
    pt = topts(result["topt"], 
                sources[lang_index].split(), 
                prev_pt,
                )

    global reloading_PTs
    reloading_PTs[lang_index] = pt

    with open(pt_name, 'w') as pt_file:
        pt_file.write(pt)
    print("\n{} written...".format(pt_name))

#######################################################

def writeLM(lang_index, Lambdas, max_order):
    lm_name = "reloading.{}.lm".format(lang_index)
    lm_file = open(lm_name, 'w')

    lm_file.write("\n\\data\\\n")
    for order in range(1, max_order+1):
        count=len([(ngram,value) for ngram, value in Lambdas[lang_index].items() if (len(ngram)==order)])
        if order==1:
            count += 3
        lm_file.write("ngram {}={}\n".format(order, count))
    for order in range(1, max_order+1):
        lm_file.write("\n\\{}-grams:\n".format(order))
        ngram_list = [(ngram, value) for ngram, value in Lambdas[lang_index].items() if len(ngram)==order];
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
            elif Lambdas[lang_index][ngram] < 0:
                if (order < max_order):
                    lm_file.write("{}\t{}\t{}\n".format(Lambdas[lang_index][ngram], " ".join(ngram), "-99"))
                else:
                    lm_file.write("{}\t{}\n".format(Lambdas[lang_index][ngram], " ".join(ngram)))
            elif Lambdas[lang_index][ngram] >= 0:
                if (order < max_order):
                    lm_file.write("{}\t{}\t{}\n".format("0", " ".join(ngram), "-99"))
                else:
                    lm_file.write("{}\t{}\n".format("0", " ".join(ngram)))
    lm_file.write("\n\\end\\\n")
    lm_file.close()

    with open(lm_name) as lm_file:
        global reloading_LM
        reloading_LMs[lang_index] = lm_file.read()

    print("\n{} written...".format(lm_name))

#######################################################i

def dualDecomposition(iters=2000, eta=0.1, max_order=3):

    translations = []
    for lang_index, src_lang in enumerate(langs):

        result = static_moses(static_ports[lang_index], 
                                sources[lang_index],
                                )

        translation = clean_translation(result['text'])
        print("\nlanguage={} translation={}".format(src_lang, translation))
        translations.append(translation)

        pt_name = "static.{}.pt".format(lang_index)
        writePT(lang_index, 
                result,
                pt_name,
                )

    Lambdas = [dd(defaultLambda)] * len(translations)

    for i in range(iters):
        print("\ntranslations={}".format(translations))
        updates = get_updates(translations, max_order)
        for lang_index, src_lang in enumerate(langs):
            #TODO: Should update be enumerated, and the update for each language 
            # is used to update the PT for the other language.  So, updates from the 
            # translation from de source updates the fr PT and vice versa?
            for ngram, value in updates[lang_index].items():
                Lambdas[lang_index][ngram] += eta * value 

            lm_name = "reloading.{}.lm".format(lang_index)
            writeLM(lang_index,
                    Lambdas, 
                    max_order,
                    )

        translations = []
        for lang_index, src_lang in enumerate(langs):

            pt_name = "reloading.{}.pt".format(lang_index)
            lm_name = "reloading.{}.lm".format(lang_index)

            contextScope = pt_name + recordSeparator + reloading_PTs[lang_index] \
                            + groupSeparator \
                            + lm_name + recordSeparator + reloading_LMs[lang_index]

            result = reloading_moses(reloading_ports[lang_index], 
                                    sources[lang_index], 
                                    contextScope,
                                    )

            translation = clean_translation(result['text'])
            print("\nlanguage={} translation={}".format(src_lang, translation))
            translations.append(translation)

            writePT(lang_index, 
                    result,
                    pt_name,
                    )

            for word in sources[lang_index].split():
                if word in translation.split():
                    handleOOV(word, lang_index)

        if len(set(translations)) == 1: 
            trans_string = ""
            for lang_index, src_lang in enumerate(langs):
                trans_string += "\n\t{}: {}".format(src_lang, translations[lang_index])
            print("\nTranslations converged:{}\nExiting.".format(trans_string))
            exit()



if __name__ == '__main__':
    dualDecomposition()

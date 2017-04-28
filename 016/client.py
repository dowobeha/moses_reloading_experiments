#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from nltk.util import ngrams
import re
import xmlrpc.client
from collections import defaultdict as dd
import argparse


groupSeparator="Moses::ContextScope::GroupSeparator"

recordSeparator="Moses::ContextScope::RecordSeparator"

def defaultLambda():
    return -1


class DualDecomp:

    def __init__(self, l0, l1, l0_static_port, l1_static_port, l0_dynamic_port, l1_dynamic_port, l0_sentfile, l1_sentfile):

        self.reloading_PTs = [None, None,]

        self.reloading_LMs = [None, None,]

        self.langs=[l0, l1,]

    #    self.sources = [u"ich kaufe sie eine katze", u"je vous achète un chat",]
                    
        self.static_ports = [l0_static_port, l1_static_port,]

        self.reloading_ports = [l0_dynamic_port, l1_dynamic_port,]

        self.sources = []
        with open(l0_sentfile) as f0, open(l1_sentfile) as f1:
            self.sources = zip(f0.readlines(), f1.readlines())

    #######################################################

    def clean_translation(self, trans):
        trans = re.sub(r"\|\d+-\d+\| +", r"", trans)
        trans = re.sub(r"UNK\S+", "<unk>", trans)
        trans = "<s> " + trans + " </s>"
        return trans

    #######################################################

    def topts(self, topts, source, featureName):

        result=""
        unknowns=[]

        for topt in topts:
            start=topt["start"]
            end=topt["end"]+1
            source_phrase=" ".join(source[start:end])
            target_phrase=topt["phrase"]
            scores=topt["labelledScores"][featureName][0]
            print("src: {}\t\ttgt: {}\t\t{}".format(source_phrase, target_phrase, scores))
            if target_phrase == "":
                unknowns.append(source_phrase)
                continue
            result += "{} ||| {} ||| {}\n".format(source_phrase, 
                                                target_phrase, 
                                                " ".join([str(score) for score in scores]),
                                                )
           
        return result, unknowns
            
    #######################################################

    def static_moses(self, port, text):
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

    def reloading_moses(self, port, text, contextScope):

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

    def unique_ngrams(self, translations, i, max_n):
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

    def gamma(self, xk, max_n):
        """ extracts all n-grams up to length n """
        multiset = dd(int)
        for n in range(1, max_n+1):
            grams = ngrams(xk.split(), n)
            for gram in grams:
                multiset[gram] += 1
        return multiset

    #######################################################

    def get_updates(self, sources, ngram_order):
        """ gets the updates """
        updates = []
        K = len(sources) # number of languages
        average = dd(float)
        gammas = []

        # average sparse vectors
        for i, xk in enumerate(sources):
            gammas.append(self.gamma(xk, ngram_order))
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
    def handleOOV(self, oov, lang_index):
        for i in range(len(self.langs)):
            if i == lang_index:
                continue
            ltt_name = "static.{}.ltt".format(i)
            with open(ltt_name) as ltt:
                for line in ltt.read().split("\n"):
                    if len(line.split()) > 0 and oov == line.split()[1]:
                        key = line.split()[0]
                        for entry in self.reloading_PTs[i].split("\n"):
                            entry = [s.strip() for s in entry.split("|||")]
                            if entry[0] == key:
                                # TODO: maybe new entry coeffs should be scaled by the prob in the ltt
                                new_entry = "{} ||| {} ||| -90 -90 -90 -90\n".format(oov, entry[1])
                                self.reloading_PTs[lang_index] += new_entry

    #######################################################

    def writePT(self, lang_index, result, prev_pt, src_pair):
        pt_name = "reloading.{}.pt".format(lang_index)
        pt, unknowns = self.topts(result["topt"], 
                       src_pair[lang_index].split(), 
                       prev_pt,
                       )

#        global self.reloading_PTs
        self.reloading_PTs[lang_index] = pt
        for unk in unknowns:
            self.handleOOV(unk, lang_index)

        with open(pt_name, 'w') as pt_file:
            pt_file.write(pt)
        print("\n{} written...".format(pt_name))

    #######################################################

    def writeLM(self, lang_index, Lambdas, max_order):
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
#            global reloading_LM
            self.reloading_LMs[lang_index] = lm_file.read()

        print("\n{} written...".format(lm_name))

    #######################################################i

    def dualDecomposition(self, max_iters=2000, eta=0.1, max_order=3):

        src0translations = []
        src1translations = []

        for src_pair in self.sources:

            if src_pair[0].startswith("<"):
                assert src_pair[0].endswith(">")
                assert src_pair[1].startswith("<")
                assert src_pair[0].endswith(">")
                src0translations.append(src_pair[0])
                src1translations.append(src_pair[1])
                continue

            translations = []

            for lang_index, src_lang in enumerate(self.langs):
                pt_name = "static.{}.pt".format(lang_index)
                with open(pt_name) as ptfile:
                    self.reloading_PTs[lang_index] = ptfile.read()

            for lang_index, src_lang in enumerate(self.langs):

                print("src_pair = {}".format(src_pair))
                print("src_sent = {}".format(src_pair[lang_index]))
                result = self.static_moses(self.static_ports[lang_index], 
                                        src_pair[lang_index],
                                        )

                translation = self.clean_translation(result['text'])
                print("\nlanguage={} translation={}".format(src_lang, translation))
                translations.append(translation)

                pt_name = "static.{}.pt".format(lang_index)
                self.writePT(lang_index, 
                        result,
                        pt_name,
                        src_pair,
                        )

            Lambdas = [dd(defaultLambda)] * len(translations)

            for i in range(max_iters):
                print("\ntranslations={}".format(translations))
                updates = self.get_updates(translations, max_order)
                for lang_index, src_lang in enumerate(self.langs):
                    #TODO: Should update be enumerated, and the update for each language 
                    # is used to update the PT for the other language.  So, updates from the 
                    # translation from de source updates the fr PT and vice versa?
                    for ngram, value in updates[lang_index].items():
                        Lambdas[lang_index][ngram] += eta * value 

                    lm_name = "reloading.{}.lm".format(lang_index)
                    self.writeLM(lang_index,
                            Lambdas, 
                            max_order,
                            )

                translations = []
                for lang_index, src_lang in enumerate(self.langs):

                    pt_name = "reloading.{}.pt".format(lang_index)
                    lm_name = "reloading.{}.lm".format(lang_index)

                    contextScope = pt_name + recordSeparator + self.reloading_PTs[lang_index] \
                                    + groupSeparator \
                                    + lm_name + recordSeparator + self.reloading_LMs[lang_index]

                    result = self.reloading_moses(self.reloading_ports[lang_index], 
                                            src_pair[lang_index], 
                                            contextScope,
                                            )

                    translation = self.clean_translation(result['text'])
                    print("\nlanguage={} translation={}".format(src_lang, translation))
                    translations.append(translation)

                    self.writePT(lang_index, 
                            result,
                            pt_name,
                            src_pair,
                            )

        #            for word in self.sources[lang_index].split():
        #                if word in translation.split():
        #                    handleOOV(word, lang_index)

                if len(set(translations)) == 1: 
                    trans_string = ""
                    for lang_index, src_lang in enumerate(self.langs):
                        trans_string += "\n\t{}: {}".format(src_lang, translations[lang_index])
                    print("\nTranslations converged:{}.".format(trans_string))
                    break

            src0translations.append(re.sub("<s>(.+)</s>", "\g<1>", translations[0]).strip())
            src1translations.append(re.sub("<s>(.+)</s>", "\g<1>", translations[1]).strip())

        with open("translations.{}.txt".format(self.langs[0]),"w") as out0:
            out0.write("\n".join(src0translations)+"\n")

        with open("translations.{}.txt".format(self.langs[1]),"w") as out1:
            out1.write("\n".join(src1translations)+"\n")

        print("\nFound tranlations for all source pairs.  Exiting.")

        print("lang0 = {}  lang1 = {}".format(self.langs[0], self.langs[1]))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--max_iters', dest='iters', default=10000, action='store', help='max # of iters for outputs to converge')
    parser.add_argument('-e', '--eta', dest='rate', default=0.1, action='store', help='learning rate')
    parser.add_argument('-o', '--max_order', dest='order', default=3, action='store', help='max order of n-grams used in LM')
    parser.add_argument('-l0', '--language0', dest='l0', action='store', help='the first source language abbreviation')
    parser.add_argument('-l1', '--language1', dest='l1', action='store', help='the second source language abbreviation')
    parser.add_argument('-i0', '--l0input', dest='l0_sentfile', action='store', help='file with one l0 input sent per line')
    parser.add_argument('-i1', '--l1input', dest='l1_sentfile', action='store', help='file with one l1 input sent per line')
    parser.add_argument('-s0', '--l0static', dest='l0_static_port', action='store', help='static moses port for l0')
    parser.add_argument('-s1', '--l1static', dest='l1_static_port', action='store', help='static moses port for l1')
    parser.add_argument('-d0', '--l0dynamic', dest='l0_dynamic_port', action='store', help='dynamic moses port for l0')
    parser.add_argument('-d1', '--l1dynamic', dest='l1_dynamic_port', action='store', help='dynamic moses port for l1')
    args = parser.parse_args()

    dualdecomp = DualDecomp(args.l0, args.l1, args.l0_static_port, args.l1_static_port, args.l0_dynamic_port, args.l1_dynamic_port, args.l0_sentfile, args.l1_sentfile)
    dualdecomp.dualDecomposition(max_iters=args.iters, eta=args.rate, max_order=args.order)





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

url = "http://localhost:8090/RPC2"
proxy = xmlrpc.client.ServerProxy(url)

texts=["je vous achète un chat"]

positive={
          texts[0]:"chat     ||| kitty ||| 2 2 2 2\nje vous achète ||| I would like to buy you ||| 1 1 1 1\n",
         }

negative={
          texts[0]:"un ||| a ||| 1000000000000000000 1000 1000 1000\n",
         }

def pt_weights(positive_weight, negative_weight, static_weight):
    return "PhraseDictionaryGroup0= {0} {0} {0} {0} {1} {1} {1} {1} {2} {2} {2} {2}".format(positive_weight, negative_weight, static_weight)

for text in texts:

    contextScope = "TranslationModel0" + recordSeparator + positive[text] + groupSeparator +\
                   "TranslationModel1" + recordSeparator + negative[text]

    positive_weight=1
    negative_weight=-1
    static_weight=0.0001

    for _ in range(1,10):

        positive_weight *= 10
        negative_weight *= 10

        weights="PhraseDictionaryGroup0="+pt_weights(positive_weight,negative_weight, static_weight)
        print(weights)
        params = {
              "text":text,
              "context-scope":contextScope,
              "weights":weights,
             }

        result = proxy.translate(params)

        print(re.sub(r"UNK\S+", "<unk>", result['text']))

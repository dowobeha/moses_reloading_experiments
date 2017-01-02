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
          texts[0]:"chat     ||| kitty-szat ||| 1 1 1 1\nje vous achète ||| I would like to buy you ||| 1 1 1 1\n",
         }

negative={
          texts[0]:"un ||| a ||| 1000000000000000000 1000 1000 1000\n",
         }

for text in texts:

    contextScope = "TranslationModel0" + recordSeparator + positive[text] + groupSeparator +\
                   "TranslationModel1" + recordSeparator + negative[text]


    params = {
              "text":text,
              "context-scope":contextScope,
             }

    result = proxy.translate(params)

    print(re.sub(r"UNK\S+", "<unk>", result['text']))

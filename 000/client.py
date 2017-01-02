#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import re
import xmlrpc.client
import datetime


#######################################################

url = "http://localhost:8090/RPC2"
proxy = xmlrpc.client.ServerProxy(url)

texts=["je vous achète un chat"]


for text in texts:


    params = {
              "text":text,
             }

    result = proxy.translate(params)

    print(re.sub(r"UNK\S+", "<unk>", result['text']))

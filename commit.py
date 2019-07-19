#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch(http_compress=True)

def doc_generator(index, data):
    for id, document in data.iterrows():
        yield {
            "_index": index,
            "_type": "_doc",
            "_id" : f"{id}",
            "_source": document.to_dict(),
        }

for name in ['cnncmall', 'deli', 'staples', 'jd-deli']:
    data = pd.read_csv(name + '.csv')
    data.replace(np.nan, '', inplace=True)
    helpers.bulk(es, doc_generator(name, data))

import pandas as pd
import numpy as np
import re
from elasticsearch import Elasticsearch

es = Elasticsearch()

data = pd.read_csv('cnncmall.csv')
data = data[['product name', 'price str']]
data.columns = ['cnncmall name', 'cnncmall price']

result = {
    'deli id': [],
    'deli name': [],
    'deli price': [],
    'staples id': [],
    'staples name': [],
    'staples price': [],
    'jd-deli id': [],
    'jd-deli name': [],
    'jd-deli price': []
}

for query in data['cnncmall name']:
    ret = es.search(index='deli', body={'query': {'match': {'title': query}}})
    ret = ret['hits']['hits']
    if len(ret):
        result['deli id'].append(ret[0]['_id'])
        result['deli name'].append(ret[0]['_source']['title'].strip())
        result['deli price'].append(float(ret[0]['_source']['price'].replace(',', '')))
    else:
        result['deli id'].append(np.nan)
        result['deli name'].append('')
        result['deli price'].append(np.nan)
    ret = es.search(index='staples', body={'query': {'match': {'title': query}}})
    ret = ret['hits']['hits']
    if len(ret):
        result['staples id'].append(ret[0]['_id'])
        result['staples name'].append(ret[0]['_source']['title'])
        price = re.search(r'[0-9.,]+', ret[0]['_source']['price']).group(0)
        result['staples price'].append(float(price.replace(',', '')))
    else:
        result['staples id'].append(np.nan)
        result['staples name'].append('')
        result['staples price'].append(np.nan)
    ret = es.search(index='jd-deli', body={'query': {'match': {'title': query}}})
    ret = ret['hits']['hits']
    if len(ret):
        result['jd-deli id'].append(ret[0]['_id'])
        result['jd-deli name'].append(ret[0]['_source']['title'].strip())
        result['jd-deli price'].append(ret[0]['_source']['price'])
    else:
        result['jd-deli id'].append(np.nan)
        result['jd-deli name'].append('')
        result['jd-deli price'].append(np.nan)

pd.concat([data, pd.DataFrame(result)], axis=1).to_csv('result.csv')

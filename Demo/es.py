from elasticsearch import Elasticsearch
from datetime import datetime
from pypinyin import lazy_pinyin
from elasticsearch.helpers import reindex

#连接ES数据库
myES = Elasticsearch("http://127.0.0.1:9200")
#myES.indices.create(index="pinyin",ignore=400)#创建索引
def build_document():
    documents=[]
    path=r'C:\Users\admin\Desktop\语音交互\WorkChat\entity_dict.txt'
    with open(path,'r',encoding='utf-8') as f:
        for line in f.readlines():
            line=line.strip()
            line=line.split('\t')
            entity,last_part=line
            tag,value=last_part.split('+++')
            doc={
                'word':entity,
                'tag':tag,
                'value':value,
                'pinyin':''.join(lazy_pinyin(entity)),
            }
            documents.append(doc)
    return documents
def gen_docs(documents):
    count=0
    for doc in documents:
        count+=1
        print(count)
        yield {
            '_index':'pinyin_tag',
            '_source':{
            '_tag':doc['tag'],
            '_word':doc['word'],
            '_value':doc['value'],
            '_pinyin':doc['pinyin'],
            'timestamp':datetime.now()
            }
        }
from elasticsearch.helpers import bulk

# 更新索引映射
def creat_index():
    mapping = {
        "properties": {
            "pinyin": {
                "type": "text",
                "analyzer": "standard",
                "similarity": "BM25"
            }
        }
    }

    es=myES.indices.create(index='pinyin_tag',body={'mappings':mapping})
    success,_=bulk(myES,gen_docs(build_document()))

def insert():
    index_name='pinyin_tag'
    data={
        "_tag": "ChemEntity",
        "_word": "氧原子",
        "_value": "氧原子",
        "_pinyin": "yangyuanzi",
        "timestamp": datetime.now()
    }
    res = myES.index(
        index=index_name,
        id=None,  # 如果不指定ID，Elasticsearch会自动生成
        document=data
    )

    # 输出结果
    print(res)
insert()
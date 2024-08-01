from pycorrector import Corrector
from pycorrector import MacBertCorrector
from Config import Config
from concurrent.futures import ThreadPoolExecutor
import Levenshtein
from Text_process import TextProcessor
from pypinyin import lazy_pinyin
from elasticsearch import Elasticsearch
class Corrector_chem():
    '''
    目前速度依然较慢，两个优化点：
    1.分词、词性标注部分
    2.添加常用词典，减少候选词
    '''
    def __init__(self):
        self.config=Config()
        self.text_process=TextProcessor()
        self.load_confusion()
        self.max_workers=20#线程数
        self.threshold=0.9#控制拼音相似度阈值
        self.myES = Elasticsearch("http://127.0.0.1:9200")
    def load_confusion(self):
        candidates = []
        with open(self.config.entity_dict, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split('\t')[0]
                candidates.append(line)
        self.entity_dict=candidates
    def error_correct_pinyin(self,text):
        if len(text)<=3:
            # 粗排召回
            recall_candidates = self.edit_distance_recall(''.join(lazy_pinyin(text)))
            # 精排排序
            pinyin_sim = self.pinyin_sorted(recall_list=recall_candidates, query_words=text)
            if pinyin_sim[0] >= self.threshold:
                text = pinyin_sim[1]
            return text
        else:
            word_cut=self.text_process.cut_words(text)
            for i in range(len(word_cut.cws[0])):
                #只对名词纠错。一般来说出错的是专业名词.
                if word_cut.pos[0][i]!='n' and word_cut.pos[0][i]!='r':
                    continue
                #粗排召回
                recall_candidates=self.edit_distance_recall(''.join(lazy_pinyin(word_cut.cws[0][i])))
                if len(recall_candidates)==0:
                    continue
                #精排排序
                pinyin_sim=self.pinyin_sorted(recall_list=recall_candidates,query_words=word_cut.cws[0][i])
                if pinyin_sim[0]>=self.threshold:
                    word_cut.cws[0][i]=pinyin_sim[1]
            return ''.join(word_cut.cws[0])
    def pinyin_sorted(self,recall_list,query_words):
        try:
            user_pinyin = ''.join(lazy_pinyin(query_words))
        except Exception as e:
            print(f"Error converting to pinyin: {e}")
            return None
        #根据拼音计算相似度
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            similarity_results=list(executor.map(lambda x: self.compute_cqr_ctr(user_pinyin,x),recall_list))
        top_results=max(similarity_results,key=lambda x:x[0])

        #[score,word]
        return top_results
    #计算cqr和ctr
    def compute_cqr_ctr(self,user_query_pinyin:str,candidate:str):
        '''
        计算cqr和ctr。后续可以加入term权重。
        :param user_query_pinyin:
        :param candidate:
        :return:
        '''
        candidate_pinyin=''.join(lazy_pinyin(candidate))
        max_length = max(len(user_query_pinyin), len(candidate_pinyin))
        cqr=self.predict_left(user_query_pinyin,candidate_pinyin)
        ctr=self.predict_left(candidate_pinyin,user_query_pinyin)
        edit_distance=Levenshtein.distance(user_query_pinyin,candidate_pinyin)
        edit_similarity=(max_length - edit_distance) / max_length

        return [cqr*ctr*0.8+edit_similarity*0.2,candidate]
    def predict_left(self,q1,q2):
        if len(q1)<1 or len(q2)<1:
            return 0
        q1=set(q1)
        q2=set(q2)
        numerator=len(q1.intersection(q2))
        denominator=len(q1.union(q2))
        return numerator/denominator
    #编辑距离召回
    def edit_distance_recall(self,pinyin,max_candidates=50):
        candidates=[]
        assert  type(pinyin)==str,'查询输入形式错误,要求为string类型'
        response = self.myES.search(
            index="pinyin_tag",
            body={
                "query": {
                    "fuzzy": {
                        "_pinyin": {
                            "value":pinyin,
                            "fuzziness": "AUTO",
                            "prefix_length": 0,
                            "max_expansions": 50
                        }
                    }
                },
                "size": 100  # 返回最多100个结果
            }
        )
        match_item=response['hits']['hits']
        for i in range(len(match_item)):
            candidates.append(match_item[i]['_source']['_value'])
        return candidates

if __name__ == '__main__':
    corrector=Corrector_chem()
    text=['画个加基本吧']
    for elem in text:
        t=corrector.error_correct_pinyin(elem)
        print(t)
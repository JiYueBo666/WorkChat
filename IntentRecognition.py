import  json
import os
import re
import jieba.posseg as psg

class IntentRecognition:
    '''
    意图识别模块，目前主要依赖于对词典、以及句子分析的识别
    '''
    def __init__(self,intent_dict="./entity_dict.txt"):
        self.entity_dict_path=intent_dict
        #用户意图
        self.intent_candidate=['draw','ask','others']
        self.slot_dict={}#实体词典
        self.load_dict()

    def load_dict(self):
        '''
        加载实体词典.
        示例：
        五哈	VarietyShow+++哈哈哈哈哈
        哈哈哈哈哈	VarietyShow+++哈哈哈哈哈
        加载结果：
        {
         '五哈': [{
          'slot_name': 'VarietyShow',
          'slot_value': '哈哈哈哈哈'
         }],
         '哈哈哈哈哈': [{
          'slot_name': 'VarietyShow',
          'slot_value': '哈哈哈哈哈'
         }],
         '故宫': [{
          'slot_name': 'Attraction',
          'slot_value': '故宫博物院'
         }],
        }
        :return:
        '''
        if not self.entity_dict_path:
            raise ValueError("实体词典路径为空")
        if not os.path.exists(self.entity_dict_path):
            raise ValueError("实体词典路径错误")

        slot_dict = {}
        with open(self.entity_dict_path, encoding="utf8") as f:
            for line in f:
                ll = line.strip().split("\t")
                if len(ll) != 2:
                    continue
                slot_info = ll[1].split('+++')
                if len(slot_info) != 2:
                    continue
                if ll[0] in slot_dict:
                    slot_dict[ll[0]].append({"slot_name": slot_info[0], "slot_value": slot_info[1]})
                else:
                    slot_dict[ll[0]] = [{"slot_name": slot_info[0], "slot_value": slot_info[1]}]
        self.slot_dict = slot_dict

    def entity_extract(self, query):
        '''
        最大后向匹配算法，提取文本实体。
        :param query:
        :return:
        '''
        query_len = len(query)
        idx = 0
        idy = query_len
        slot_get = []
        tmp_slot_get_len = 0
        while idy > 0:
            while idx < idy:
                if query[idx:idy] in self.slot_dict:
                    for item in self.slot_dict[query[idx:idy]]:
                        slot_get.append({"slot_word": query[idx:idy],
                                         "slot_name": item["slot_name"],
                                         "slot_value": item["slot_value"],
                                         "slot_start": idx,
                                         "slot_end": idy
                                         })
                    break
                idx = idx + 1
            if len(slot_get) != tmp_slot_get_len:
                idy = idx
                idx = 0
                tmp_slot_get_len = len(slot_get)
            else:
                idx = 0
                idy = idy - 1
        return slot_get

    def intent_predict(self,query):
        '''
        用户意图的判断部分
        :param query:
        :return:
        '''

        #规则：如果有名词，有动词，且名词在动词之前，可能是命令式的query。
        #绘制类：化学实体+动词。例如：绘制苯环
        intent=None
        found_noun=False
        noun_list=[]
        found_verb=False
        verb_list=[]

        entity_extract=self.entity_extract(query)

        intent_slot=[]
        #分词，进行词性标注
        words = psg.cut(query)
        for word_pair in words:
            if word_pair.flag=="v":#名词
                found_verb=True
                verb_list.append(word_pair.word)
            if word_pair.flag=="n":#动词
                if found_verb==True:
                    for entity in entity_extract:
                        if entity["slot_name"]=="ChemEntity":#绘制类
                            #绘制意图
                            intent_slot.append(entity["slot_value"])
                            intent=self.intent_candidate[0]
                            return intent



if __name__ == '__main__':
    intentRecognizer=IntentRecognition()
    print(intentRecognizer.slot_dict)
    query="我们来画一个苯环"
    res=intentRecognizer.intent_predict(query)
    print(res)
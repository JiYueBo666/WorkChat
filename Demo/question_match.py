import re
import json
import pandas
import itertools
from collections import defaultdict

class Demo:
    def __init__(self):
        self.templets_path=r"./drawTemplate.xlsx"
        self.schem_path=r"./schem.json"
        self.load()

    def load(self):
        self.load_order_templet(self.templets_path)
        self.load_schem(self.schem_path)
        return
    def load_order_templet(self, templet_path):
        dataframe = pandas.read_excel(templet_path)
        self.order_templet = []
        for index in range(len(dataframe)):
            question = dataframe["order"][index]
            cypher_check = dataframe["check"][index]
            cypher=dataframe["cypher"][index]
            self.order_templet.append([question,json.loads(cypher_check),cypher])
        return
    def load_schem(self,path):
        with open(path, encoding="utf8") as f:
            schema = json.load(f)
        self.entity_set = set(schema["ENT"])
        self.actions_set = set(schema["ACT"])
        self.number_set = set(schema["NUM"])
        self.position_set = set(schema["POS"])
        return
    def get_mention_entitys(self, sentence):
        return re.findall("|".join(self.entity_set), sentence)
    # 获取问题中谈到的动作
    def get_mention_actions(self, sentence):
        return re.findall("|".join(self.actions_set), sentence)
    # 获取问题中谈到的数量
    def get_mention_numbers(self, sentence):
        return re.findall("|".join(self.number_set), sentence)
   #获取问题中提到的位置信息
    def get_mention_positions(self, sentence):
        return re.findall("|".join(self.position_set), sentence)
    def check_info_valid(self,info,check):
        for key,required_count in check.items():
            if len(info.get(key,[]))<required_count:
                return False
        return True
    def get_combinations(self,check,info):
        slot_values=[]
        for key,required_count in check.items():
            slot_values.append(itertools.combinations(info.get(key),required_count))
        value_combinations=itertools.product(*slot_values)
        combinations=[]
        for value_combination in value_combinations:
            combinations.append(self.decode_value_combination(value_combination,check))
        return combinations
    #将提取到的值分配到键上
    def decode_value_combination(self,value_combination,check):
        res={}
        for index,(key,required_count) in enumerate(check.items()):
            if required_count==1:
                res[key]=value_combination[index][0]
            else:
                for i in range(required_count):
                    key_num=key[:-1]+str(i)+"%"
                    res[key_num]=value_combination[index][i]
        return res

    def replace_token(self,template:str,combination_dict):
        for key,value in combination_dict.items():

            template=template.replace(key,value)

        return template
    def expand_templet(self,order,check,cypher,info):
        #对单条模板，根据抽取到的属性进行扩展，形成列表
        combinations=self.get_combinations(check,info)
        templet_cpyher=[]
        for combination in combinations:
            replaced_templet = self.replace_token(order,combination)
            replaced_cypher = self.replace_token(cypher,combination)
            templet_cpyher.append([replaced_templet,check,replaced_cypher])
        return templet_cpyher

    def expand_question_and_cypher(self,info):
        templet_cypher_pair=[]
        for order,check,cypher in self.order_templet:
            if self.check_info_valid(info,check):
                templet_cypher_pair+=self.expand_templet(order,check,cypher,info)
        return templet_cypher_pair

    def sentence_similarity_function(self,string1,string2):
        jaccard_distance = len(set(string1) & set(string2)) / len(set(string1) | set(string2))
        return jaccard_distance
    def cypher_match(self,sentence,info):
        #扩展问题
        templet_cypher_pair=self.expand_question_and_cypher(info)
        result=[]
        for templet,check,cypher in templet_cypher_pair:
            score=self.sentence_similarity_function(sentence,templet)
            result.append([templet,check,score,cypher])
        result=sorted(result,reverse=True,key=lambda x:x[2])
        print(result[0])
        return result
    #对问题进行预处理，提取需要的信息
    def parse_sentence(self, sentence):
        entitys = self.get_mention_entitys(sentence)
        actions = self.get_mention_actions(sentence)
        numbers = self.get_mention_numbers(sentence)
        positions = self.get_mention_positions(sentence)
        return {"%ENT%":entitys,
                "%ACT%":actions,
                "%NUM%":numbers,
                "%POS%":positions}
    def parse_result(self,result,info):
        parse_result=self.replace_token_in_string(result)
    def replace_token_in_string(self,string):
        pass
    def query(self,sentence):
        info=self.parse_sentence(sentence)
        template_score=self.cypher_match(sentence, info)  #cypher匹配
        return template_score

if __name__ == '__main__':
    demo=Demo()
    result=demo.query("把苯环上的氢原子删了")
    # print(result)

from collections import defaultdict
import json
from Config import Config
import re
import pandas
import torch
import itertools
class DialogueManager:
    def __init__(self, intent_list):
        self.config=Config()
        self.schem_path=self.config.schema_path
        self.__load_schem(self.schem_path)
        self.__load_order_templet(self.config.templets_path)
    def __load_order_templet(self,path):
        dataframe = pandas.read_excel(path)
        self.order_templet = []
        for index in range(len(dataframe)):
            question = dataframe["order"][index]
            cypher_check = dataframe["check"][index]
            cypher=dataframe["cypher"][index]
            self.order_templet.append([question,json.loads(cypher_check),cypher])
        return
    def __load_entities(self,path):
        self.entity_set=set()
        with open(path, encoding="utf8") as f:
            for line in f:
                line=line.strip().split()
                self.entity_set.add(line[0])
    def __load_schem(self,path):
        with open(path, encoding="utf8") as f:
            schema = json.load(f)
        #加载化学实体
        self.__load_entities(path=self.config.entity_dict)
        self.actions_set = set(schema["ACT"])
        self.number_set = set(schema["NUM"])
        self.position_set = set(schema["POS"])
    def receive_state(self,sentence,intent=None,model=None,tokenizer=None):
        '''
        :param sentence:当前用户输入
        :param intent: 意图
        :return:
        '''
        #进行信息抽取
        info=self.__parse_extract(sentence,intent)
        #绘图意图的管理
        if intent=='绘图':
            templet_cypher_score = self.__cypher_match(sentence, info)# cypher匹配
            score=templet_cypher_score[0][2]
            if score>=0.8:
                return {"code":200,"response":self.__transfer_to_json(templet_cypher_score[0][3])}
            else:
                return {"code":-1,"response":"没能理解您的意图"}
        elif intent=="提问":
            if model is not None:
                templet_cypher_score = self.__cypher_match(sentence, info)# cypher匹配
                question=templet_cypher_score[0][0]
                return self.__answer_question(question,model,tokenizer)
    def __answer_question(self,question,model,tokenizer):
        #进行信息抽取
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        prompt = self.config.questionHelperPrompt
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt + question}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(device)
        generated_ids = model.generate(
            model_inputs.input_ids,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        print(response)
    def __cypher_match(self,sentence,info):
        #扩展问题
        templet_cypher_pair=self.__expand_question_and_cypher(info)
        result=[]
        for templet,check,cypher in templet_cypher_pair:
            score=self.__sentence_similarity_function(sentence,templet)
            result.append([templet,check,score,cypher])
        result=sorted(result,reverse=True,key=lambda x:x[2])
        return result
    def __check_info_valid(self,info,check):
        for key,required_count in check.items():
            if len(info.get(key,[]))<required_count:
                return False
        return True
    def __get_combinations(self,check,info):
        slot_values=[]
        for key,required_count in check.items():
            slot_values.append(itertools.combinations(info.get(key),required_count))
        value_combinations=itertools.product(*slot_values)
        combinations=[]
        for value_combination in value_combinations:
            combinations.append(self.__decode_value_combination(value_combination,check))
        return combinations
    #将提取到的值分配到键上
    def __decode_value_combination(self,value_combination,check):
        res={}
        for index,(key,required_count) in enumerate(check.items()):
            if required_count==1:
                res[key]=value_combination[index][0]
            else:
                for i in range(required_count):
                    key_num=key[:-1]+str(i)+"%"
                    res[key_num]=value_combination[index][i]
        return res



if __name__ == '__main__':
    dialogue_manager=DialogueManager(['提问'])
    dialogue_manager.receive_state("甲基苯是什么","提问")

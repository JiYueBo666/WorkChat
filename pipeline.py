import re
import copy
from dialogue_manager import DialogueManager
from IntentRecognition import IntentRecognition
from Corrector import Corrector_chem
from Text_process import TextProcessor
import unicorn,uvicorn
from fastapi import FastAPI
from transformers import AutoModelForCausalLM, AutoTokenizer
from pydantic import BaseModel
import  datetime
import logging
from utils import  *
from Config import Config
class QueryUnderstander():
    '''
    query理解模块。负责对语音识别结果的处理。
    1:预处理包括大小写转换，繁体简体转换，全半角转换。
    2.query纠错
    3.去除停用词、无关词。使用词典实现。
    4.分词，词性标注
    5. 意图 实体召回
    6.槽位填充
    7.送入Unity，执行相应功能
    '''
    def __init__(self,llm_path=None):
        self.model,self.llm_tokenizer=None,None
        if llm_path is not None:
            self.model=AutoModelForCausalLM.from_pretrained(
                llm_path,
                torch_dtype="auto",
                device_map="auto"
            )
            self.llm_tokenizer=AutoTokenizer.from_pretrained(llm_path)
        self.config = Config()
        self.corrector=Corrector_chem()#纠错模块
        self.text_processor=TextProcessor()
        self.intent_recognizer=IntentRecognition(self.model,self.llm_tokenizer)#意图识别模块
        self.entity_extractor=entity_extractor()
        self.sensitive_words=[]
        self.load_sensitive_words()
        self.dialogue_manager=DialogueManager(intent_list=self.config.intent_list)

    def query_process(self,text):
        #错误修改
        text_corrector_result=self.corrector.error_correct(text)
        text=text_corrector_result[0]['target']
        #去除停用词
        text=self.text_processor.remove_stopwords(text)
        text=self.text_processor.clean_text(text)
        return text
    def load_sensitive_words(self):
        #拒识模块，过滤政治反动色情等敏感词
        with open(self.config.sensitive_path,'r',encoding='utf-8') as f:
            for line in f:
                # 去除每行末尾的换行符（\n）
                self.sensitive_words.append(line.strip())
        return False
    def reject(self,text):
        pattern='|'.join(re.escape(words) for words in self.sensitive_words)
        match=re.search(pattern,text)
        if match is not None:
            return True
        return False
    def intent_recognize(self,text):
        #产生意图判断
        intent = self.intent_recognizer.intent_predict(text)
        return intent
    def name_entity_recognizer(self,text):
        entity_list= self.entity_extractor.entity_extract(text)
        return entity_list
    def slot_filling(self,text:str,intent:str):
        text=self.corrector.error_correct_pinyin(text)
        logger.info("纠错后的文本:{}".format(text))
        slot_template=None
        if self.DST is not None:
                slot_template=self.DST
        else:
            slot_template=copy.deepcopy(self.config.intent_slot[intent])
        logger.info("初始化slot_template:{}".format(slot_template))
        #实体抽取
        entities_dict=self.name_entity_recognizer(text)
        if intent=="绘图":
            for slot in entities_dict:
                if slot['slot_name']=='ChemEntity':
                    slot_template['实体']['slot']=slot['slot_value']
                elif slot['slot_name']=='verb':
                    slot_template['动作']['slot']=slot['slot_value']
        elif intent=="提问":
            for slot in entities_dict:
                if slot['slot_name']=='ChemEntity':
                    slot_template['实体']['slot']=slot['slot_value']
                if slot['slot_name']=="pron":
                    slot_template['询问词']['slot']=slot['slot_value']
        #状态记录
        self.DST=slot_template
        logger.info("状态追踪:{}".format(self.DST))
        #槽位检查
        check_result= self.slot_check(slot_template,intent)
        if check_result['response']==slot_template:
            slot_template=None
            self.DST=None
        return check_result
    def slot_check(self,slot_template,intent):
        print(slot_template)
        if intent=="绘图":
            if slot_template['动作']['slot']==None:
                response=slot_template['动作']['追问话术']
                return {"msg":-1,'response':response}
            elif slot_template['实体']['slot']==None:
                response = slot_template['实体']['追问话术']
                return {"msg":-1,'response':response}
        return {"msg":200,"response":slot_template}
    def pipline(self,text):
        #敏感词拦截
        if self.reject(text):
            return {"code":-1,"response":"对不起，我无法回答这个问题"}
        #文本纠错
        text=self.corrector.error_correct_pinyin(text)
        logger.info("纠错后的文本:{}".format(text))
        intent_recognize_result=self.intent_recognize(text)
        intent = intent_recognize_result['intent']
        logger.info("意图识别结果:{}".format(intent_recognize_result['intent']))
        if intent_recognize_result['code']==200 and intent in self.config.intent_list:
            analyse_json=self.dialogue_manager.receive_state(text,intent,self.model,self.llm_tokenizer)
            return analyse_json
        else:
            return {"code":-1,"response":"对不起，我不能明白您的意思"}

app=FastAPI()
qu=QueryUnderstander(r"C:\Users\admin\Desktop\project\text-generation-webui\models\Qwen1.5-14B-Chat-GPTQ-Int8")
class Query(BaseModel):
    text:str
    intent:str
@app.post("/pipline/")
async def pipeline(query:Query):
    result=qu.pipline(query.text)
    return result

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    uvicorn.run(app,host="127.0.0.1",port=8000)

from IntentRecognition import IntentRecognition
from Corrector import Corrector_chem
from Text_process import TextProcessor
import unicorn,uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import  datetime
from utils import  *
def get_asr_sentence(text:str):
    '''
    获取ASR识别结果。
    '''
    return text

class QueryUnderstander():
    '''
    query理解模块。负责对语音识别结果的处理。
    query理解步骤。

    1:预处理包括大小写转换，繁体简体转换，全半角转换。
    2.query纠错
    3.去除停用词、无关词。使用词典实现。
    4.分词，词性标注
    5. 意图 实体召回
    6.query改写
    7.送入Unity，执行相应功能
    '''
    def __init__(self):
        self.corrector=Corrector_chem()#纠错模块
        self.text_processor=TextProcessor()
        self.intent_recognizer=IntentRecognition(r"C:\Users\admin\Desktop\project\text-generation-webui\models\Qwen1.5-7B-Chat")
        self.entity_extractor=entity_extractor()

    def query_process(self,text):
        #错误修改
        text_corrector_result=self.corrector.error_correct(text)
        text=text_corrector_result[0]['target']
        #去除停用词
        text=self.text_processor.remove_stopwords(text)
        text=self.text_processor.clean_text(text)
        return text
    def intent_recognize(self,text):
        #产生意图判断
        intent = self.intent_recognizer.intent_predict(text)
        return intent
    def name_entity_recognizer(self,text):
        entity_list= self.entity_extractor.entity_extract(text)
        print(entity_list)
        return entity_list

app=FastAPI()
qu=QueryUnderstander()
class Query(BaseModel):
    text:str

@app.post("/IntentRecognize/")
async def IntentRecognize(query:Query):
    result=qu.intent_recognize(query.text)
    return result
@app.post("/NER/")
async def enetity_extract(query:Query):
    result=qu.name_entity_recognizer(query.text)
    return result
if __name__ == '__main__':
   uvicorn.run(app,host="127.0.0.1",port=8000)

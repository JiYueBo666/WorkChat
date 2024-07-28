from IntentRecognition import IntentRecognition
from Corrector import Corrector_chem
from Text_process import TextProcessor
def get_asr_sentence(text:str):
    '''
    获取ASR识别结果。
    '''
    return text

class QueryUnstander():
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
        self.corrector=Corrector_chem()
        self.text_processor=TextProcessor()
        self.intent_recognizer=IntentRecognition()
    def get_user_content(self,text):
        #错误修改
        text_corrector_result=self.corrector.error_correct(text)
        text=text_corrector_result[0]['target']
        #去除停用词
        text=self.text_processor.remove_stopwords(text)
        text=self.text_processor.clean_text(text)
        return text
    def get_intent(self,text):
        #产生意图以及实体候选单元召回
        res = self.intent_recognizer.intent_predict(text)
        print(res)
       # intent,verb,noun,refers,member,direction
        #query改写


if __name__ == '__main__':
    chatBot=QueryUnstander()
    user_content=get_asr_sentence("好，那你帮我找一下是什么苯环")
    text=chatBot.get_user_content(text=user_content)
    chatBot.get_user_content(user_content)
    chatBot.get_intent(text)

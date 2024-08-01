import re
from Config import Config
import torch
class IntentRecognition:
    '''
    意图识别模块，目前主要依赖于对词典、以及句子分析的识别
    '''
    def __init__(self,model=None,tokenizer=None):
        self.config=Config()
        if model is not None and tokenizer is not None:
            self.model=model
            self.llm_tokenizer=tokenizer
        elif (model==None and tokenizer is not None) or (model is not None and tokenizer==None):
            print("模型和分词器需要同时存在")
        #规则
        self.actions_draw=self.config.actions_draw
        self.actions_asking=self.config.actions_asking
    def intent_predict(self,query):
        '''
        意图识别
        主要基于规则+大模型，后续可以将大模型换成bert。
        :param query:
        :return:
        '''
        pattern_draw='|'.join(re.escape(action) for action in self.actions_draw)
        pattern_asking='|'.join(re.escape(action) for action in self.actions_asking)
        match_draw=re.search(pattern_draw,query)
        match_asking=re.search(pattern_asking,query)
        if match_draw is not None:
            return {"code":200,"intent":"绘图"}
        elif match_asking is not None:
            return {"code":200,"intent":"提问"}
        else:
            if self.model is not None:
                print("使用大模型进行意图识别")
                return self.model_predict(query)
            else:
                return {"code":-1,"intent":"未能识别意图"}
    def model_predict(self,query):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        prompt = self.config.intentHelperPrompt
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt + query}
        ]
        text = self.llm_tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.llm_tokenizer([text], return_tensors="pt").to(device)
        generated_ids = self.model.generate(
            model_inputs.input_ids,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.llm_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        intent = response.split(' ')[0]
        return {"code": 200, "intent": intent}



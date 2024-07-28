from pycorrector import Corrector
from Config import Config
class Corrector_chem():
    def __init__(self):
        self.config=Config()
        self.corrector=Corrector(custom_confusion_path_or_dict=self.config.confusion_path)
    def error_detect(self,text):
        errors=self.corrector.detect(text)
        return errors
    def error_correct(self,text):
        return self.corrector.correct_batch([text])
    def error_correct_batch(self,batch_text):
        return self.corrector.correct_batch([batch_text])
    def detect_and_reverse_match(self,entity_dict):
        '''
        错误召回，然后利用实体词典做反向最大匹配纠错。
        :param entity_dict:
        :return:
        '''
        return

if __name__ == '__main__':
    corrector=Corrector_chem()
    result=corrector.error_correct("我们来画一个本环")
    print(result)
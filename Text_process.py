import jionlp as jio
class TextProcessor:
    def __init__(self):
        self.text_helper=jio
        pass
    def remove_stopwords(self,text):
        """
        从文本中移除停用词。
        Args:
            text (str): 待处理的文本字符串。
        Returns:
            str: 移除停用词后的文本字符串。
        """
        return ''.join(self.text_helper.remove_stopwords(text,save_negative_words=['什么']))
    def cha2sim(self,text):
        """
        将繁体中文文本转换为简体中文文本。
        Args:
            text (str): 待转换的繁体中文文本。
        Returns:
            str: 转换后的简体中文文本。
        """
        return  self.text_helper.tra2sim(text)
    def clean_text(self,text):
        '''
        去除 html 标签、去除异常字符、去除冗余字符、去除括号补充内容、去除 URL、去除 E-mail、去除电话号码，将全角字母数字空格替换为半角，
        :param text:
        :return:
        '''
        return self.text_helper.clean_text(text)


if __name__ == '__main__':
    pre_process=TextProcessor()
    text_analyzer=Words_Analyser()
    text='<p><br></p>       <p><span>在17日举行的十三届全国人大一次会议记者会上，环境保护部部长李干杰就“打好污染防治攻坚战”相关问题回答记者提问。李干杰表示'
    text=pre_process.clean_text(text)
    print(text)
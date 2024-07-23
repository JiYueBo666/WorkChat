import jionlp as jio
from Cut_words import Words_Analyser
class Text_process:
    def __init__(self):
        pass

    def remove_stopwords(self,text):
        """
        从文本中移除停用词。

        Args:
            text (str): 待处理的文本字符串。

        Returns:
            str: 移除停用词后的文本字符串。

        """
        return ''.join(jio.remove_stopwords(text))


    def get_char_radical(self,text:str):
        '''
        解析文本偏旁与字形结构特征
        dict:{
        'radical':偏旁,
        'structure':字形结构
        'corner_coding':四角编码
        'stroke_order':笔画顺序
        'wubi_coding':五笔编码
        :param text:
        :return: List[dict]
        '''
        return jio.char_radical(text)

if __name__ == '__main__':
    pre_process=Text_process()
    text_analyzer=Words_Analyser()
    text='额，好，接下来我们画一个苯环'
    text=pre_process.get_char_radical(text)

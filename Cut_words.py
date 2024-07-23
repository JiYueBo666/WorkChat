import jieba
import jieba.posseg as pseg

class Words_Analyser:
    def __init__(self, dict_path=None):
        self.dict_path = dict_path  # 自定义分词词典路径
        self.initial()  # 初始化方法调用

    def initial(self):
        if self.dict_path is not None:
            jieba.load_userdict(self.dict_path)  # 加载用户自定义词典

    def add_word(self, word, freq=None):
        """
        向jieba分词词典中添加一个词及其词频。

        Args:
            word (str): 要添加的词。
            freq (int, optional): 词的词频。默认为None，表示使用默认词频。

        Returns:
            None: 该函数没有返回值，直接修改jieba分词词典。
        """
        jieba.add_word(word, freq)

    def cut_words(self, text, mode=False):
        """
        对输入文本进行精确或全模式分词。

        Args:
            text (str): 需要进行分词的文本。
            mode (bool, optional): 是否使用全模式分词。默认为False，即精确模式。

        Returns:
            list: 分词后的结果列表。
        """
        if mode:
            words = jieba.cut(text, cut_all=mode)
        else:
            words = jieba.cut(text)
        return list(words)  # 返回分词结果列表

    def cut_for_search(self, text):
        """
        对输入文本进行搜索模式下的分词。

        Args:
            text (str): 需要进行分词的文本。

        Returns:
            list: 搜索模式下分词的结果列表。
        """
        words = jieba.cut_for_search(text)
        return list(words)

    def words_tagging(self, text):
        """
        对输入的文本进行词性标注。

        Args:
            text (str): 待词性标注的文本字符串。

        Returns:
            list: 由二元组构成的列表，每个二元组包含单词和其词性。
        """
        tagging = []
        words = pseg.cut(text)
        for word_pair in words:
            tagging.append([word_pair.word, word_pair.flag])
        return tagging

# 主程序入口
if __name__ == '__main__':
    words_analyser = Words_Analyser()  # 创建Words_Analyser实例
    text = "我爱北京天安门，天安门太漂亮了"
    print(words_analyser.words_tagging(text))
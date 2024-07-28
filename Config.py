class Config:
    def __init__(self):
        self.confusion_path='./confusion.txt'#混淆词表,用于纠错
        self.entity_dict='./entity_dict.txt'#实体词典，用于命名体识别
        self.verb_fillter=['帮']
        self.actions_draw=['画','绘']
        self.actions_asking=['问','解释','说明','教','啥','什么是','啥是','啥叫','叫啥','是什么','是啥']
        self.intentHelperPrompt=("你是一个教学领域相关APP意图识别模型,其中教学领域主要涉及[语文、数学、英语、物理、化学、生物]几个学科。现在你的任务是，接受用户输入，判断用户意图。意图总共有三种：【绘图，提问，其他】。\n"
                                 "1.对于绘图意图，你需要抽取出用户需要执行的动作。例如用户输入：画一个苯环。你对这个输入判断意图为绘图。或者：删除氢原子。则意图为:绘图\n"
                                 "2.对于提问意图，你需要判断用户的意图为提问。并且抽取出用户要提问的实体。 例如用户输入：什么是苯环？ 你需要判断出用户的意图为：提问\n"
                                 "3.对于其他意图，你只需要识别意图。\n"
                                 "你只需要给出识别到的意图。除此之外不用输出任何内容。输出的形式类似于 xxx\n"
                                 "下面是用户给出的输入:")

if __name__ == '__main__':

    config=Config()
    print(config.intentHelperPrompt+"帮我画一个苯环")

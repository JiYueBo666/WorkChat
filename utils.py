import os
import Levenshtein
from concurrent.futures import ThreadPoolExecutor
class entity_extractor:
    def __init__(self,entity_dict='./entity_dict.txt'):
        self.entity_dict_path= entity_dict
        self.load_dict()
    def load_dict(self):
        '''
        加载实体词典.
        示例：
        五哈	VarietyShow+++哈哈哈哈哈
        哈哈哈哈哈	VarietyShow+++哈哈哈哈哈
        加载结果：
        {
         '五哈': [{
          'slot_name': 'VarietyShow',
          'slot_value': '哈哈哈哈哈'
         }],
        }
        :return:
        '''
        if not self.entity_dict_path:
            raise ValueError("实体词典路径为空")
        if not os.path.exists(self.entity_dict_path):
            raise ValueError("实体词典路径错误")
        slot_dict = {}
        with open(self.entity_dict_path, encoding="utf8") as f:
            for line in f:
                ll = line.strip().split("\t")
                if len(ll) != 2:
                    continue
                slot_info = ll[1].split('+++')
                if len(slot_info) != 2:
                    continue
                if ll[0] in slot_dict:
                    slot_dict[ll[0]].append({"slot_name": slot_info[0], "slot_value": slot_info[1]})
                else:
                    slot_dict[ll[0]] = [{"slot_name": slot_info[0], "slot_value": slot_info[1]}]
        self.slot_dict = slot_dict
    def entity_extract(self,query):
        '''
        最大后向匹配算法，提取文本实体。
        :param query:
        :return:
        '''
        query_len = len(query)
        idx = 0
        idy = query_len
        slot_get = []
        tmp_slot_get_len = 0
        while idy > 0:
            while idx < idy:
                if query[idx:idy] in self.slot_dict:
                    for item in self.slot_dict[query[idx:idy]]:
                        slot_get.append({"slot_word": query[idx:idy],
                                         "slot_name": item["slot_name"],
                                         "slot_value": item["slot_value"],
                                         "slot_start": idx,
                                         "slot_end": idy
                                         })
                    break
                idx = idx + 1
            if len(slot_get) != tmp_slot_get_len:
                idy = idx
                idx = 0
                tmp_slot_get_len = len(slot_get)
            else:
                idx = 0
                idy = idy - 1
        return slot_get
def process_file_a_to_b(file_a_path, file_b_path):
    # 读取文件a的内容
    with open(file_a_path, 'w', encoding='utf-8') as file_a:
    # 处理每一行并写入文件b
        with open(file_b_path, 'r', encoding='utf-8') as file_b:
            lines=file_b.readlines()
            for line in lines:
                # 假设每行都是中文文本后面跟着一个数字，中间用制表符分隔
                line=line.strip().split('\t')
                text= line[0]
                # 构建新格式的行
                new_line = f"{text}\tChemEntity+++{text}\n"
                # 写入文件b
                file_a.write(new_line)
        file_b.close()
    file_a.close()


def compute_levenshtein_distance(self, input_string, target):
    """计算并返回输入字符串与目标字符串的编辑距离及目标字符串"""
    return [Levenshtein.distance(input_string, target), target]


def levenshtein_recall(self, user_query, entity_dict,top_n=20):
    """计算用户查询与混淆列表中词语的编辑距离，并返回编辑距离最小的几个词"""
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
        # 并行计算编辑距离
        results = list(executor.map(lambda word: self.compute_levenshtein_distance(user_query, word),entity_dict))
    # 按编辑距离排序并获取最小的几个
    top_results = sorted(results, key=lambda x: x[0])[:top_n]
    # [[distance,word]....]
    return top_results
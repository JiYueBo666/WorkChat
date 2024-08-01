import pkuseg

print("开始切词")
seg=pkuseg.pkuseg(postag=True,user_dict=r'C:\Users\admin\Desktop\语音交互\WorkChat\confusion.txt')
text=seg.cut("画个加基本吧")
print("切词结束")

res=[list(x) for x in text]
print(res)
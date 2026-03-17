# 文件操作和数据处理练习
# 数字
sum = 0
# 关注的数字
att = ['2','0','1','9']
for i in range(1,2020):
    for c in att:
        if c in str(i):
            sum += i**2
            break
print(sum)

# 初值条件
an = 1
an_1 = 1
an_2 = 1
for i in range(4,20190325):
    temp = an
    # 只保留后四位，不足时前面补0
    an = int(('{:0>4d}'.format(an + an_1 + an_2))[-4::])
    # 更新值
    an_2 = an_1
    an_1 = temp
print('{:0>4d}'.format(an))

# 卡片
# 统计已用卡片数
cards = [0 for i in range(10)]
# 判断卡片是否足够
def enough(cards):
    for i in range(9):
        if cards[i] > 2021:
            return False
    return True
num = 0
while enough(cards):
    num += 1
    # 消耗卡片
    for c in str(num):
        cards[int(c)] += 1
print(num)

# 破译密文
encode_text = input('密文:')
decode_text = ''
for c in encode_text:
    if c.islower():
        if c == 'a':
            decode_text += 'y'
        elif c == 'b':
            decode_text += 'z'
        else:
            decode_text += chr(ord(c)-2)
    else:
        decode_text += c
print(decode_text)

# 分词与词频统计
import jieba
filepath = './'
# 读文件
with open(filepath+'西游记.txt','r',encoding='utf-8') as file:
    text = file.read()
# 分词
words = jieba.lcut(text)
# 写文件
with open(filepath+'西游记词汇.txt','w',encoding='utf-8') as file:
    file.write(' '.join(words))
# 统计词频
count = 0
for word in words:
    if word == '八戒':
        count += 1
print(count)
text = file.read()
# 分词
words = jieba.lcut(text)
# 写文件
with open(filepath+'西游记词汇.txt','w',encoding='utf-8') as file:
    file.write(' '.join(words))
# 统计词频
count = 0
for word in words:
    if word == '八戒':
        count += 1
print(count)
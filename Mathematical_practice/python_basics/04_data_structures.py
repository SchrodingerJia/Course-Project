# 数据结构和字典练习
# 省份简称
province_abbreviation = {
    # 直辖市
    "北京市": "京",
    "天津市": "津",
    "上海市": "沪",
    "重庆市": "渝",
    # 自治区
    "内蒙古自治区": "蒙",
    "广西壮族自治区": "桂",
    "西藏自治区": "藏",
    "宁夏回族自治区": "宁",
    "新疆维吾尔自治区": "新",
    # 省
    "河北省": "冀",
    "山西省": "晋",
    "辽宁省": "辽",
    "吉林省": "吉",
    "黑龙江省": "黑",
    "江苏省": "苏",
    "浙江省": "浙",
    "安徽省": "皖",
    "福建省": "闽",
    "江西省": "赣",
    "山东省": "鲁",
    "河南省": "豫",
    "湖北省": "鄂",
    "湖南省": "湘",
    "广东省": "粤",
    "海南省": "琼",
    "四川省": "川",
    "贵州省": "黔",
    "云南省": "云",
    "陕西省": "陕",
    "甘肃省": "甘",
    "青海省": "青",
    "台湾省": "台",
    # 特别行政区
    "香港特别行政区": "港",
    "澳门特别行政区": "澳"
}
key = input('请输入省份为:')
print(f'{key}的简称为{province_abbreviation[key]}')

# 猜单词游戏
from random import choice,randint,seed
seed(0)
WORDS = ['apple', 'pear', 'banana', 'cherry', 'good', 'better', 'best', 'python', 'while', 'tuple', 'dictionary', 'jumble', 'difficult', 'aesthetic', 'stereotype', 'civilization', 'anniversary']
# 生成jumble
def get_jumble(WORDS):
    ans = choice(WORDS)
    word = [i for i in ans]
    jumble = ''
    while word:
        jumble += word.pop(randint(0,len(word)-1))
    return jumble, ans
# 猜测循环
print('欢迎参加猜单词游戏！\n请把乱序后的字母组成一个单词')
q = 'Y'
while q == 'Y':
    # 获取jumble及正确答案
    jumble, ans = get_jumble(WORDS)
    print(f'乱序后的单词:{jumble}')
    guess = input('请输入您猜测的结果:')
    while guess != ans:
        guess = input('结果不对，请重新猜测:')
    q = input('恭喜您，猜对了！\n是否继续(Y/N)?')
print('谢谢参与，欢迎下次再玩！')

# 身份证号校验码
# 权重列表
weight = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]
# ZM映射字典
Mlist = ['1','0','X','9','8','7','6','5','4','3','2']
ZMdict = {i:Mlist[i] for i in range(11)}
# 输入身份证号
num = [i for i in input('请输入18位身份证号:')]
# 计算M
sum = 0
for i in range(17):
    sum += weight[i]*int(num[i])
M = ZMdict[sum % 11]
# 核验
if num[-1] == M:
    print(f'身份证号规则核验通过，校验码是:{M}')
else:
    print(f'身份证号规则核验失败，校验码应为{M}，当前校验码是:{num[-1]}')
M = ZMdict[sum % 11]
# 核验
if num[-1] == M:
    print(f'身份证号规则核验通过，校验码是:{M}')
else:
    print(f'身份证号规则核验失败，校验码应为{M}，当前校验码是:{num[-1]}')
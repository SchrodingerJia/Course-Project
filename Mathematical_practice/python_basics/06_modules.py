# 闰年判断
def leap(year:int):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
# 日期统计
def count_days(date:str):
    days = [31,28,31,30,31,30,31,31,30,31,30,31]
    # 日期分割
    year, month, day = map(int,date.split('.'))
    # 闰年处理
    days[1] = 29 if leap(year) else 28
    # 统计天数
    count = day
    for i in range(month-1):
        count += days[i]
    print(f'{date}是{year}年的第{count}天')
date = input('请输入日期(如2025.7.1):')
count_days(date)
# 判断回文
def ispal(s:str):
    # 双指针
    l = 0
    r = len(s) - 1
    while r-l > 0:
        if s[l] != s[r]:
            return False
        l += 1
        r -= 1
    return True
s = input('输入字符串:')
if ispal(s):
    print(f'{s}是回文字符串')
else:
    print(f'{s}不是回文字符串')
    # 偶数倒数求和
def resum_even(n:int):
    if n == 2:
        return 0.5
    else:
        return resum_even(n-2) + 1.0/n

# 奇数倒数求和
def resum_odd(n:int):
    if n == 1:
        return 1.0
    else:
        return resum_odd(n-2) + 1.0/n

# 倒数求和
def resum(n:int):  
    if n % 2 == 0:
        return resum_even(n)
    else:
        return resum_odd(n)
    
n = int(input('n='))
print(resum(n))
# 星座字典，格式为:月份：(分隔日期，<=分隔日期时的星座，>分隔日期时的星座)
constellation = {1:(19,'摩羯座','水瓶座'),
                 2:(18,'水瓶座','双鱼座'),
                 3:(20,'双鱼座','白羊座'),
                 4:(19,'白羊座','金牛座'),
                 5:(20,'金牛座','双子座'),
                 6:(21,'双子座','巨蟹座'),
                 7:(22,'巨蟹座','狮子座'),
                 8:(22,'狮子座','处女座'),
                 9:(22,'处女座','天秤座'),
                 10:(23,'天秤座','天蝎座'),
                 11:(22,'天蝎座','射手座'),
                 12:(21,'射手座','摩羯座')}
# 判断前后
def get_constellation(day:int,t:tuple):
    return t[1] if day<=t[0] else t[2]
month, day = map(int,input('请输入日期(如7.1):').split('.'))
print(f'所属星座:{get_constellation(day,constellation[month])}')

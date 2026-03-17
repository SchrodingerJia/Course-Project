class Geese:
    def __init__(self,beak,wing,claw):
        print('我是大雁类！我有以下特征：')
        print(beak)
        print(wing)
        print(claw)
    def fly(self,state):
        print(state)
    
beak_1 = '喙的基部较高，长度和头部的长度几乎相等'
wing_1 = '翅膀长而尖'
claw_1 = "爪子是蹼状的"
wildGoose = Geese(beak_1,wing_1,claw_1)
wildGoose.fly('我飞行的之后，一会儿排成个人字，一会儿排成个一字')

class Fruit: # 定义水果类（基类)
    color = '绿色' # 定义类属性
    def harvest(self, color):
        print("水果是："+ color +'的！') # 输出的是形式参数colon
        print("水果已经收获.")
        print("水果原来是："+ Fruit.color +"的！") # 输出的是类属性color

class Apple(Fruit): # 定义苹果类（派生类)
    color = "红色"
    def _init_(self):
        print("我是苹果")
        
class Orange(Fruit):# 定义橘子类 (派生类)
    color="橙色"
    def __init__(self):
        print("\n我是橘子")
    # 重写harvest方法的代码
    def harvest(self,color):
        print("橘子是："+color+"的！") # 输出的是形式参数color
        print("橘子已经收获.")
        print("橘子原来是："+Fruit.color+"的！") # 输出的是类属性color

apple = Apple() # 创建类的实例（苹果)
apple.harvest(apple.color) # 调用基类的harvest方法
orange = Orange() # 创建类的实例（橘子)
orange.harvest(orange.color) # 调用基类的harvest方法

class Fruit: # 定义水果类（基类)
    def __init__(self, color = '绿色'):
        Fruit.color = color
    def harvest(self, color):
        print("水果是："+ color +'的！') # 输出的是形式参数colon
        print("水果已经收获.")
        print("水果原来是："+ Fruit.color +"的！") # 输出的是类属性color

class Apple(Fruit): # 定义苹果类（派生类)
    color = "红色"
    def _init_(self):
        print("我是苹果")
        
class Sapodilla(Fruit):# 定义橘子类 (派生类)
    def __init__(self,color):
        print("\n我是人参果")
        super().__init__(color)
    # 重写harvest方法的代码
    def harvest(self,color):
        print("人参果是："+color+"的！") # 输出的是形式参数color
        print("人参果已经收获.")
        print("人参果原来是："+Fruit.color+"的！") # 输出的是类属性color

apple = Apple() # 创建类的实例（苹果)
apple.harvest(apple.color) # 调用基类的harvest方法
sapodilla = Sapodilla('白色') # 创建类的实例（人参果)
sapodilla.harvest('金黄色带紫色条纹') # 调用基类的harvest方法
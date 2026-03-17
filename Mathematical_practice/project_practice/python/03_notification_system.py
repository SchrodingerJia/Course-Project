import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas as pd
messages_file = '../data/messages.csv'
dishes_file = '../data/dishes.csv'
users_file = '../data/users.csv'
def SendMessege(text,phone):
    print(f"模拟发送给{phone}如下信息:")
    print(text)
    print()
def OrderUpdate(messages:pd.DataFrame, users:pd.DataFrame) -> None:
    if messages.empty: return
    for i in messages.index:
        stat = messages['status'][i]
        if stat == '已取消':
            phone = users['phone'][messages['merchant'][i]]
            items_str = ''
            for item in messages['items'][i][:-1].split(';'):
                name,num = item.split(':')
                items_str += f'\t{name} x {num}\n'
            text =  ( f"尊敬的{messages['merchant'][i]}，"
                    + f"您的顾客{messages['student'][i]}"
                    + f"取消了订单号为 {messages['id'][i]} 的订单，菜品如下:\n"
                    + items_str
                    + "请及时处理！")
            SendMessege(text,phone)
        elif stat == '已完成':
            phone = users['phone'][messages['student'][i]]
            items_str = ''
            for item in messages['items'][i][:-1].split(';'):
                name,num = item.split(':')
                items_str += f'\t{name} x {num}\n'
            text =  ( f"亲爱的{messages['student'][i]}同学，"
                    + f"您于 {messages['orderTime'][i]} "
                    + f"在{messages['merchant'][i]}订购的\n"
                    + items_str
                    + f"已经制作完成，订单号为 {messages['id'][i]}，"
                    + f"请尽快前往{messages['merchant'][i]}取餐哦！")
            SendMessege(text,phone)
        elif stat == '待处理':
            phone = users['phone'][messages['merchant'][i]]
            items_str = ''
            for item in messages['items'][i][:-1].split(';'):
                name,num = item.split(':')
                items_str += f'\t{name} x {num}\n'
            text =  ( f"尊敬的{messages['merchant'][i]}，"
                    + f"您的顾客{messages['student'][i]}"
                    + f"于 {messages['orderTime'][i]} "
                    + f"下单了\n"
                    + items_str
                    + f"订单号为 {messages['id'][i]}，"
                    + "请尽快制作哦！")
            SendMessege(text,phone)
    messages.drop(messages.index, inplace=True)
    messages.to_csv(messages_file,encoding='gbk',index=False)
def StockWarning(dishes:pd.DataFrame, users:pd.DataFrame, warning_line = 50):
    if dishes.empty : return
    for i in dishes.index:
        if dishes['stock'][i] < warning_line and not dishes['warning'][i]:
            phone = phone = users['phone'][dishes['merchant'][i]]
            text = ( f"尊敬的{dishes['merchant'][i]}，"
                    +f"您供应的 {dishes['dishName'][i]} 存货已不足{warning_line}，"
                    +f"仅剩余{dishes['stock'][i]}份，请尽快补货！")
            SendMessege(text,phone)
            dishes.loc[i,'warning'] = 1
        elif dishes['stock'][i] >= warning_line and dishes['warning'][i]:
            dishes.loc[i,'warning'] = 0
    dishes.to_csv(dishes_file,encoding='gbk',index=False,index_label='merchant')
class FileWriteHandler(FileSystemEventHandler):
    """处理文件写入事件的处理器"""
    def __init__(self, file_path):
        self.target_file = file_path
    def on_modified(self, event):
        """文件被修改时触发"""
        time.sleep(0.1)
        users = pd.read_csv(users_file,encoding='gbk',index_col=0)
        messages = pd.read_csv(messages_file,encoding='gbk')
        dishes = pd.read_csv(dishes_file,encoding='gbk')
        OrderUpdate(messages,users)
        StockWarning(dishes,users)
def monitor_file(file_path):
    """监控指定文件的变化"""
    # 创建观察者
    observer = Observer()
    # 创建事件处理器
    event_handler = FileWriteHandler(file_path)
    # 获取文件所在目录
    directory = file_path if "." not in file_path else "/".join(file_path.split("/")[:-1])
    # 开始监控
    observer.schedule(event_handler, path=directory, recursive=False)
    try:
        observer.start()
        print("通知系统已开启")
    except Exception as e:
        print("找不到需要监视的文件")
        exit(1)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
if __name__ == "__main__":
    # 设置要监控的文件路径
    target_file = "../data/messages.csv"
    monitor_file(target_file)
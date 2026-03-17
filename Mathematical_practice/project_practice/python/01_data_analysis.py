# 数据分析模块 - 热销菜品分析、销售额可视化、用户统计分析
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import warnings
# 忽略警告
warnings.filterwarnings('ignore')
# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
def load_and_preprocess_data(user,file_path):
    """
    加载并预处理订单数据
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误：文件 '{file_path}' 不存在")
        return None, None
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path,encoding='utf-8' if '模拟' in file_path else 'gbk')
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None, None
    # 数据清洗
    # 处理菜品详情列
    def parse_dishes(dishes_str):
        # 使用正则表达式提取菜品名称和数量
        pattern = r'([^(;]+)\(x(\d+)\)'
        matches = re.findall(pattern, dishes_str)
        return matches
    try:
        if user[1] == 1:
            df = df[df['商家'] == user[0]]
        elif user[1] == 2:
            df = df[df['学生'] == user[0]]
        # 解析菜品详情
        df['菜品详情'] = df['菜品详情'].str.strip('"')  # 去除双引号
        df['菜品列表'] = df['菜品详情'].apply(parse_dishes)
        # 创建菜品销售记录
        dish_records = []
        for _, row in df.iterrows():
            order_id = row['订单号']
            student = row['学生']
            merchant = row['商家']
            order_time = row['下单时间']
            status = row['状态']
            total_amount = row['总金额']
            for dish, quantity in row['菜品列表']:
                dish_records.append({
                    '订单号': order_id,
                    '学生': student,
                    '商家': merchant,
                    '下单时间': order_time,
                    '状态': status,
                    '总金额': total_amount,
                    '菜品': dish.strip(),
                    '数量': int(quantity)
                })
        # 创建菜品销售DataFrame
        dish_df = pd.DataFrame(dish_records)
        # 转换时间格式
        dish_df['下单时间'] = pd.to_datetime(dish_df['下单时间'])
        # 添加日期相关列
        dish_df['日期'] = dish_df['下单时间'].dt.date
        dish_df['月份'] = dish_df['下单时间'].dt.to_period('M')
        dish_df['星期'] = dish_df['下单时间'].dt.day_name()
        # 计算每个菜品的销售额（按数量比例分配总金额）
        # 首先计算每个订单中每个菜品的数量占比
        order_total_quantity = dish_df.groupby('订单号')['数量'].transform('sum')
        dish_df['数量占比'] = dish_df['数量'] / order_total_quantity
        dish_df['菜品销售额'] = dish_df['总金额'] * dish_df['数量占比']
        return df, dish_df
    except Exception as e:
        print(f"数据处理失败: {e}")
        return None, None
def best_selling_dishes_analysis(dish_df, mode = -1):
    """
    热销菜品分析
    """
    # 按菜品分组统计
    dish_stats = dish_df.groupby('菜品').agg(
        销售数量=('数量', 'sum'),
        销售额=('菜品销售额', 'sum'),
        订单数=('订单号', 'nunique'),
        商家数=('商家', 'nunique'),
        平均价格=('菜品销售额', lambda x: x.sum() / dish_df.loc[x.index, '数量'].sum())
    ).reset_index()
    # 排序
    top_by_quantity = dish_stats.sort_values('销售数量', ascending=False).head(10)
    top_by_revenue = dish_stats.sort_values('销售额', ascending=False).head(10)
    if mode == -1:
        plt.clf()
        ax = sns.barplot(x='销售数量', y='菜品', data=top_by_quantity, palette='viridis')
        plt.title('热销菜品TOP10（按销售数量）', fontsize=14, fontweight='bold')
        plt.xlabel('销售数量', fontsize=12)
        plt.ylabel('菜品', fontsize=12)
        # 在条形上添加数值
        for p in ax.patches:
            width = p.get_width()
            plt.text(width + 1, p.get_y() + p.get_height()/2, f'{int(width)}',
                    ha='left', va='center', fontsize=10)
    elif mode == 1:
        plt.clf()
        plt.subplot(1, 2, 1)
        ax = sns.barplot(x='销售数量', y='菜品', data=top_by_quantity, palette='viridis')
        plt.title('热销菜品TOP10（按销售数量）', fontsize=14, fontweight='bold')
        plt.xlabel('销售数量', fontsize=12)
        plt.ylabel('菜品', fontsize=12)
        # 在条形上添加数值
        for p in ax.patches:
            width = p.get_width()
            plt.text(width + 1, p.get_y() + p.get_height()/2, f'{int(width)}',
                    ha='left', va='center', fontsize=10)
        plt.subplot(1, 2, 2)
        ax = sns.barplot(x='销售额', y='菜品', data=top_by_revenue, palette='magma')
        plt.title('热销菜品TOP10（按销售额）', fontsize=14, fontweight='bold')
        plt.xlabel('销售额（元）', fontsize=12)
        plt.ylabel('菜品', fontsize=12)
        # 在条形上添加数值
        for p in ax.patches:
            width = p.get_width()
            plt.text(width + 5, p.get_y() + p.get_height()/2, f'{width:.1f}',
                    ha='left', va='center', fontsize=10)
    elif mode == 2:
        plt.clf()
        ax = sns.barplot(x='销售数量', y='菜品', data=top_by_quantity, palette='viridis')
        plt.title('最喜爱菜品TOP10', fontsize=14, fontweight='bold')
        plt.xlabel('购买数量', fontsize=12)
        plt.ylabel('菜品', fontsize=12)
        # 在条形上添加数值
        for p in ax.patches:
            width = p.get_width()
            plt.text(width + 0.1, p.get_y() + p.get_height()/2, f'{int(width)}',
                    ha='left', va='center', fontsize=10)
    plt.tight_layout()
    plt.show()
def sales_trend_analysis(dish_df, mode = 1):
    """
    销售趋势分析
    """
    # 按月份统计
    monthly_sales = dish_df.groupby('月份').agg(
        总销售额=('菜品销售额', 'sum'),
        总订单数=('订单号', 'nunique'),
        总菜品数=('数量', 'sum')
    ).reset_index()
    monthly_sales['月份'] = monthly_sales['月份'].astype(str)
    # 按星期统计
    weekdays_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_sales = dish_df.groupby('星期').agg(
        总销售额=('菜品销售额', 'sum'),
        总订单数=('订单号', 'nunique')
    ).reset_index()
    weekday_sales['星期'] = pd.Categorical(weekday_sales['星期'], categories=weekdays_order, ordered=True)
    weekday_sales = weekday_sales.sort_values('星期')
    # 转换为中文星期
    weekday_map = {
        'Monday': '周一',
        'Tuesday': '周二',
        'Wednesday': '周三',
        'Thursday': '周四',
        'Friday': '周五',
        'Saturday': '周六',
        'Sunday': '周日'
    }
    weekday_sales['星期'] = weekday_sales['星期'].map(weekday_map)
    plt.clf()
    if mode == 1 or mode == -1:
        # 月度销售趋势
        plt.subplot(1, 2, 1)
        ax = sns.lineplot(x='月份', y='总销售额', data=monthly_sales, marker='o',
                        color='royalblue', linewidth=2.5)
        plt.title('月度销售额趋势', fontsize=14, fontweight='bold')
        plt.xlabel('月份', fontsize=12)
        plt.ylabel('销售额（元）', fontsize=12)
        plt.xticks(rotation=45)
        # 添加数据标签
        for x, y in zip(monthly_sales['月份'], monthly_sales['总销售额']):
            plt.text(x, y + 1, f'{y:.0f}', ha='center', va='bottom', fontsize=10)
        # 周销售分析
        plt.subplot(1, 2, 2)
        ax = sns.barplot(x='星期', y='总销售额', data=weekday_sales, palette='Set2')
        plt.title('周销售额分布', fontsize=14, fontweight='bold')
        plt.xlabel('星期', fontsize=12)
        plt.ylabel('销售额（元）', fontsize=12)
        # 添加数据标签
        for p in ax.patches:
            height = p.get_height()
            plt.text(p.get_x() + p.get_width()/2., height + 2,
                    f'{height:.0f}', ha='center', va='bottom', fontsize=10)
    elif mode == 2:
        # 月度消费趋势
        plt.subplot(1, 2, 1)
        ax = sns.lineplot(x='月份', y='总销售额', data=monthly_sales, marker='o',
                        color='royalblue', linewidth=2.5)
        plt.title('月度消费趋势', fontsize=14, fontweight='bold')
        plt.xlabel('月份', fontsize=12)
        plt.ylabel('消费金额（元）', fontsize=12)
        plt.xticks(rotation=45)
        # 添加数据标签
        for x, y in zip(monthly_sales['月份'], monthly_sales['总销售额']):
            plt.text(x, y + 1, f'{y:.0f}', ha='center', va='bottom', fontsize=10)
        # 周消费分析
        plt.subplot(1, 2, 2)
        ax = sns.barplot(x='星期', y='总销售额', data=weekday_sales, palette='Set2')
        plt.title('周消费分布', fontsize=14, fontweight='bold')
        plt.xlabel('星期', fontsize=12)
        plt.ylabel('消费金额（元）', fontsize=12)
        # 添加数据标签
        for p in ax.patches:
            height = p.get_height()
            plt.text(p.get_x() + p.get_width()/2., height + 2,
                    f'{height:.0f}', ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.show()
def merchant_analysis(dish_df, mode):
    """
    商家销售分析
    """
    # 商家销售统计
    merchant_stats = dish_df.groupby('商家').agg(
        总销售额=('菜品销售额', 'sum'),
        总订单数=('订单号', 'nunique'),
        总菜品数=('数量', 'sum'),
        菜品种类数=('菜品', 'nunique'),
        平均订单额=('菜品销售额', 'mean')
    ).reset_index()
    # 商家菜品销售情况
    merchant_dish = dish_df.groupby(['商家', '菜品']).agg(
        销售数量=('数量', 'sum'),
        销售额=('菜品销售额', 'sum')
    ).reset_index()
    # 找出每个商家最畅销的菜品
    top_dishes_by_merchant = merchant_dish.loc[merchant_dish.groupby('商家')['销售额'].idxmax()]
    plt.clf()
    if mode == -1:
        # 商家销售分析
        plt.subplot(1, 2, 1)
        top_merchants = merchant_stats.sort_values('总销售额', ascending=False).head(5)
        ax = sns.barplot(x='总销售额', y='商家', data=top_merchants, palette='rocket')
        plt.title('商家销售额TOP5', fontsize=14, fontweight='bold')
        plt.xlabel('销售额（元）', fontsize=12)
        plt.ylabel('商家', fontsize=12)
        # 添加数据标签
        for p in ax.patches:
            width = p.get_width()
            plt.text(width + 5, p.get_y() + p.get_height()/2, f'{width:.1f}',
                    ha='left', va='center', fontsize=10)
        # 商家畅销菜品分析
        plt.subplot(1, 2, 2)
        top_merchant_dishes = top_dishes_by_merchant.sort_values('销售额', ascending=False).head(8)
        ax = sns.barplot(x='销售额', y='商家', hue='菜品', data=top_merchant_dishes,
                        dodge=False, palette='tab10')
        plt.title('商家最畅销菜品', fontsize=14, fontweight='bold')
        plt.xlabel('销售额（元）', fontsize=12)
        plt.ylabel('商家', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='菜品')
    elif mode == 2:
        # 商家销售分析
        plt.subplot(1, 2, 1)
        top_merchants = merchant_stats.sort_values('总销售额', ascending=False).head(5)
        ax = sns.barplot(x='总销售额', y='商家', data=top_merchants, palette='rocket')
        plt.title('消费商家TOP5', fontsize=14, fontweight='bold')
        plt.xlabel('消费总金额（元）', fontsize=12)
        plt.ylabel('商家', fontsize=12)
        # 添加数据标签
        for p in ax.patches:
            width = p.get_width()
            plt.text(width + 5, p.get_y() + p.get_height()/2, f'{width:.1f}',
                    ha='left', va='center', fontsize=10)
        # 商家畅销菜品分析
        plt.subplot(1, 2, 2)
        top_merchant_dishes = top_dishes_by_merchant.sort_values('销售数量', ascending=False).head(8)
        ax = sns.barplot(x='销售数量', y='商家', hue='菜品', data=top_merchant_dishes,
                        dodge=False, palette='tab10')
        plt.title('各商家最喜爱菜品', fontsize=14, fontweight='bold')
        plt.xlabel('购买数量', fontsize=12)
        plt.ylabel('商家', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='菜品')
    plt.tight_layout()
    plt.show()
def customer_analysis(dish_df):
    """
    顾客消费分析
    """
    # 顾客消费统计
    customer_stats = dish_df.groupby('学生').agg(
        总消费额=('菜品销售额', 'sum'),
        订单数=('订单号', 'nunique'),
        购买菜品数=('数量', 'sum'),
        平均订单额=('菜品销售额', 'mean')
    ).reset_index()
    # 顶级顾客
    top_customers = customer_stats.sort_values('总消费额', ascending=False).head(10)
    plt.clf()
    # 顾客消费分析
    ax = sns.barplot(x='总消费额', y='学生', data=top_customers, palette='mako')
    plt.title('高价值顾客TOP10', fontsize=14, fontweight='bold')
    plt.xlabel('总消费额（元）', fontsize=12)
    plt.ylabel('学生', fontsize=12)
    # 添加数据标签
    for p in ax.patches:
        width = p.get_width()
        plt.text(width + 5, p.get_y() + p.get_height()/2, f'{width:.1f}',
                 ha='left', va='center', fontsize=10)
    plt.tight_layout()
    plt.show()
def price_analysis(dish_df, mode = 1):
    # 按菜品分组统计
    dish_stats = dish_df.groupby('菜品').agg(
        销售数量=('数量', 'sum'),
        销售额=('菜品销售额', 'sum'),
        订单数=('订单号', 'nunique'),
        商家数=('商家', 'nunique'),
        平均价格=('菜品销售额', lambda x: x.sum() / dish_df.loc[x.index, '数量'].sum())
    ).reset_index()
    plt.clf()
    if mode == 1 or mode == -1:
        # 菜品价格分布
        sns.histplot(dish_stats['平均价格'], bins=20, kde=True, color='teal')
        plt.title('菜品价格分布', fontsize=14, fontweight='bold')
        plt.xlabel('平均价格（元）', fontsize=12)
        plt.ylabel('菜品数量', fontsize=12)
    plt.tight_layout()
    plt.show()
def stat_analysis(dish_df):
    """
    订单状态分析
    """
    plt.clf()
    status_counts = dish_df['状态'].value_counts()
    plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%',
            colors=sns.color_palette('pastel'), startangle=90)
    plt.title('订单状态分布', fontsize=14, fontweight='bold')
    plt.axis('equal')  # 保持圆形
    plt.tight_layout()
    plt.show()
# 管理员模式
def admin(user,csv_file):
    # 加载和预处理数据
    order_df, dish_df = load_and_preprocess_data(user,csv_file)
    if order_df is None or dish_df is None:
        print("数据处理失败，请检查输入文件")
        return
    while True:
        print()
        print('可选择功能如下:')
        print('1. 查看热销商品')
        print('2. 查看销售趋势')
        print('3. 查看商家情况')
        print('4. 查看顾客情况')
        print('5. 查看菜品价格情况')
        print('6. 查看订单状态分布')
        print('0. 退出')
        choice = input('请选择:')
        match choice:
            case '1':
                best_selling_dishes_analysis(dish_df[dish_df['状态'] == '已完成'],-1)
                continue
            case '2':
                sales_trend_analysis(dish_df[dish_df['状态'] == '已完成'],-1)
                continue
            case '3':
                merchant_analysis(dish_df[dish_df['状态'] == '已完成'],-1)
                continue
            case '4':
                customer_analysis(dish_df[dish_df['状态'] == '已完成'])
                continue
            case '5':
                price_analysis(dish_df[dish_df['状态'] == '已完成'],-1)
                continue
            case '6':
                stat_analysis(dish_df)
                continue
            case '0':
                print('退出系统')
                exit(0)
            case _:
                print('无效功能，请重新输入!')
                continue
# 商户模式
def merchant(user,csv_file):
    # 加载和预处理数据
    order_df, dish_df = load_and_preprocess_data(user,csv_file)
    if order_df is None or dish_df is None:
        print("数据处理失败，请检查输入文件")
        return
    while True:
        print()
        print('可选择功能如下:')
        print('1. 查看热销商品')
        print('2. 查看销售趋势')
        print('3. 查看顾客情况')
        print('4. 查看菜品价格情况')
        print('5. 查看订单状态分布')
        print('0. 退出')
        choice = input('请选择:')
        match choice:
            case '1':
                best_selling_dishes_analysis(dish_df[dish_df['状态'] == '已完成'],1)
                continue
            case '2':
                sales_trend_analysis(dish_df[dish_df['状态'] == '已完成'],1)
                continue
            case '3':
                customer_analysis(dish_df[dish_df['状态'] == '已完成'])
                continue
            case '4':
                price_analysis(dish_df[dish_df['状态'] == '已完成'],1)
                continue
            case '5':
                stat_analysis(dish_df)
                continue
            case '0':
                print('退出系统')
                exit(0)
            case _:
                print('无效功能，请重新输入!')
                continue
# 学生模式
def student(user,csv_file):
    # 加载和预处理数据
    order_df, dish_df = load_and_preprocess_data(user,csv_file)
    if order_df is None or dish_df is None:
        print("数据处理失败，请检查输入文件")
        return
    while True:
        print()
        print('可选择功能如下:')
        print('1. 查看最喜爱菜品')
        print('2. 查看消费趋势')
        print('3. 查看最喜爱商户')
        print('4. 查看订单状态分布')
        print('0. 退出')
        choice = input('请选择:')
        match choice:
            case '1':
                best_selling_dishes_analysis(dish_df[dish_df['状态'] == '已完成'],2)
                continue
            case '2':
                sales_trend_analysis(dish_df[dish_df['状态'] == '已完成'],2)
                continue
            case '3':
                merchant_analysis(dish_df[dish_df['状态'] == '已完成'],2)
                continue
            case '4':
                stat_analysis(dish_df)
                continue
            case '0':
                print('退出系统')
                exit(0)
            case _:
                print('无效功能，请重新输入!')
                continue
# 登录系统
def login(user_file) -> tuple:
    """
    返回用户名称(str)与用户类型(int):
    管理员登录:-1
    商户登录:1
    学生登录:2
    """
    # 检查路径
    if not os.path.exists(user_file):
        print(f"错误：文件 '{user_file}' 不存在")
        exit(1)
        return None,None
    # 读取用户数据
    try :
        users = pd.read_csv(user_file,encoding='gbk',index_col=0)
    except Exception as e:
        print(f"读取文件失败: {e}")
        exit(1)
        return None,None
    user_name = input("请输入用户名称:")
    while not user_name in users.index.tolist():
        user_name = input("用户不存在，请重新输入用户名称:")
    user_password = input("请输入密码:")
    while user_password != users.loc[user_name,'password']:
        user_password = input("密码错误，请重新输入密码:")
    print(f"登录成功！欢迎您，{user_name}!")
    match users.loc[user_name,'userType']:
        case 'admin':
            return user_name,-1
        case 'merchant':
            return  user_name,1
        case 'student':
            return  user_name,2
        case _:
            return None,None
if __name__ == "__main__":
    # 文件路径
    csv_file = "../data/order_records.csv"
    user_file = "../data/users.csv"
    # 登录系统
    user = login(user_file)
    match user[1]:
        case -1:
            admin(user,csv_file)
        case 1:
            merchant(user,csv_file)
        case 2:
            student(user,csv_file)
        case _:
            raise Exception("用户类型错误！")
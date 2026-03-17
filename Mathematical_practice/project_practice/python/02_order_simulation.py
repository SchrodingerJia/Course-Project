import csv
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
# np.random.seed(20250323)
# 文件位置
userfile = '../data/users.csv'
dishfile = '../data/dishes.csv'
# 提取用户数据
users = pd.read_csv('../data/users.csv', index_col=0, encoding='gbk')
# 商家列表
merchants = users[users['userType']=='merchant'].index.to_list()
# 商家热度向量
# m_popularity = np.random.randint(1,10,len(merchants))
m_popularity = np.array([4,9,5,5,6,2,4])
# 学生列表
students = users[users['userType']=='student'].index.to_list()
# 菜品数据 - 按商家聚集，包含菜品名称、价格和（随机生成的）受欢迎程度权重
dishes_df = pd.read_csv('../data/dishes.csv', encoding='gbk')
dishes = {}
for merchant in merchants:
    dish_df = dishes_df[dishes_df['merchant'] == merchant]
    popularity = np.random.randint(1,10,len(dish_df))
    dishes[merchant] = np.concatenate((np.array(dish_df)[:,1:],np.array([popularity]).T),axis=1)
# 状态列表
statuses = ["待处理", "已完成", "已取消"]
status_weights = [0.001, 0.949, 0.05]  # 状态概率权重
# 生成订单日期范围
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
# 生成时间段的销售趋势 - 模拟午餐和晚餐高峰
def get_time_trend(hour):
    """根据时间生成销售趋势权重"""
    if 11 <= hour < 13:  # 午餐高峰
        return 1.5
    elif 17 <= hour < 19:  # 晚餐高峰
        return 1.8
    elif 8 <= hour < 10:  # 早餐时间
        return 0.7
    elif 13 <= hour < 17:  # 下午茶
        return 0.5
    else:  # 其他时间
        return 0.3
# 生成工作日/周末销售趋势
def get_day_trend(date):
    """根据日期生成销售趋势权重"""
    weekday = date.weekday()  # 0=周一, 6=周日
    if weekday < 5:  # 工作日
        return 1.0
    else:  # 周末
        return 1.3
# 生成季节销售趋势
def get_season_trend(date):
    """根据季节生成销售趋势权重"""
    month = date.month
    if 3 <= month <= 5:  # 春季
        return 1.0
    elif 6 <= month <= 8:  # 夏季
        return 1.2
    elif 9 <= month <= 11:  # 秋季
        return 1.1
    else:  # 冬季
        return 1.3
# 生成单个订单
def generate_order(order_id, date):
    """生成单个订单记录"""
    # 随机选择学生和商家
    student = random.choice(students)
    merchant = random.choices(merchants,m_popularity)[0]
    # 生成订单时间 (在指定日期内随机时间)
    hour = random.randint(6, 22)  # 6:00-22:00之间
    minute = random.randint(0, 59)
    order_time = date.replace(hour=hour, minute=minute)
    # 随机选择状态
    status = random.choices(statuses, weights=status_weights, k=1)[0]
    # 计算当前时间段的销售趋势
    time_trend = get_time_trend(hour)
    day_trend = get_day_trend(date)
    season_trend = get_season_trend(date)
    # 综合趋势因子
    trend_factor = time_trend * day_trend * season_trend
    # 生成菜品列表 - 菜品数量根据趋势因子调整
    num_dishes = min(dishes[merchant].shape[0],max(1, min(4, int(np.random.poisson(1.75 * trend_factor)))))
    # 选择菜品 - 考虑菜品受欢迎程度
    selected_dishes = []
    available_dishes = dishes[merchant]
    for _ in range(num_dishes):
        # 根据受欢迎程度概率选择菜品
        dish = random.choices(available_dishes, weights=list(available_dishes[:,-1]), k=1)[0]
        # 数量 - 热门菜品可能被点更多份
        quantity = max(1, int(np.random.poisson(1.0 + 0.2 * dish[3]/10)))
        selected_dishes.append({
            "name": dish[0],
            "quantity": quantity,
            "price": dish[1]
        })
        # print(available_dishes)
        available_dishes = np.delete(available_dishes, np.where(available_dishes[:, 0]==dish[0])[0], axis=0)
    # 计算总金额
    total_amount = sum(dish["price"] * dish["quantity"] for dish in selected_dishes)
    # 格式化菜品详情
    dish_details = ";".join([f"{dish['name']}(x{dish['quantity']})" for dish in selected_dishes]) + ';'
    return {
        "订单号": order_id,
        "学生": student,
        "商家": merchant,
        "下单时间": order_time.strftime("%Y-%m-%d %H:%M:%S"),
        "状态": status,
        "总金额": total_amount,
        "菜品详情": dish_details
    }
# 生成订单记录CSV文件
def generate_order_records(output_file, num_orders=1000):
    """生成订单记录并保存为CSV文件"""
    # 生成日期列表
    date_range = (end_date - start_date).days + 1
    dates = [start_date + timedelta(days=i) for i in range(date_range)]
    # 按日期分配订单数量 - 考虑季节性趋势
    orders_per_day = {}
    for date in dates:
        # 基础订单数量
        base_orders = num_orders // date_range
        # 调整因子 - 周末和季节影响
        day_factor = 1.5 if date.weekday() >= 5 else 1.0  # 周末订单多
        season_factor = get_season_trend(date)
        # 最终该天订单数量
        orders_per_day[date] = max(1, int(base_orders * day_factor * season_factor))
    # 确保总订单数量接近要求
    total_orders = sum(orders_per_day.values())
    if total_orders < num_orders:
        # 随机选择一些日期增加订单
        extra_orders = num_orders - total_orders
        for _ in range(extra_orders):
            random_date = random.choice(dates)
            orders_per_day[random_date] += 1
    # 生成订单
    orders = []
    order_id = 1
    for date, daily_orders in orders_per_day.items():
        for _ in range(daily_orders):
            order = generate_order(order_id, date)
            orders.append(order)
            order_id += 1
    # 写入CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["订单号", "学生", "商家", "下单时间", "状态", "总金额", "菜品详情"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for order in orders:
            writer.writerow(order)
    print(f"成功生成 {len(orders)} 条订单记录到 {output_file}")
# 生成1000条订单记录
if __name__ == "__main__":
    generate_order_records("../data/simulated_orders.csv", num_orders=1000)
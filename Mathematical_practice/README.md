# 校园订餐系统 - 数学实践课程项目

## 项目概述

本项目是一个综合性的校园订餐系统，融合了Java和Python两种编程语言，涵盖了从基础语法学习到完整项目实践的完整流程。项目分为三个主要板块：Java基础、Python基础和项目实践，旨在通过实际应用场景巩固编程知识。

## 项目结构

```
数学实践/
├── java_basics/                    # Java基础学习
│   └── 01_basic/                   # 基础语法练习
│       ├── App.java                # 应用程序入口
│       ├── ArrayOperation.java     # 数组操作练习
│       ├── BMI.java                # BMI计算器
│       ├── Calculator.java         # 计算器
│       ├── Methods.java            # 方法练习
│       ├── ProductSystem.java      # 产品管理系统
│       ├── StringOperation.java    # 字符串操作
│       ├── StudentCourseSystem.java # 学生课程系统
│       ├── Temperature.java        # 温度转换
│       └── Triangle.java           # 三角形计算
│
├── python_basics/                  # Python基础学习
│   ├── 03_control_flow.py          # 流程控制（九九乘法表、三角形判断、猜数字等）
│   ├── 04_data_structures.py       # 数据结构（字典、列表等）
│   ├── 05_file_io.py               # 文件操作（读写、数据处理）
│   ├── 06_modules.py               # 模块使用（日期、回文、函数、星座）
│   ├── 07_advanced_topics.py       # 高级主题（面向对象编程）
│   └── 11_project_integration.py   # 项目集成（数据分析与可视化）
│
└── project_practice/               # 项目实践
    ├── java/                       # Java实现部分
    │   └── order_system/           # 订餐系统
    │       ├── Main.java           # 系统主程序
    │       └── README.md           # Java系统说明
    │
    ├── python/                     # Python实现部分
    │   ├── 01_data_analysis.py     # 数据分析模块
    │   ├── 02_order_simulation.py  # 订单模拟模块
    │   ├── 03_notification_system.py # 通知系统模块
    │   └── 04_order_system_test.py # 系统测试模块
    │
    └── data/                       # 数据文件
        ├── dishes.csv              # 菜品数据
        ├── users.csv               # 用户数据
        ├── orders.csv              # 订单数据
        ├── messages.csv            # 消息记录
        ├── simulated_orders.csv    # 模拟订单数据
        ├── order_records.csv       # 订单记录报告
        ├── sales_analysis_report.txt # 销售分析报告
        └── backup/                 # 数据备份
            ├── dishes_backup.csv
            ├── users_backup.csv
            ├── orders_backup.csv
            └── messages_backup.csv
```

## 功能模块

| 模块 | Java部分 | Python部分 |
|------|----------|------------|
| **用户系统** | 学生/商家登录注册<br>**CSV管理用户数据**<br>管理员登录，管理用户与订单系统后台 | - |
| **菜单管理** | 商家管理菜品（名称/价格/库存）<br>**CSV管理菜品数据** | - |
| **订餐流程** | 学生下单/取消订单<br>自动计算金额 | - |
| **数据分析** | 生成订单记录CSV | 热销菜品分析<br>销售额可视化<br>**针对不同用户的统计分析** |
| **通知系统** | - | 订单状态短信提醒（模拟）<br>低库存预警 |

## 使用说明

### 环境要求

- **Java环境**: JDK 8 或更高版本
- **Python环境**: Python 3.6 或更高版本
- **Python依赖**: 安装 `requirements.txt` 中的包（可选）

### 运行Java订餐系统

1. 进入项目目录：
   ```bash
   cd project_practice/java/order_system/
   ```

2. 编译Java文件：
   ```bash
   javac Main.java
   ```

3. 运行程序：
   ```bash
   java Main
   ```

4. 系统支持三种角色登录：
   - **学生**: 浏览菜单、下单、取消订单
   - **商家**: 管理菜品、查看订单
   - **管理员**: 管理用户、查看系统数据

### 运行Python模块

1. 进入Python项目目录：
   ```bash
   cd project_practice/python/
   ```

2. 运行各个功能模块：
   ```bash
   # 数据分析
   python 01_data_analysis.py
   
   # 订单模拟
   python 02_order_simulation.py
   
   # 通知系统
   python 03_notification_system.py
   
   # 系统测试
   python 04_order_system_test.py
   ```

### 数据文件说明

- **users.csv**: 存储用户信息，包括用户名、密码、用户类型（学生/商家/管理员）、手机号
- **dishes.csv**: 存储菜品信息，包括商家名称、菜品名、价格、库存量、预警值
- **orders.csv**: 存储订单信息，包括订单号、学生、商家、下单时间、状态、总金额、菜品详情
- **messages.csv**: 存储系统消息记录，用于通知系统
- **order_records.csv**: 生成的订单统计报告
- **simulated_orders.csv**: 模拟生成的订单数据，用于测试和分析
- **sales_analysis_report.txt**: 销售分析文本报告

## 项目特点

1. **双语言集成**: 结合Java和Python的优势，Java负责核心业务逻辑，Python负责数据分析和通知功能
2. **模块化设计**: 各功能模块独立，便于维护和扩展
3. **数据驱动**: 使用CSV文件存储数据，便于理解和修改
4. **实用性强**: 基于真实的校园订餐场景，具有实际应用价值
5. **学习导向**: 从基础语法到项目实践，适合编程学习者

## 学习目标

通过本项目，学习者可以掌握：

1. Java和Python的基础语法和高级特性
2. 面向对象编程思想
3. 文件读写和数据处理
4. 模块化编程和代码组织
5. 实际项目的开发流程
6. 数据分析和可视化技术
7. 多语言协同开发

## 注意事项

1. 首次运行Java系统时会创建示例数据
2. 所有CSV文件使用UTF-8编码，部分文件可能使用GBK编码
3. 系统退出时会自动保存数据更改
4. Python数据分析模块需要安装相关依赖包
5. 通知系统的短信功能为模拟实现，实际不发送真实短信

## 许可证

本项目仅供学习使用，未经许可不得用于商业用途。

---
#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 导入必要的库
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


# In[2]:


# 设置设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用设备: {device}")  # 打印当前使用的设备信息


# In[3]:


# 数据预处理和加载
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))  # MNIST 标准化参数
])

# 加载 MNIST 数据集,使用 transforms 进行数据预处理和标准化
train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)

# 创建数据加载器
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)


# In[4]:


# 建立全连接神经网络模型
model = nn.Sequential(
    nn.Flatten(),  # 将 28x28 图像展平为 784 维向量
    nn.Linear(784, 128),  # 全连接层，128 个神经元
    nn.ReLU(),  # ReLU 激活函数
    nn.Linear(128, 10)  # 输出层，10 个神经元
).to(device)


# In[5]:


# 配置训练方法：优化器、损失函数
optimizer = optim.Adam(model.parameters())
criterion = nn.CrossEntropyLoss()


# In[6]:


# 训练模型
model.train()
for epoch in range(5):
    for data, target in train_loader:
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
    
    print(f'Epoch {epoch+1} completed')


# In[7]:


# 模型评估
model.eval()
test_loss = 0
correct = 0
total = 0

with torch.no_grad():
    for data, target in test_loader:
        data, target = data.to(device), target.to(device)
        output = model(data)
        test_loss += criterion(output, target).item()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        total += target.size(0)

test_loss /= len(test_loader)
accuracy = 100. * correct / total

print(f'Test set: Average loss: {test_loss:.4f}, Accuracy: {correct}/{total} ({accuracy:.2f}%)')


# # 任务2

# ## 1、批量大小对训练速度和内存使用的影响

# In[10]:


# 导入必要的库
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# 设置设备 - 检查是否有可用的GPU，如果有则使用GPU，否则使用CPU
# 这可以显著加速训练过程，因为GPU擅长并行计算
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用设备: {device}")  # 打印当前使用的设备信息

# 数据预处理和加载
# transforms.Compose 将多个数据转换操作组合在一起
transform = transforms.Compose([
    transforms.ToTensor(),  # 将PIL图像或numpy数组转换为PyTorch张量
    transforms.Normalize((0.1307,), (0.3081,))  # 使用MNIST数据集的均值和标准差进行标准化
    # 标准化公式: (input - mean) / std
])

# 加载MNIST数据集
# datasets.MNIST是PyTorch提供的MNIST数据集加载器
# root: 数据集存储路径
# train=True: 加载训练集
# download=True: 如果数据集不存在则自动下载
# transform: 应用上面定义的数据转换
train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)

# 创建数据加载器
# DataLoader负责批量加载数据，支持多进程数据加载和数据打乱
# batch_size: 每个批次包含样本数
# shuffle=True: 在每个epoch开始时打乱训练数据顺序
batches = [32, 64, 128]
# 添加时间记录和内存监控
import time
import psutil

# 建立全连接神经网络模型
# nn.Sequential是一个顺序容器，模块将按照它们在构造函数中传递的顺序添加
model = nn.Sequential(
    nn.Flatten(),  # 将28x28的图像展平为784维的向量
    nn.Linear(784, 128),  # 全连接层，输入维度784，输出维度128
    nn.ReLU(),  # ReLU激活函数，引入非线性
    nn.Linear(128, 10)  # 输出层，输入维度128，输出维度10（对应10个数字类别）
).to(device)  # 将模型移动到指定的设备（GPU或CPU）

# 配置训练方法：优化器、损失函数
# optim.Adam是一种自适应学习率的优化算法，结合了AdaGrad和RMSProp的优点
optimizer = optim.Adam(model.parameters())  # 传入模型参数以便优化器知道要优化什么
# nn.CrossEntropyLoss是交叉熵损失函数，适用于多分类问题
# 它内部已经包含了Softmax操作，所以模型最后一层不需要添加Softmax
criterion = nn.CrossEntropyLoss()

times = []
memories = []
for batch_size in batches:
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)  # 测试集不需要打乱

    start_time = time.time()
    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    # 训练模型
    model.train()  # 将模型设置为训练模式，这会启用dropout和batch normalization等训练特定行为
    for epoch in range(5):  # 训练5个epoch
        for data, target in train_loader:  # 遍历训练数据加载器中的每个批次
            data, target = data.to(device), target.to(device)  # 将数据移动到指定设备
            
            optimizer.zero_grad()  # 清除之前的梯度，防止梯度累积
            output = model(data)  # 前向传播，计算模型输出
            loss = criterion(output, target)  # 计算损失
            loss.backward()  # 反向传播，计算梯度
            optimizer.step()  # 更新模型参数
        
        print(f'Epoch {epoch+1} completed')  # 打印当前epoch完成信息

    # 在训练循环结束后记录时间和内存
    end_time = time.time()
    final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    print(f'Training time: {end_time - start_time:.2f} seconds')
    times.append(end_time - start_time)
    print(f'Memory usage: {final_memory - initial_memory:.2f} MB')
    memories.append(final_memory - initial_memory)


# In[16]:


import matplotlib.pyplot as plt
import numpy as np

# 设置图表大小
plt.figure(figsize=(10, 6))

# 设置柱子的位置和宽度
x = np.arange(len(batches))  # batch size的位置
width = 0.35  # 柱子的宽度

# 创建双柱状图
fig, ax1 = plt.subplots(figsize=(10, 6))

# 绘制训练时间的柱状图（使用左侧y轴）
bars1 = ax1.bar(x - width/2, times, width, label='Training Time (s)', color='blue', alpha=0.7)
ax1.set_xlabel('Batch Size')
ax1.set_ylabel('Training Time (seconds)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_xticks(x)
ax1.set_xticklabels(batches)

# 在训练时间柱子上方添加数值
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}s',
             ha='center', va='bottom')

# 创建右侧y轴用于内存使用
ax2 = ax1.twinx()

# 绘制内存使用的柱状图（使用右侧y轴）
bars2 = ax2.bar(x + width/2, memories, width, label='Memory Usage (MB)', color='red', alpha=0.7)
ax2.set_ylabel('Memory Usage (MB)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# 在内存使用柱子上方添加数值
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}MB',
             ha='center', va='bottom')

# 添加标题和图例
plt.title('Training Time and Memory Usage vs Batch Size')
plt.grid(True, axis='y', alpha=0.3)

# 调整布局
plt.tight_layout()
plt.show()



# ## 2、计算数据集的均值和标准差vs预设的MNIST标准化参数

# In[17]:


# 计算数据集的均值和标准差
def calculate_stats(dataloader):
    mean = 0.0
    std = 0.0
    total_images = 0
    
    for images, _ in dataloader:
        batch_samples = images.size(0)
        images = images.view(batch_samples, images.size(1), -1)
        mean += images.mean(2).sum(0)
        std += images.std(2).sum(0)
        total_images += batch_samples
    
    mean /= total_images
    std /= total_images
    return mean, std

# 创建临时数据加载器用于计算统计量
temp_loader = DataLoader(train_dataset, batch_size=1000, shuffle=False)
calculated_mean, calculated_std = calculate_stats(temp_loader)
print(f"计算得到的均值: {calculated_mean}")
print(f"计算得到的标准差: {calculated_std}")

# 预设的MNIST参数
preset_mean = torch.tensor([0.1307])
preset_std = torch.tensor([0.3081])

# 创建两个不同的数据集
transform_calculated = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(calculated_mean, calculated_std)
])

transform_preset = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(preset_mean, preset_std)
])

# 加载两个版本的数据集
train_dataset_calc = datasets.MNIST('./data', train=True, download=True, transform=transform_calculated)
test_dataset_calc = datasets.MNIST('./data', train=False, download=True, transform=transform_calculated)

train_dataset_preset = datasets.MNIST('./data', train=True, download=True, transform=transform_preset)
test_dataset_preset = datasets.MNIST('./data', train=False, download=True, transform=transform_preset)

def train_and_evaluate(train_dataset, test_dataset, method_name):
    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)
    
    # 创建模型
    model = nn.Sequential(
        nn.Flatten(),
        nn.Linear(784, 128),
        nn.ReLU(),
        nn.Linear(128, 10)
    ).to(device)
    
    optimizer = optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss()
    
    # 训练模型
    model.train()
    train_losses = []
    for epoch in range(5):
        epoch_loss = 0
        for data, target in train_loader:
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        train_losses.append(epoch_loss / len(train_loader))
    
    # 评估模型
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.size(0)
    
    accuracy = 100. * correct / total
    return train_losses, accuracy

# 训练两个版本的模型
calc_losses, calc_accuracy = train_and_evaluate(train_dataset_calc, test_dataset_calc, "Calculated Stats")
preset_losses, preset_accuracy = train_and_evaluate(train_dataset_preset, test_dataset_preset, "Preset Stats")


# In[18]:


# 绘制对比图表
plt.figure(figsize=(12, 5))

# 训练损失对比
plt.subplot(1, 2, 1)
epochs = range(1, 6)
plt.plot(epochs, calc_losses, 'b-', label='Calculated Stats')
plt.plot(epochs, preset_losses, 'r-', label='Preset Stats')
plt.xlabel('Epoch')
plt.ylabel('Training Loss')
plt.title('Training Loss Comparison')
plt.legend()
plt.grid(True)

# 准确率对比
plt.subplot(1, 2, 2)
methods = ['Calculated Stats', 'Preset Stats']
accuracies = [calc_accuracy, preset_accuracy]
bars = plt.bar(methods, accuracies, color=['blue', 'red'], alpha=0.7)
plt.ylabel('Accuracy (%)')
plt.title('Final Accuracy Comparison')

# 在柱子上方添加具体数值
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}%',
             ha='center', va='bottom')

plt.tight_layout()
plt.show()


# ## 3、不同的网络深度(3层、5层、7层)

# In[ ]:


# 导入必要的库
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import time

# 设置设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 数据预处理和加载
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# 定义不同深度的网络模型
def create_model(depth):
    layers = [nn.Flatten()]
    
    # 根据深度添加隐藏层
    if depth == 3:
        layers.extend([
            nn.Linear(784, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        ])
    elif depth == 5:
        layers.extend([
            nn.Linear(784, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        ])
    elif depth == 7:
        layers.extend([
            nn.Linear(784, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        ])
    
    return nn.Sequential(*layers).to(device)

def train_and_evaluate_model(model, train_loader, test_loader, epochs=5):
    optimizer = optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss()
    
    # 记录训练过程中的指标
    train_losses = []
    train_accuracies = []
    test_accuracies = []
    training_times = []
    
    for epoch in range(epochs):
        model.train()
        start_time = time.time()
        running_loss = 0.0
        correct = 0
        total = 0
        
        # 训练阶段
        for data, target in train_loader:
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
        
        # 计算训练时间和准确率
        epoch_time = time.time() - start_time
        training_times.append(epoch_time)
        epoch_loss = running_loss / len(train_loader)
        epoch_accuracy = 100. * correct / total
        train_losses.append(epoch_loss)
        train_accuracies.append(epoch_accuracy)
        
        # 测试阶段
        model.eval()
        test_correct = 0
        test_total = 0
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                _, predicted = output.max(1)
                test_total += target.size(0)
                test_correct += predicted.eq(target).sum().item()
        
        test_accuracy = 100. * test_correct / test_total
        test_accuracies.append(test_accuracy)
        
        print(f'Epoch {epoch+1}: Loss={epoch_loss:.4f}, Train Acc={epoch_accuracy:.2f}%, Test Acc={test_accuracy:.2f}%, Time={epoch_time:.2f}s')
    
    return train_losses, train_accuracies, test_accuracies, training_times


# In[20]:


# 训练不同深度的模型
depths = [3, 5, 7]
results = {}

for depth in depths:
    print(f"\nTraining {depth}-layer network:")
    model = create_model(depth)
    train_losses, train_accs, test_accs, times = train_and_evaluate_model(model, train_loader, test_loader)
    results[depth] = {
        'train_losses': train_losses,
        'train_accuracies': train_accs,
        'test_accuracies': test_accs,
        'training_times': times
    }


# In[21]:


# 绘制对比图表
plt.figure(figsize=(15, 5))

# 训练损失对比
plt.subplot(1, 3, 1)
epochs = range(1, 6)
for depth in depths:
    plt.plot(epochs, results[depth]['train_losses'], label=f'{depth}-layer')
plt.xlabel('Epoch')
plt.ylabel('Training Loss')
plt.title('Training Loss Comparison')
plt.legend()
plt.grid(True)

# 训练准确率对比
plt.subplot(1, 3, 2)
for depth in depths:
    plt.plot(epochs, results[depth]['train_accuracies'], label=f'{depth}-layer')
plt.xlabel('Epoch')
plt.ylabel('Training Accuracy (%)')
plt.title('Training Accuracy Comparison')
plt.legend()
plt.grid(True)

# 测试准确率对比
plt.subplot(1, 3, 3)
for depth in depths:
    plt.plot(epochs, results[depth]['test_accuracies'], label=f'{depth}-layer')
plt.xlabel('Epoch')
plt.ylabel('Test Accuracy (%)')
plt.title('Test Accuracy Comparison')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()


# ## 4、不同的神经元数量(64、128、256、512)

# In[ ]:


# 导入必要的库
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import time

# 设置设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 数据预处理和加载
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# 定义不同神经元数量的网络模型
def create_model(neurons):
    return nn.Sequential(
        nn.Flatten(),
        nn.Linear(784, neurons),
        nn.ReLU(),
        nn.Linear(neurons, 10)
    ).to(device)


# In[23]:


# 训练不同神经元数量的模型
neuron_counts = [64, 128, 256, 512]
results = {}

for neurons in neuron_counts:
    print(f"\nTraining model with {neurons} neurons:")
    model = create_model(neurons)
    train_losses, train_accs, test_accs, times = train_and_evaluate_model(model, train_loader, test_loader)
    results[neurons] = {
        'train_losses': train_losses,
        'train_accuracies': train_accs,
        'test_accuracies': test_accs,
        'training_times': times
    }


# In[24]:


# 绘制对比图表
plt.figure(figsize=(15, 5))

# 训练损失对比
plt.subplot(1, 3, 1)
epochs = range(1, 6)
for neurons in neuron_counts:
    plt.plot(epochs, results[neurons]['train_losses'], label=f'{neurons} neurons')
plt.xlabel('Epoch')
plt.ylabel('Training Loss')
plt.title('Training Loss Comparison')
plt.legend()
plt.grid(True)

# 训练准确率对比
plt.subplot(1, 3, 2)
for neurons in neuron_counts:
    plt.plot(epochs, results[neurons]['train_accuracies'], label=f'{neurons} neurons')
plt.xlabel('Epoch')
plt.ylabel('Training Accuracy (%)')
plt.title('Training Accuracy Comparison')
plt.legend()
plt.grid(True)

# 测试准确率对比
plt.subplot(1, 3, 3)
for neurons in neuron_counts:
    plt.plot(epochs, results[neurons]['test_accuracies'], label=f'{neurons} neurons')
plt.xlabel('Epoch')
plt.ylabel('Test Accuracy (%)')
plt.title('Test Accuracy Comparison')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()


# ## 5、激活函数替换

# In[ ]:


# 导入必要的库
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import time

# 设置设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 数据预处理和加载
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# 定义使用不同激活函数的网络模型
def create_model(activation):
    if activation == 'ReLU':
        act = nn.ReLU()
    elif activation == 'Sigmoid':
        act = nn.Sigmoid()
    elif activation == 'Tanh':
        act = nn.Tanh()
    elif activation == 'LeakyReLU':
        act = nn.LeakyReLU(0.2)
    
    return nn.Sequential(
        nn.Flatten(),
        nn.Linear(784, 128),
        act,
        nn.Linear(128, 10)
    ).to(device)


# In[26]:


# 训练使用不同激活函数的模型
activations = ['ReLU', 'Sigmoid', 'Tanh', 'LeakyReLU']
results = {}

for activation in activations:
    print(f"\nTraining model with {activation} activation:")
    model = create_model(activation)
    train_losses, train_accs, test_accs, times = train_and_evaluate_model(model, train_loader, test_loader)
    results[activation] = {
        'train_losses': train_losses,
        'train_accuracies': train_accs,
        'test_accuracies': test_accs,
        'training_times': times
    }


# In[27]:


# 绘制对比图表
plt.figure(figsize=(15, 5))

# 训练损失对比
plt.subplot(1, 3, 1)
epochs = range(1, 6)
for activation in activations:
    plt.plot(epochs, results[activation]['train_losses'], label=activation)
plt.xlabel('Epoch')
plt.ylabel('Training Loss')
plt.title('Training Loss Comparison')
plt.legend()
plt.grid(True)

# 训练准确率对比
plt.subplot(1, 3, 2)
for activation in activations:
    plt.plot(epochs, results[activation]['train_accuracies'], label=activation)
plt.xlabel('Epoch')
plt.ylabel('Training Accuracy (%)')
plt.title('Training Accuracy Comparison')
plt.legend()
plt.grid(True)

# 测试准确率对比
plt.subplot(1, 3, 3)
for activation in activations:
    plt.plot(epochs, results[activation]['test_accuracies'], label=activation)
plt.xlabel('Epoch')
plt.ylabel('Test Accuracy (%)')
plt.title('Test Accuracy Comparison')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# 绘制最终性能对比
plt.figure(figsize=(12, 5))

# 最终测试准确率对比
plt.subplot(1, 2, 1)
final_accuracies = [results[act]['test_accuracies'][-1] for act in activations]
bars = plt.bar(activations, final_accuracies, color=['blue', 'green', 'red', 'purple'], alpha=0.7)
plt.xlabel('Activation Function')
plt.ylabel('Final Test Accuracy (%)')
plt.title('Final Test Accuracy Comparison')

# 在柱子上方添加具体数值
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}%',
             ha='center', va='bottom')

# 平均训练时间对比
plt.subplot(1, 2, 2)
avg_times = [sum(results[act]['training_times'])/len(results[act]['training_times']) for act in activations]
bars = plt.bar(activations, avg_times, color=['blue', 'green', 'red', 'purple'], alpha=0.7)
plt.xlabel('Activation Function')
plt.ylabel('Average Training Time per Epoch (seconds)')
plt.title('Training Time Comparison')

# 在柱子上方添加具体数值
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}s',
             ha='center', va='bottom')

plt.grid(True, axis='y', alpha=0.3)
plt.tight_layout()
plt.show()


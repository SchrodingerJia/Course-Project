# %% [markdown]
# # 实验要求
# %% [markdown]
# 基于猫狗数据集，构建多层的神经网络结构，实现模型训练与预测，并得出相应结论。要求：
#
# 1、请结合目前所学的神经网络内容，构造三种不同复杂度的神经网络结构；
#
# 2、 结合前面介绍的torchvision库，实现数据集的数据加载与预处理；
#
# 3、实践四种正则化方法，调试超参数，得到最优参数，来减少模型过拟合；
#
# 4、需要调试学习率、批处理、迭代次数等参数，记录调参过程以及绘制损失函数和准确率的变化趋势图。
#
# 具体细节要求：
#
# 1、构造三种不同复杂度的神经网络结构：
# - 简单网络：2-3个隐藏层，每层神经元数不超过128
# - 中等网络：4-5个隐藏层，包含Dropout层
# - 复杂网络：6+个隐藏层，结合多种正则化技术
#
# 2、 数据加载预处理：
# - 使用torchvision完成数据加载和预处理
# - 实现数据增强（至少3种变换）
# - 创建训练集、验证集、测试集
# - 使用DataLoader实现批量加载
#
# 3、实践四种正则化方法：
# - L1/L2正则化、Dropout 、提前停止、数据增强
#
# 4、训练预测、调参绘图：
# - 实现自定义的训练循环
# - 调试学习率、批大小等超参数，记录训练过程中的指标变化
# - 模型保存和加载功能
# - 使用matplotlib或seaborn绘制损失和准确率曲线
# - 在GPU环境上运行（如可用）
#
# 5、实验报告
# - 记录每次实验的超参数设置和结果
# - 分析不同正则化方法的效果
# - 比较三种网络结构的优缺点
# - 总结过拟合问题的解决方案
#
# 数据集结构：
# data-cat-dog
# ├── training_data
# │   ├── cats
# │   │   ├── cat.0.jpg
# │   │   ├── cat.1.jpg
# │   │   └── ...
# │   └── dogs
# │       ├── dog.0.jpg
# │       ├── dog.1.jpg
# │       └── ...
# └── testing_data
#     ├── cats
#     │   ├── cat.1000.jpg
#     │   ├── cat.1001.jpg
#     │   ├── ...
#     │   └── cat.1199.jpg
#     └── dogs
#         ├── dog.1000.jpg
#         ├── dog.1001.jpg
#         ├── ...
#         └── dog.1199.jpg
# %%
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import transforms, datasets
import matplotlib.pyplot as plt
import numpy as np
import os
# %%
# 定义数据预处理和增强
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(15),
    transforms.RandomAffine(0, shear=10, scale=(0.8, 1.2)),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
# %%
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        # 使用自适应池化来处理不同尺寸的输入
        self.adaptive_pool = nn.AdaptiveAvgPool2d((6, 6))
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 6 * 6, 512),
            nn.ReLU(),
            nn.Linear(512, 2)
        )
    def forward(self, x):
        x = self.features(x)
        x = self.adaptive_pool(x)
        x = self.classifier(x)
        return x
class MediumNet(nn.Module):
    def __init__(self):
        super(MediumNet, self).__init__()
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(3, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout(0.25),
            # Block 2
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout(0.25),
            # Block 3
            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(256, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout(0.25)
        )
        # 使用自适应池化
        self.adaptive_pool = nn.AdaptiveAvgPool2d((7, 7))
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 7 * 7, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.5),
            nn.Linear(256, 2)
        )
    def forward(self, x):
        x = self.features(x)
        x = self.adaptive_pool(x)
        x = self.classifier(x)
        return x
class ComplexNet(nn.Module):
    def __init__(self):
        super(ComplexNet, self).__init__()
        # 使用Sequential构建网络
        self.features = nn.Sequential(
            # 初始卷积层
            nn.Conv2d(3, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=False),
            # 残差块1
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=False),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            # 下采样
            nn.Conv2d(64, 128, 3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=False),
            # 残差块2
            nn.Conv2d(128, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=False),
            # 下采样
            nn.Conv2d(128, 256, 3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=False),
            # 残差块3
            nn.Conv2d(256, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=False),
        )
        # 自适应池化
        self.adaptive_pool = nn.AdaptiveAvgPool2d((7, 7))
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 7 * 7, 1024),
            nn.ReLU(inplace=False),
            nn.BatchNorm1d(1024),
            nn.Dropout(0.5),
            nn.Linear(1024, 512),
            nn.ReLU(inplace=False),
            nn.BatchNorm1d(512),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(inplace=False),
            nn.BatchNorm1d(256),
            nn.Dropout(0.3),
            nn.Linear(256, 2)
        )
    def forward(self, x):
        # 保存初始特征用于残差连接
        identity1 = x
        # 第一层卷积
        x = self.features[0:3](x)  # Conv2d + BatchNorm + ReLU
        # 残差块1
        identity2 = x
        x = self.features[3:8](x)  # 两层卷积
        x = x + identity2  # 残差连接
        x = F.relu(x, inplace=False)
        # 继续后续层
        x = self.features[8:](x)
        # 池化和分类
        x = self.adaptive_pool(x)
        x = self.classifier(x)
        return x
# %%
def train_model(model, train_loader, val_loader,
                criterion, optimizer, num_epochs=10, patience=5,
                device='cuda', path = '', use_scheduler=True):
    model.to(device)
    best_acc = 0.0
    train_losses, val_losses = [], []
    train_accs, val_accs = [], []
    patience_counter = 0
    if use_scheduler:
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
    learning_rates = []
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        current_lr = optimizer.param_groups[0]['lr']
        learning_rates.append(current_lr)
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            # L1正则化
            l1_reg = torch.tensor(0.).to(device)
            for param in model.parameters():
                l1_reg += torch.norm(param, 1)
            loss += 0.0001 * l1_reg
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
        train_loss = running_loss / len(train_loader)
        train_acc = 100. * correct / total
        # 验证阶段
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        val_loss = val_loss / len(val_loader)
        val_acc = 100. * correct / total
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
        print(f'Epoch [{epoch+1}/{num_epochs}] Train Loss: {train_loss:.4f} Val Loss: {val_loss:.4f} Train Acc: {train_acc:.2f}% Val Acc: {val_acc:.2f}%')
        # 更新学习率调度器
        if use_scheduler:
            # 对于ReduceLROnPlateau，需要传入验证指标
            if isinstance(scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                scheduler.step(val_acc)  # 传入验证准确率
            else:
                scheduler.step()
        # 保存最佳模型
        if val_acc > best_acc:
            best_acc = val_acc
            patience_counter = 0
            best_model_path = os.path.join(path, 'best_model.pth')
            torch.save(model.state_dict(), best_model_path)
        else:
            patience_counter += 1
        # 提前停止逻辑
        if patience_counter >= patience:
            print(f'Early stopping at epoch {epoch+1}')
            break
    return train_losses, val_losses, train_accs, val_accs, learning_rates
# %%
def experiment(model, learning_rate, batch_size, patience, epoch, use_scheduler=True, path=''):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print("Training with gpu" if torch.cuda.is_available() else "Training with cpu")
    print("Loading dataset...")
    # 加载数据集
    train_path = os.path.join(path, 'data-cat-dog', 'training_data')
    test_path = os.path.join(path, 'data-cat-dog', 'testing_data')
    train_dataset = datasets.ImageFolder(train_path, transform=train_transform)
    test_dataset = datasets.ImageFolder(test_path, transform=test_transform)
    # 划分训练集和验证集
    train_size = int(0.8 * len(train_dataset))
    val_size = len(train_dataset) - train_size
    train_dataset, val_dataset = random_split(train_dataset, [train_size, val_size])
    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    print("Dataset prepared.")
    # 选择模型
    if model == 'SimpleNet':
        model = SimpleNet()
    elif model == 'MediumNet':
        model = MediumNet()
    elif model == 'ComplexNet':
        model = ComplexNet()
    else:
        raise ValueError('Invalid model name')
    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)  # L2正则化
    print("Training model...")
    # 训练模型
    train_losses, val_losses, train_accs, val_accs, learning_rates = train_model(
        model, train_loader, val_loader, criterion, optimizer, num_epochs=epoch,
        patience=patience, device=device, use_scheduler=use_scheduler, path=path)
    print("Model trained.")
    # 绘制训练过程
    plt.figure(figsize=(15, 5))
    # 子图1: 损失函数
    plt.subplot(1, 3, 1)
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Val Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    # 子图2: 准确率
    plt.subplot(1, 3, 2)
    plt.plot(train_accs, label='Train Acc')
    plt.plot(val_accs, label='Val Acc')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    # 子图3: 学习率变化
    plt.subplot(1, 3, 3)
    plt.plot(learning_rates, label='Learning Rate', color='red')
    plt.title('Learning Rate Schedule')
    plt.xlabel('Epoch')
    plt.ylabel('Learning Rate')
    plt.legend()
    plt.tight_layout()
    plt.show()
    # 测试模型
    best_model_path = os.path.join(path, 'best_model.pth')
    model.load_state_dict(torch.load(best_model_path))
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    print(f'Test Accuracy: {100. * correct / total:.2f}%')
    return {
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_accs': train_accs,
        'val_accs': val_accs,
        'learning_rates': learning_rates,
        'test_accuracy': 100. * correct / total
    }
# %% [markdown]
# ## 实验
# %%
path = "lab2"
# %%
experiment('SimpleNet', 0.001, 32, 10, 20, use_scheduler=True, path=path)
# %%
experiment('MediumNet', 0.0005, 32, 10, 30, use_scheduler=True, path=path)
# %%
experiment('ComplexNet', 0.0001, 32, 10, 40, use_scheduler=True, path=path)
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import transforms, datasets
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import time
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
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
class SimpleNet(nn.Module):
    def __init__(self, hidden_size = 256, dropout_rate = 0.5, activation = 'ReLU'):
        super(SimpleNet, self).__init__()
        self.features = nn.Sequential(
            nn.Flatten(),
            nn.Linear(224 * 224 * 3, hidden_size),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(inplace=False) if activation == 'ReLU' else nn.Sigmoid(inplace=False),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size, 2)
        )
    def forward(self, x):
        x = self.features(x)
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
        x = self.features[0:3](x)
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
def train_model(model, train_loader, val_loader,
                criterion, optimizer, num_epochs=10, patience=5,
                device='cuda', path='', use_scheduler=True):
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
def experiment(model_name, learning_rate, batch_size, patience, optimizer_name, epoch, use_scheduler=True, path=''):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print("Training with gpu" if torch.cuda.is_available() else "Training with cpu")
    print("Loading dataset...")
    # 加载数据集
    train_path = os.path.join(path, 'training_data')
    test_path = os.path.join(path, 'testing_data')
    train_dataset = datasets.ImageFolder(train_path, transform=train_transform)
    test_dataset = datasets.ImageFolder(test_path, transform=test_transform)
    # 划分训练集和验证集
    train_size = int(0.8 * len(train_dataset))
    val_size = len(train_dataset) - train_size
    train_dataset, val_dataset = random_split(train_dataset, [train_size, val_size])
    # 创建数据加载器
    num_workers = min(4, os.cpu_count())
    train_loader = DataLoader(train_dataset,
                              batch_size=batch_size,
                              shuffle=True,
                              num_workers=num_workers,
                              pin_memory=True,  # 加速GPU传输
                              persistent_workers=True if num_workers > 0 else False,  # 保持工作进程
                              prefetch_factor=2 if num_workers > 0 else None  # 预取数据
                             )
    val_loader = DataLoader(val_dataset,
                            batch_size=batch_size,
                            shuffle=True,
                            num_workers=num_workers,
                            pin_memory=True,  # 加速GPU传输
                            persistent_workers=True if num_workers > 0 else False,  # 保持工作进程
                            prefetch_factor=2 if num_workers > 0 else None  # 预取数据
                            )
    test_loader = DataLoader(test_dataset,
                             batch_size=batch_size,
                             shuffle=True,
                             num_workers=num_workers,
                             pin_memory=True,  # 加速GPU传输
                             persistent_workers=True if num_workers > 0 else False,  # 保持工作进程
                             prefetch_factor=2 if num_workers > 0 else None  # 预取数据
                            )
    print("Dataset prepared.")
    # 选择模型
    if model_name == 'ComplexNet':
        model = ComplexNet()
    else:
        model = SimpleNet()
    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    if optimizer_name == 'Adam':
        optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    elif optimizer_name == 'SGD':
        optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9, weight_decay=1e-4)
    elif optimizer_name == 'RMSProp':
        optimizer = optim.RMSprop(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    else:
        raise ValueError('Invalid optimizer name')
    print("Training model...")
    start_time = time.time()
    # 训练模型
    train_losses, val_losses, train_accs, val_accs, learning_rates = train_model(
        model, train_loader, val_loader, criterion, optimizer, num_epochs=epoch,
        patience=patience, device=device, use_scheduler=use_scheduler, path=path)
    training_time = time.time() - start_time
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
    plt.savefig(f'training_process_{optimizer_name}_{learning_rate}.png')
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
    print(f'Training Time: {training_time:.2f} seconds')
    return {
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_accs': train_accs,
        'val_accs': val_accs,
        'learning_rates': learning_rates,
        'test_accuracy': 100. * correct / total,
        'training_time': training_time
    }
def task1_optimizer_comparison(path):
    """
    任务一：基础优化器对比实验
    使用三种优化器，每种尝试3个学习率，记录训练曲线和训练时间
    """
    optimizers = ['Adam', 'SGD', 'RMSProp']
    learning_rates = [0.0005, 0.0001, 0.00002]
    results = {}
    for opt_name in optimizers:
        print(f"\n=== Testing Optimizer: {opt_name} ===")
        opt_results = {}
        for lr in learning_rates:
            print(f"\n--- Learning Rate: {lr} ---")
            # 训练模型
            history = experiment(
                model_name='S',
                learning_rate=lr,
                batch_size=128,
                epoch=24,
                patience=8,
                optimizer_name=opt_name,
                use_scheduler=True,
                path=path
            )
            # 保存结果
            opt_results[lr] = {
                'history': history,
                'final_train_acc': history['train_accs'][-1],
                'final_val_acc': history['val_accs'][-1],
                'training_time': history['training_time']
            }
        results[opt_name] = opt_results
    # 可视化对比结果
    plt.figure(figsize=(20, 15))
    # 准确率对比
    plt.subplot(2, 2, 1)
    for opt_name, opt_results in results.items():
        for lr, data in opt_results.items():
            plt.plot(data['history']['val_accs'],
                    label=f"{opt_name} (lr={lr})")
    plt.title('Validation Accuracy Comparison')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    # Loss对比
    plt.subplot(2, 2, 2)
    for opt_name, opt_results in results.items():
        for lr, data in opt_results.items():
            plt.plot(data['history']['val_losses'],
                    label=f"{opt_name} (lr={lr})")
    plt.title('Validation Loss Comparison')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    # 训练时间对比
    plt.subplot(2, 2, 3)
    training_times = []
    labels = []
    for opt_name, opt_results in results.items():
        for lr, data in opt_results.items():
            training_times.append(data['training_time'])
            labels.append(f"{opt_name}\nlr={lr}")
    plt.bar(labels, training_times)
    plt.title('Training Time Comparison')
    plt.ylabel('Time (seconds)')
    plt.xticks(rotation=45)
    # 最终准确率对比
    plt.subplot(2, 2, 4)
    final_accs = []
    for opt_name, opt_results in results.items():
        for lr, data in opt_results.items():
            final_accs.append(data['final_val_acc'])
    plt.bar(labels, final_accs)
    plt.title('Final Validation Accuracy')
    plt.ylabel('Accuracy')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('optimizer_comparison.png')
    plt.show()
    # 分析结果
    print("\n=== 优化器性能分析 ===")
    # 收敛速度分析
    print("\n1. 收敛速度分析：")
    for opt_name, opt_results in results.items():
        for lr, data in opt_results.items():
            val_accs = data['history']['val_accs']
            convergence_epoch = next((i for i, acc in enumerate(val_accs)
                                    if acc >= 0.8), len(val_accs))
            print(f"{opt_name} (lr={lr}): 收敛到80%准确率需要 {convergence_epoch} 个epoch")
    # 稳定性分析
    print("\n2. 稳定性分析：")
    for opt_name, opt_results in results.items():
        for lr, data in opt_results.items():
            val_accs = data['history']['val_accs']
            std_dev = np.std(val_accs[-5:])  # 最后5个epoch的标准差
            print(f"{opt_name} (lr={lr}): 最后5个epoch准确率标准差 = {std_dev:.4f}")
    # 训练时间分析
    print("\n3. 训练时间分析：")
    for opt_name, opt_results in results.items():
        avg_time = np.mean([data['training_time'] for data in opt_results.values()])
        print(f"{opt_name}: 平均训练时间 = {avg_time:.2f} 秒")
    return results
if __name__ == "__main__":
    print("=== 任务一：基础优化器对比实验 ===")
    print("=== 任务一：基础优化器对比实验 ===")
    lp = './limited_dataset'
    fp = './data-cat-dog'
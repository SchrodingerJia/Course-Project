import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, Subset
from torchvision import transforms, datasets
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import time
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
from PIL import Image
import pandas as pd
# 启用CUDA基准模式，加速卷积运算
torch.backends.cudnn.benchmark = True
# 启用TF32（在Ampere架构及以上的GPU上）
torch.backends.cuda.matmul.fp32_precision = 'tf32'
torch.backends.cudnn.conv.fp32_precision = 'tf32'
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
    num_workers = min(16, os.cpu_count())
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
    test_accuracy = 100. * correct / total
    print(f'Test Accuracy: {test_accuracy:.2f}%')
    print(f'Training Time: {training_time:.2f} seconds')
    return {
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_accs': train_accs,
        'val_accs': val_accs,
        'learning_rates': learning_rates,
        'test_accuracy': test_accuracy,
        'training_time': training_time,
        'model': model,
        'test_loader': test_loader,
        'test_dataset': test_dataset
    }
def task3_model_visualization_and_error_analysis(path):
    """
    任务三：模型可视化与错误分析
    基于任务一得到的最优模型（Adam+lr=0.0001）
    """
    # 使用最优参数训练模型
    result = experiment(
        model_name='ComplexNet',
        learning_rate=0.0001,
        batch_size=256,
        epoch=30,
        patience=10,
        optimizer_name='Adam',
        use_scheduler=True,
        path=path
    )
    model = result['model']
    test_loader = result['test_loader']
    test_dataset = result['test_dataset']
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # 1. 随机选择5张测试集图片，显示原图+预测结果
    print("\n1. 随机选择5张测试集图片，显示原图+预测结果")
    visualize_predictions(model, test_dataset, device, num_samples=5)
    # 2. 绘制混淆矩阵
    print("\n2. 绘制混淆矩阵")
    plot_confusion_matrix(model, test_loader, device, test_dataset.classes)
    wrong_samples(model, test_dataset, device, num_samples=10)
    # 3. 找出最难分类的图片（预测概率接近0.5的样本）
    print("\n3. 找出最难分类的图片")
    find_hard_samples(model, test_dataset, device, num_samples=10)
    return result
def visualize_predictions(model, test_dataset, device, num_samples=5):
    """随机选择测试集图片并显示预测结果"""
    # 随机选择样本索引
    indices = random.sample(range(len(test_dataset)), num_samples)
    # 创建子图
    fig, axes = plt.subplots(1, num_samples, figsize=(15, 3))
    if num_samples == 1:
        axes = [axes]
    model.eval()
    class_names = test_dataset.classes
    for i, idx in enumerate(indices):
        # 获取图像和标签
        image, true_label = test_dataset[idx]
        # 预测
        with torch.no_grad():
            input_tensor = image.unsqueeze(0).to(device)
            output = model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            predicted_prob, predicted_label = torch.max(probabilities, 1)
        # 转换图像为可显示格式
        image_np = image.numpy().transpose((1, 2, 0))
        # 反标准化
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image_np = std * image_np + mean
        image_np = np.clip(image_np, 0, 1)
        # 显示图像
        axes[i].imshow(image_np)
        axes[i].axis('off')
        # 获取类别名称
        true_class = class_names[true_label]
        predicted_class = class_names[predicted_label.item()]
        # 设置标题
        color = 'green' if true_label == predicted_label.item() else 'red'
        axes[i].set_title(f'True: {true_class}\nPred: {predicted_class}\nProb: {predicted_prob.item():.3f}',
                         color=color, fontsize=10)
    plt.tight_layout()
    plt.savefig('random_predictions.png', dpi=300, bbox_inches='tight')
def plot_confusion_matrix(model, test_loader, device, class_names):
    """绘制混淆矩阵"""
    model.eval()
    all_predictions = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    # 计算混淆矩阵
    cm = confusion_matrix(all_labels, all_predictions)
    # 绘制混淆矩阵
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
    # 打印分类报告
    print("\nClassification Report:")
    print(classification_report(all_labels, all_predictions, target_names=class_names))
def find_hard_samples(model, test_dataset, device, num_samples=10):
    """找出预测概率接近0.5的样本（最难分类的样本）"""
    model.eval()
    all_probabilities = []
    all_indices = []
    all_predictions = []
    all_labels = []
    # 收集所有样本的预测概率
    with torch.no_grad():
        for idx in range(len(test_dataset)):
            image, true_label = test_dataset[idx]
            input_tensor = image.unsqueeze(0).to(device)
            output = model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            # 获取最大概率和对应的预测标签
            max_prob, predicted_label = torch.max(probabilities, 1)
            all_probabilities.append(max_prob.item())
            all_indices.append(idx)
            all_predictions.append(predicted_label.item())
            all_labels.append(true_label)
    # 创建DataFrame以便分析
    df = pd.DataFrame({
        'index': all_indices,
        'true_label': all_labels,
        'predicted_label': all_predictions,
        'confidence': all_probabilities,
        'difficulty': [abs(0.5 - prob) for prob in all_probabilities]  # 离0.5越近越难
    })
    # 按难度排序（最难的排前面）
    df_sorted = df.sort_values('difficulty').head(num_samples)
    print(f"\nTop {num_samples} 最难分类的样本（预测概率最接近0.5）:")
    print(df_sorted[['index', 'true_label', 'predicted_label', 'confidence', 'difficulty']])
    # 可视化最难分类的样本
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.ravel()
    class_names = test_dataset.classes
    for i, (_, row) in enumerate(df_sorted.iterrows()):
        if i >= 10:  # 只显示前10个
            break
        idx = int(row['index'])
        image, true_label = test_dataset[idx]
        # 转换图像为可显示格式
        image_np = image.numpy().transpose((1, 2, 0))
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image_np = std * image_np + mean
        image_np = np.clip(image_np, 0, 1)
        # 显示图像
        axes[i].imshow(image_np)
        axes[i].axis('off')
        true_class = class_names[true_label]
        predicted_class = class_names[int(row['predicted_label'])]
        confidence = row['confidence']
        color = 'green' if true_label == row['predicted_label'] else 'red'
        axes[i].set_title(f'True: {true_class}\nPred: {predicted_class}\nConf: {confidence:.3f}',
                         color=color, fontsize=9)
    plt.tight_layout()
    plt.savefig('hard_samples.png', dpi=300, bbox_inches='tight')
    # 分析错误原因
    print("\n最难分类样本的错误分析:")
    wrong_predictions = df_sorted[df_sorted['true_label'] != df_sorted['predicted_label']]
    if len(wrong_predictions) > 0:
        print(f"共有 {len(wrong_predictions)} 个最难分类的样本被错误预测")
    else:
        print("所有最难分类的样本都被正确预测")
    return df_sorted
def wrong_samples(model, test_dataset, device, num_samples=10):
    """找出预测错误的样本"""
    model.eval()
    all_probabilities = []
    all_indices = []
    all_predictions = []
    all_labels = []
    # 收集所有样本的预测概率
    with torch.no_grad():
        for idx in range(len(test_dataset)):
            image, true_label = test_dataset[idx]
            input_tensor = image.unsqueeze(0).to(device)
            output = model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            # 获取最大概率和对应的预测标签
            max_prob, predicted_label = torch.max(probabilities, 1)
            all_probabilities.append(max_prob.item())
            all_indices.append(idx)
            all_predictions.append(predicted_label.item())
            all_labels.append(true_label)
    # 创建DataFrame以便分析
    df = pd.DataFrame({
        'index': all_indices,
        'true_label': all_labels,
        'predicted_label': all_predictions,
        'confidence': all_probabilities,
    })
    # 筛选预测错误的样本
    df_wrong = df[df['true_label'] != df['predicted_label']]
    # 按错误排序（最错的排前面）
    df_sorted = df_wrong.sort_values('confidence', ascending=False).head(num_samples)
    # 可视化错误的样本
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.ravel()
    class_names = test_dataset.classes
    for i, (_, row) in enumerate(df_sorted.iterrows()):
        if i >= 10:  # 只显示前10个
            break
        idx = int(row['index'])
        image, true_label = test_dataset[idx]
        # 转换图像为可显示格式
        image_np = image.numpy().transpose((1, 2, 0))
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image_np = std * image_np + mean
        image_np = np.clip(image_np, 0, 1)
        # 显示图像
        axes[i].imshow(image_np)
        axes[i].axis('off')
        true_class = class_names[true_label]
        predicted_class = class_names[int(row['predicted_label'])]
        confidence = row['confidence']
        color = 'green' if true_label == row['predicted_label'] else 'red'
        axes[i].set_title(f'True: {true_class}\nPred: {predicted_class}\nConf: {confidence:.3f}',
                         color=color, fontsize=9)
    plt.tight_layout()
    plt.savefig('wrong_samples.png', dpi=300, bbox_inches='tight')
if __name__ == "__main__":
    print("=== 任务三：模型可视化与错误分析 ===")
    fp = './data-cat-dog'
    task3_result = task3_model_visualization_and_error_analysis(path=fp)
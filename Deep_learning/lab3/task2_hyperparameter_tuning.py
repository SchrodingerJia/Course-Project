import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torch.amp import autocast, GradScaler
from torchvision import transforms, datasets
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import time
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

plt.rcParams['font.sans-serif'] = ['SimHei'] # 使用黑体
plt.rcParams['axes.unicode_minus'] = False # 正常显示负号

# 启用CUDA基准模式，加速卷积运算
torch.backends.cudnn.benchmark = True
# 启用TF32（在Ampere架构及以上的GPU上）
torch.backends.cuda.matmul.fp32_precision = 'tf32'
torch.backends.cudnn.conv.fp32_precision = 'tf32'

def get_device(gpu_id=1):
    """
    获取指定GPU的设备
    Args:
        gpu_id: GPU ID，默认为1
    Returns:
        torch.device: 指定的设备
    """
    if torch.cuda.is_available():
        device = torch.device(f'cuda:{gpu_id}')
        print(f"Using GPU: {torch.cuda.get_device_name(gpu_id)}")
        # 设置当前GPU
        torch.cuda.set_device(gpu_id)
    else:
        device = torch.device('cpu')
        print("Using CPU")
    return device

# 定义数据预处理和增强 - 优化版本
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(15),
    # 减少数据增强复杂度以提高速度
    transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.05),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def create_dataloaders(train_dataset, val_dataset, test_dataset, batch_size):
    # 设置multiprocessing的启动方法为spawn
    torch.multiprocessing.set_start_method('spawn', force=True)
    
    # 根据CPU核心数动态调整num_workers
    num_workers = min(8, os.cpu_count() // 2)  # 使用一半CPU核心
    
    train_loader = DataLoader(train_dataset, 
                              batch_size=batch_size, 
                              shuffle=True, 
                              num_workers=num_workers,
                              pin_memory=True,
                              persistent_workers=True if num_workers > 0 else False,
                              prefetch_factor=2 if num_workers > 0 else None,
                              drop_last=True)  # 丢弃不完整的batch
    
    val_loader = DataLoader(val_dataset, 
                            batch_size=batch_size, 
                            shuffle=False, 
                            num_workers=num_workers,
                            pin_memory=True,
                            persistent_workers=True if num_workers > 0 else False,
                            prefetch_factor=2 if num_workers > 0 else None)
    
    test_loader = DataLoader(test_dataset, 
                             batch_size=batch_size, 
                             shuffle=False, 
                             num_workers=num_workers,
                             pin_memory=True,
                             persistent_workers=True if num_workers > 0 else False,
                             prefetch_factor=2 if num_workers > 0 else None)
    
    print(f"数据加载器配置: num_workers={num_workers}, batch_size={batch_size}")
    return train_loader, val_loader, test_loader

# 优化模型结构 - 使用卷积网络提高GPU利用率
class OptimizedNet(nn.Module):
    def __init__(self, hidden_size=512, dropout_rate=0.5, activation='ReLU'):
        super(OptimizedNet, self).__init__()
        
        self.conv_layers = nn.Sequential(
            # 第一层卷积 - 增加通道数
            nn.Conv2d(3, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True) if activation == 'ReLU' else nn.Sigmoid(),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True) if activation == 'ReLU' else nn.Sigmoid(),
            nn.MaxPool2d(2),
            
            # 第二层卷积 - 增加通道数
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True) if activation == 'ReLU' else nn.Sigmoid(),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True) if activation == 'ReLU' else nn.Sigmoid(),
            nn.MaxPool2d(2),
            
            # 第三层卷积 - 增加通道数
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True) if activation == 'ReLU' else nn.Sigmoid(),
            nn.Conv2d(512, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True) if activation == 'ReLU' else nn.Sigmoid(),
            nn.MaxPool2d(2),
            
            # 第四层卷积
            nn.Conv2d(512, 1024, kernel_size=3, padding=1),
            nn.BatchNorm2d(1024),
            nn.ReLU(inplace=True) if activation == 'ReLU' else nn.Sigmoid(),
            nn.AdaptiveAvgPool2d((7, 7))
        )
        
        # 增加分类器复杂度
        self.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(1024 * 7 * 7, hidden_size),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(inplace=True) if activation == 'ReLU' else nn.Sigmoid(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.BatchNorm1d(hidden_size // 2),
            nn.ReLU(inplace=True) if activation == 'ReLU' else nn.Sigmoid(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size // 2, 2)
        )
    
    def forward(self, x):
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

# 保留原来的SimpleNet用于兼容性
class SimpleNet(nn.Module):
    def __init__(self, hidden_size=256, dropout_rate=0.5, activation='ReLU'):
        super(SimpleNet, self).__init__()
        
        self.features = nn.Sequential(
            nn.Flatten(),
            nn.Linear(224 * 224 * 3, hidden_size),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(inplace=True) if activation == 'ReLU' else nn.Sigmoid(),  # 使用inplace节省内存
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size, 2)
        )
    
    def forward(self, x):
        x = self.features(x)
        return x

# 优化的训练函数
def train_model(model, train_loader, val_loader, 
                criterion, optimizer, num_epochs=24, patience=10, 
                gpu_id=1, path='', use_scheduler=True, accumulation_steps=4):
    device = get_device(gpu_id)
    model.to(device)
    
    # 使用更大的初始缩放因子
    scaler = GradScaler(device, init_scale=2.**12)
    
    best_acc = 0.0
    train_losses, val_losses = [], []
    train_accs, val_accs = [], []
    patience_counter = 0

    # 使用OneCycleLR调度器获得更快收敛
    if use_scheduler:
        scheduler = optim.lr_scheduler.OneCycleLR(
            optimizer, 
            max_lr=optimizer.param_groups[0]['lr'] * 10,  # 更高的最大学习率
            epochs=num_epochs, 
            steps_per_epoch=len(train_loader),
            pct_start=0.3  # 更长的学习率上升阶段
        )

    learning_rates = []
    
    # 预热阶段
    print("开始训练预热...")
    model.train()
    for i, (inputs, labels) in enumerate(train_loader):
        if i >= I:
            break
        inputs, labels = inputs.to(device, non_blocking=True), labels.to(device, non_blocking=True)
        
        with autocast('cuda'):
            outputs = model(inputs)
            loss = criterion(outputs, labels) / accumulation_steps
        
        scaler.scale(loss).backward()
    
    optimizer.zero_grad()
    print("预热完成")
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        current_lr = optimizer.param_groups[0]['lr']
        learning_rates.append(current_lr)

        # 训练阶段
        batch_start_time = time.time()
        for i, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device, non_blocking=True), labels.to(device, non_blocking=True)
            
            with autocast('cuda'):
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                # 只有在需要时才计算L1正则化
                if epoch > 2:  # 前几个epoch不应用L1
                    l1_reg = torch.tensor(0.).to(device)
                    for param in model.parameters():
                        l1_reg += torch.norm(param, 1)
                    loss += 0.0001 * l1_reg
                
                loss = loss / accumulation_steps
            
            scaler.scale(loss).backward()
            
            if (i + 1) % accumulation_steps == 0:
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
            
            running_loss += loss.item() * accumulation_steps
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            # 每50个batch打印一次进度
            if (i + 1) % 50 == 0:
                batch_time = time.time() - batch_start_time
                print(f'Epoch [{epoch+1}], Batch [{i+1}/{len(train_loader)}], '
                      f'Time: {batch_time:.2f}s, Loss: {loss.item()*accumulation_steps:.4f}')
                batch_start_time = time.time()
        
        train_loss = running_loss / len(train_loader)
        train_acc = 100. * correct / total
        
        # 验证阶段 - 使用混合精度加速
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device, non_blocking=True), labels.to(device, non_blocking=True)
                
                with autocast('cuda'):
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
        
        print(f'Epoch [{epoch+1}/{num_epochs}] '
              f'Train Loss: {train_loss:.4f} Val Loss: {val_loss:.4f} '
              f'Train Acc: {train_acc:.2f}% Val Acc: {val_acc:.2f}% '
              f'LR: {current_lr:.6f}')
        
        # 更新学习率调度器
        if use_scheduler:
            scheduler.step()

        # 保存最佳模型
        if val_acc > best_acc:
            best_acc = val_acc
            patience_counter = 0
            best_model_path = os.path.join(path, '2_best_model-.pth') 
            torch.save(model.state_dict(), best_model_path)
        else:
            patience_counter += 1

        # 提前停止逻辑
        if patience_counter >= patience:
            print(f'Early stopping at epoch {epoch+1}')
            break
    
    return train_losses, val_losses, train_accs, val_accs, learning_rates

def process_fold(fold_data):
    """
    处理单个fold - 优化版本
    """
    # 获取数据和参数
    train_subset = fold_data['train_subset']
    val_subset = fold_data['val_subset']
    gpu_id = fold_data['gpu_id']
    param_grid = fold_data['param_grid']
    
    # 使用优化的数据加载器配置
    num_workers = min(4, os.cpu_count() // 4)  # 减少workers避免内存问题
    
    train_loader = DataLoader(train_subset, 
                             batch_size=param_grid['batch_size'], 
                             shuffle=True, 
                             num_workers=num_workers,
                             pin_memory=True,
                             persistent_workers=True if num_workers > 0 else False)
    
    val_loader = DataLoader(val_subset, 
                           batch_size=param_grid['batch_size'], 
                           shuffle=False, 
                           num_workers=num_workers,
                           pin_memory=True,
                           persistent_workers=True if num_workers > 0 else False)
    
    # 创建模型 - 使用优化版本
    model = OptimizedNet(
        hidden_size=param_grid['hidden_size'],
        dropout_rate=param_grid['dropout_rate'],
        activation=param_grid['activation']
    )
    
    # 使用单个GPU
    device = torch.device(f'cuda:{gpu_id}' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    # 定义优化器 - 添加权重衰减
    if param_grid['optimizer'] == 'Adam':
        optimizer = optim.Adam(model.parameters(), lr=param_grid['lr'], weight_decay=1e-4)
    elif param_grid['optimizer'] == 'SGD':
        optimizer = optim.SGD(model.parameters(), lr=param_grid['lr'], momentum=0.9, weight_decay=1e-4)
    elif param_grid['optimizer'] == 'RMSProp':
        optimizer = optim.RMSprop(model.parameters(), lr=param_grid['lr'], weight_decay=1e-4)
    
    criterion = nn.CrossEntropyLoss()
    
    # 训练模型
    _, _, _, val_accs, _ = train_model(
        model, train_loader, val_loader, criterion, optimizer,
        num_epochs=num_epochs,
        patience=patience,
        gpu_id=gpu_id,
        accumulation_steps=4
    )
    
    return max(val_accs)

def k_fold_cross_validation(model_class, param_grid, k=5, num_epochs=24, path='', gpu_id=1):
    """
    K折交叉验证 - 优化版本
    """
    dataset = datasets.ImageFolder(os.path.join(path, 'training_data'), 
                                 transform=train_transform)
    
    # 计算每折的大小
    fold_size = len(dataset) // k
    indices = list(range(len(dataset)))
    random.shuffle(indices)
    
    # 准备所有fold的数据
    fold_data_list = []
    for fold in range(k):
        val_indices = indices[fold*fold_size : (fold+1)*fold_size]
        train_indices = indices[:fold*fold_size] + indices[(fold+1)*fold_size:]
        
        train_subset = torch.utils.data.Subset(dataset, train_indices)
        val_subset = torch.utils.data.Subset(dataset, val_indices)
        
        # 轮询使用GPU
        if isinstance(gpu_id, list):
            current_gpu = gpu_id[fold % len(gpu_id)]
        else:
            current_gpu = gpu_id
        
        fold_data_list.append({
            'train_subset': train_subset,
            'val_subset': val_subset,
            'gpu_id': current_gpu,
            'param_grid': param_grid
        })
    
    # 使用线程池处理所有fold - 限制最大workers
    max_workers = min(2, len(fold_data_list))  # 减少并发数量
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        fold_results = list(executor.map(process_fold, fold_data_list))
    
    return np.mean(fold_results), np.std(fold_results)

def evaluate_combination(args):
    """
    评估单个参数组合 - 优化版本
    """
    combination, param_names, param_grid, k, path, gpu_id = args
    params = dict(zip(param_names, combination))
    print(f"\n测试参数组合: {params}")
    
    try:
        # 执行K折交叉验证
        mean_acc, std_acc = k_fold_cross_validation(
            OptimizedNet,  # 使用优化模型
            params,
            k=k,
            path=path,
            num_epochs=num_epochs,
            gpu_id=gpu_id
        )
        
        # 保存结果
        result = {
            'params': params,
            'mean_accuracy': mean_acc,
            'std_accuracy': std_acc
        }
        
        print(f"平均准确率: {mean_acc:.2f}%, 标准差: {std_acc:.2f}%")
        return result
    except Exception as e:
        print(f"参数组合 {params} 训练失败: {e}")
        return {
            'params': params,
            'mean_accuracy': 0.0,
            'std_accuracy': 0.0
        }

def grid_search(param_grid, k=5, path='', gpu_id=1):
    """
    网格搜索超参数 - 优化版本
    """
    best_params = None
    best_score = 0
    results = []
    
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    
    from itertools import product
    
    # 生成所有参数组合
    all_combinations = list(product(*param_values))
    print(f"总参数组合数: {len(all_combinations)}")
    
    # 分批处理，避免内存爆炸
    batch_size = 2  # 减少并发数量
    for i in range(0, len(all_combinations), batch_size):
        batch_combinations = all_combinations[i:i+batch_size]
        
        # 使用线程池并行评估当前批次的参数组合
        with ThreadPoolExecutor(max_workers=min(2, len(batch_combinations))) as executor:
            batch_results = list(executor.map(
                evaluate_combination,
                [(comb, param_names, param_grid, k, path, gpu_id) 
                 for comb in batch_combinations]
            ))
        
        results.extend(batch_results)
        
        # 更新最佳参数
        for result in batch_results:
            if result['mean_accuracy'] > best_score:
                best_score = result['mean_accuracy']
                best_params = result['params']
        
        print(f"已完成批次 {i//batch_size + 1}/{(len(all_combinations)-1)//batch_size + 1}")
    
    return best_params, results

def analyze_parameters(results):
    """
    分析参数对性能的影响
    Args:
        results: 网格搜索的结果
    """
    # 创建DataFrame用于分析
    import pandas as pd
    df = pd.DataFrame([r['params'] for r in results])
    df['accuracy'] = [r['mean_accuracy'] for r in results]
    
    # 分析每个参数的影响
    plt.figure(figsize=(20, 15))
    
    for i, param in enumerate(df.columns[:-1], 1):
        plt.subplot(2, 3, i)
        param_values = df[param].unique()
        for value in param_values:
            accs = df[df[param] == value]['accuracy']
            plt.bar(str(value), accs.mean(), yerr=accs.std(), label=f'{value}')
        plt.title(f'Parameter {param} Impact on Performance')
        plt.ylabel('Accuracy (%)')
        plt.legend()
    
    plt.tight_layout()
    plt.savefig('parameter_impact-.png')
    plt.show()
    
    # 只对数值型参数计算相关性
    numeric_df = df.copy()
    
    # 将分类变量转换为数值编码
    if 'optimizer' in numeric_df.columns:
        optimizer_map = {'Adam': 0, 'SGD': 1, 'RMSProp': 2}
        numeric_df['optimizer'] = numeric_df['optimizer'].map(optimizer_map)
    
    if 'activation' in numeric_df.columns:
        activation_map = {'ReLU': 0, 'sigmoid': 1}
        numeric_df['activation'] = numeric_df['activation'].map(activation_map)
    
    # 只选择数值型列计算相关性
    numeric_columns = numeric_df.select_dtypes(include=[np.number]).columns
    correlation_matrix = numeric_df[numeric_columns].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Parameter Correlation Matrix (Numeric Parameters Only)')
    plt.savefig('parameter_correlation-.png')
    plt.show()
    
    # 打印参数重要性分析
    print("\n=== 参数重要性分析 ===")
    param_importance = {}
    
    for param in df.columns[:-1]:  # 排除accuracy列
        if param in ['optimizer', 'activation']:
            # 对于分类变量，使用分组均值差异作为重要性指标
            grouped = df.groupby(param)['accuracy'].mean()
            importance = grouped.max() - grouped.min()
        else:
            # 对于数值变量，使用相关系数作为重要性指标
            correlation = abs(numeric_df[param].corr(numeric_df['accuracy']))
            importance = correlation
        
        param_importance[param] = importance
    
    # 按重要性排序
    sorted_importance = sorted(param_importance.items(), key=lambda x: x[1], reverse=True)
    
    print("参数重要性排序:")
    for param, importance in sorted_importance:
        print(f"  {param}: {importance:.4f}")

def task2_optimizer_comparison(path, gpu_id=[0,1]):
    """
    任务二：系统化的超参数调优 - 支持多GPU
    Args:
        path: 数据集路径
        gpu_id: GPU ID列表
    """
    print("任务二：系统化的超参数调优")
    print("="*50)
    
    # 设置multiprocessing的启动方法为spawn
    torch.multiprocessing.set_start_method('spawn', force=True)
    
    # 定义参数网格 (保持不变)
    param_grid = {
        'optimizer': ['Adam', 'SGD', 'RMSProp'],
        'lr': [0.001, 0.01, 0.1],
        'batch_size': [32, 64],
        'hidden_size': [128, 256],
        'dropout_rate': [0.5, 0.7],
        'activation': ['ReLU', 'sigmoid']
    }
    
    # 执行网格搜索
    best_params, results = grid_search(param_grid, k=k, path=path, gpu_id=gpu_id)  # 减少k值
    
    # 分析参数影响
    analyze_parameters(results)
    
    print("\n=== 最佳参数组合 ===")
    print(f"Best parameters: {best_params}")
    print(f"Best validation accuracy: {max(r['mean_accuracy'] for r in results):.2f}%")
    
    # 在测试集上验证最佳模型
    print("\n=== 训练最佳模型 ===")
    model = OptimizedNet(
        hidden_size=best_params['hidden_size'],
        dropout_rate=best_params['dropout_rate'],
        activation=best_params['activation']
    )
    
    # 使用单个GPU
    device = torch.device(f'cuda:{gpu_id[0]}' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    # 加载测试集
    train_dataset = datasets.ImageFolder(os.path.join(path, 'training_data'), 
                                      transform=test_transform)
    train_loader = DataLoader(train_dataset, batch_size=best_params['batch_size'], 
                           shuffle=False, num_workers=4, pin_memory=True)
    test_dataset = datasets.ImageFolder(os.path.join(path, 'testing_data'), 
                                      transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=best_params['batch_size'], 
                           shuffle=False, num_workers=4, pin_memory=True)
    
    # 定义优化器
    if best_params['optimizer'] == 'Adam':
        optimizer = optim.Adam(model.parameters(), lr=best_params['lr'], weight_decay=1e-4)
    elif best_params['optimizer'] == 'SGD':
        optimizer = optim.SGD(model.parameters(), lr=best_params['lr'], momentum=0.9, weight_decay=1e-4)
    elif best_params['optimizer'] == 'RMSProp':
        optimizer = optim.RMSprop(model.parameters(), lr=best_params['lr'], weight_decay=1e-4)
    
    criterion = nn.CrossEntropyLoss()
    
    # 训练模型
    train_losses, val_losses, train_accs, val_accs, learning_rates = train_model(
        model, train_loader, test_loader, criterion, optimizer,
        num_epochs=num_epochs,
        gpu_id=gpu_id[0],
        accumulation_steps=4
    )

    # 在测试集上评估模型
    # 在测试集上评估最终模型
    print("\n=== 在测试集上评估最终模型 ===")
    model.eval()
    test_correct = 0
    test_total = 0
    test_loss = 0.0
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device, non_blocking=True), labels.to(device, non_blocking=True)
            
            with autocast('cuda'):
                outputs = model(inputs)
                loss = criterion(outputs, labels)
            
            test_loss += loss.item()
            _, predicted = outputs.max(1)
            test_total += labels.size(0)
            test_correct += predicted.eq(labels).sum().item()
    
    test_accuracy = 100. * test_correct / test_total
    test_loss = test_loss / len(test_loader)
    
    print(f"测试集结果 - 损失: {test_loss:.4f}, 准确率: {test_accuracy:.2f}%")
    
    # 绘制训练曲线
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.plot(train_losses, label='训练损失')
    plt.plot(val_losses, label='验证损失')
    plt.title('损失曲线')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 3, 2)
    plt.plot(train_accs, label='训练准确率')
    plt.plot(val_accs, label='验证准确率')
    plt.axhline(y=test_accuracy, color='r', linestyle='--', label=f'测试准确率: {test_accuracy:.2f}%')
    plt.title('准确率曲线')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 3, 3)
    plt.plot(learning_rates)
    plt.title('学习率变化')
    plt.xlabel('Epoch')
    plt.ylabel('Learning Rate')
    plt.yscale('log')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('final_model_performance.png', dpi=300, bbox_inches='tight')
    
    return best_params, results

num_epochs = 24
k = 5
patience = 8
n = 3
I = 4
if __name__ == "__main__":
    print("=== 任务二：系统化的超参数调优 ===")
    path = os.path.abspath('./limited_dataset')
    
    # GPU监控
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"GPU {i}: {props.name}, 显存: {props.total_memory/1e9:.1f}GB")
    
    task2_optimizer_comparison(path, gpu_id=[0,1,2,3])
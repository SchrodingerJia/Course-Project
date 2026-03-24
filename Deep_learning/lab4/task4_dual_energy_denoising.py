{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bfe05d2c",
   "metadata": {},
   "outputs": [],
   "source": [
    "\"\"\"\n",
    "双能谱图像校正深度学习实现\n",
    "环境要求：\n",
    "- Python 3.8+\n",
    "- PyTorch 1.10+\n",
    "- CUDA 11.3+ (如需GPU训练)\n",
    "- numpy, matplotlib, tqdm\n",
    "\n",
    "注意：请根据实际情况调整文件路径和超参数\n",
    "\"\"\"\n",
    "\n",
    "import numpy as np\n",
    "import torch\n",
    "import torch.nn as nn\n",
    "import torch.optim as optim\n",
    "from torch.utils.data import Dataset, DataLoader\n",
    "import matplotlib.pyplot as plt\n",
    "from tqdm import tqdm\n",
    "import os\n",
    "import warnings\n",
    "warnings.filterwarnings('ignore')\n",
    "\n",
    "# ==================== 配置参数 ====================\n",
    "class Config:\n",
    "    # 数据路径 - 请根据实际文件位置修改\n",
    "    TRAIN_NOISY_PATH = 'dataset/phantom_input_train.npy'      # 噪声训练图像\n",
    "    TRAIN_CLEAN_PATH = 'dataset/phantom_target_train.npy'     # 干净训练图像\n",
    "    TEST_SIM_PATH = 'dataset/phantom_input_test.npy'          # 模拟测试图像\n",
    "    TEST_REAL_PATH = 'dataset/real_input_test.npy'            # 真实测试图像\n",
    "    \n",
    "    # 训练参数\n",
    "    BATCH_SIZE = 16\n",
    "    EPOCHS = 100\n",
    "    LEARNING_RATE = 0.001\n",
    "    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'\n",
    "    \n",
    "    # 模型参数\n",
    "    CHANNELS = 2  # 双通道图像 (f, g)\n",
    "    IMG_SIZE = 256\n",
    "    \n",
    "    # 保存路径\n",
    "    MODEL_SAVE_PATH = 'best_model.pth'\n",
    "    RESULTS_DIR = 'results/'\n",
    "\n",
    "config = Config()\n",
    "\n",
    "# 创建结果目录\n",
    "os.makedirs(config.RESULTS_DIR, exist_ok=True)\n",
    "\n",
    "# ==================== 数据加载器 ====================\n",
    "class DualEnergyDataset(Dataset):\n",
    "    \"\"\"双能谱图像数据集\"\"\"\n",
    "    \n",
    "    def __init__(self, noisy_path, clean_path=None, is_train=True):\n",
    "        \"\"\"\n",
    "        参数:\n",
    "            noisy_path: 噪声图像路径\n",
    "            clean_path: 干净图像路径 (训练时使用)\n",
    "            is_train: 是否为训练模式\n",
    "        \"\"\"\n",
    "        self.noisy_images = np.load(noisy_path)  # 形状: (N, 2, 256, 256)\n",
    "        self.is_train = is_train\n",
    "        \n",
    "        if is_train and clean_path:\n",
    "            self.clean_images = np.load(clean_path)\n",
    "            assert len(self.noisy_images) == len(self.clean_images), \"数据数量不匹配\"\n",
    "        \n",
    "        # 归一化参数 (根据数据统计估算，可根据实际情况调整)\n",
    "        self.noise_mean = self.noisy_images.mean()\n",
    "        self.noise_std = self.noisy_images.std()\n",
    "        \n",
    "    def __len__(self):\n",
    "        return len(self.noisy_images)\n",
    "    \n",
    "    def __getitem__(self, idx):\n",
    "        # 获取噪声图像\n",
    "        noisy = self.noisy_images[idx].astype(np.float32)\n",
    "        \n",
    "        # 简单归一化\n",
    "        noisy = (noisy - self.noise_mean) / (self.noise_std + 1e-8)\n",
    "        \n",
    "        if self.is_train:\n",
    "            # 训练模式：返回噪声-干净图像对\n",
    "            clean = self.clean_images[idx].astype(np.float32)\n",
    "            clean = (clean - self.noise_mean) / (self.noise_std + 1e-8)\n",
    "            return torch.FloatTensor(noisy), torch.FloatTensor(clean)\n",
    "        else:\n",
    "            # 测试模式：只返回噪声图像\n",
    "            return torch.FloatTensor(noisy)\n",
    "\n",
    "# ==================== 神经网络模型 ====================\n",
    "class ResidualBlock(nn.Module):\n",
    "    \"\"\"残差块\"\"\"\n",
    "    \n",
    "    def __init__(self, channels):\n",
    "        super(ResidualBlock, self).__init__()\n",
    "        self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)\n",
    "        self.bn1 = nn.BatchNorm2d(channels)\n",
    "        self.relu = nn.ReLU(inplace=True)\n",
    "        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)\n",
    "        self.bn2 = nn.BatchNorm2d(channels)\n",
    "        \n",
    "    def forward(self, x):\n",
    "        residual = x\n",
    "        out = self.relu(self.bn1(self.conv1(x)))\n",
    "        out = self.bn2(self.conv2(out))\n",
    "        out += residual\n",
    "        out = self.relu(out)\n",
    "        return out\n",
    "\n",
    "class DualEnergyDenoiser(nn.Module):\n",
    "    \"\"\"\n",
    "    双能谱图像去噪网络\n",
    "    采用U-Net风格架构，带有残差连接\n",
    "    \"\"\"\n",
    "    \n",
    "    def __init__(self, in_channels=2, out_channels=2):\n",
    "        super(DualEnergyDenoiser, self).__init__()\n",
    "        \n",
    "        # 编码器\n",
    "        self.enc1 = nn.Sequential(\n",
    "            nn.Conv2d(in_channels, 64, 3, padding=1),\n",
    "            nn.BatchNorm2d(64),\n",
    "            nn.ReLU(inplace=True),\n",
    "            nn.Conv2d(64, 64, 3, padding=1),\n",
    "            nn.BatchNorm2d(64),\n",
    "            nn.ReLU(inplace=True)\n",
    "        )\n",
    "        \n",
    "        self.pool1 = nn.MaxPool2d(2)\n",
    "        \n",
    "        self.enc2 = nn.Sequential(\n",
    "            nn.Conv2d(64, 128, 3, padding=1),\n",
    "            nn.BatchNorm2d(128),\n",
    "            nn.ReLU(inplace=True),\n",
    "            nn.Conv2d(128, 128, 3, padding=1),\n",
    "            nn.BatchNorm2d(128),\n",
    "            nn.ReLU(inplace=True)\n",
    "        )\n",
    "        \n",
    "        self.pool2 = nn.MaxPool2d(2)\n",
    "        \n",
    "        # 瓶颈层 (带残差连接)\n",
    "        self.bottleneck = nn.Sequential(\n",
    "            nn.Conv2d(128, 256, 3, padding=1),\n",
    "            nn.BatchNorm2d(256),\n",
    "            nn.ReLU(inplace=True),\n",
    "            *[ResidualBlock(256) for _ in range(3)],\n",
    "            nn.Conv2d(256, 128, 3, padding=1),\n",
    "            nn.BatchNorm2d(128),\n",
    "            nn.ReLU(inplace=True)\n",
    "        )\n",
    "        \n",
    "        # 解码器\n",
    "        self.up2 = nn.ConvTranspose2d(128, 128, 2, stride=2)\n",
    "        self.dec2 = nn.Sequential(\n",
    "            nn.Conv2d(256, 128, 3, padding=1),  # 跳连连接\n",
    "            nn.BatchNorm2d(128),\n",
    "            nn.ReLU(inplace=True),\n",
    "            nn.Conv2d(128, 64, 3, padding=1),\n",
    "            nn.BatchNorm2d(64),\n",
    "            nn.ReLU(inplace=True)\n",
    "        )\n",
    "        \n",
    "        self.up1 = nn.ConvTranspose2d(64, 64, 2, stride=2)\n",
    "        self.dec1 = nn.Sequential(\n",
    "            nn.Conv2d(128, 64, 3, padding=1),  # 跳连连接\n",
    "            nn.BatchNorm2d(64),\n",
    "            nn.ReLU(inplace=True),\n",
    "            nn.Conv2d(64, out_channels, 3, padding=1)\n",
    "        )\n",
    "        \n",
    "    def forward(self, x):\n",
    "        # 编码\n",
    "        enc1_out = self.enc1(x)\n",
    "        enc2_out = self.enc2(self.pool1(enc1_out))\n",
    "        \n",
    "        # 瓶颈\n",
    "        bottleneck_out = self.bottleneck(self.pool2(enc2_out))\n",
    "        \n",
    "        # 解码\n",
    "        dec2_in = torch.cat([self.up2(bottleneck_out), enc2_out], dim=1)\n",
    "        dec2_out = self.dec2(dec2_in)\n",
    "        \n",
    "        dec1_in = torch.cat([self.up1(dec2_out), enc1_out], dim=1)\n",
    "        output = self.dec1(dec1_in)\n",
    "        \n",
    "        return output\n",
    "\n",
    "# ==================== 训练函数 ====================\n",
    "def train_model(model, train_loader, val_loader, config):\n",
    "    \"\"\"训练模型\"\"\"\n",
    "    \n",
    "    # 损失函数和优化器\n",
    "    criterion = nn.MSELoss()  # 均方误差损失\n",
    "    optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE)\n",
    "    scheduler = optim.lr_scheduler.ReduceLROnPlateau(\n",
    "        optimizer, mode='min', factor=0.5, patience=10\n",
    "    )\n",
    "    best_val_loss = float('inf')\n",
    "    train_losses, val_losses = [], []\n",
    "    \n",
    "    print(f\"开始训练，使用设备: {config.DEVICE}\")\n",
    "    print(f\"训练样本数: {len(train_loader.dataset)}\")\n",
    "    \n",
    "    for epoch in range(config.EPOCHS):\n",
    "        # 训练阶段\n",
    "        model.train()\n",
    "        train_loss = 0.0\n",
    "        \n",
    "        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{config.EPOCHS}')\n",
    "        for batch_idx, (noisy, clean) in enumerate(pbar):\n",
    "            noisy, clean = noisy.to(config.DEVICE), clean.to(config.DEVICE)\n",
    "            \n",
    "            optimizer.zero_grad()\n",
    "            outputs = model(noisy)\n",
    "            loss = criterion(outputs, clean)\n",
    "            loss.backward()\n",
    "            optimizer.step()\n",
    "            \n",
    "            train_loss += loss.item()\n",
    "            pbar.set_postfix({'loss': loss.item()})\n",
    "        \n",
    "        avg_train_loss = train_loss / len(train_loader)\n",
    "        train_losses.append(avg_train_loss)\n",
    "        \n",
    "        # 验证阶段\n",
    "        model.eval()\n",
    "        val_loss = 0.0\n",
    "        \n",
    "        with torch.no_grad():\n",
    "            for noisy, clean in val_loader:\n",
    "                noisy, clean = noisy.to(config.DEVICE), clean.to(config.DEVICE)\n",
    "                outputs = model(noisy)\n",
    "                loss = criterion(outputs, clean)\n",
    "                val_loss += loss.item()\n",
    "        \n",
    "        avg_val_loss = val_loss / len(val_loader)\n",
    "        val_losses.append(avg_val_loss)\n",
    "        \n",
    "        # 学习率调整\n",
    "        scheduler.step(avg_val_loss)\n",
    "\n",
    "        # 手动打印学习率调整信息\n",
    "        current_lr = optimizer.param_groups[0]['lr']\n",
    "        print(f\"当前学习率: {current_lr:.6f}\")\n",
    "        \n",
    "        # 保存最佳模型\n",
    "        if avg_val_loss < best_val_loss:\n",
    "            best_val_loss = avg_val_loss\n",
    "            torch.save({\n",
    "                'epoch': epoch,\n",
    "                'model_state_dict': model.state_dict(),\n",
    "                'optimizer_state_dict': optimizer.state_dict(),\n",
    "                'loss': best_val_loss,\n",
    "            }, config.MODEL_SAVE_PATH)\n",
    "            print(f\"保存最佳模型，验证损失: {best_val_loss:.6f}\")\n",
    "        \n",
    "        print(f\"Epoch {epoch+1}: 训练损失 = {avg_train_loss:.6f}, 验证损失 = {avg_val_loss:.6f}\")\n",
    "    \n",
    "    # 绘制损失曲线\n",
    "    plt.figure(figsize=(10, 5))\n",
    "    plt.plot(train_losses, label='Training Loss')\n",
    "    plt.plot(val_losses, label='Validation Loss')\n",
    "    plt.xlabel('Epoch')\n",
    "    plt.ylabel('Loss')\n",
    "    plt.legend()\n",
    "    plt.title('Training and Validation Loss')\n",
    "    plt.savefig(f'{config.RESULTS_DIR}training_loss.png')\n",
    "    plt.close()\n",
    "    \n",
    "    return model, train_losses, val_losses\n",
    "\n",
    "# ==================== 推理函数 ====================\n",
    "def predict(model, test_loader, config, dataset_type='simulated'):\n",
    "    \"\"\"在测试集上进行预测\"\"\"\n",
    "    \n",
    "    model.eval()\n",
    "    predictions = []\n",
    "    \n",
    "    print(f\"开始在{dataset_type}测试集上进行预测...\")\n",
    "    \n",
    "    with torch.no_grad():\n",
    "        for noisy in tqdm(test_loader):\n",
    "            noisy = noisy.to(config.DEVICE)\n",
    "            output = model(noisy)\n",
    "            predictions.append(output.cpu().numpy())\n",
    "    \n",
    "    # 合并所有batch的预测结果\n",
    "    predictions = np.concatenate(predictions, axis=0)\n",
    "    \n",
    "    # 保存预测结果\n",
    "    # 根据dataset_type调整文件名\n",
    "    if dataset_type == 'phantom':\n",
    "        save_path = f'{config.RESULTS_DIR}phantom_predictions.npy'\n",
    "    else:\n",
    "        save_path = f'{config.RESULTS_DIR}real_predictions.npy'\n",
    "    \n",
    "    np.save(save_path, predictions)\n",
    "    print(f\"预测结果已保存到: {save_path}\")\n",
    "    \n",
    "    # 可视化结果 - 使用新的可视化函数\n",
    "    visualize_results(predictions, dataset_type, config, num_samples=max(3, len(predictions)))\n",
    "    \n",
    "    return predictions\n",
    "    \n",
    "def visualize_results(predictions, dataset_type, config, num_samples=50):\n",
    "    \"\"\"可视化预测结果\"\"\"\n",
    "    \n",
    "    # 创建独立的图像文件，每张图片显示一个样本的两个通道\n",
    "    for sample_idx in range(min(num_samples, len(predictions))):\n",
    "        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))\n",
    "        \n",
    "        # 获取当前样本的两个通道\n",
    "        channel_f = predictions[sample_idx, 0]  # 第一个通道 f\n",
    "        channel_g = predictions[sample_idx, 1]  # 第二个通道 g\n",
    "        \n",
    "        # 显示第一个通道 (f)\n",
    "        if dataset_type == 'real':\n",
    "            title_f = 'real_test_input_f'\n",
    "        else:\n",
    "            title_f = 'phantom_test_input_f'\n",
    "        \n",
    "        im1 = ax1.imshow(channel_f, vmin=0)\n",
    "        ax1.set_title(title_f, fontsize=14, fontweight='bold')\n",
    "        ax1.axis('off')\n",
    "        \n",
    "        # 添加颜色条到第一个子图\n",
    "        cbar1 = fig.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)\n",
    "        cbar1.ax.tick_params(labelsize=10)\n",
    "        \n",
    "        # 显示第二个通道 (g)\n",
    "        if dataset_type == 'real':\n",
    "            title_g = 'real_test_input_g'\n",
    "        else:\n",
    "            title_g = 'phantom_test_input_g'\n",
    "        \n",
    "        im2 = ax2.imshow(channel_g, vmin=0)\n",
    "        ax2.set_title(title_g, fontsize=14, fontweight='bold')\n",
    "        ax2.axis('off')\n",
    "        \n",
    "        # 添加颜色条到第二个子图\n",
    "        cbar2 = fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)\n",
    "        cbar2.ax.tick_params(labelsize=10)\n",
    "        \n",
    "        # 设置整体布局\n",
    "        plt.suptitle(f'test_{dataset_type}_result - sample {sample_idx+1}', fontsize=16, y=0.98)\n",
    "        plt.tight_layout()\n",
    "        \n",
    "        # 保存图像\n",
    "        if dataset_type == 'real':\n",
    "            folder = 'real'\n",
    "        else:\n",
    "            folder = 'phantom'\n",
    "        save_path = f'{config.RESULTS_DIR}' + folder + '/' + f'{dataset_type}_test_sample_{sample_idx+1}.png'\n",
    "        plt.savefig(save_path, dpi=150, bbox_inches='tight')\n",
    "        plt.close()\n",
    "        \n",
    "        print(f\"保存样本{sample_idx+1}的可视化结果: {save_path}\")\n",
    "\n",
    "def visualize_all_results(predictions, dataset_type, config, max_samples=3):\n",
    "    \"\"\"将所有样本的可视化结果合并到一个图像中（备选方案）\"\"\"\n",
    "    \n",
    "    # 限制显示的样本数量\n",
    "    num_samples = min(max_samples, len(predictions))\n",
    "    \n",
    "    # 创建大图，每行显示一个样本的两个通道\n",
    "    fig, axes = plt.subplots(num_samples, 2, figsize=(12, 4*num_samples))\n",
    "    \n",
    "    # 如果只有一个样本，调整axes的维度\n",
    "    if num_samples == 1:\n",
    "        axes = axes.reshape(1, -1)\n",
    "    \n",
    "    for sample_idx in range(num_samples):\n",
    "        # 获取当前样本的两个通道\n",
    "        channel_f = predictions[sample_idx, 0]\n",
    "        channel_g = predictions[sample_idx, 1]\n",
    "        \n",
    "        # 设置标题\n",
    "        if dataset_type == 'real':\n",
    "            title_f = 'real test input f'\n",
    "            title_g = 'real_test_input_g'\n",
    "        else:\n",
    "            title_f = 'phantom_test_input_f'\n",
    "            title_g = 'phantom_test_input_g'\n",
    "        \n",
    "        # 显示第一个通道\n",
    "        im1 = axes[sample_idx, 0].imshow(channel_f, vmin=0)\n",
    "        axes[sample_idx, 0].set_title(title_f, fontsize=14, fontweight='bold')\n",
    "        axes[sample_idx, 0].axis('off')\n",
    "        fig.colorbar(im1, ax=axes[sample_idx, 0], fraction=0.046, pad=0.04)\n",
    "        \n",
    "        # 显示第二个通道\n",
    "        im2 = axes[sample_idx, 1].imshow(channel_g, vmin=0)\n",
    "        axes[sample_idx, 1].set_title(title_g, fontsize=14, fontweight='bold')\n",
    "        axes[sample_idx, 1].axis('off')\n",
    "        fig.colorbar(im2, ax=axes[sample_idx, 1], fraction=0.046, pad=0.04)\n",
    "    \n",
    "    plt.tight_layout()\n",
    "    \n",
    "    # 保存图像\n",
    "    save_path = f'{config.RESULTS_DIR}{dataset_type}_test_all_samples.png'\n",
    "    plt.savefig(save_path, dpi=150, bbox_inches='tight')\n",
    "    plt.close()\n",
    "    \n",
    "    print(f\"保存所有样本的可视化结果: {save_path}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "d2fb6b06",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "==================================================\n",
      "双能谱图像校正深度学习项目\n",
      "==================================================\n",
      "使用GPU: NVIDIA GeForce RTX 3090\n",
      "\n",
      "1. 加载数据集...\n",
      "训练集: 1600 个样本\n",
      "验证集: 400 个样本\n",
      "模拟测试集: 25 个样本\n",
      "真实测试集: 25 个样本\n",
      "\n",
      "2. 初始化模型...\n",
      "模型参数总数: 4,921,282\n"
     ]
    }
   ],
   "source": [
    "torch.manual_seed(42)\n",
    "np.random.seed(42)\n",
    "\n",
    "\n",
    "print(\"=\"*50)\n",
    "print(\"双能谱图像校正深度学习项目\")\n",
    "print(\"=\"*50)\n",
    "\n",
    "# 检查CUDA是否可用\n",
    "if config.DEVICE == 'cuda':\n",
    "    print(f\"使用GPU: {torch.cuda.get_device_name(0)}\")\n",
    "else:\n",
    "    print(\"使用CPU\")\n",
    "\n",
    "# 1. 加载数据集\n",
    "print(\"\\n1. 加载数据集...\")\n",
    "\n",
    "# 训练集 (使用80%训练，20%验证)\n",
    "full_dataset = DualEnergyDataset(\n",
    "    config.TRAIN_NOISY_PATH, \n",
    "    config.TRAIN_CLEAN_PATH, \n",
    "    is_train=True\n",
    ")\n",
    "\n",
    "# 分割训练集和验证集\n",
    "train_size = int(0.8 * len(full_dataset))\n",
    "val_size = len(full_dataset) - train_size\n",
    "train_dataset, val_dataset = torch.utils.data.random_split(\n",
    "    full_dataset, [train_size, val_size]\n",
    ")\n",
    "\n",
    "train_loader = DataLoader(\n",
    "    train_dataset, \n",
    "    batch_size=config.BATCH_SIZE, \n",
    "    shuffle=True, \n",
    "    num_workers=4\n",
    ")\n",
    "\n",
    "val_loader = DataLoader(\n",
    "    val_dataset, \n",
    "    batch_size=config.BATCH_SIZE, \n",
    "    shuffle=False, \n",
    "    num_workers=4\n",
    ")\n",
    "\n",
    "# 测试集\n",
    "test_sim_dataset = DualEnergyDataset(\n",
    "    config.TEST_SIM_PATH, \n",
    "    is_train=False\n",
    ")\n",
    "\n",
    "test_real_dataset = DualEnergyDataset(\n",
    "    config.TEST_REAL_PATH, \n",
    "    is_train=False\n",
    ")\n",
    "\n",
    "test_sim_loader = DataLoader(\n",
    "    test_sim_dataset, \n",
    "    batch_size=config.BATCH_SIZE, \n",
    "    shuffle=False, \n",
    "    num_workers=4\n",
    ")\n",
    "\n",
    "test_real_loader = DataLoader(\n",
    "    test_real_dataset, \n",
    "    batch_size=config.BATCH_SIZE, \n",
    "    shuffle=False, \n",
    "    num_workers=4\n",
    ")\n",
    "\n",
    "print(f\"训练集: {len(train_dataset)} 个样本\")\n",
    "print(f\"验证集: {len(val_dataset)} 个样本\")\n",
    "print(f\"模拟测试集: {len(test_sim_dataset)} 个样本\")\n",
    "print(f\"真实测试集: {len(test_real_dataset)} 个样本\")\n",
    "\n",
    "# 2. 初始化模型\n",
    "print(\"\\n2. 初始化模型...\")\n",
    "model = DualEnergyDenoiser(\n",
    "    in_channels=config.CHANNELS, \n",
    "    out_channels=config.CHANNELS\n",
    ").to(config.DEVICE)\n",
    "\n",
    "# 打印模型信息\n",
    "total_params = sum(p.numel() for p in model.parameters())\n",
    "print(f\"模型参数总数: {total_params:,}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "5ad9fefa",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "3. 开始训练...\n",
      "开始训练，使用设备: cuda\n",
      "训练样本数: 1600\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 1/100: 100%|██████████| 100/100 [00:19<00:00,  5.08it/s, loss=0.0226]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "保存最佳模型，验证损失: 0.021477\n",
      "Epoch 1: 训练损失 = 0.053538, 验证损失 = 0.021477\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 2/100: 100%|██████████| 100/100 [00:19<00:00,  5.07it/s, loss=0.0107]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "保存最佳模型，验证损失: 0.013629\n",
      "Epoch 2: 训练损失 = 0.022473, 验证损失 = 0.013629\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 3/100: 100%|██████████| 100/100 [00:19<00:00,  5.02it/s, loss=0.0246]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "保存最佳模型，验证损失: 0.010366\n",
      "Epoch 3: 训练损失 = 0.020761, 验证损失 = 0.010366\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 4/100: 100%|██████████| 100/100 [00:19<00:00,  5.05it/s, loss=0.00566]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "保存最佳模型，验证损失: 0.006013\n",
      "Epoch 4: 训练损失 = 0.011727, 验证损失 = 0.006013\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 5/100: 100%|██████████| 100/100 [00:19<00:00,  5.02it/s, loss=0.0109]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 5: 训练损失 = 0.010467, 验证损失 = 0.008170\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 6/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.00555]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 6: 训练损失 = 0.010585, 验证损失 = 0.006824\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 7/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.0067]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "保存最佳模型，验证损失: 0.004098\n",
      "Epoch 7: 训练损失 = 0.009802, 验证损失 = 0.004098\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 8/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.0278]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 8: 训练损失 = 0.008636, 验证损失 = 0.005932\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 9/100: 100%|██████████| 100/100 [00:20<00:00,  5.00it/s, loss=0.00811]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 9: 训练损失 = 0.008105, 验证损失 = 0.005540\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 10/100: 100%|██████████| 100/100 [00:20<00:00,  5.00it/s, loss=0.00401]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 10: 训练损失 = 0.005835, 验证损失 = 0.007136\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 11/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.0068]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 11: 训练损失 = 0.005455, 验证损失 = 0.010041\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 12/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00658]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "保存最佳模型，验证损失: 0.003995\n",
      "Epoch 12: 训练损失 = 0.006849, 验证损失 = 0.003995\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 13/100: 100%|██████████| 100/100 [00:19<00:00,  5.02it/s, loss=0.00399]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 13: 训练损失 = 0.006584, 验证损失 = 0.007275\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 14/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00685]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 14: 训练损失 = 0.006417, 验证损失 = 0.007964\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 15/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00291]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "保存最佳模型，验证损失: 0.003711\n",
      "Epoch 15: 训练损失 = 0.005510, 验证损失 = 0.003711\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 16/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00443]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 16: 训练损失 = 0.005150, 验证损失 = 0.008681\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 17/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.00682]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 17: 训练损失 = 0.005538, 验证损失 = 0.006322\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 18/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00479]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "保存最佳模型，验证损失: 0.003320\n",
      "Epoch 18: 训练损失 = 0.004829, 验证损失 = 0.003320\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 19/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00262]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 19: 训练损失 = 0.004366, 验证损失 = 0.003638\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 20/100: 100%|██████████| 100/100 [00:20<00:00,  4.96it/s, loss=0.00466]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 20: 训练损失 = 0.004682, 验证损失 = 0.004460\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 21/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00366]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 21: 训练损失 = 0.004151, 验证损失 = 0.005085\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 22/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00541]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 22: 训练损失 = 0.005443, 验证损失 = 0.006699\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 23/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00649]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 23: 训练损失 = 0.004399, 验证损失 = 0.007662\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 24/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00626]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "保存最佳模型，验证损失: 0.002477\n",
      "Epoch 24: 训练损失 = 0.004635, 验证损失 = 0.002477\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 25/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00249]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 25: 训练损失 = 0.004760, 验证损失 = 0.002926\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 26/100: 100%|██████████| 100/100 [00:20<00:00,  5.00it/s, loss=0.00841]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "保存最佳模型，验证损失: 0.002270\n",
      "Epoch 26: 训练损失 = 0.004141, 验证损失 = 0.002270\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 27/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.00482]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 27: 训练损失 = 0.004630, 验证损失 = 0.006793\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 28/100: 100%|██████████| 100/100 [00:20<00:00,  4.96it/s, loss=0.00339]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 28: 训练损失 = 0.003868, 验证损失 = 0.003117\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 29/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00455]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 29: 训练损失 = 0.003738, 验证损失 = 0.004649\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 30/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00268]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 30: 训练损失 = 0.004615, 验证损失 = 0.005738\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 31/100: 100%|██████████| 100/100 [00:19<00:00,  5.01it/s, loss=0.00364]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 31: 训练损失 = 0.003619, 验证损失 = 0.003888\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 32/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00209]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 32: 训练损失 = 0.003377, 验证损失 = 0.003189\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 33/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.00614]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 33: 训练损失 = 0.003559, 验证损失 = 0.002556\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 34/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00282]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 34: 训练损失 = 0.004693, 验证损失 = 0.004022\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 35/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00283]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 35: 训练损失 = 0.003369, 验证损失 = 0.004161\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 36/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00451]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.001000\n",
      "Epoch 36: 训练损失 = 0.003942, 验证损失 = 0.004295\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 37/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00332]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 37: 训练损失 = 0.003364, 验证损失 = 0.003560\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 38/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00179]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "保存最佳模型，验证损失: 0.002110\n",
      "Epoch 38: 训练损失 = 0.002390, 验证损失 = 0.002110\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 39/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00202]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 39: 训练损失 = 0.002534, 验证损失 = 0.002138\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 40/100: 100%|██████████| 100/100 [00:19<00:00,  5.03it/s, loss=0.00245]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "保存最佳模型，验证损失: 0.001582\n",
      "Epoch 40: 训练损失 = 0.002291, 验证损失 = 0.001582\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 41/100: 100%|██████████| 100/100 [00:20<00:00,  5.00it/s, loss=0.00137]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 41: 训练损失 = 0.002423, 验证损失 = 0.001992\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 42/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00225]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 42: 训练损失 = 0.002560, 验证损失 = 0.001907\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 43/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00146]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 43: 训练损失 = 0.002648, 验证损失 = 0.002042\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 44/100: 100%|██████████| 100/100 [00:19<00:00,  5.01it/s, loss=0.00174]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "保存最佳模型，验证损失: 0.001500\n",
      "Epoch 44: 训练损失 = 0.002340, 验证损失 = 0.001500\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 45/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.00208]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 45: 训练损失 = 0.002172, 验证损失 = 0.002134\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 46/100: 100%|██████████| 100/100 [00:19<00:00,  5.01it/s, loss=0.00299]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 46: 训练损失 = 0.002617, 验证损失 = 0.001974\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 47/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00327]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 47: 训练损失 = 0.002288, 验证损失 = 0.001637\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 48/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00183]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 48: 训练损失 = 0.002519, 验证损失 = 0.002022\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 49/100: 100%|██████████| 100/100 [00:20<00:00,  5.00it/s, loss=0.00301]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 49: 训练损失 = 0.002396, 验证损失 = 0.002637\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 50/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00267]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 50: 训练损失 = 0.002586, 验证损失 = 0.001586\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 51/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00235]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "保存最佳模型，验证损失: 0.001427\n",
      "Epoch 51: 训练损失 = 0.002225, 验证损失 = 0.001427\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 52/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00212]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 52: 训练损失 = 0.002203, 验证损失 = 0.002143\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 53/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00232]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 53: 训练损失 = 0.002888, 验证损失 = 0.001787\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 54/100: 100%|██████████| 100/100 [00:20<00:00,  4.96it/s, loss=0.00251]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 54: 训练损失 = 0.002569, 验证损失 = 0.004214\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 55/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00237]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 55: 训练损失 = 0.002356, 验证损失 = 0.001443\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 56/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00243]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 56: 训练损失 = 0.002270, 验证损失 = 0.001541\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 57/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.002] \n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 57: 训练损失 = 0.002370, 验证损失 = 0.001616\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 58/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00125]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 58: 训练损失 = 0.002595, 验证损失 = 0.001811\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 59/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00303]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 59: 训练损失 = 0.002875, 验证损失 = 0.002129\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 60/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00169]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 60: 训练损失 = 0.002687, 验证损失 = 0.001765\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 61/100: 100%|██████████| 100/100 [00:20<00:00,  4.96it/s, loss=0.0018] \n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000500\n",
      "Epoch 61: 训练损失 = 0.002663, 验证损失 = 0.002559\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 62/100: 100%|██████████| 100/100 [00:20<00:00,  4.96it/s, loss=0.00146]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 62: 训练损失 = 0.002493, 验证损失 = 0.002011\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 63/100: 100%|██████████| 100/100 [00:20<00:00,  4.96it/s, loss=0.00189]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "保存最佳模型，验证损失: 0.001162\n",
      "Epoch 63: 训练损失 = 0.001812, 验证损失 = 0.001162\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 64/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.00119]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 64: 训练损失 = 0.001757, 验证损失 = 0.001463\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 65/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.00176]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 65: 训练损失 = 0.001696, 验证损失 = 0.001313\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 66/100: 100%|██████████| 100/100 [00:19<00:00,  5.01it/s, loss=0.00118]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 66: 训练损失 = 0.001916, 验证损失 = 0.001398\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 67/100: 100%|██████████| 100/100 [00:19<00:00,  5.02it/s, loss=0.00124]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 67: 训练损失 = 0.001650, 验证损失 = 0.001504\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 68/100: 100%|██████████| 100/100 [00:20<00:00,  5.00it/s, loss=0.00203]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 68: 训练损失 = 0.001726, 验证损失 = 0.001288\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 69/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00146]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 69: 训练损失 = 0.001620, 验证损失 = 0.001187\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 70/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00338]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "保存最佳模型，验证损失: 0.001129\n",
      "Epoch 70: 训练损失 = 0.001775, 验证损失 = 0.001129\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 71/100: 100%|██████████| 100/100 [00:20<00:00,  5.00it/s, loss=0.0017] \n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 71: 训练损失 = 0.001848, 验证损失 = 0.001883\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 72/100: 100%|██████████| 100/100 [00:20<00:00,  4.95it/s, loss=0.00238]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 72: 训练损失 = 0.001807, 验证损失 = 0.001387\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 73/100: 100%|██████████| 100/100 [00:20<00:00,  4.96it/s, loss=0.00137]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 73: 训练损失 = 0.001850, 验证损失 = 0.001887\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 74/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00143]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 74: 训练损失 = 0.001791, 验证损失 = 0.001228\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 75/100: 100%|██████████| 100/100 [00:19<00:00,  5.01it/s, loss=0.00117]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 75: 训练损失 = 0.001896, 验证损失 = 0.001649\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 76/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00127]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 76: 训练损失 = 0.001809, 验证损失 = 0.001188\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 77/100: 100%|██████████| 100/100 [00:19<00:00,  5.01it/s, loss=0.00128]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 77: 训练损失 = 0.001829, 验证损失 = 0.001230\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 78/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00117]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 78: 训练损失 = 0.002201, 验证损失 = 0.001843\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 79/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00145]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 79: 训练损失 = 0.001871, 验证损失 = 0.001522\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 80/100: 100%|██████████| 100/100 [00:19<00:00,  5.03it/s, loss=0.00206]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000250\n",
      "Epoch 80: 训练损失 = 0.001656, 验证损失 = 0.001572\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 81/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00295]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 81: 训练损失 = 0.001641, 验证损失 = 0.001828\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 82/100: 100%|██████████| 100/100 [00:19<00:00,  5.01it/s, loss=0.00143]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "保存最佳模型，验证损失: 0.001105\n",
      "Epoch 82: 训练损失 = 0.001441, 验证损失 = 0.001105\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 83/100: 100%|██████████| 100/100 [00:19<00:00,  5.02it/s, loss=0.00289]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 83: 训练损失 = 0.001510, 验证损失 = 0.001107\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 84/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.00221]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 84: 训练损失 = 0.001487, 验证损失 = 0.001393\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 85/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.00262]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 85: 训练损失 = 0.001597, 验证损失 = 0.001145\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 86/100: 100%|██████████| 100/100 [00:20<00:00,  4.96it/s, loss=0.00142]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 86: 训练损失 = 0.001521, 验证损失 = 0.001241\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 87/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.000859]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "保存最佳模型，验证损失: 0.000972\n",
      "Epoch 87: 训练损失 = 0.001469, 验证损失 = 0.000972\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 88/100: 100%|██████████| 100/100 [00:20<00:00,  4.96it/s, loss=0.00135]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 88: 训练损失 = 0.001509, 验证损失 = 0.001106\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 89/100: 100%|██████████| 100/100 [00:20<00:00,  4.92it/s, loss=0.00444]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 89: 训练损失 = 0.001481, 验证损失 = 0.001575\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 90/100: 100%|██████████| 100/100 [00:20<00:00,  4.92it/s, loss=0.00163]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 90: 训练损失 = 0.001633, 验证损失 = 0.001228\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 91/100: 100%|██████████| 100/100 [00:19<00:00,  5.02it/s, loss=0.00118]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 91: 训练损失 = 0.001574, 验证损失 = 0.001135\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 92/100: 100%|██████████| 100/100 [00:20<00:00,  4.88it/s, loss=0.00127]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 92: 训练损失 = 0.001452, 验证损失 = 0.001006\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 93/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.000864]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 93: 训练损失 = 0.001604, 验证损失 = 0.001177\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 94/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.000685]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 94: 训练损失 = 0.001549, 验证损失 = 0.001035\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 95/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00138]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 95: 训练损失 = 0.001518, 验证损失 = 0.001178\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 96/100: 100%|██████████| 100/100 [00:20<00:00,  4.98it/s, loss=0.00225]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 96: 训练损失 = 0.001454, 验证损失 = 0.001581\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 97/100: 100%|██████████| 100/100 [00:20<00:00,  4.97it/s, loss=0.00146]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000125\n",
      "Epoch 97: 训练损失 = 0.001405, 验证损失 = 0.001184\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 98/100: 100%|██████████| 100/100 [00:19<00:00,  5.00it/s, loss=0.00305]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000063\n",
      "Epoch 98: 训练损失 = 0.001556, 验证损失 = 0.001549\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 99/100: 100%|██████████| 100/100 [00:20<00:00,  5.00it/s, loss=0.00193]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000063\n",
      "保存最佳模型，验证损失: 0.000960\n",
      "Epoch 99: 训练损失 = 0.001401, 验证损失 = 0.000960\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "Epoch 100/100: 100%|██████████| 100/100 [00:20<00:00,  4.99it/s, loss=0.00104]\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n",
      "findfont: Generic family 'sans-serif' not found because none of the following families were found: SimHei\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "当前学习率: 0.000063\n",
      "Epoch 100: 训练损失 = 0.001306, 验证损失 = 0.001043\n"
     ]
    }
   ],
   "source": [
    "# 3. 训练模型\n",
    "print(\"\\n3. 开始训练...\")\n",
    "model, train_loss, val_loss = train_model(model, train_loader, val_loader, config)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "d3a62f3c",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "4. 加载最佳模型进行测试...\n",
      "加载epoch 98的模型，验证损失: 0.001050\n"
     ]
    }
   ],
   "source": [
    "# 4. 加载最佳模型进行测试\n",
    "print(\"\\n4. 加载最佳模型进行测试...\")\n",
    "checkpoint = torch.load(config.MODEL_SAVE_PATH, map_location=config.DEVICE)\n",
    "model.load_state_dict(checkpoint['model_state_dict'])\n",
    "print(f\"加载epoch {checkpoint['epoch']}的模型，验证损失: {checkpoint['loss']:.6f}\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "id": "bf75e3d8",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "5. 在测试集上进行预测...\n",
      "开始在phantom测试集上进行预测...\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 2/2 [00:00<00:00,  2.01it/s]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "预测结果已保存到: results/phantom_predictions.npy\n",
      "保存样本1的可视化结果: results/phantom/phantom_test_sample_1.png\n",
      "保存样本2的可视化结果: results/phantom/phantom_test_sample_2.png\n",
      "保存样本3的可视化结果: results/phantom/phantom_test_sample_3.png\n",
      "保存样本4的可视化结果: results/phantom/phantom_test_sample_4.png\n",
      "保存样本5的可视化结果: results/phantom/phantom_test_sample_5.png\n",
      "保存样本6的可视化结果: results/phantom/phantom_test_sample_6.png\n",
      "保存样本7的可视化结果: results/phantom/phantom_test_sample_7.png\n",
      "保存样本8的可视化结果: results/phantom/phantom_test_sample_8.png\n",
      "保存样本9的可视化结果: results/phantom/phantom_test_sample_9.png\n",
      "保存样本10的可视化结果: results/phantom/phantom_test_sample_10.png\n",
      "保存样本11的可视化结果: results/phantom/phantom_test_sample_11.png\n",
      "保存样本12的可视化结果: results/phantom/phantom_test_sample_12.png\n",
      "保存样本13的可视化结果: results/phantom/phantom_test_sample_13.png\n",
      "保存样本14的可视化结果: results/phantom/phantom_test_sample_14.png\n",
      "保存样本15的可视化结果: results/phantom/phantom_test_sample_15.png\n",
      "保存样本16的可视化结果: results/phantom/phantom_test_sample_16.png\n",
      "保存样本17的可视化结果: results/phantom/phantom_test_sample_17.png\n",
      "保存样本18的可视化结果: results/phantom/phantom_test_sample_18.png\n",
      "保存样本19的可视化结果: results/phantom/phantom_test_sample_19.png\n",
      "保存样本20的可视化结果: results/phantom/phantom_test_sample_20.png\n",
      "保存样本21的可视化结果: results/phantom/phantom_test_sample_21.png\n",
      "保存样本22的可视化结果: results/phantom/phantom_test_sample_22.png\n",
      "保存样本23的可视化结果: results/phantom/phantom_test_sample_23.png\n",
      "保存样本24的可视化结果: results/phantom/phantom_test_sample_24.png\n",
      "保存样本25的可视化结果: results/phantom/phantom_test_sample_25.png\n",
      "开始在real测试集上进行预测...\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 2/2 [00:00<00:00,  3.21it/s]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "预测结果已保存到: results/real_predictions.npy\n",
      "保存样本1的可视化结果: results/real/real_test_sample_1.png\n",
      "保存样本2的可视化结果: results/real/real_test_sample_2.png\n",
      "保存样本3的可视化结果: results/real/real_test_sample_3.png\n",
      "保存样本4的可视化结果: results/real/real_test_sample_4.png\n",
      "保存样本5的可视化结果: results/real/real_test_sample_5.png\n",
      "保存样本6的可视化结果: results/real/real_test_sample_6.png\n",
      "保存样本7的可视化结果: results/real/real_test_sample_7.png\n",
      "保存样本8的可视化结果: results/real/real_test_sample_8.png\n",
      "保存样本9的可视化结果: results/real/real_test_sample_9.png\n",
      "保存样本10的可视化结果: results/real/real_test_sample_10.png\n",
      "保存样本11的可视化结果: results/real/real_test_sample_11.png\n",
      "保存样本12的可视化结果: results/real/real_test_sample_12.png\n",
      "保存样本13的可视化结果: results/real/real_test_sample_13.png\n",
      "保存样本14的可视化结果: results/real/real_test_sample_14.png\n",
      "保存样本15的可视化结果: results/real/real_test_sample_15.png\n",
      "保存样本16的可视化结果: results/real/real_test_sample_16.png\n",
      "保存样本17的可视化结果: results/real/real_test_sample_17.png\n",
      "保存样本18的可视化结果: results/real/real_test_sample_18.png\n",
      "保存样本19的可视化结果: results/real/real_test_sample_19.png\n",
      "保存样本20的可视化结果: results/real/real_test_sample_20.png\n",
      "保存样本21的可视化结果: results/real/real_test_sample_21.png\n",
      "保存样本22的可视化结果: results/real/real_test_sample_22.png\n",
      "保存样本23的可视化结果: results/real/real_test_sample_23.png\n",
      "保存样本24的可视化结果: results/real/real_test_sample_24.png\n",
      "保存样本25的可视化结果: results/real/real_test_sample_25.png\n",
      "\n",
      "==================================================\n",
      "项目完成!\n",
      "结果保存在: results/\n",
      "==================================================\n"
     ]
    }
   ],
   "source": [
    "# 5. 在测试集上预测\n",
    "print(\"\\n5. 在测试集上进行预测...\")\n",
    "# 设置中文\n",
    "plt.rcParams['font.sans-serif'] = ['DejaVu Serif']\n",
    "plt.rcParams['axes.unicode_minus'] = False\n",
    "\n",
    "# 模拟测试集\n",
    "sim_predictions = predict(model, test_sim_loader, config, dataset_type='phantom')\n",
    "\n",
    "# 真实测试集\n",
    "real_predictions = predict(model, test_real_loader, config, dataset_type='real')\n",
    "\n",
    "print(\"\\n\" + \"=\"*50)\n",
    "print(\"项目完成!\")\n",
    "print(f\"结果保存在: {config.RESULTS_DIR}\")\n",
    "print(\"=\"*50)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "77d6c87d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Minimal network architecture diagram saved as unet_minimal_architecture.png\n"
     ]
    }
   ],
   "source": [
    "import graphviz\n",
    "from graphviz import Digraph\n",
    "\n",
    "# 创建有向图\n",
    "dot = Digraph('U-Net Architecture', format='png')\n",
    "dot.attr(rankdir='TB', size='10,14', dpi='300', nodesep='0.3', ranksep='0.4')\n",
    "\n",
    "# 设置全局样式\n",
    "dot.attr('node', shape='box', style='filled', fontname='Arial', fontsize='9', width='1.8', height='0.6')\n",
    "dot.attr('edge', fontname='Arial', fontsize='8')\n",
    "\n",
    "# 定义颜色\n",
    "colors = {\n",
    "    'io': '#F0F0F0',\n",
    "    'encoder': '#FFF0D0',\n",
    "    'bottleneck': '#E8D8FF',\n",
    "    'decoder': '#D0E8FF',\n",
    "    'skip': 'white'\n",
    "}\n",
    "\n",
    "# 创建节点 - 使用更简洁的标签\n",
    "dot.node('in', 'Input\\n2×256×256', fillcolor=colors['io'], shape='ellipse')\n",
    "dot.node('e1', 'Enc1\\nConv 64×2', fillcolor=colors['encoder'])\n",
    "dot.node('p1', 'Pool1\\n2×2', fillcolor=colors['encoder'], shape='diamond')\n",
    "dot.node('e2', 'Enc2\\nConv 128×2', fillcolor=colors['encoder'])\n",
    "dot.node('p2', 'Pool2\\n2×2', fillcolor=colors['encoder'], shape='diamond')\n",
    "dot.node('bt', 'Bottleneck\\nConv 256+Res×3\\nConv 128', fillcolor=colors['bottleneck'])\n",
    "dot.node('u2', 'Up2\\nTransConv 128', fillcolor=colors['decoder'], shape='parallelogram')\n",
    "dot.node('c2', '⊕', fillcolor=colors['skip'], shape='circle', width='0.5', height='0.5')\n",
    "dot.node('d2', 'Dec2\\nConv 128+64', fillcolor=colors['decoder'])\n",
    "dot.node('u1', 'Up1\\nTransConv 64', fillcolor=colors['decoder'], shape='parallelogram')\n",
    "dot.node('c1', '⊕', fillcolor=colors['skip'], shape='circle', width='0.5', height='0.5')\n",
    "dot.node('d1', 'Dec1\\nConv 64+2', fillcolor=colors['decoder'])\n",
    "dot.node('out', 'Output\\n2×256×256', fillcolor=colors['io'], shape='ellipse')\n",
    "\n",
    "# 主路径连接\n",
    "main_edges = [\n",
    "    ('in', 'e1'),\n",
    "    ('e1', 'p1'),\n",
    "    ('p1', 'e2'),\n",
    "    ('e2', 'p2'),\n",
    "    ('p2', 'bt'),\n",
    "    ('bt', 'u2'),\n",
    "    ('u2', 'c2'),\n",
    "    ('c2', 'd2'),\n",
    "    ('d2', 'u1'),\n",
    "    ('u1', 'c1'),\n",
    "    ('c1', 'd1'),\n",
    "    ('d1', 'out')\n",
    "]\n",
    "\n",
    "# 跳连连接\n",
    "skip_edges = [\n",
    "    ('e2', 'c2'),\n",
    "    ('e1', 'c1')\n",
    "]\n",
    "\n",
    "# 添加边\n",
    "for start, end in main_edges:\n",
    "    dot.edge(start, end, penwidth='1.2')\n",
    "\n",
    "for start, end in skip_edges:\n",
    "    dot.edge(start, end, style='dashed', color='#666666')\n",
    "\n",
    "# 添加解释性文本\n",
    "dot.node('legend1', 'Encoder: Feature extraction\\nand downsampling', \n",
    "         shape='plaintext', style='', fontsize='8', width='2')\n",
    "dot.node('legend2', 'Decoder: Feature reconstruction\\nand upsampling', \n",
    "         shape='plaintext', style='', fontsize='8', width='2')\n",
    "dot.node('legend3', 'Skip connections: Preserve\\nspatial details', \n",
    "         shape='plaintext', style='', fontsize='8', width='2')\n",
    "\n",
    "# 添加图例连接（仅用于布局）\n",
    "dot.edge('legend1', 'e1', style='invis')\n",
    "dot.edge('legend2', 'd2', style='invis')\n",
    "dot.edge('legend3', 'c2', style='invis')\n",
    "\n",
    "# 保存\n",
    "dot.render('unet_minimal_architecture', view=True, cleanup=True)\n",
    "print(\"Minimal network architecture diagram saved as unet_minimal_architecture.png\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "fd4dbf16",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Compact network architecture diagram saved as unet_compact_architecture.png\n"
     ]
    }
   ],
   "source": [
    "import graphviz\n",
    "from graphviz import Digraph\n",
    "\n",
    "# 创建有向图\n",
    "dot = Digraph('U-Net Architecture', format='png')\n",
    "dot.attr(rankdir='TB', size='12,18', dpi='300')\n",
    "dot.attr('graph', concentrate='true')  # 使图形更紧凑\n",
    "\n",
    "# 设置全局节点样式\n",
    "dot.attr('node', shape='box', style='filled', fontname='Arial', fontsize='10')\n",
    "\n",
    "# 定义颜色方案\n",
    "colors = {\n",
    "    'input_output': 'lightgray',\n",
    "    'encoder': '#FFE4B5',  # 浅橙色\n",
    "    'bottleneck': '#D8BFD8',  # 淡紫色\n",
    "    'decoder': '#ADD8E6',  # 淡蓝色\n",
    "    'skip': 'white'\n",
    "}\n",
    "\n",
    "# 输入层 - 使用一个节点代表整个输入\n",
    "dot.node('input', 'Input Image\\n2×256×256', \n",
    "         fillcolor=colors['input_output'], \n",
    "         shape='ellipse')\n",
    "\n",
    "# 编码器部分 - 合并相关层以减少节点数量\n",
    "dot.node('enc1', 'Encoder Block 1\\nConv(64)+BN+ReLU×2\\nOutput: 64×256×256', \n",
    "         fillcolor=colors['encoder'])\n",
    "dot.node('pool1', 'MaxPool 2×2\\nOutput: 64×128×128', \n",
    "         fillcolor=colors['encoder'], shape='diamond')\n",
    "\n",
    "dot.node('enc2', 'Encoder Block 2\\nConv(128)+BN+ReLU×2\\nOutput: 128×128×128', \n",
    "         fillcolor=colors['encoder'])\n",
    "dot.node('pool2', 'MaxPool 2×2\\nOutput: 128×64×64', \n",
    "         fillcolor=colors['encoder'], shape='diamond')\n",
    "\n",
    "# 瓶颈层 - 简化表示\n",
    "dot.node('bottleneck', 'Bottleneck\\nConv(256)+BN+ReLU\\nResidual Blocks×3\\nConv(128)+BN+ReLU\\nOutput: 128×64×64', \n",
    "         fillcolor=colors['bottleneck'])\n",
    "\n",
    "# 解码器部分\n",
    "dot.node('up2', 'Upsample 2×2\\nConvTranspose(128)\\nOutput: 128×128×128', \n",
    "         fillcolor=colors['decoder'], shape='parallelogram')\n",
    "dot.node('concat2', 'Concatenate\\nwith Encoder Block 2 output', \n",
    "         fillcolor=colors['skip'], shape='circle')\n",
    "dot.node('dec2', 'Decoder Block 2\\nConv(128)+BN+ReLU\\nConv(64)+BN+ReLU\\nOutput: 64×128×128', \n",
    "         fillcolor=colors['decoder'])\n",
    "\n",
    "dot.node('up1', 'Upsample 2×2\\nConvTranspose(64)\\nOutput: 64×256×256', \n",
    "         fillcolor=colors['decoder'], shape='parallelogram')\n",
    "dot.node('concat1', 'Concatenate\\nwith Encoder Block 1 output', \n",
    "         fillcolor=colors['skip'], shape='circle')\n",
    "dot.node('dec1', 'Decoder Block 1\\nConv(64)+BN+ReLU\\nConv(2)\\nOutput: 2×256×256', \n",
    "         fillcolor=colors['decoder'])\n",
    "\n",
    "# 输出层\n",
    "dot.node('output', 'Output Image\\n2×256×256', \n",
    "         fillcolor=colors['input_output'], \n",
    "         shape='ellipse')\n",
    "\n",
    "# 主路径连接\n",
    "main_edges = [\n",
    "    ('input', 'enc1'),\n",
    "    ('enc1', 'pool1'),\n",
    "    ('pool1', 'enc2'),\n",
    "    ('enc2', 'pool2'),\n",
    "    ('pool2', 'bottleneck'),\n",
    "    ('bottleneck', 'up2'),\n",
    "    ('up2', 'concat2'),\n",
    "    ('concat2', 'dec2'),\n",
    "    ('dec2', 'up1'),\n",
    "    ('up1', 'concat1'),\n",
    "    ('concat1', 'dec1'),\n",
    "    ('dec1', 'output')\n",
    "]\n",
    "\n",
    "# 跳连连接 (虚线)\n",
    "skip_edges = [\n",
    "    ('enc2', 'concat2'),\n",
    "    ('enc1', 'concat1')\n",
    "]\n",
    "\n",
    "# 添加所有边\n",
    "for start, end in main_edges:\n",
    "    dot.edge(start, end, penwidth='1.5')\n",
    "\n",
    "for start, end in skip_edges:\n",
    "    dot.edge(start, end, style='dashed', color='gray', penwidth='1')\n",
    "\n",
    "# 添加层组标签\n",
    "with dot.subgraph(name='cluster_encoder') as c:\n",
    "    c.attr(label='Encoder', style='dashed', color='gray')\n",
    "    c.node('enc1')\n",
    "    c.node('pool1')\n",
    "    c.node('enc2')\n",
    "    c.node('pool2')\n",
    "\n",
    "with dot.subgraph(name='cluster_decoder') as c:\n",
    "    c.attr(label='Decoder', style='dashed', color='gray')\n",
    "    c.node('dec2')\n",
    "    c.node('up1')\n",
    "    c.node('dec1')\n",
    "\n",
    "# 保存图像\n",
    "dot.render('unet_compact_architecture', view=True, cleanup=True)\n",
    "print(\"Compact network architecture diagram saved as unet_compact_architecture.png\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

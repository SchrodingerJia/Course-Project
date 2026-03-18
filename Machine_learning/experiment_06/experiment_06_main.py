import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score
from sklearn.manifold import TSNE
import warnings
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_and_preprocess_data_without_region(filename):
    """加载数据并进行标准化处理 - 不考虑地区特征"""
    # 读取Excel文件
    data = pd.read_excel(filename)
    # 检查数据基本信息
    print(f"\n数据形状: {data.shape}")
    print(f"列名: {data.columns.tolist()}")
    # 提取数值特征（排除地区列）
    feature_columns = ['工资性收入', '经营净收入', '财产净收入', '转移净收入']
    features = data[feature_columns]
    # 数据标准化
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    print(f"\n标准化后的特征形状: {features_scaled.shape}")
    print(f"使用的特征: {feature_columns}")
    print(f"样本数量: {len(features)}")
    # 显示特征的基本统计信息
    print(f"\n特征描述统计:")
    print(features.describe())
    return features_scaled, feature_columns, data

class KMeans:
    def __init__(self, k=3, max_iters=100, random_state=42):
        self.k = k
        self.max_iters = max_iters
        self.random_state = random_state
        self.iteration = 0
    def _initialize_centroids(self, X):
        """随机初始化质心"""
        np.random.seed(self.random_state)
        random_idx = np.random.permutation(X.shape[0])
        centroids = X[random_idx[:self.k]]
        return centroids
    def _compute_distance(self, X, centroids):
        """计算每个点到质心的距离"""
        distances = np.zeros((X.shape[0], self.k))
        for i in range(self.k):
            distances[:, i] = np.linalg.norm(X - centroids[i], axis=1)
        return distances
    def _assign_clusters(self, distances):
        """分配每个点到最近的质心"""
        return np.argmin(distances, axis=1)
    def _update_centroids(self, X, labels):
        """更新质心位置"""
        centroids = np.zeros((self.k, X.shape[1]))
        for i in range(self.k):
            if np.sum(labels == i) > 0:
                centroids[i] = X[labels == i].mean(axis=0)
        return centroids
    def fit(self, X):
        """训练K-means模型"""
        self.centroids = self._initialize_centroids(X)
        for iteration in range(self.max_iters):
            # 计算距离并分配簇
            distances = self._compute_distance(X, self.centroids)
            self.labels = self._assign_clusters(distances)
            # 更新质心
            new_centroids = self._update_centroids(X, self.labels)
            # 检查收敛
            if np.allclose(self.centroids, new_centroids):
                self.iteration = iteration + 1
                print(f"K-means 在 {iteration+1} 次迭代后收敛")
                break
            self.centroids = new_centroids
        # 计算SSE
        self.sse = self._compute_sse(X, self.labels, self.centroids)
        return self
    def _compute_sse(self, X, labels, centroids):
        """计算簇内误差平方和"""
        sse = 0
        for i in range(self.k):
            cluster_points = X[labels == i]
            if len(cluster_points) > 0:
                sse += np.sum(np.linalg.norm(cluster_points - centroids[i], axis=1) ** 2)
        return sse
    def predict(self, X):
        """预测新数据的簇标签"""
        distances = self._compute_distance(X, self.centroids)
        return self._assign_clusters(distances)

class HierarchicalClustering:
    def __init__(self, max_k=8):
        self.max_k = max_k
        self.all_results = {}  # 存储所有K值的结果
    def _compute_distance_matrix(self, X):
        """计算距离矩阵"""
        n = X.shape[0]
        distance_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i+1, n):
                distance_matrix[i, j] = np.linalg.norm(X[i] - X[j])
                distance_matrix[j, i] = distance_matrix[i, j]
        return distance_matrix
    def _compute_cluster_distance(self, cluster1, cluster2, distance_matrix):
        """计算两个簇之间的距离（平均链接）"""
        total_distance = 0
        count = 0
        for i in cluster1:
            for j in cluster2:
                total_distance += distance_matrix[i, j]
                count += 1
        return total_distance / count if count > 0 else float('inf')
    def fit(self, X):
        """训练层次聚类模型，记录所有K值的结果"""
        n = X.shape[0]
        distance_matrix = self._compute_distance_matrix(X)
        # 初始化：每个点作为一个簇
        clusters = [[i] for i in range(n)]
        # 记录当前聚类结果
        current_labels = np.arange(n)
        self.all_results[n] = {
            'labels': current_labels.copy(),
            'clusters': [cluster.copy() for cluster in clusters]
        }
        # 逐步合并簇，直到只剩下1个簇
        while len(clusters) > 1:
            # 找到距离最近的两个簇
            min_distance = float('inf')
            merge_i, merge_j = -1, -1
            for i in range(len(clusters)):
                for j in range(i+1, len(clusters)):
                    distance = self._compute_cluster_distance(clusters[i], clusters[j], distance_matrix)
                    if distance < min_distance:
                        min_distance = distance
                        merge_i, merge_j = i, j
            # 合并簇
            clusters[merge_i].extend(clusters[merge_j])
            clusters.pop(merge_j)
            # 更新标签
            current_labels = np.zeros(n, dtype=int)
            for cluster_idx, cluster in enumerate(clusters):
                for point_idx in cluster:
                    current_labels[point_idx] = cluster_idx
            # 记录当前K值的结果（如果K值在我们关心的范围内）
            current_k = len(clusters)
            if current_k <= self.max_k:
                self.all_results[current_k] = {
                    'labels': current_labels.copy(),
                    'clusters': [cluster.copy() for cluster in clusters]
                }
        return self
    def get_results(self, k):
        """获取指定K值的聚类结果"""
        if k in self.all_results:
            return self.all_results[k]['labels']
        else:
            raise ValueError(f"K值 {k} 不在记录范围内")

def evaluate_clustering(X, labels, method_name):
    """评估聚类结果"""
    if len(np.unique(labels)) == 1:
        print(f"{method_name} - 警告：所有样本都在同一个簇中，无法计算轮廓系数")
        silhouette_avg = -1
    else:
        silhouette_avg = silhouette_score(X, labels)
        print(f"{method_name} - 轮廓系数: {silhouette_avg:.4f}")
    # 计算SSE
    sse = 0
    unique_labels = np.unique(labels)
    for label in unique_labels:
        cluster_points = X[labels == label]
        centroid = cluster_points.mean(axis=0)
        sse += np.sum(np.linalg.norm(cluster_points - centroid, axis=1) ** 2)
    print(f"{method_name} - SSE: {sse:.4f}")
    return silhouette_avg, sse

def find_elbow_k(k_values, sse_values):
    """寻找SSE肘部（下降骤减处）对应的K值"""
    # 计算SSE的二次差分，找到变化最大的点
    sse_array = np.array(sse_values)
    # 计算一阶差分
    first_diff = np.diff(sse_array)
    # 计算二阶差分（变化率的变化）
    second_diff = np.diff(first_diff)
    # 找到二阶差分最大的点（变化最剧烈的点）
    if len(second_diff) > 0:
        elbow_idx = np.argmax(np.abs(second_diff)) + 1  # +1 因为二阶差分比原始数据少2个点
        elbow_k = k_values[elbow_idx]
    else:
        # 如果没有明显的肘部，选择SSE开始平缓的点
        # 计算SSE的相对变化率
        relative_change = [abs((sse_values[i] - sse_values[i-1]) / sse_values[i-1]) for i in range(1, len(sse_values))]
        if len(relative_change) > 0:
            # 找到变化率小于平均变化率一半的第一个点
            avg_change = np.mean(relative_change)
            for i, change in enumerate(relative_change):
                if change < avg_change * 0.5:
                    elbow_k = k_values[i+1]
                    break
            else:
                elbow_k = k_values[len(relative_change) // 2]  # 默认选择中间值
        else:
            elbow_k = k_values[len(k_values) // 2]
    return elbow_k

def find_optimal_k(k_values, sse_values, silhouette_scores):
    """在肘部之后选取轮廓系数峰值作为最优K值"""
    # 寻找肘部点
    elbow_k = find_elbow_k(k_values, sse_values)
    print(f"检测到的肘部K值: {elbow_k}")
    # 找到肘部点在k_values中的索引
    elbow_idx = k_values.index(elbow_k)
    # 在肘部点及之后的K值中寻找轮廓系数峰值
    candidate_k_values = k_values[elbow_idx:]
    candidate_silhouettes = silhouette_scores[elbow_idx:]
    if len(candidate_k_values) == 0:
        # 如果没有候选K值，则在整个范围内选择轮廓系数峰值
        optimal_idx = np.argmax(silhouette_scores)
        optimal_k = k_values[optimal_idx]
        print(f"肘部后无候选K值，选择全局轮廓系数峰值: K={optimal_k}")
    else:
        # 在候选K值中选择轮廓系数峰值
        candidate_optimal_idx = np.argmax(candidate_silhouettes)
        optimal_k = candidate_k_values[candidate_optimal_idx]
        print(f"在肘部K={elbow_k}及之后的范围{list(candidate_k_values)}中，选择轮廓系数峰值: K={optimal_k}")
    return optimal_k

def visualize_clustering_separate(X, kmeans_labels, hierarchical_labels, kmeans_centroids, kmeans_k, hierarchical_k):
    """分别使用t-SNE可视化K-means和层次聚类的聚类结果"""
    # t-SNE降维
    tsne = TSNE(n_components=2, random_state=105, perplexity=6)
    X_tsne = tsne.fit_transform(X)
    # 绘制结果 - 两个子图分别显示两种方法
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    # K-means结果
    scatter1 = ax1.scatter(X_tsne[:, 0], X_tsne[:, 1], c=kmeans_labels, cmap='viridis', alpha=0.7)
    # 绘制K-means质心（在t-SNE空间中）
    centroids_tsne = []
    for i in range(len(kmeans_centroids)):
        # 找到最接近质心的点
        distances = np.linalg.norm(X - kmeans_centroids[i], axis=1)
        closest_point_idx = np.argmin(distances)
        centroids_tsne.append(X_tsne[closest_point_idx])
    centroids_tsne = np.array(centroids_tsne)
    ax1.scatter(centroids_tsne[:, 0], centroids_tsne[:, 1], marker='x', s=200, linewidths=3, color='red', label='质心')
    ax1.set_title(f'K-means 聚类 (K={kmeans_k})')
    ax1.legend()
    # 层次聚类结果
    scatter2 = ax2.scatter(X_tsne[:, 0], X_tsne[:, 1], c=hierarchical_labels, cmap='viridis', alpha=0.7)
    ax2.set_title(f'层次聚类 (K={hierarchical_k})')
    # 添加颜色条
    plt.colorbar(scatter1, ax=ax1)
    plt.colorbar(scatter2, ax=ax2)
    plt.tight_layout()
    plt.show()

# 加载数据
filename = '../data/rural_income_2020.xlsx'
X, feature_names, original_data = load_and_preprocess_data_without_region(filename)
print(f"\n数据形状: {X.shape}")
print(f"特征名称: {feature_names}")
# 测试不同的K值
k_values = range(2, 16)
kmeans_results = []

print("\n=== K-means调参过程和结果 ===")
# K-means需要为每个K值单独训练
# 记录收敛轮次
convergence_rounds = []
for k in k_values:
    print(f"\n--- K = {k} ---")
    # K-means聚类
    kmeans = KMeans(k=k, random_state=42)
    kmeans.fit(X)
    kmeans_silhouette, kmeans_sse = evaluate_clustering(X, kmeans.labels, "K-means")
    kmeans_results.append({
        'k': k,
        'silhouette': kmeans_silhouette,
        'sse': kmeans_sse,
        'model': kmeans
    })
    convergence_rounds.append(kmeans.iteration)
# 绘制收敛轮次折线图
plt.figure(figsize=(10, 5))
plt.plot(k_values, convergence_rounds, marker='o')
plt.xlabel('K值')
plt.ylabel('收敛轮次')
plt.title('K-means收敛轮次随K值变化')
plt.grid(True)
plt.show()

# 层次聚类训练
print("\n=== 层次聚类调参过程和结果 ===")
hierarchical = HierarchicalClustering(max_k=max(k_values))
hierarchical.fit(X)
hierarchical_results = []
for k in k_values:
    print(f"\n--- K = {k} ---")
    hierarchical_labels = hierarchical.get_results(k)
    hierarchical_silhouette, hierarchical_sse = evaluate_clustering(X, hierarchical_labels, "层次聚类")
    hierarchical_results.append({
        'k': k,
        'silhouette': hierarchical_silhouette,
        'sse': hierarchical_sse,
        'labels': hierarchical_labels
    })

print(f"\n=== 最佳K值选择 ===")
# K-means最佳K值选择
kmeans_silhouettes = [result['silhouette'] for result in kmeans_results]
kmeans_sses = [result['sse'] for result in kmeans_results]
kmeans_elbow_k = find_elbow_k(k_values, kmeans_sses)
# 使用新策略选择K-means最佳K值
best_kmeans_k = find_optimal_k(list(k_values), kmeans_sses, kmeans_silhouettes)
best_kmeans_idx = list(k_values).index(best_kmeans_k)
best_kmeans = kmeans_results[best_kmeans_idx]['model']
# 层次聚类最佳K值选择
hierarchical_silhouettes = [result['silhouette'] for result in hierarchical_results]
hierarchical_sses = [result['sse'] for result in hierarchical_results]
hierarchical_elbow_k = find_elbow_k(k_values, hierarchical_sses)
# 使用新策略选择层次聚类最佳K值
best_hierarchical_k = find_optimal_k(list(k_values), hierarchical_sses, hierarchical_silhouettes)
best_hierarchical_labels = hierarchical.get_results(best_hierarchical_k)
print(f"\n最终选择的K值:")
print(f"K-means最佳K值: {best_kmeans_k} (轮廓系数: {kmeans_silhouettes[best_kmeans_idx]:.4f})")
print(f"层次聚类最佳K值: {best_hierarchical_k} (轮廓系数: {hierarchical_silhouettes[list(k_values).index(best_hierarchical_k)]:.4f})")

# 获取最佳模型
best_kmeans_idx = best_kmeans_k - min(k_values)
best_kmeans = kmeans_results[best_kmeans_idx]['model']
best_hierarchical_labels = hierarchical.get_results(best_hierarchical_k)

# 绘制评估指标图
plt.figure(figsize=(12, 5))
# 轮廓系数图
plt.subplot(1, 2, 1)
plt.plot(k_values, [result['silhouette'] for result in kmeans_results], 'o-', label='K-means')
plt.plot(k_values, [result['silhouette'] for result in hierarchical_results], 's-', label='层次聚类')
# 标记最佳K值
plt.axvline(x=best_kmeans_k, color='blue', linestyle='--', alpha=0.7, label=f'K-means最佳K={best_kmeans_k}')
plt.axvline(x=best_hierarchical_k, color='orange', linestyle='--', alpha=0.7, label=f'层次聚类最佳K={best_hierarchical_k}')
plt.xlabel('K值')
plt.ylabel('轮廓系数')
plt.title('轮廓系数 vs K值')
plt.legend()
plt.grid(True)
# SSE图（肘部法则）
plt.subplot(1, 2, 2)
plt.plot(k_values, [result['sse'] for result in kmeans_results], 'o-', label='K-means')
plt.plot(k_values, [result['sse'] for result in hierarchical_results], 's-', label='层次聚类')
# 标记肘部K值
plt.axvline(x=kmeans_elbow_k, color='blue', linestyle='--', alpha=0.7, label=f'K-means肘部K={kmeans_elbow_k}')
plt.axvline(x=hierarchical_elbow_k, color='orange', linestyle='--', alpha=0.7, label=f'层次聚类肘部K={hierarchical_elbow_k}')
plt.xlabel('K值')
plt.ylabel('SSE')
plt.title('肘部法则图')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

print(f"\n=== 使用最佳K值进行可视化 ===")
print(f"K-means最佳K值: {best_kmeans_k}")
print(f"层次聚类最佳K值: {best_hierarchical_k}")
# 分别可视化K-means和层次聚类的最佳结果
visualize_clustering_separate(X, best_kmeans.labels, best_hierarchical_labels, best_kmeans.centroids, best_kmeans_k, best_hierarchical_k)
# 输出聚类统计信息
print(f"\n=== 聚类统计信息 ===")
print(f"K-means聚类分布 (K={best_kmeans_k}):")
unique, counts = np.unique(best_kmeans.labels, return_counts=True)
for cluster, count in zip(unique, counts):
    print(f"  簇 {cluster}: {count} 个样本")
print(f"\n层次聚类分布 (K={best_hierarchical_k}):")
unique, counts = np.unique(best_hierarchical_labels, return_counts=True)
for cluster, count in zip(unique, counts):
    print(f"  簇 {cluster}: {count} 个样本")

import pandas as pd
import numpy as np
df = pd.read_excel(filename)
# 添加K-means分类结果列
df['K均值聚类'] = best_kmeans.labels
# 添加层次聚类分类结果列
df['层次聚类'] = best_hierarchical_labels
# 显示结果
print("\n添加分类结果后的数据集：")
print(df.head(31))  # 只显示前几行
print(f"\n数据集形状: {df.shape}")
# 保存
df.to_excel('../data/clustering_results.xlsx', index=False)
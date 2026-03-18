# %%
import pandas as pd
import numpy as np
from collections import Counter
import warnings
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.metrics import classification_report, f1_score
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
import matplotlib.pyplot as plt
warnings.filterwarnings(action='ignore')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# %% [markdown]
# # 任务一：使用Python自编程构建K近邻模型，实现空气质量的预测与评价
# %%
def load_and_preprocess_data():
    """加载并预处理数据"""
    # 分别读取训练集和测试集
    print("加载训练集...")
    df_train = pd.read_excel('../data/beijing_air_quality_train.xlsx')
    print("加载测试集...")
    df_test = pd.read_excel('../data/beijing_air_quality_test.xlsx')
    # 处理数值列的0值和NaN值
    numeric_columns = ['PM2.5', 'PM10', 'SO2', 'CO', 'NO2', 'O3']
    # 首先将空气质量等级转换为数值，以便分组
    quality_mapping = {'优': 0, '良': 1, '轻度污染': 2, '中度污染': 3, '重度污染': 4, '严重污染': 5}
    df_train['质量等级_数值'] = df_train['质量等级'].map(quality_mapping)
    df_test['质量等级_数值'] = df_test['质量等级'].map(quality_mapping)
    # 处理训练集的0值
    for col in numeric_columns:
        for quality_level in range(6):
            mask = (df_train['质量等级_数值'] == quality_level) & (df_train[col] != 0)
            median_val = df_train.loc[mask, col].median()  # 使用中位数
            if not pd.isna(median_val):
                df_train.loc[(df_train['质量等级_数值'] == quality_level) & (df_train[col] == 0), col] = median_val
    # 处理测试集的0值（使用训练集对应类别的均值）
    print("\n处理测试集0值...")
    for col in numeric_columns:
        for quality_level in range(6):  # 0-5 对应不同的空气质量等级
            mask = (df_train['质量等级_数值'] == quality_level) & (df_train[col] != 0)
            mean_val = df_train.loc[mask, col].mean()  # 使用训练集的均值
            if not pd.isna(mean_val):  # 确保均值不是NaN
                df_test.loc[(df_test['质量等级_数值'] == quality_level) & (df_test[col] == 0), col] = mean_val
    # 检查并处理特征列中的NaN值
    print("\n检查特征列中的NaN值:")
    for col in numeric_columns:
        train_nan = df_train[col].isnull().sum()
        test_nan = df_test[col].isnull().sum()
        if train_nan > 0 or test_nan > 0:
            print(f"{col} - 训练集NaN值: {train_nan}, 测试集NaN值: {test_nan}")
            # 使用对应类别的均值填充NaN值
            for quality_level in range(6):
                mask = df_train['质量等级_数值'] == quality_level
                mean_val = df_train.loc[mask, col].mean()
                if not pd.isna(mean_val):
                    df_train.loc[mask & df_train[col].isnull(), col] = mean_val
                    df_test.loc[df_test['质量等级_数值'] == quality_level & df_test[col].isnull(), col] = mean_val
    # 删除包含NaN值的行
    df_train = df_train.dropna()
    df_test = df_test.dropna()
    # 确保所有数据都是数值类型
    for col in numeric_columns:
        df_train[col] = pd.to_numeric(df_train[col], errors='coerce')
        df_test[col] = pd.to_numeric(df_test[col], errors='coerce')
    # 选择特征和目标变量
    features = ['PM2.5', 'PM10', 'SO2', 'CO', 'NO2', 'O3']
    X_train = df_train[features].values
    y_train = df_train['质量等级_数值'].values
    X_test = df_test[features].values
    y_test = df_test['质量等级_数值'].values
    print(f"\n训练集大小: {X_train.shape[0]}")
    print(f"测试集大小: {X_test.shape[0]}")
    return X_train, y_train, X_test, y_test, quality_mapping, features
# %%
def feature_effectiveness_analysis(X, y, feature_names):
    """特征有效性分析"""
    print("\n" + "="*60)
    print("特征有效性分析")
    print("="*60)
    # 1. 单变量特征分析（F检验）
    print("\n1. 单变量特征分析 (F检验):")
    selector = SelectKBest(score_func=f_classif, k='all')
    selector.fit(X, y)
    f_scores = pd.DataFrame({
        '特征': feature_names,
        'F值': selector.scores_,
        'P值': selector.pvalues_
    }).sort_values('F值', ascending=False)
    print(f_scores)
    # 2. PCA分析
    print("\n2. PCA分析:")
    # 标准化数据
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # 执行PCA
    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)
    # 计算方差贡献度
    explained_variance_ratio = pca.explained_variance_ratio_
    cumulative_variance_ratio = np.cumsum(explained_variance_ratio)
    # 获取特征重要性（主成分载荷）
    components = pca.components_
    # 为每个主成分找到最重要的原始特征
    feature_importance = []
    for i, component in enumerate(components):
        # 获取每个主成分中绝对值最大的特征索引
        max_feature_idx = np.argmax(np.abs(component))
        feature_importance.append(feature_names[max_feature_idx])
    # 创建PCA结果表格
    pca_results = pd.DataFrame({
        '主成分': [f'PC{i+1}({feature})' for i, feature in enumerate(feature_importance)],
        '方差贡献度': explained_variance_ratio,
        '累计方差贡献度': cumulative_variance_ratio
    })
    print(pca_results)
    # 3. 特征选择建议
    print("\n3. 特征选择建议:")
    # 基于F检验选择特征
    significant_features_f = f_scores[f_scores['P值'] < 0.05]['特征'].tolist()
    print(f"基于F检验的显著特征 (p<0.05): {significant_features_f}")
    # 基于PCA选择特征
    # 找到累计贡献度超过85%的主成分数量
    n_components_85 = np.argmax(cumulative_variance_ratio >= 0.85) + 1
    print(f"达到85%累计方差贡献度所需主成分数: {n_components_85}")
    # 绘制特征重要性图
    plt.figure(figsize=(15, 5))
    # 子图1: F值
    plt.subplot(1, 3, 1)
    plt.barh(f_scores['特征'], f_scores['F值'])
    plt.xlabel('F值')
    plt.title('特征F值重要性')
    # 子图2: 方差贡献度
    plt.subplot(1, 3, 2)
    plt.bar(pca_results['主成分'], pca_results['方差贡献度'])
    plt.xlabel('主成分')
    plt.ylabel('方差贡献度')
    plt.title('各主成分方差贡献度')
    plt.xticks(rotation=45)
    # 子图3: 累计方差贡献度
    plt.subplot(1, 3, 3)
    plt.plot(range(1, len(cumulative_variance_ratio)+1), cumulative_variance_ratio, 'bo-')
    plt.axhline(y=0.85, color='r', linestyle='--', label='85%阈值')
    plt.xlabel('主成分数量')
    plt.ylabel('累计方差贡献度')
    plt.title('累计方差贡献度')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    return significant_features_f, n_components_85
# %%
def select_features(X, y, feature_names, method='pca', scaler_method='standard', n_features=None):
    """特征选择"""
    # 不同的特征缩放方法
    if scaler_method == 'standard':
        scaler = StandardScaler()
    elif scaler_method == 'minmax':
        scaler = MinMaxScaler()
    elif scaler_method == 'robust':
        scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    if method == 'pca':
        # 使用PCA选择特征
        if n_features is None:
            # 自动选择达到85%方差贡献度的主成分数
            pca = PCA()
            X_pca = pca.fit_transform(X_scaled)
            cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
            n_features = np.argmax(cumulative_variance >= 0.85) + 1
        pca = PCA(n_components=n_features)
        X_selected = pca.fit_transform(X_scaled)
        # 获取特征重要性（主成分载荷）
        components = pca.components_
        # 为每个主成分找到最重要的原始特征
        feature_importance = []
        for i, component in enumerate(components):
            # 获取每个主成分中绝对值最大的特征索引
            max_feature_idx = np.argmax(np.abs(component))
            feature_importance.append(feature_names[max_feature_idx])
        print(f"使用PCA选择了 {n_features} 个主成分，累计方差贡献度: {np.sum(pca.explained_variance_ratio_):.4f}")
        print(f"各主成分主要对应的原始特征: {feature_importance}")
        # 创建特征名称映射
        pca_feature_names = [f"PC{i+1}({feature})" for i, feature in enumerate(feature_importance)]
        return X_selected, scaler, pca, pca_feature_names
    elif method == 'f_test':
        # 使用F检验选择特征
        if n_features is None:
            n_features = 4  # 默认选择4个最重要的特征
        selector = SelectKBest(score_func=f_classif, k=n_features)
        X_selected = selector.fit_transform(X_scaled, y)
        selected_indices = selector.get_support(indices=True)
        selected_features = [feature_names[i] for i in selected_indices]
        print(f"使用F检验选择了 {n_features} 个特征: {selected_features}")
        return X_selected, scaler, selector, selected_features
    else:
        # 不使用特征选择
        print("不使用特征选择，使用所有原始特征")
        return X_scaled, scaler, None, feature_names
# %%
class MyKNN:
    """自编程实现K-近邻算法"""
    def __init__(self, k=5, weights='uniform'):
        self.k = k
        self.weights = weights
        self.X_train = None
        self.y_train = None
    def fit(self, X, y):
        """训练模型"""
        self.X_train = X
        self.y_train = y
        return self
    def euclidean_distance(self, x1, x2):
        """计算欧氏距离"""
        return np.sqrt(np.sum((x1 - x2) ** 2))
    def predict(self, X_test):
        """预测"""
        if self.X_train is None or self.y_train is None:
            raise ValueError("模型尚未训练，请先调用fit方法")
        if len(X_test) == 0:
            return np.array([])
        predictions = []
        for x in X_test:
            # 计算与所有训练样本的距离
            distances = [self.euclidean_distance(x, x_train) for x_train in self.X_train]
            # 获取最近的k个邻居的索引
            k_indices = np.argsort(distances)[:self.k]
            # 获取这k个邻居的标签
            k_nearest_labels = [self.y_train[i] for i in k_indices]
            # 投票决定预测结果
            most_common = Counter(k_nearest_labels).most_common(1)
            predictions.append(most_common[0][0])
        return np.array(predictions)
# %%
def evaluate_model(y_true, y_pred, model_name):
    """评估模型性能"""
    print(f"\n{model_name} 评估结果:")
    print("=" * 50)
    # 获取实际存在的类别并转换为整数
    unique_labels = np.unique(np.concatenate([y_true, y_pred])).astype(int)
    quality_labels = ['优', '良', '轻度污染', '中度污染', '重度污染', '严重污染']
    actual_labels = [quality_labels[i] for i in unique_labels]
    # 计算加权F1分数
    weighted_f1 = f1_score(y_true, y_pred, average='weighted')
    print(f"加权F1分数: {weighted_f1:.4f}")
    # 详细分类报告
    print("\n详细分类报告:")
    print(classification_report(y_true, y_pred, labels=unique_labels, target_names=actual_labels))
    return weighted_f1
# %%
def find_best_k(X_train, y_train, X_val, y_val, k_range):
    """寻找最佳K值"""
    print("调参过程:")
    print("=" * 30)
    best_k = 1
    best_score = 0
    results = []
    for k in k_range:
        # 自编程KNN
        my_knn = MyKNN(k=k)
        my_knn.fit(X_train, y_train)
        y_pred_val = my_knn.predict(X_val)
        score = f1_score(y_val, y_pred_val, average='weighted')
        results.append((k, score))
        print(f"K={k}, 加权F1分数: {score:.4f}")
        if score > best_score:
            best_score = score
            best_k = k
    print(f"\n最佳K值: {best_k}, 最佳加权F1分数: {best_score:.4f}")
    # 绘制K值与F1分数关系图
    plt.figure(figsize=(10, 6))
    k_values, scores = zip(*results)
    plt.plot(k_values, scores, 'bo-', linewidth=2, markersize=8)
    plt.xticks(k_values)
    plt.xlabel('K值')
    plt.ylabel('加权F1分数')
    plt.title('K值与模型性能关系')
    plt.grid(True, alpha=0.3)
    plt.show()
    return best_k
# %%
def main():
    """主函数"""
    print("实验四：使用K-近邻模型实现空气质量的预测")
    print("=" * 60)
    # 1. 加载和预处理数据
    print("步骤1: 数据加载和预处理")
    X_train, y_train, X_test, y_test, quality_mapping, feature_names = load_and_preprocess_data()
    # 2. 从训练集中划分验证集
    print("\n步骤2: 从训练集划分验证集")
    X_train_split, X_val, y_train_split, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42, stratify=y_train)
    print(f"训练集大小: {X_train_split.shape[0]}")
    print(f"验证集大小: {X_val.shape[0]}")
    print(f"测试集大小: {X_test.shape[0]}")
    # 3. 特征有效性分析
    print("\n步骤3: 特征有效性分析")
    # 使用训练集进行特征分析
    significant_features_f, n_components_85 = feature_effectiveness_analysis(X_train, y_train, feature_names)
    # 4. 特征选择
    print("\n步骤4: 特征选择")
    # 使用训练集进行特征选择
    feature_method = 'pca'  # 可选: 'pca', 'f_test', 'none'
    X_train_selected, scaler, feature_selector, selected_feature_names = select_features(
        X_train_split, y_train_split, feature_names, method=feature_method)
    # 对验证集和测试集应用相同的特征选择
    if feature_method == 'pca':
        X_val_selected = scaler.transform(X_val)
        X_val_selected = feature_selector.transform(X_val_selected)
        X_test_selected = scaler.transform(X_test)
        X_test_selected = feature_selector.transform(X_test_selected)
    elif feature_method == 'f_test':
        X_val_selected = scaler.transform(X_val)
        X_val_selected = feature_selector.transform(X_val_selected)
        X_test_selected = scaler.transform(X_test)
        X_test_selected = feature_selector.transform(X_test_selected)
    else:
        # 不使用特征选择，只进行标准化
        X_val_selected = scaler.transform(X_val)
        X_test_selected = scaler.transform(X_test)
    print(f"训练集特征维度: {X_train_selected.shape[1]}")
    print(f"验证集特征维度: {X_val_selected.shape[1]}")
    print(f"测试集特征维度: {X_test_selected.shape[1]}")
    # 5. 调参寻找最佳K值（使用训练集和验证集）
    print("\n步骤5: 调参过程")
    k_range = range(1, 21)
    best_k = find_best_k(X_train_selected, y_train_split, X_val_selected, y_val, k_range)
    # 6. 使用最佳K值训练自编程KNN模型
    print("\n步骤6: 自编程KNN模型训练和评估")
    my_knn_best = MyKNN(k=best_k, weights='distance')
    my_knn_best.fit(X_train_selected, y_train_split)
    # 在测试集上评估
    y_pred_myknn = my_knn_best.predict(X_test_selected)
    f1_myknn = evaluate_model(y_test, y_pred_myknn, "自编程KNN模型")
    # 7. 使用sklearn的KNN模型
    print("\n步骤7: sklearn KNN模型训练和评估")
    sklearn_knn = KNeighborsClassifier(n_neighbors=best_k, weights='distance')
    sklearn_knn.fit(X_train_selected, y_train_split)
    # 在测试集上评估
    y_pred_sklearn = sklearn_knn.predict(X_test_selected)
    f1_sklearn = evaluate_model(y_test, y_pred_sklearn, "sklearn KNN模型")
    # 8. 交叉验证（使用训练集）
    print("\n步骤8: 交叉验证")
    cv_scores = cross_val_score(sklearn_knn, X_train_selected, y_train_split, cv=4, scoring='f1_weighted')
    print(f"4折交叉验证平均加权F1分数: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    # 9. 检查是否满足要求
    print("\n" + "=" * 60)
    print("实验要求检查:")
    print(f"自编程KNN加权F1分数: {f1_myknn:.4f} {'✓ 达到要求' if f1_myknn > 0.85 else '✗ 未达到要求'}")
    print(f"sklearn KNN加权F1分数: {f1_sklearn:.4f} {'✓ 达到要求' if f1_sklearn > 0.85 else '✗ 未达到要求'}")
    # 10. 模型比较
    print("\n模型比较:")
    comparison_df = pd.DataFrame({
        '模型': ['自编程KNN', 'sklearn KNN'],
        '特征选择方法': [feature_method, feature_method],
        '特征维度': [X_train_selected.shape[1], X_train_selected.shape[1]],
        '最佳K值': [best_k, best_k],
        '加权F1分数': [f1_myknn, f1_sklearn],
        '是否达标': ['是' if f1_myknn > 0.85 else '否', '是' if f1_sklearn > 0.85 else '否']
    })
    print(comparison_df)
# %%
if __name__ == "__main__":
    main()
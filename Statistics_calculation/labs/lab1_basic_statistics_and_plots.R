vec <- seq(from = 10, to = 30, by = 3)

print(vec)

mat <- matrix(x, nrow = 2, ncol = 3, byrow = TRUE)
rownames(mat) <- c("row1", "row2")
colnames(mat) <- c("C.1", "C.2", "C.3")
print(mat)


set.seed(1011)

# 1. 生成t(1)分布的1000个随机数
t1_random <- rt(1000, df = 1)

# 2. 生成F(2,5)分布的1000个随机数
f25_random <- rf(1000, df1 = 2, df2 = 5)

# 3. 生成混合正态分布的200个随机数
# 100个N(0,1)和100个N(1,5)
normal1 <- rnorm(100, mean = 0, sd = 1)
normal2 <- rnorm(100, mean = 1, sd = sqrt(5))  # 注意：R中使用标准差，所以sd=sqrt(5)
mixed_normal <- c(normal1, normal2)

# 创建图形布局
par(mfrow = c(3, 2))  # 3行2列的图形布局

# 绘制t(1)分布的图形
plot(t1_random, main = "t(1)分布散点图", xlab = "索引", ylab = "值", pch = 20, col = "blue")
hist(t1_random, main = "t(1)分布直方图", xlab = "值", col = "lightblue", breaks = 30)

# 绘制F(2,5)分布的图形
plot(f25_random, main = "F(2,5)分布散点图", xlab = "索引", ylab = "值", pch = 20, col = "red")
hist(f25_random, main = "F(2,5)分布直方图", xlab = "值", col = "lightcoral", breaks = 30)

# 绘制混合正态分布的图形
plot(mixed_normal, main = "混合正态分布散点图", xlab = "索引", ylab = "值", pch = 20, col = "green")
hist(mixed_normal, main = "混合正态分布直方图", xlab = "值", col = "lightgreen", breaks = 30)

# 恢复默认图形布局
par(mfrow = c(1, 1))

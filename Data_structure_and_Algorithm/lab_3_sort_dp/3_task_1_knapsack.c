#include <stdio.h>
#include <stdlib.h>

int main() {
    int C, n;
    scanf("%d %d", &C, &n);

    // 不同时间点获得的最大价值
    int *dp = (int*)calloc(C + 1, sizeof(int));

    for (int i = 0; i < n; i++) {
        int ci, wi;
        scanf("%d %d", &ci, &wi);
        // 对第i种草药,遍历采草药的时间ci至总时间C
        for (int j = ci; j <= C; j++) {
            // 若j-ci时能采集到的最大价值与采集i之和大于当前最优值,替换
            if (dp[j - ci] + wi > dp[j]) {
                dp[j] = dp[j - ci] + wi;
            }
        }
    }

    printf("%d\n", dp[C]);
    free(dp);
    return 0;
}

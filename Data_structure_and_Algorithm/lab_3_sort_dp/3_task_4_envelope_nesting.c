#include <stdio.h>
#include <stdlib.h>

// 信封结构体
typedef struct {
    int width;
    int height;
} Envelope;

int compare(const void* a, const void* b) {
    const Envelope* e1 = (const Envelope*)a;
    const Envelope* e2 = (const Envelope*)b;
    if (e1->width != e2->width) {
        return e1->width - e2->width; // 宽度升序排列
    } else {
        return e2->height - e1->height; // 宽度相同时高度降序排列
    }
}

int maxEnvelopes(Envelope* envelopes, int n) {
    // 排序
    qsort(envelopes, n, sizeof(Envelope), compare);
    // 统计最大嵌套层数
    int max = 0;
    int *dp = (int*)calloc(n, sizeof(int));
    // 遍历信封
    for (int i = 0; i < n; i++){
        // 当前信封嵌套层数为可装进的信封的最大嵌套层数+1
        for (int j = 0; j < i; j++){
            if (envelopes[i].height > envelopes[j].height && envelopes[i].width > envelopes[j].width && dp[j]+1 > dp[i]){
                dp[i] = dp[j] + 1;
            }
        }
        // 若大于当前最大值,更新最大值
        if (dp[i] > max){
            max = dp[i];
        }
    }
    free(dp);
    // 实际最大值要+1
    return max + 1;
}

int main() {
    int n;
    scanf("%d", &n);

    Envelope* envelopes = (Envelope*)malloc(n * sizeof(Envelope));
    for (int i = 0; i < n; i++) {
        scanf("%d %d", &envelopes[i].width, &envelopes[i].height);
    }

    int result = maxEnvelopes(envelopes, n);
    printf("%d\n", result);

    free(envelopes);
    return 0;
}

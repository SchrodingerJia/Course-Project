#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int original;   // 原始值
    int mapped;     // 映射值
    int index;      // 原始索引
} Node;

int compare(const void *a, const void *b) {
    const Node *nodeA = (const Node *)a;
    const Node *nodeB = (const Node *)b;
    // 映射值递减排序
    if (nodeA->mapped < nodeB->mapped) return -1;
    if (nodeA->mapped > nodeB->mapped) return 1;
    // 映射值相等时,比较索引值
    return nodeA->index - nodeB->index;
}

void sortJumbled(int *mapping, int *nums, int numsSize) {
    Node *nodes = (Node *)malloc(numsSize * sizeof(Node));
    for (int i = 0; i < numsSize; i++) {
        int num = nums[i];
        int mapped = 0; // 标记位
        // 数字转字符串
        char buffer[20];
        snprintf(buffer, sizeof(buffer), "%d", num);
        // 从最高位开始,逐位映射
        for (int j = 0; buffer[j] != '\0'; j++) {
            char c = buffer[j];
            int digit = c - '0';
            mapped = mapped * 10 + mapping[digit];  // 左移一位后,增添当前位
        }
        nodes[i].original = num;
        nodes[i].mapped = mapped;
        nodes[i].index = i;
    }
    // 排序
    qsort(nodes, numsSize, sizeof(Node), compare);
    // 输出
    for (int i = 0; i < numsSize; i++) {
        printf("%d ", nodes[i].original);
    }
    printf("\n");
    free(nodes);
}
/*****************************************************/

/******************* 读取数据 *******************/
void readInput(int **mapping, int **nums, int *numsSize) {
    scanf("%d", numsSize);

    *mapping = (int *)malloc(10 * sizeof(int));
    for (int i = 0; i < 10; i++) {
        scanf("%d", &((*mapping)[i]));
    }

    *nums = (int *)malloc((*numsSize) * sizeof(int));
    for (int i = 0; i < *numsSize; i++) {
        scanf("%d", &((*nums)[i]));
    }
}
/*****************************************************/

int main() {
    int *mapping, *nums, numsSize;
    readInput(&mapping, &nums, &numsSize);
    sortJumbled(mapping, nums, numsSize);

    return 0;
}

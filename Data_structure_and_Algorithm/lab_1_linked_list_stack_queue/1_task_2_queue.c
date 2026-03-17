#include <stdio.h>
#include <stdlib.h>

typedef int ElemType;

typedef struct {
    ElemType *elem;    // 空间基地址，空间存放纸牌正反面状态值,正/反分别用1/0表示
    int length;        // 存放纸牌数
    int listsize;      // 存放空间的容量
} SqList;

// 初始化顺序表
void InitList(SqList *L, int n) {
    L->elem = (ElemType *)malloc(n * sizeof(ElemType));
    if (!L->elem) {
        printf("内存分配失败\n");
        exit(1);
    }
    L->length = n;
    L->listsize = n+1;
    for (int i = 1; i < n+1; i++) {
        L->elem[i] = 1; // 初始所有牌正面朝上
    }
}

// 翻转纸牌
void FlipCards(SqList *L) {
    for (int k = 2; k <= L->length; k++) { // 从第2张开始，基数k从2到length
        for (int i = k; i <= L->length; i += k) { // 每隔k张牌翻转一次
            L->elem[i] = !L->elem[i]; // 翻转状态
        }
    }
}

// 输出正面朝上的纸牌编号
void PrintUpCards(SqList *L) {
    int count = 0;
    for (int i = 1; i <= L->length; i++) {
        if (L->elem[i] == 1) {
            printf("%d ", i); // 编号从1开始
            count++;
        }
    }
    printf("\n%d\n", count);
}

// 释放顺序表空间
void FreeList(SqList *L) {
    free(L->elem);
    L->elem = NULL;
    L->length = 0;
    L->listsize = 0;
}

int main() {
    int n;
    scanf("%d", &n);
    SqList L;
    InitList(&L, n);
    FlipCards(&L);
    PrintUpCards(&L);
    FreeList(&L);
    return 0;
}

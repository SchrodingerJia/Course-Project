#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char c;
    int freq;
} CharFreq;

int compare(const void* a, const void* b) {
    const CharFreq* cf1 = (const CharFreq*)a;
    const CharFreq* cf2 = (const CharFreq*)b;
    // 优先根据频率排序
    if (cf1->freq > cf2->freq) return -1;
    if (cf1->freq < cf2->freq) return 1;
    // 频率相同,按字符编码排序
    return cf1->c - cf2->c;
}

char* frequencySort(char* s) {
    // 出现次数统计
    int count[128] = {0};
    int len = strlen(s);
    for (int i = 0; i < len; ++i) {
        count[(int)s[i]]++;
    }
    // 结构化存储字符与出现次数,统计出现的字符个数
    CharFreq* arr = malloc(128 * sizeof(CharFreq));
    int size = 0;
    for (int i = 0; i < 128; ++i) {
        if (count[i] > 0) {
            arr[size].c = (char)i;
            arr[size].freq = count[i];
            size++;
        }
    }
    // 排序
    qsort(arr, size, sizeof(CharFreq), compare);
    // 还原字符串
    char* result = malloc(len + 1);
    int pos = 0;
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < arr[i].freq; ++j) {
            result[pos++] = arr[i].c;
        }
    }
    result[pos] = '\0';

    free(arr);
    return result;
}

int main() {
    char s[1000];
    scanf("%s", s);

    char* result = frequencySort(s);
    printf("%s\n", result);
    free(result);

    return 0;
}

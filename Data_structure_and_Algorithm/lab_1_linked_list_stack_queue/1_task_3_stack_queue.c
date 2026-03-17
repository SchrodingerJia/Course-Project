#include <stdio.h>
#include <stdlib.h>

#define MAX_SIZE 100

// 定义栈结构体
typedef struct {
    int data[MAX_SIZE];
    int top;
} Stack;

// 初始化栈
void initStack(Stack *s) {
    s->top = -1;
}

// 判断栈是否为空
int isStackEmpty(Stack *s) {
    return s->top == -1;
}

// 判断栈是否已满
int isStackFull(Stack *s) {
    return s->top == MAX_SIZE - 1;
}

// 入栈操作
void push(Stack *s, int value) {
    if (isStackFull(s)) {
        printf("栈已满，无法入栈\n");
        exit(1);
    }
    s->data[++(s->top)] = value;
}

// 出栈操作
int pop(Stack *s) {
    if (isStackEmpty(s)) {
        printf("栈为空，无法出栈\n");
        exit(1);
    }
    return s->data[(s->top)--];
}

// 获取栈顶元素
int peek(Stack *s) {
    if (isStackEmpty(s)) {
        printf("栈为空，无法获取栈顶元素\n");
        exit(1);
    }
    return s->data[s->top];
}

// 定义队列结构体
typedef struct {
    int data[MAX_SIZE];
    int front;
    int rear;
} Queue;

// 初始化队列
void initQueue(Queue *q) {
    q->front = 0;
    q->rear = 0;
}

// 判断队列是否为空
int isQueueEmpty(Queue *q) {
    return q->front == q->rear;
}

// 判断队列是否已满
int isQueueFull(Queue *q) {
    return (q->rear + 1) % MAX_SIZE == q->front;
}

// 入队操作
void enqueue(Queue *q, int value) {
    if (isQueueFull(q)) {
        printf("队列已满，无法入队\n");
        exit(1);
    }
    q->data[q->rear] = value;
    q->rear = (q->rear + 1) % MAX_SIZE;
}

// 出队操作
int dequeue(Queue *q) {
    if (isQueueEmpty(q)) {
        printf("队列为空，无法出队\n");
        exit(1);
    }
    int value = q->data[q->front];
    q->front = (q->front + 1) % MAX_SIZE;
    return value;
}

// 获取队首元素
int front(Queue *q) {
    if (isQueueEmpty(q)) {
        printf("队列为空，无法获取队首元素\n");
        exit(1);
    }
    return q->data[q->front];
}

void input_data(Stack *s1, Stack *s2) {
    int value;
    while (scanf("%d", &value) != EOF) {
        push(s1, value);
        if (getchar() == '\n') break;
    }
    while (scanf("%d", &value) != EOF) {
        push(s2, value);
        if (getchar() == '\n') break;
    }
}

void sort_data(Stack *s1, Stack *s2, Queue *q) {
    while (!isStackEmpty(s1) && !isStackEmpty(s2)) {
        if (peek(s1) < peek(s2)) {
            enqueue(q, pop(s1));
        } else {
            enqueue(q, pop(s2));
        }
    }
    while (!isStackEmpty(s1)) {
        enqueue(q, pop(s1));
    }
    while (!isStackEmpty(s2)) {
        enqueue(q, pop(s2));
    }
}

void output_data(Queue *q) {
    while (!isQueueEmpty(q)) {
        printf("%d ", dequeue(q));
    }
    printf("\n");
}

int main() {
    Stack s1, s2;
    Queue q;
    initStack(&s1);
    initStack(&s2);
    initQueue(&q);

    input_data(&s1, &s2);
    sort_data(&s1, &s2, &q);
    output_data(&q);

    return 0;
}

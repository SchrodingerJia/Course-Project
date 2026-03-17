#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#define MAX_SIZE 1000

typedef struct {
    char data[MAX_SIZE];
    int top;
} Stack;

void initStack(Stack *s) {
    s->top = -1;
}

bool isEmpty(Stack *s) {
    return s->top == -1;
}

void push(Stack *s, char c) {
    if (s->top == MAX_SIZE - 1) {
        printf("Stack overflow\n");
        return;
    }
    s->data[++(s->top)] = c;
}

char pop(Stack *s) {
    if (isEmpty(s)) {
        printf("Stack underflow\n");
        return '\0';
    }
    return s->data[(s->top)--];
}

void Reverse(char *string, int k, char *newstring) {
    Stack stack;
    initStack(&stack);
    int len = strlen(string);
    int n = len / k;
    int i = 0;
    int j = 0;
    while (i < n + 1) {
        if (i % 2 == 0) {
            j = 0;
            while (j < k && i*k+j < len) {
                push(&stack,string[i*k+j]);
                j++;
            }
            j = 0;
            while (j < k && i*k+j < len) {
                newstring[i*k+j] = pop(&stack);
                j++;
            }
        }
        else {
            j = 0;
            while (j < k && i*k+j < len) {
                newstring[i*k+j] = string[i*k+j];
                j++;
            }
        }
        i++;
    }
}

int main() {
    char s[MAX_SIZE],ns[MAX_SIZE];
    int k;
    scanf("%s",s);
    scanf("%d",k);
    Reverse(&s,k,&ns);
    printf("%s\n",ns);
    return 0;
}

#include<stdio.h>
#include<string.h>
#include<ctype.h>
#include<stdlib.h>
#define INF 4
#define DOU 8
#define N 20
typedef union
{
    int ival;
    double dval;
}dat;
typedef struct node
{
    int type;
    dat val;
}NodeType;
typedef struct stack
{
    NodeType data;
    struct stack *next;
}STACK;
STACK *Push(STACK *top,NodeType data);
STACK *Pop(STACK *top);
NodeType OpInt(int d1,int d2,int op);
NodeType OpDouble(double d1,double d2,int op);
NodeType OpData(NodeType *d1,NodeType *d2,int op);
int isdouble(char *p);
int main(void)
{
    char word[N];
    NodeType d1,d2,d3;
    STACK *top=NULL;
    while (scanf("%s",word)==1&&word[0]!='#')
    {
        if(isdigit(word[0]))
        {
            if(isdouble(word)==0)
            {
                d1.type=4;
                d1.val.ival=atoi(word);
                d1.val.dval=atof(word);
                top=Push(top,d1);
            }
            else if(isdouble(word)==1)
            {
                d1.type=8;
                d1.val.dval=atof(word);
                top=Push(top,d1);
            }
            else
            {
                printf("Errow!");
                exit(1);
            }
        }
        else
        {
            d2=top->data;
            top=Pop(top);
            d1=top->data;
            top=Pop(top);
            d3=OpData(&d1,&d2,word[0]);
            top=Push(top,d3);
        }
    }
    d1=top->data;
    if(d1.type==4) printf("%d\n",d1.val.ival);
    else printf("%lf\n",d1.val.dval);
    top=Pop(top);
    return 0;
}
STACK *Push(STACK *top,NodeType data)
{
    STACK *p;
    p=(STACK *)malloc(sizeof(STACK));
    p->data=data;
    p->next=top;
    top=p;
    return top;
}
STACK *Pop(STACK *top)
{
    STACK *p;
    if(top==NULL)
    {
        return NULL;
    }
    else
    {
        p=top;
        top=top->next;
        free(p);
    }
    return top;
}
NodeType OpInt(int d1,int d2,int op)
{
    NodeType res;
    res.type=4;
    switch(op)
    {
    case '+':
        res.val.ival=d1+d2;
        break;
    case '-':
        res.val.ival=d1-d2;
        break;
    case '*':
        res.val.ival=d1*d2;
        break;
    case '/':
        res.val.ival=d1/d2;
        break;
    }
    res.val.dval=(double)res.val.dval;
    return res;
}
NodeType OpDouble(double d1,double d2,int op)
{
    NodeType res;
    res.type=8;
    switch(op)
    {
    case '+':
        res.val.dval=d1+d2;
        break;
    case '-':
        res.val.dval=d1-d2;
        break;
    case '*':
        res.val.dval=d1*d2;
        break;
    case '/':
        res.val.dval=d1/d2;
        break;
    }
    return res;
}
NodeType OpData(NodeType *d1,NodeType *d2,int op)
{
    NodeType res;
    if(d1->type==4&&d2->type==4)
        res=OpInt(d1->val.ival,d2->val.ival,op);
    else
        res=OpDouble(d1->val.dval,d2->val.dval,op);
    return res;
}
int isdouble(char *p)
{
    int find=0;
    while(*p!='\0')
    {
        if(*p=='.') find++;
        p++;
    }
    return find;
}

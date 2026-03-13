#include<stdio.h>
int main(void)
{
    printf("Number:ID\nName:NAME\nExperiment No.2 - program No.2\n\n");
    scanf("%d",&a);
    if(a%3==0)
    {
        b=1;
        printf("3");
    }
    if(a%5==0)
    {
        c=1;
        if(b==1)
            printf(" 5");
        else
            printf("5");
    }
    if(a%7==0)
    {
        if(b==1||c==1)
            printf(" 7");
        else
            printf("7");
    }
    if(a%3!=0&&a%5!=0&&a%7!=0)
        printf("n");
    return 0;
}
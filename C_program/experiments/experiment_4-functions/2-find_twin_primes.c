#include<stdio.h>
int F(int a)
{
    if(a==1) return 0;
    int i;
    for(i=2;i<=a/2;i++)
    {
        if(a%i==0) return 0;
    }
    return 1;
}

int main(void)
{
    int c,d,k=0,i;
    scanf("%d,%d",&c,&d);
    for(i=c;i<=d-2;i++)
    {
        if(F(i)==1&&F(i+2)==1)
        {
            printf("(%d,%d)",i,i+2);
            k++;
        }
    }
    printf("\n%d",k);
    return 0;
}


#include<stdio.h>
int F(int L[],int a)
{
    int i,s=0;
    for(i=0;i<a;i++)
    {
        if(L[i]<L[a]) s++;
    }
    return s;
}
int main(void)
{
    int n,i;
    scanf("%d",&n);
    int L[n];
    for(i=0;i<n;i++)
    {
        scanf("%d",&L[i]);
    }
    printf("0");
    for(i=1;i<n;i++)
        printf(" %d",F(L,i));
    return 0;
}

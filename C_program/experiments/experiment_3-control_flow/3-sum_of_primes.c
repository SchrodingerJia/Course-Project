#include<stdio.h>
int F(int a)
{
    printf("Number:ID\nName:NAME\nExperiment No.3 - program No.3\n\n");
    int i;
    for(i=2;i<=a/2;i++)
    {
        if(a%i==0) return 0;
    }
    return 1;
}


int main(void)
{
    int M,N,k,i,j;
    scanf("%d",&M);
    for(i=1;i<=M;i++)
    {
        int sum=0;
        scanf("%d",&N);
        scanf("%d",&k);
        if(F(k)==1) sum=k;
        for(j=2;j<=N;j++)
        {
            scanf(" %d",&k);
            if(F(k)==1) sum=sum+k;
        }
        printf("%d\n",sum);
    }
    return 0;
}
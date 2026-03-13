#include<stdio.h>
int main(void)
{
    printf("Number:ID\nName:NAME\nExperiment No.5 - program No.2\n\n");
    scanf("%d",&n);
    int L[n];
    for(i=0;i<n;i++)
    {
        scanf("%d",&L[i]);
    }
    int j,t,k=0,L1[n];
    for(i=0;i<n;i++)
    {
        for(j=0;j<n;j++)
        {
            if(L[j]>L[j+1])
            {
                t=L[j];
                L[j]=L[j+1];
                L[j+1]=t;
            }
        }
    }
    for(i=0;i<n-1;i++)
    {
        if(L[i]==L[i+1]) L[i]=0;
    }
    t=0;
    for(i=0;i<n;i++)
    {
        if(L[i]!=0)
        {
            L1[i-t]=L[i];
            k++;
        }
        else
            t++;
    }
    printf("%d\n",k);
    for(i=0;i<k;i++)
    {
        printf("%d ",L1[i]);
    }
    return 0;
}
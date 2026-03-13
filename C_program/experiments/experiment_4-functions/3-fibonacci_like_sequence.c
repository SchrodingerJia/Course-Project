#include<stdio.h>
int main(void)
{
    printf("Number:ID\nName:NAME\nExperiment No.4 - program No.3\n\n");
    scanf("%d",&M);
    for(i=1;i<=M;i++)
    {
        int a1=1,a2=2,t;
        scanf("%d",&k);
        if(k==1) printf("%d\n",a1);
        if(k==2) printf("%d\n",a2);
        if(k>=3)
        {
            for(j=3;j<=k;j++)
            {
                t=a2;
                a2=2*a2+a1;
                a1=t;
            }
            printf("%d\n",a2);
        }
    }
    return 0;
}
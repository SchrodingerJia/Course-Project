#include<stdio.h>
#include<math.h>
int Max(int a)
    printf("Number:ID\nName:NAME\nExperiment No.7 - program No.2\n\n");
    int i,j,temp,max=0,figure[4];
    for(i=0;i<4;i++)
        figure[i]=a%(int)(pow(10,i+1))/(int)(pow(10,i));
    for(i=0;i<3;i++)
    {
        for(j=i+1;j<4;j++)
        {
            if(figure[i]>figure[j])
            {
                temp=figure[i];
                figure[i]=figure[j];
                figure[j]=temp;
            }
        }
    }
    for(i=0;i<4;i++)
        max+=figure[i]*(int)(pow(10,i));
    return max;
}
int Min(int a)
{
    int i,j,temp,min=0,figure[4];
    for(i=0;i<4;i++)
        figure[i]=a%(int)(pow(10,i+1))/(int)(pow(10,i));
    for(i=0;i<3;i++)
    {
        for(j=i+1;j<4;j++)
        {
            if(figure[i]<figure[j])
            {
                temp=figure[i];
                figure[i]=figure[j];
                figure[j]=temp;
            }
        }
    }
    for(i=0;i<4;i++)
        min+=figure[i]*(int)(pow(10,i));
    return min;
}
int main(void)
{
    int x,count=1,n;
    scanf("%d",&x);
    while(x!=6174)
    {
        n=Min(x);
        x=Max(x);
        printf("[%d]:%d-%d=%d\n",count,x,n,x-n);
        x=x-n;
        count++;
    }
    return 0;
}
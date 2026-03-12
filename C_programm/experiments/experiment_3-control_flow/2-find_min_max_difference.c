#include<stdio.h>
int main(void)
{
    printf("Number:ID\nName:NAME\nExperiment No.3 - program No.2\n\n");
    scanf("%d",&n);
    scanf("%d",&k);
    min=k;
    max=k;
    for(i=2;i<=n;i++)
    {
        scanf(" %d",&k);
        if(k<=min) min=k;
        if(k>=max) max=k;
    }
    printf("%d",max-min);
    return 0;
}
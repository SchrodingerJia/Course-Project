#include<stdio.h>
int main(void)
{
    printf("Number:ID\nName:NAME\nExperiment No.3 - program No.1\n\n");
    int i,Y;
    scanf("%f %f %d",&R,&M,&Y);
    for(i=1;i<=Y;i++)
    {
        M=M*(1+R/100);
    }
    printf("%d",(int)M+1);
    return 0;
}
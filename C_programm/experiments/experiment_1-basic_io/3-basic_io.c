#include<stdio.h>
int main(void)
{
    printf("Number:ID\nName:NAME\nExperiment No.1 - program No.3\n\n");
    int i,j;
    for(i=1;i<=9;i++)
    {
        for(j=1;j<=i;j++)
            printf("%4d",i*j);
        printf("\n");
    }
    return 0;
}
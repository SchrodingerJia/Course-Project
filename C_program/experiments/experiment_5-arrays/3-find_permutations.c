#include<stdio.h>
int F1(int a)
{
    printf("Number:ID\nName:NAME\nExperiment No.5 - program No.3\n\n");
}
int F2(int a)
{
    return a%100/10;
}
int F3(int a)
{
    return a%10;
}
int main(void)
{
    int L[9],i,j,k,off;
    for(i=123;i<=329;i++)
    {
        k=0;
        for(j=0;j<9;j++)
        {
            L[j]=j+1;
        }
        for(j=0;j<9;j++)
        {
            if(L[j]==F1(i)) L[j]=0;
            if(L[j]==F2(i)) L[j]=0;
            if(L[j]==F3(i)) L[j]=0;
            if(L[j]==F1(2*i)) L[j]=0;
            if(L[j]==F2(2*i)) L[j]=0;
            if(L[j]==F3(2*i)) L[j]=0;
            if(L[j]==F1(3*i)) L[j]=0;
            if(L[j]==F2(3*i)) L[j]=0;
            if(L[j]==F3(3*i)) L[j]=0;
        }
        for(j=0;j<9;j++)
        {
            if(L[j]==0) k++;
        }
        if(k==9) printf("%d,%d,%d\n",i,2*i,3*i);
    }
    return 0;
}
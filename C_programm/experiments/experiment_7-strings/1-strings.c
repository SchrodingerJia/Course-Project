#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#define N 26
int Figure(int num[])
{
    int i,figure;
    for(i=N*2-1;i>=0;i--)
        if(num[i]!=0) return i+1;
}
int Figurestr(char str[])
{
    int i,figure;
    for(i=N*2-1;i>=0;i--)
        if(str[i]!='\0') return i+1;
}
void PrintNum(int num[],int n)
{
    int i;
    for(i=n-1;i>=0;i--)
        printf("%d",num[i]);
}
int main(void)
{
    char str1[2*N],str2[2*N];
    int i,num1[2*N-1],num2[2*N-1],sum[2*N-1];
    for(i=0;i<2*N;i++)
    {
        str1[i]='\0';
        str2[i]='\0';
    }
    gets(str1);
    gets(str2);
    int n1=Figurestr(str1),n2=Figurestr(str2);
    for(i=0;i<2*N;i++)
    {
        num1[i]=0;
        num2[i]=0;
        sum[i]=0;
    }
    for(i=0;i<n1;i++)
    {
        if(str1[i]!='\0')
            num1[n1-1-i]=(int)(str1[i])-48;
        else num1[n1-1-i]=0;
    }
    /*PrintNum(num1,Figure(num1));
    printf("\n");*/
    for(i=0;i<n2;i++)
    {
        if(str2[i]!='\0')
            num2[n2-1-i]=(int)(str2[i])-48;
        else num2[n2-1-i]=0;
    }
    /*PrintNum(num2,Figure(num2));
    printf("\n");*/
    for(i=0;i<N*2-1;i++)
        sum[i]=num1[i]+num2[i];
    /*PrintNum(sum,Figure(sum));
    printf("\n");*/
    for(i=0;i<2*N-1;i++)
    {
        sum[i+1]=sum[i]/10+sum[i+1];
        sum[i]=sum[i]%10;
    }
    PrintNum(sum,Figure(sum));
    return 0;
}

#include<stdio.h>
#define N 10
#define M 10
void Printmatrix(int *a,int m,int n)
{
    int i,j;
    for(i=0;i<m;i++)
    {
        for(j=0;j<n;j++)
        {
            printf("%-4d",*(a+i*M+j));
        }
        printf("\n");
    }
}
void InputArray(int *p,int m,int n)
{
    int i,j;
    printf("Input a %dx%d array:\n",m,n);
    for(i=0;i<m;i++)
    {
        for(j=0;j<n;j++)
        {
            scanf("%d%*c",p+i*M+j);
        }
    }
}
int FindMax(int *p,int m,int n,int *pRow,int *pCol)
{
    int i,j,max=0;
    *pRow=0;*pCol=0;
    for(i=0;i<m;i++)
    {
        for(j=0;j<n;j++)
        {
            if(*(p+i*M+j)>max)
            {
                max=*(p+i*M+j);
                *pRow=i;
                *pCol=j;
            }
        }
    }
    return max;
}
int main(void)
{
    int i,j,m,n,choice;
    printf("Input m:");
    scanf("%d",&m);
    getchar();
    printf("Input n:");
    scanf("%d",&n);
    getchar();
    int a[M][N],row,col;
    InputArray(a,m,n);
    printf("Your matrix is:\n");
    Printmatrix(a,m,n);
    int *pR=&row,*pC=&col;
    int max=FindMax(a,m,n,pR,pC);
    printf("The max number is %d,",max);
    printf("which locates on row(%d),col(%d).",row,col);
    return 0;
}

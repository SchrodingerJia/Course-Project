#include<stdio.h>
void Printmatrix(int *a,int m,int n)
{
    int i,j;
    for(i=0;i<m;i++)
    {
        for(j=0;j<n;j++)
        {
            printf("%-4d",*(a+i*m+j));
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
            scanf("%d%*c",p+i*m+j);
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
            if(*(p+i*m+j)>max)
            {
                max=*(p+i*m+j);
                *pRow=i;
                *pCol=j;
            }
        }
    }
    return max;
}
int main(void)
{
    int i,j,m,n,*p=NULL;
    printf("Input m:");
    scanf("%d",&m);
    getchar();
    printf("Input n:");
    scanf("%d",&n);
    getchar();
    p=(int *)calloc(m*n,sizeof(int));
    if(p==NULL)
    {
        printf("No enough memory!\n");
        exit(1);
    }
    int row,col;
    InputArray(p,m,n);
    printf("Your array is:\n");
    Printmatrix(p,m,n);
    int *pR=&row,*pC=&col;
    int max=FindMax(p,m,n,pR,pC);
    printf("The max grade is %d,",max);
    printf("which locates on Class(%d),No.%d.",row+1,col+1);
    free(p);
    return 0;
}

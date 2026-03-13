#include<stdio.h>
#define N 10
#define M 10
void Swap(int *p1,int *p2)
{
    int temp;
    temp=*p1;
    *p1=*p2;
    *p2=temp;
}
void Transpose1(int a[][N],int at[][M],int m,int n)
{
    int i,j;
    for(i=0;i<m;i++)
    {
        for(j=0;j<n;j++)
        {
            at[j][i]=a[i][j];
        }
    }
}
void Transpose2(int (*a)[N],int (*at)[M],int m,int n)
{
    int i,j;
    for(i=0;i<m;i++)
    {
        for(j=0;j<n;j++)
        {
            (*(at+j))[i]=(*(a+i))[j];
        }
    }
}
void Transpose3(int *a,int *at,int m,int n)
{
    int i,j;
    for(i=0;i<m;i++)
    {
        for(j=0;j<n;j++)
        {
            *(at+j*N+i)=*(a+i*M+j);
        }
    }
}
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
int main(void)
{
    int i,j,m,n,choice;
    printf("Input m:");
    scanf("%d",&m);
    getchar();
    printf("Input n:");
    scanf("%d",&n);
    getchar();
    int a[M][N],at[N][M];
    printf("Input a %dx%d matrix:\n",m,n);
    for(i=0;i<m;i++)
    {
        for(j=0;j<n;j++)
        {
            scanf("%d%*c",&a[i][j]);
        }
    }
    printf("Your matrix is:\n");
    Printmatrix(a,m,n);
    printf("Choose a function:");
    scanf("%d",&choice);
    switch(choice)
    {
    case 1:
        Transpose1(a,at,m,n);
        break;
    case 2:
        Transpose2(a,at,m,n);
        break;
    case 3:
        Transpose3(a,at,m,n);
        break;
    default:
        printf("Errow!");
        break;
    }
    printf("The transposed matrix is:\n");
    Printmatrix(at,n,m);
    return 0;
}


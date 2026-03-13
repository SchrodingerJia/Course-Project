#include<stdio.h>
#define N 10
void Swap(int *p1,int *p2)
{
    int temp;
    temp=*p1;
    *p1=*p2;
    *p2=temp;
}
void Transpose1(int a[][N],int n)
{
    int i,j;
    for(i=0;i<n;i++)
    {
        for(j=i;j<n;j++)
        {
            Swap(&a[j][i],&a[i][j]);
        }
    }
}
void Transpose2(int (*a)[N],int n)
{
    int i,j;
    for(i=0;i<n;i++)
    {
        for(j=i;j<n;j++)
        {
            Swap(*(a+i)+j,*(a+j)+i);
        }
    }
}
void Transpose3(int *a,int n)
{
    int i,j;
    for(i=0;i<n;i++)
    {
        for(j=i;j<n;j++)
        {
            Swap(a+j*N+i,a+i*N+j);
        }
    }
}
void Printmatrix(int *a,int n)
{
    int i,j;
    for(i=0;i<n;i++)
    {
        for(j=0;j<n;j++)
        {
            printf("%-4d",*(a+i*N+j));
        }
        printf("\n");
    }
}
int main(void)
{
    int i,j,n,choice;
    printf("Input n:");
    scanf("%d",&n);
    getchar();
    int a[N][N];
    printf("Input a %dx%d matrix:\n",n,n);
    for(i=0;i<n;i++)
    {
        for(j=0;j<n;j++)
        {
            scanf("%d%*c",&a[i][j]);
        }
    }
    printf("Your matrix is:\n");
    Printmatrix(a,n);
    printf("Choose a function:");
    scanf("%d",&choice);
    switch(choice)
    {
    case 1:
        Transpose1(a,n);
        break;
    case 2:
        Transpose2(a,n);
        break;
    case 3:
        Transpose3(a,n);
        break;
    default:
        printf("Errow!");
        break;
    }
    printf("The transposed matrix is:\n");
    Printmatrix(a,n);
    return 0;
}

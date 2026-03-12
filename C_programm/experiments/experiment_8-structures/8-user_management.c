#include<stdio.h>
#include<string.h>
#include<stdlib.h>
#define N 10
typedef struct user
{
    int ID;
    char name[N];
    int income;
    int expenses;
}USER;
char list[4][N]={"ID","UserName","Income","Expenses"};
int Input(USER users[N])
{
    printf("请输入用户人数：");
    int n,i;
    scanf("%d",&n);
    for(i=0;i<n;i++)
    {
        scanf("%d",&users[i].ID);
        scanf("%s",users[i].name);
        scanf("%d",&users[i].income);
        scanf("%d",&users[i].expenses);
        getchar();
    }
    return n;
}
void Reverse(USER users[N],int n)
{
    int i,j;
    USER temp;
    for(i=0;i<n;i++)
    {
        for(j=i+1;j<n;j++)
        {
            if(strcmp(users[i].name,users[j].name)<0)
            {
                temp=users[i];
                users[i]=users[j];
                users[j]=temp;
            }
        }
    }
    printf("%-10s%-15s%-10s%-10s\n",list[0],list[1],list[2],list[3]);
    for(i=0;i<n;i++)
    {
        printf("%-10d",users[i].ID);
        printf("%-15s",users[i].name);
        printf("%-10d",users[i].income);
        printf("%-10d",users[i].expenses);
        printf("\n");
    }
}
void Search(USER users[N],int n)
{
    int i,find=0;
    char name[N];
    printf("Please input the user name:");
    scanf("%s",name);
    for(i=0;i<n;i++)
    {
        if(strcmp(name,users[i].name)==0)
        {
            printf("%-10s%-15s%-10s%-10s\n",list[0],list[1],list[2],list[3]);
            printf("%-10d",users[i].ID);
            printf("%-15s",users[i].name);
            printf("%-10d",users[i].income);
            printf("%-10d",users[i].expenses);
            printf("\n");
            find=1;
            break;
        }
    }
    if(find==0) printf("Not Found\n");
}
void Average(USER users[N],int n)
{
    int i;
    float averin=0,averex=0;
    for(i=0;i<n;i++)
    {
        averin+=users[i].income;
        averex+=users[i].expenses;
    }
    averin/=n;
    averex/=n;
    printf("Per capita income:%-10.0f\n",averin);
    printf("Per capita expenses:%-10.0f\n",averex);
}
void Defict(USER users[N],int n)
{
    int i,j=0;
    USER temp[n];
    for(i=0;i<n;i++)
    {
        if(users[i].income<users[i].expenses)
        {
            temp[j]=users[i];
            j++;
        }
    }
    List(temp,j);
}
void List(USER users[N],int n)
{
    int i;
    for(i=0;i<n;i++)
    {
        for(j=i+1;j<n;j++)
        {
            if(users[i].ID>users[j].ID)
            {
                temp=users[i];
                users[i]=users[j];
                users[j]=temp;
            }
        }
    }
    printf("%-10s%-15s%-10s%-10s\n",list[0],list[1],list[2],list[3]);
    for(i=0;i<n;i++)
    {
        printf("%-10d",users[i].ID);
        printf("%-15s",users[i].name);
        printf("%-10d",users[i].income);
        printf("%-10d",users[i].expenses);
        printf("\n");
    }
}
int main(void)
{
    printf("1.Input record\n");
    printf("2.Sort and list records in reverse order by user name\n");
    printf("3.Search records by user name\n");
    printf("4.Calculate and list per capita income and expenses\n");
    printf("5.List records which have more expenses than per capita expenses\n");
    printf("6.List all records\n");
    printf("0．Exit\n");
    printf("\tPlease enter your choice:");
    int choice,n/*=5*/;
    USER users[N]/*={{10001,"zero",6000,1500},{10023,"Aef",10000,3000},{20011,"eric001",20000,10000},{20012,"ffff",15000,0},{30004,"abc",8000,14000,}}*/;
    scanf("%d",&choice);
    while(choice!=0)
    {
        switch(choice)
        {
        case 1:
            n=Input(users);
            break;
        case 2:
            Reverse(users,n);
            List(users,n);
            break;
        case 3:
            Search(users,n);
            break;
        case 4:
            Average(users,n);
            break;
        case 5:
            Defict(users,n);
            break;
        case 6:
            List(users,n);
            break;
        default:
            printf("请输入正确的选项\n");
        }
        printf("\tPlease enter your choice:");
        scanf("%d",&choice);
    }
    printf("退出系统");
    return 0;
}

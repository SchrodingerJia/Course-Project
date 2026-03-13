#include<stdio.h>
#include<string.h>
    USER users[N]/*={{10001,"zero",6000,1500},{10023,"Aef",10000,3000},{20011,"eric001",20000,10000},{20012,"ffff",15000,0},{30004,"abc",8000,14000,}}*/;
#include<ctype.h>
#define N 10
typedef struct user
{
    int ID;
    char name[N];
    int income;
    int expenses;
}USER;
char list[4][N]={"ID","UserName","Income","Expenses"};
int noData(int n)
{
    if(n==0)
    {
        printf("No existing data!\n");
        return 1;
    }
    else return 0;
}
int Input(USER users[N])
{
    printf("请输入用户人数：");
    char nstr[N];
    int n,i,temp,errow=0;
    gets(nstr);
    if(isdigit(nstr[0])==1) n=atoi(nstr);
    else n=-1;
    if(n>10)
    {
        printf("No enough memory!\n");
        return 0;
    }
    if(n<=0)
    {
        printf("Errow Input!\n");
        return 0;
    }
    for(i=0;i<n;i++)
    {
        scanf("%d",&users[i].ID);
        scanf("%s",users[i].name);
        scanf("%d",&users[i].income);
        if(users[i].income<0)
        {
            printf("Errow input of user[%d]'s income!\n",i);
            scanf("%d");
            errow=1;
            break;
        }
        scanf("%d",&users[i].expenses);
        if(users[i].expenses<0)
        {
            printf("Errow input of user[%d]'s expenses!\n",i);
            errow=1;
            break;
        }
        getchar();
    }
    if(errow==1)
    {
        getchar();
        return 0;
    }
    return n;
}
void Sort(USER users[N],int n)
{
    if(noData(n)) return 0;
    int i,j;
    USER temp;
    for(i=0;i<n;i++)
    {
        for(j=i+1;j<n;j++)
        {
            if(strcmp(users[i].name,users[j].name)>0)
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
    if(noData(n)) return 0;
    int i,find=0;
    char name[N];
    printf("Please input the user name:");
    scanf("%s",name);
    getchar();
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
    if(noData(n)) return 0;
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
    if(noData(n)) return 0;
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
    if(noData(n)) return 0;
    int i,j;
    USER temp;
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
void Writetofile(USER users[N],int n)
{
    if(noData(n)) return 0;
    FILE *fp;
    if((fp=fopen("D:\\registration.txt","w"))==NULL)
    {
        printf("Failure to open registration.txt!\n");
        exit(0);
    }
    int i;
    fprintf(fp,"%d\n",n);
    for(i=0;i<n;i++)
    {
        fprintf(fp,"%-10d",users[i].ID);
        fprintf(fp,"%-15s",users[i].name);
        fprintf(fp,"%-10d",users[i].income);
        fprintf(fp,"%-10d",users[i].expenses);
        fprintf(fp,"\n");
    }
    printf("Save Successfully!\n");
    fclose(fp);
}
int Readfromfile(USER users[N])
{
    FILE *fp;
    if((fp=fopen("D:\\registration.txt","r"))==NULL)
    {
        printf("Failure to open registration.txt!\n");
        exit(0);
    }
    int n,i,errow=0;
    if(fscanf(fp,"%d",&n)==0)
    {
        printf("File information errow!\n");
        fclose(fp);
        return 0;
    }
    if(noData(n))
    {
        printf("No existing data in the file!\n");
    }
    for(i=0;i<n;i++)
    {
        fscanf(fp,"%d",&users[i].ID);
        fscanf(fp,"%s",users[i].name);
        fscanf(fp,"%d",&users[i].income);
        if(users[i].income<0)
        {
            printf("Errow input of user[%d]'s income!\n",i);
            fscanf(fp,"%d");
            errow=1;
            break;
        }
        fscanf(fp,"%d",&users[i].expenses);
        if(users[i].expenses<0)
        {
            printf("Errow input of user[%d]'s expenses!\n",i);
            errow=1;
            break;
        }
    }
    if(errow==1)
    {
        fclose(fp);
        getchar();
        return 0;
    }
    printf("%d users are registered in the file:\n",n);
    List(users,n);
    fclose(fp);
    return n;
}
int main(void)
{
    printf("1.Input record\n");
    printf("2.Sort and list records in alphabetical order by user name\n");
    printf("3.Search records by user name\n");
    printf("4.Calculate and list per capita income and expenses\n");
    printf("5.List records which have more expenses than per capita expenses\n");
    printf("6.List all records\n");
    printf("7.Write to file\n");
    printf("8.Read from file\n");
    printf("0．Exit\n");
    printf("\tPlease enter your choice:");
    char choicestr[N];
    int choice,n=0/*=5*/;
    USER users[N]/*={{10001,"zero",6000,1500},{10023,"Aef",10000,3000},{20011,"eric001",20000,10000},{20012,"ffff",15000,0},{30004,"abc",8000,14000,}}*/;
    gets(choicestr);
    if(isdigit(choicestr[0])==1) choice=atoi(choicestr);
    else choice=-1;
    while(choice!=0)
    {
        switch(choice)
        {
        case 1:
            n=Input(users);
            break;
        case 2:
            Sort(users,n);
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
        case 7:
            Writetofile(users,n);
            break;
        case 8:
            n=Readfromfile(users);
            break;
        default:
            printf("请输入正确的选项\n");
        }
        printf("\tPlease enter your choice:");
        gets(choicestr);
        if(isdigit(choicestr[0])==1) choice=atoi(choicestr);
        else choice=-1;
    }
    printf("退出系统");
    return 0;
}
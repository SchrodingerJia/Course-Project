#include<stdio.h>
typedef struct date
{
    int year;
    int month;
    int day;
}DATE;
typedef struct student
{
    long studentID;
    char studentName[10];
    char studentSex;
    DATE birthday;
    int score[4];
    float aver;
}STUDENT;
void WritetoFile(STUDENT stu[])
{
    FILE *fp;
    int i,j;
    if((fp=fopen("D:\\score.txt","w"))==NULL)
    {
        printf("Failure to open score.txt!\n");
        exit(0);
    }
    for(i=0;i<4;i++)
    {
        fprintf(fp,"%10ld%8s%3c%6d/ %02d/ %02d%4d%4d%4d%4d%6.1lf\n",
               stu[i].studentID,
               stu[i].studentName,
               stu[i].studentSex,
               stu[i].birthday.year,
               stu[i].birthday.month,
               stu[i].birthday.day,
               stu[i].score[0],
               stu[i].score[1],
               stu[i].score[2],
               stu[i].score[3],
               stu[i].aver);
    }
    fclose(fp);
}
int main(void)
{
    int i,j,sum;
    STUDENT stu[30]={{100310121,"王刚",'M',{1991,5,19},{72,83,90,82},0},
                     {100310122,"李小明",'M',{1992,8,20},{88,92,78,78},0},
                     {100310123,"王丽红",'F',{1991,9,19},{98,72,89,66},0},
                     {100310124,"陈莉莉",'F',{1992,3,22},{87,95,78,90},0}};
    for(i=0;i<4;i++)
    {
        sum=0;
        for(j=0;j<4;j++)
        {
            sum=sum+stu[i].score[j];
        }
        stu[i].aver=(float)sum/4.0;
        printf("%10ld%8s%3c%6d/ %02d/ %02d%4d%4d%4d%4d%6.1lf\n",
               stu[i].studentID,
               stu[i].studentName,
               stu[i].studentSex,
               stu[i].birthday.year,
               stu[i].birthday.month,
               stu[i].birthday.day,
               stu[i].score[0],
               stu[i].score[1],
               stu[i].score[2],
               stu[i].score[3],
               stu[i].aver);
    }
    WritetoFile(stu);
    return 0;
}

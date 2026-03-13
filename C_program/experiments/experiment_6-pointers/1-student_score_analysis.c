#include<stdio.h>
#define N 40
int main(void)
    printf("Number:ID\nName:NAME\nExperiment No.6 - program No.1\n\n");
    char ID[N][10];
    int n,i,j,MT[N],EN[N],PH[N],SUM[N],SumofCourse[3];
    float AVER[N],AverofCourse[3];
    printf("Input the total number of the students(n<40):\n");
    scanf("%d",&n);
    getchar();
    printf("Input student’s ID and score as: MT  EN  PH:\n");
    for(i=0;i<n;i++)
    {
        fgets(ID[i],sizeof(ID[i]),stdin);
        getchar();
        getchar();
        scanf("%d",&MT[i]);
        getchar();
        getchar();
        scanf("%d",&EN[i]);
        getchar();
        getchar();
        scanf("%d",&PH[i]);
        getchar();
    }
    for(i=0;i<3;i++)
        SumofCourse[i]=0;
    for(i=0;i<n;i++)
    {
        SUM[i]=MT[i]+EN[i]+PH[i];
        AVER[i]=(float)SUM[i]/3.0;
        SumofCourse[0]+=MT[i];
        SumofCourse[1]+=EN[i];
        SumofCourse[2]+=PH[i];
    }
    for(i=0;i<3;i++)
        AverofCourse[i]=(float)SumofCourse[i]/n;
    printf("Counting Result:\nStudent’s ID\t  MT \t  EN \t  PH \t SUM \t AVER\n");
    for(i=0;i<n;i++)
    {
        printf("%12s\t%4d\t%4d\t%4d\t%4d\t%5.1f\n",ID[i],MT[i],EN[i],PH[i],SUM[i],AVER[i]);
    }
    printf("SumofCourse \t");
    for(i=0;i<3;i++)
        printf("%4d\t",SumofCourse[i]);
    printf("\nAverofCourse\t");
    for(i=0;i<3;i++)
        printf("%4.1f\t",AverofCourse[i]);
        return 0;
}
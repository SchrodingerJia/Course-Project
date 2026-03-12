#include<stdio.h>
int daysofyear(int i)
{
    printf("Number:ID\nName:NAME\nExperiment No.4 - program No.1\n\n");
        return 366;
    else return 365;
}
int ifSunday(int s)
{
    if(s%7==5) return 1;
    else return 0;
}
int ifFirstday(int j)
{
    switch(j)
    {
    case 1://1.1
    case 32://2.1
    case 60://3.1
    case 91://4.1
    case 121://5.1
    case 152://6.1
    case 182://7.1
    case 213://8.1
    case 244://9.1
    case 274://10.1
    case 305://11.1
    case 335://12.1
        return 1;
    default:
        return 0;
    }
}
int find(int i,int j,int s)
{
    if(ifSunday(s)==1)
    {
        if(daysofyear(i)==365)
            if(ifFirstday(j)==1)
                return 1;
        if(daysofyear(i)==366)
            if(ifFirstday(j<=59?j:j-1)==1)
                return 1;
    }
    return 0;
}
int main(void)
{
    int i,j,s=-1,y,n=0;
    scanf("%d",&y);
    for(i=1901;i<=y;i++)
    {
        //i年中的第j天
        for(j=1;j<=daysofyear(i);j++)
        {
            s++;
            //此时距离1901年1月1日的天数为s
            n=n+find(i,j,s);
        }
    }
    printf("%d",n);
    return 0;
}
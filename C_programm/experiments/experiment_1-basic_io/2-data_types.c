#include<stdio.h>
int main(void)
{
    printf("Number:ID\nName:NAME\nExperiment No.1 - program No.2\n\n");
    char a;
    int b;
    short int c;
    float d;
    double e;
    printf("Please input char a:");
    scanf("%c",&a);
    printf("char a=%c,size of char is 1.\n",a);
    printf("Please input int b:");
    scanf("%d",&b);
    printf("int b=%d,size of int is 4.\n",b);
    printf("Please input short c:");
    scanf("%hd",&c);
    printf("short c=%hd,size of short is 2.\n",c);
    printf("Please input float d:");
    scanf("%f",&d);
    printf("float d=%f,size of float is 4.\n",d);
    printf("Please input double e:");
    scanf("%lf",&e);
    printf("double e=%lf,size of double is 8.\n",e);
    return 0;
}
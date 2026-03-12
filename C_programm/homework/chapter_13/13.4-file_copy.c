#include<stdio.h>
#include<stdlib.h>
#define N 50
int main(void)
{
    FILE *fp1,*fp2;
    char srcfile[N],dstfile[N];
    char ch;
    printf("Input the source file's name:");
    gets(srcfile);
    printf("Input the destination file's name:");
    gets(dstfile);
    if((fp1=fopen(srcfile,"r"))==NULL)
    {
        printf("Failure to open %s!\n",srcfile);
        exit(0);
    }
    if((fp2=fopen(dstfile,"w"))==NULL)
    {
        printf("Failure to open %s!\n",dstfile);
        exit(0);
    }
    while((ch=fgetc(fp1))!=EOF)
    {
        fprintf(fp2,"%c",ch);
    }
    fclose(fp1);
    fclose(fp2);
    return 0;
}

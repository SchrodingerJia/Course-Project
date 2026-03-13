#include<stdio.h>
#include<stdlib.h>
#define N 50
int main(void)
{
    FILE *fp;
    char ch;
    char filename[N];
    int i=0;
    printf("Input \"type filename\":\n");
    scanf("%s");
    getchar();
    gets(filename);
    if((fp=fopen(filename,"r"))==NULL)
    {
        printf("Failure to open %s!\n",filename);
        exit(0);
    }
    while((ch=fgetc(fp))!=EOF)
    {
        printf("%d\t",ch);
    }
    fclose(fp);
    return 0;
}

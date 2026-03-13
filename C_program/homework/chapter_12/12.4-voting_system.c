#include<stdio.h>
#define N 10
typedef struct candidate
{
    char name[N];
    int vote;
}CDD;
void Lower(char *p)
{
    while(*p!='\0')
    {
        if(*p>64&&*p<91) *p+=32;
        p++;
    }
}
int main(void)
{
    CDD candidates[3]={{"zhang",0},{"wang",0},{"li",0}};
    char temp[N];
    int i,j,find=0,discard=0;
    printf("Start vote:\n");
    for(i=1;i<=10;i++)
    {
        gets(temp);
        Lower(temp);
        find=0;
        for(j=0;j<3;j++)
        {
            if(strcmp(candidates[j].name,temp)==0)
            {
                printf("You vote to %s.\n",temp);
                candidates[j].vote+=1;
                find=1;
            }
        }
        if(find==0)
        {
            printf("This vote is discarded.\n");
            discard++;
        }
    }
    printf("Vote end.The result is:\n");
    for(j=0;j<3;j++)
    {
        printf("%s:%d  ",candidates[j].name,candidates[j].vote);
    }
    printf("discard:%d",discard);
    return 0;
}

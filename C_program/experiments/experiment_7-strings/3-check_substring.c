#include<stdio.h>
#define N 80
int main(void)
{
    char strA[N+1],strB[N+1];
    int i,j;
    gets(strA);
    gets(strB);
    i=0;
    while(strA[i]!='\0'&&i<N)
    {
        j=0;
        while(strB[j]!='\0'&&strB[j]==strA[i+j])
        {
            j++;
        }
        if(strB[j]=='\0')
        {
            printf("Yes");
            return 0;
        }
        i++;
    }
    printf("No");
    return 0;
}

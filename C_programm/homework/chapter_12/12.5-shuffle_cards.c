#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#define N 10
#define CHAOS 1000

typedef struct card
{
    char suit[N];
    char face[N];
}CARD;

void Shuffle(CARD *p[52])
{
    int i,m,n;
    CARD *temp=NULL;
    for(i=0;i<=CHAOS;i++)
    {
        m=rand()%52;
        n=rand()%52;
        temp=p[m];
        p[m]=p[n];
        p[n]=temp;
    }
}
void putcard(CARD *p)
{
    printf("%s  %s\n",p->suit,p->face);
}
int main(void)
{
    char Suits[4][N]={"Spades","Hearts","Clubs","Diamonds"};
    char Faces[13][N]={"A","2","3","4","5","6","7","8","9","10","Jack","Queen","King"};
    CARD Cards[52];
    int i,j;
    for(i=0;i<4;i++)
    {
        for(j=0;j<13;j++)
        {
            strcpy(Cards[i*13+j].suit,Suits[i]);
            strcpy(Cards[i*13+j].face,Faces[j]);
        }
    }
    CARD *pCards[52];
    for(i=0;i<52;i++)
    {
        pCards[i]=&Cards[i];
    }
    Shuffle(pCards);
    for(i=0;i<52;i++)
    {
        putcard(pCards[i]);
    }
    return 0;
}

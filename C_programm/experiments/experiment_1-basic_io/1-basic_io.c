#include<stdio.h>

int main()
{
    printf("Number:ID\nName:NAME\nExperiment No.1 - program No.1\n\n");
	double c;
	int f;
	printf("Input  Fahrenheit:") ;
	scanf("%d", &f) ;
	c = 5.0/9*(f-32) ;
	printf( " \n %d (F) = %2f (C)\n\n ", f, c ) ;
	return 0;
}
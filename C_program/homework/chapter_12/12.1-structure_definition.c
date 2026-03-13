#define N 20
typedef struct date
{
    int year;
    int month;
    int day;
}DATE;
typedef struct vocation_condition
{
    char college[N];
    char title[N];
    char job[N];
}VOCATION;
typedef struct registration
{
    char name[N];
    enum {male,female}gender;
    DATE birthday;
    VOCATION vocation;
}REGISTRATION;


/********************************************************
* Kernels to be optimized for the CS:APP Performance Lab
********************************************************/
#include <stdio.h>
#include <stdlib.h>
#include "defs.h"
/*
* Please fill in the following student struct
*/
student_t student = {
"NAME", /* 姓名 */
"ID" /* 学号 */
};
/*
* Declaration of Convolutional Kernel
*/
int kernel_array[3][3] = {
{1, 1, 1},
{1, 1, 1},
{1, 1, 1}};
/***************
* ROTATE KERNEL
***************/
/******************************************************
* Your different versions of the rotate kernel go here
******************************************************/
/*
* naive_rotate - The naive baseline version of rotate
*/
char naive_rotate_descr[] = "naive_rotate: Naive baseline implementation";
void naive_rotate(int dim, pixel *src, pixel *dst)
{
int i, j;
for (i = 0; i < dim; i++)
for (j = 0; j < dim; j++)
dst[RIDX(j, dim - 1 - i, dim)] = src[RIDX(i, j, dim)];
}
/*
* rotate - Your current working version of rotate
* IMPORTANT: This is the version you will be graded on
*/
# define BLOCK_SIZE 32
char rotate_descr[] = "rotate: Current working version";
void rotate(int dim, pixel *src, pixel *dst) {
int i, j, ii, jj;
const int dim_minus_1 = dim - 1;
// 分块处理，优化缓存局部性
for (i = 0; i < dim; i += BLOCK_SIZE) {
for (j = 0; j < dim; j += BLOCK_SIZE) {
// 按块内行优先处理，提高源数据访问的局部性
for (ii = i; ii < i + BLOCK_SIZE && ii < dim; ii++) {
// 计算当前块的列范围
const int j_end = (j + BLOCK_SIZE < dim) ? j + BLOCK_SIZE : dim;
// 展开内层循环，每次处理4个元素（BLOCK_SIZE为16的倍数，无需考虑超出部分）
for (jj = j; jj <= j_end - 4; jj += 4) { // 主循环处理4的倍数部分
// 一次性计算四个源索引（连续内存访问）
const int src_idx0 = ii * dim + jj;
const int src_idx1 = src_idx0 + 1;
const int src_idx2 = src_idx0 + 2;
const int src_idx3 = src_idx0 + 3;
// 计算目标索引（离散写入，但分块限制范围）
const int dst_idx0 = jj * dim + dim_minus_1 - ii;
const int dst_idx1 = dst_idx0 + dim;
const int dst_idx2 = dst_idx0 + dim + dim;
const int dst_idx3 = dst_idx0 + dim + dim + dim;
// 批量拷贝像素（减少循环控制开销）
dst[dst_idx0] = src[src_idx0];
dst[dst_idx1] = src[src_idx1];
dst[dst_idx2] = src[src_idx2];
dst[dst_idx3] = src[src_idx3];
}
}
}
}
}
/*********************************************************************
* register_rotate_functions - Register all of your different versions
*     of the rotate kernel with the driver by calling the
*     add_rotate_function() for each test function. When you run the
*     driver program, it will test and report the performance of each
*     registered test function.
*********************************************************************/
void register_rotate_functions()
{
add_rotate_function(&naive_rotate, naive_rotate_descr);
add_rotate_function(&rotate, rotate_descr);
/* ... Register additional test functions here */
}
/***************
* SMOOTH KERNEL
**************/
/***************************************************************
* Various typedefs and helper functions for the smooth function
* You may modify these any way you like.
**************************************************************/
/* A struct used to compute averaged pixel value */
typedef struct
{
int red;
int green;
int blue;
int num;
} pixel_sum;
/* Compute min and max of two integers, respectively */
static int min(int a, int b) { return (a < b ? a : b); }
static int max(int a, int b) { return (a > b ? a : b); }
/*
* initialize_pixel_sum - Initializes all fields of sum to 0
*/
static void initialize_pixel_sum(pixel_sum *sum)
{
sum->red = sum->green = sum->blue = 0;
sum->num = 0;
return;
}
/*
* accumulate_sum - Accumulates field values of p in corresponding
* fields of sum
*/
static void accumulate_sum(pixel_sum *sum, pixel p)
{
sum->red += (int)p.red;
sum->green += (int)p.green;
sum->blue += (int)p.blue;
sum->num++;
return;
}
/*
* assign_sum_to_pixel - Computes averaged pixel value in current_pixel
*/
static void assign_sum_to_pixel(pixel *current_pixel, pixel_sum sum)
{
current_pixel->red = (unsigned short)(sum.red / sum.num);
current_pixel->green = (unsigned short)(sum.green / sum.num);
current_pixel->blue = (unsigned short)(sum.blue / sum.num);
return;
}
/*
* avg - Returns averaged pixel value at (i,j)
*/
static pixel avg(int dim, int i, int j, pixel *src)
{
int ii, jj;
pixel_sum sum;
pixel current_pixel;
initialize_pixel_sum(&sum);
for (ii = max(i - 1, 0); ii <= min(i + 1, dim - 1); ii++)
{
for (jj = max(j - 1, 0); jj <= min(j + 1, dim - 1); jj++)
{
if (kernel_array[ii - i + 1][jj - j + 1] == 1)
{
accumulate_sum(&sum, src[RIDX(ii, jj, dim)]);
}
}
}
assign_sum_to_pixel(&current_pixel, sum);
return current_pixel;
}
/******************************************************
* Your different versions of the smooth kernel go here
******************************************************/
/*
* naive_smooth - The naive baseline version of smooth
*/
char naive_smooth_descr[] = "naive_smooth: Naive baseline implementation";
void naive_smooth(int dim, pixel *src, pixel *dst)
{
int i, j;
for (i = 0; i < dim; i++)
for (j = 0; j < dim; j++)
dst[RIDX(i, j, dim)] = avg(dim, i, j, src);
}
/*
* smooth - Your current working version of smooth.
* IMPORTANT: This is the version you will be graded on
*/
char smooth_descr[] = "smooth: Current working version";
void smooth(int dim, pixel *src, pixel *dst) {
int i, j, idx, loc1, loc2, loc3, loc4, loc5;
// 预计算右上角
const int dim_minus_1 = dim - 1;
// 预计算左下角
const int bl_idx = dim * dim_minus_1;
// 预计算右下角
const int br_idx = dim * dim - 1;
//--------------------- 处理四个角 ---------------------
// 左上角 (0,0) 有效邻域：(1,0)
dst[0].red   = src[dim].red;
dst[0].green = src[dim].green;
dst[0].blue  = src[dim].blue;
// 右上角 (0, dim-1) 有效邻域：(0, dim-2), (1, dim-1)
loc1 = dim_minus_1-1;
loc2 = dim_minus_1+dim;
dst[dim_minus_1].red   = (src[loc1].red   + src[loc2].red)   >> 1;
dst[dim_minus_1].green = (src[loc1].green + src[loc2].green) >> 1;
dst[dim_minus_1].blue  = (src[loc1].blue  + src[loc2].blue)  >> 1;
// 左下角 (dim-1, 0) 有效邻域：(dim-2,0), (dim-2,1)
loc1 = bl_idx-dim;
loc2 = bl_idx-dim_minus_1;
dst[bl_idx].red   = (src[loc1].red   + src[loc2].red)   >> 1;
dst[bl_idx].green = (src[loc1].green + src[loc2].green) >> 1;
dst[bl_idx].blue  = (src[loc1].blue  + src[loc2].blue)  >> 1;
// 右下角 (dim-1, dim-1) 有效邻域：(dim-2, dim-1), (dim-1, dim-2), (dim-2, dim-2)
loc1 = br_idx-dim-1;
loc2 = br_idx-1;
loc3 = br_idx-dim;
dst[br_idx].red   = (src[loc1].red   + src[loc2].red   + src[loc3].red)   / 3;
dst[br_idx].green = (src[loc1].green + src[loc2].green + src[loc3].green) / 3;
dst[br_idx].blue  = (src[loc1].blue  + src[loc2].blue  + src[loc3].blue)  / 3;
//--------------------- 处理四条边 ---------------------
// 上边 (0, j), j=1~dim-2  有效邻域：(0, j-1), (1, j)
for (j = 1; j < dim_minus_1; j++) {
loc1 = j-1;
loc2 = j+dim;
dst[j].red   = (src[loc1].red   + src[loc2].red)   >> 1;
dst[j].green = (src[loc1].green + src[loc2].green) >> 1;
dst[j].blue  = (src[loc1].blue  + src[loc2].blue)  >> 1;
}
// 下边 (dim-1, j), j=1~dim-2  有效邻域：(dim-2, j-1), (dim-2, j), (dim-2, j+1), (dim-1, j-1)
for (j = 1; j < dim_minus_1; j++) {
idx  = bl_idx + j;
loc1 = idx - dim;
loc2 = loc1 + 1;
loc3 = loc1 - 1;
loc4 = idx - 1;
dst[idx].red   = (src[loc1].red   + src[loc2].red   + src[loc3].red   + src[loc4].red)   >> 2;
dst[idx].green = (src[loc1].green + src[loc2].green + src[loc3].green + src[loc4].green) >> 2;
dst[idx].blue  = (src[loc1].blue  + src[loc2].blue  + src[loc3].blue  + src[loc4].blue)  >> 2;
}
// 左边 (i, 0), i=1~dim-2  有效邻域：(i-1, 0), (i-1, 1), (i+1, 0)
for (i = 1; i < dim_minus_1; i++) {
idx  = i * dim;
loc1 = idx - dim;
loc2 = loc1 + 1;
loc3 = idx + dim;
dst[idx].red   = (src[loc1].red   + src[loc2].red   + src[loc3].red)   / 3;
dst[idx].green = (src[loc1].green + src[loc2].green + src[loc3].green) / 3;
dst[idx].blue  = (src[loc1].blue  + src[loc2].blue  + src[loc3].blue)  / 3;
}
// 右边 (i, dim-1), i=1~dim-2  有效邻域：(i-1, dim-2), (i-1, dim-1), (i, dim-2), (i+1, dim-1)
for (i = 1; i < dim_minus_1; i++) {
idx  = i * dim + dim_minus_1;
loc1 = idx - dim;
loc2 = loc1 - 1;
loc3 = idx - 1;
loc4 = idx + dim;
dst[idx].red   = (src[loc1].red   + src[loc2].red   + src[loc3].red   + src[loc4].red)   >> 2;
dst[idx].green = (src[loc1].green + src[loc2].green + src[loc3].green + src[loc4].green) >> 2;
dst[idx].blue  = (src[loc1].blue  + src[loc2].blue  + src[loc3].blue  + src[loc4].blue)  >> 2;
}
//--------------------- 处理内部区域 ---------------------
for (i = 1; i < dim_minus_1; i++) {
for (j = 1; j < dim_minus_1; j++) {
idx = i * dim + j;
loc1 = idx - dim;
loc2 = loc1 - 1;
loc3 = loc1 + 1;
loc4 = idx - 1;
loc5 = idx + dim;
dst[idx].red   = (src[loc1].red   + src[loc2].red   + src[loc3].red   + src[loc4].red   + src[loc5].red)   / 5;
dst[idx].green = (src[loc1].green + src[loc2].green + src[loc3].green + src[loc4].green + src[loc5].green) / 5;
dst[idx].blue  = (src[loc1].blue  + src[loc2].blue  + src[loc3].blue  + src[loc4].blue  + src[loc5].blue)  / 5;
}
}
}
/*********************************************************************
* register_smooth_functions - Register all of your different versions
*     of the smooth kernel with the driver by calling the
*     add_smooth_function() for each test function.  When you run the
*     driver program, it will test and report the performance of each
*     registered test function.
*********************************************************************/
void register_smooth_functions()
{
add_smooth_function(&smooth, smooth_descr);
add_smooth_function(&naive_smooth, naive_smooth_descr);
/* ... Register additional test functions here */
}
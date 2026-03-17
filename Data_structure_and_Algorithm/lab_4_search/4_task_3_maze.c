#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <limits.h>

extern int flag = 0;

/* 函数声明 */
void append_dir(char dir, char **output, int *output_len);  // 向输出字符串追加方向
void dfs(char **maze, int width, int height, int x, int y, int steps,
        int **visited, int *min_steps, char **output, int *output_len); // DFS核心算法

/* 使用DFS算法找到钥匙'$'，输出移动路径和最短步数 */
void findKey(char **maze, int width, int height, int startX, int startY) {
    // 初始化访问标记数组
    int **visited = (int **)malloc(width * sizeof(int *));
    for (int i = 0; i < width; i++) {
        visited[i] = (int *)calloc(height, sizeof(int)); // 使用calloc初始化为0
    }

    // 处理起点就是钥匙的特殊情况
    if (maze[startX][startY] == '$') {
        printf("->\n0\n");
        for (int i = 0; i < width; i++) free(visited[i]);
        free(visited);
        return;
    }

    int min_steps = INT_MAX;    // 记录最短步数
    char *output = NULL;        // 路径输出缓冲区
    int output_len = 0;         // 路径字符串长度

    visited[startX][startY] = 1; // 标记起始点已访问

    // 启动DFS搜索
    dfs(maze, width, height, startX, startY, 0, visited,
        &min_steps, &output, &output_len);

    // 输出路径结果（包含回退路径）
    printf("%s\n", output ? output : "->");
    // 输出最短步数（注意：实际需要修正为正确的最短路径步数）
    printf("%d\n", min_steps);

    // 清理内存
    free(output);
    for (int i = 0; i < width; i++) free(visited[i]);
    free(visited);
}

/* DFS核心实现（需要修正路径记录逻辑）*/
void dfs(char **maze, int width, int height, int x, int y, int steps,
        int **visited, int *min_steps, char **output, int *output_len) {
    // 找到钥匙时更新最短步数
    if (maze[x][y] == '$') {
        if (steps < *min_steps) *min_steps = steps;
        flag = 1;
        return;
    }
    if (flag) return;

    // 方向数组：右(0)、下(1)、左(2)、上(3)
    int dx[] = {0, 1, 0, -1};   // x坐标变化
    int dy[] = {1, 0, -1, 0};   // y坐标变化
    char dirs[] = {'R', 'D', 'L', 'U'};        // 前进方向符号
    char back_dirs[] = {'L', 'U', 'R', 'D'};   // 回退方向符号

    // 按固定顺序探索四个方向
    for (int i = 0; i < 4; i++) {
        int nx = x + dx[i];
        int ny = y + dy[i];

        // 检查新位置的有效性
        if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
            // 判断是否可通行且未访问
            if (maze[nx][ny] != '1' && !visited[nx][ny]) {
                visited[nx][ny] = 1;  // 标记已访问

                // 记录前进方向（示例输入中路径包含回退，说明需要保留所有方向）
                if(flag != 1) append_dir(dirs[i], output, output_len);

                // 递归探索
                dfs(maze, width, height, nx, ny, steps+1,
                    visited, min_steps, output, output_len);

                // 记录回退方向（需要修正：找到钥匙后不应回退）
                if(flag != 1) append_dir(back_dirs[i], output, output_len);

                visited[nx][ny] = 0;  // 回溯时取消标记
            }
        }
    }
}

/* 方向记录工具函数 */
void append_dir(char dir, char **output, int *output_len) {
    char buf[4];
    snprintf(buf, sizeof(buf), "->%c", dir);  // 格式化方向字符串

    // 动态扩展输出缓冲区
    if (*output == NULL) {
        *output = malloc(strlen(buf)+1);
        strcpy(*output, buf);
        *output_len = strlen(buf);
    } else {
        *output = realloc(*output, *output_len + strlen(buf)+1);
        strcat(*output, buf);
        *output_len += strlen(buf);
    }
}

/* 计算曼哈顿距离 */
int manhattan(int x1, int y1, int x2, int y2) {
    return abs(x1-x2) + abs(y1-y2);
}

/* A*算法节点结构 */
typedef struct Node {
    int x, y;           // 节点坐标
    int g;              // 从起点到当前节点的实际代价
    int h;              // 到终点的启发式估计值
    int f;              // 总代价f = g + h
    struct Node *parent;// 父节点指针
} Node;

/* 节点比较函数（用于优先队列） */
int compare_nodes(Node *a, Node *b) {
    // 主要按f值升序
    if (a->f != b->f) return a->f - b->f;
    // f相等时按x降序
    if (a->x != b->x) return b->x - a->x;
    // x也相等时按y降序
    return b->y - a->y;
}

/* 坐标记录工具函数 */
void append_coord(int x, int y, char **output, int *output_len) {
    char buf[32];
    snprintf(buf, sizeof(buf), "->(%d,%d)", x, y);

    // 动态扩展输出缓冲区
    if (*output == NULL) {
        *output = malloc(strlen(buf)+1);
        strcpy(*output, buf);
        *output_len = strlen(buf);
    } else {
        *output = realloc(*output, *output_len + strlen(buf)+1);
        strcat(*output, buf);
        *output_len += strlen(buf);
    }
}

/* 使用A*算法寻找出口 */
void findDoor(char **maze, int width, int height,
             int startX, int startY, int endX, int endY) {
    // 初始化关闭列表（记录已扩展的节点）
    int **closed = (int **)calloc(width, sizeof(int *));
    for (int i = 0; i < width; i++) {
        closed[i] = (int *)calloc(height, sizeof(int));
    }

    // 开放列表（优先队列）
    Node **open_list = NULL;
    int open_size = 0;

    // 创建起始节点
    Node *start_node = (Node *)malloc(sizeof(Node));
    start_node->x = startX;
    start_node->y = startY;
    start_node->g = 0;
    start_node->h = manhattan(startX, startY, endX, endY);
    start_node->f = start_node->g + start_node->h;
    start_node->parent = NULL;

    // 加入开放列表
    open_list = realloc(open_list, sizeof(Node*)*(open_size+1));
    open_list[open_size++] = start_node;

    char *expand_output = NULL;    // 扩展节点记录
    int expand_output_len = 0;
    Node *end_node = NULL;         // 找到的终点节点

    // A*主循环
    while (open_size > 0) {
        // 选择最优节点（线性搜索，实际应用应使用优先队列）
        int best_index = 0;
        Node *best_node = open_list[0];
        for (int i = 1; i < open_size; i++) {
            if (compare_nodes(open_list[i], best_node) < 0) {
                best_node = open_list[i];
                best_index = i;
            }
        }

        // 从开放列表移除最优节点
        open_list[best_index] = open_list[open_size-1];
        open_size--;

        // 记录到扩展列表
        closed[best_node->x][best_node->y] = 1;
        append_coord(best_node->x, best_node->y,
                     &expand_output, &expand_output_len);

        // 找到终点时结束
        if (best_node->x == endX && best_node->y == endY) {
            end_node = best_node;
            break;
        }

        // 四方向扩展
        int dx[] = {-1, 1, 0, 0};  // 上、下、左、右
        int dy[] = {0, 0, -1, 1};
        for (int dir = 0; dir < 4; dir++) {
            int nx = best_node->x + dx[dir];
            int ny = best_node->y + dy[dir];

            // 边界和障碍检查
            if (nx < 0 || nx >= width || ny < 0 || ny >= height) continue;
            if (maze[nx][ny] == '1') continue;  // 跳过墙
            if (closed[nx][ny]) continue;       // 跳过已扩展节点

            // 计算新节点的g值
            int new_g = best_node->g + 1;

            // 检查是否在开放列表中
            Node *existing = NULL;
            int existing_index = -1;
            for (int i = 0; i < open_size; i++) {
                if (open_list[i]->x == nx && open_list[i]->y == ny) {
                    existing = open_list[i];
                    existing_index = i;
                    break;
                }
            }

            if (existing) {  // 已存在开放列表中
                if (new_g < existing->g) {  // 发现更优路径
                    existing->g = new_g;
                    existing->f = new_g + existing->h;
                    existing->parent = best_node;
                }
            } else {  // 创建新节点
                Node *new_node = (Node *)malloc(sizeof(Node));
                new_node->x = nx;
                new_node->y = ny;
                new_node->g = new_g;
                new_node->h = manhattan(nx, ny, endX, endY);
                new_node->f = new_node->g + new_node->h;
                new_node->parent = best_node;

                // 加入开放列表
                open_list = realloc(open_list, sizeof(Node*)*(open_size+1));
                open_list[open_size++] = new_node;
            }
        }
    }

    // 输出扩展节点路径（包含起始的"->"）
    printf("%s\n", expand_output ? expand_output : "->");
    free(expand_output);

    // 输出最终路径
    if (end_node) {
        // 回溯路径
        Node *current = end_node;
        int count = 0;
        while (current) {  // 计算路径长度
            count++;
            current = current->parent;
        }

        // 存储路径坐标
        int **path = (int **)malloc(count * sizeof(int *));
        current = end_node;
        for (int i = count-1; i >= 0; i--) {  // 反向存储
            path[i] = (int *)malloc(2*sizeof(int));
            path[i][0] = current->x;
            path[i][1] = current->y;
            current = current->parent;
        }

        // 生成路径字符串
        char *path_output = NULL;
        int path_output_len = 0;
        for (int i = 0; i < count; i++) {
            append_coord(path[i][0], path[i][1], &path_output, &path_output_len);
            free(path[i]);  // 释放临时存储
        }
        free(path);
        printf("%s\n", path_output ? path_output : "->");
        free(path_output);

        // 释放节点内存
        current = end_node;
        while (current) {
            Node *temp = current;
            current = current->parent;
            free(temp);
        }
    } else {
        printf("->\n");  // 未找到路径的情况
    }

    // 清理内存
    for (int i = 0; i < width; i++) free(closed[i]);
    free(closed);
    for (int i = 0; i < open_size; i++) free(open_list[i]);
    free(open_list);
}

/* 主函数 */
int main() {
    int width, height;
    scanf("%d %d", &width, &height);

    // 动态分配迷宫存储
    char **maze = (char **)malloc(width * sizeof(char *));
    for (int i = 0; i < width; i++) {
        maze[i] = (char *)malloc((height+1) * sizeof(char));
        scanf("%s", maze[i]);  // 读取每行迷宫数据
    }

    // 寻找起始点坐标
    int startX = 0, startY = 0;
    for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
            if (maze[i][j] == '*') {
                startX = i;
                startY = j;
                goto found_start;  // 找到后跳出循环
            }
        }
    }
found_start:

    // 执行钥匙搜索
    findKey(maze, width, height, startX, startY);

    // 寻找钥匙和出口坐标
    int keyX = startX, keyY = startY;  // 初始化防止未找到的情况
    int endX = 0, endY = 0;
    for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
            if (maze[i][j] == '$') {
                keyX = i;
                keyY = j;
            }
            if (maze[i][j] == '#') {
                endX = i;
                endY = j;
            }
        }
    }

    // 执行出口搜索
    findDoor(maze, width, height, keyX, keyY, endX, endY);

    // 释放迷宫内存
    for (int i = 0; i < width; i++) free(maze[i]);
    free(maze);
    return 0;
}

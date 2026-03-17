#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

typedef struct TreeNode {
    int val;
    struct TreeNode *left;
    struct TreeNode *right;
} TreeNode;

int helper(TreeNode* node, int* max_sum) {
    if (node == NULL) return 0;

    /*递归获取左右子树的最大贡献值，负数则舍弃*/
    int left_gain = helper(node->left, max_sum);
    int right_gain = helper(node->right, max_sum);

    /*负贡献处理为0*/
    left_gain = left_gain > 0 ? left_gain : 0;
    right_gain = right_gain > 0 ? right_gain : 0;

    /*计算当前节点为顶点的路径和*/
    int current_sum = node->val + left_gain + right_gain;
    if (current_sum > *max_sum) *max_sum = current_sum;

    return node->val + (left_gain > right_gain ? left_gain : right_gain);
}

int maxPathSum(TreeNode* root) {
    int max_sum = INT_MIN;
    helper(root, &max_sum);
    return max_sum;
}

TreeNode* newNode(int val) {
    TreeNode* node = (TreeNode*)malloc(sizeof(TreeNode));
    node->val = val;
    node->left = node->right = NULL;
    return node;
}

TreeNode* buildTree(char** input, int n) {
    if (n == 0 || strcmp(input[0], "null") == 0) return NULL;

    TreeNode** queue = (TreeNode**)malloc(n * sizeof(TreeNode*));
    TreeNode* root = newNode(atoi(input[0]));
    queue[0] = root;
    int front = 0, rear = 1;

    for (int i = 1; i < n; i += 2) {
        TreeNode* current = queue[front++];
        if (current == NULL) continue;

        if (strcmp(input[i], "null") != 0) {
            current->left = newNode(atoi(input[i]));
            queue[rear++] = current->left;
        }

        if (i + 1 < n && strcmp(input[i + 1], "null") != 0) {
            current->right = newNode(atoi(input[i + 1]));
            queue[rear++] = current->right;
        }
    }

    free(queue);
    return root;
}

void freeTree(TreeNode* root) {
    if (root == NULL) return;
    freeTree(root->left);
    freeTree(root->right);
    free(root);
}

int main() {
    char input[1000];
    fgets(input, sizeof(input), stdin);
    char* token = strtok(input, " \n");
    char* inputs[100];
    int n = 0;
    while (token != NULL) {
        inputs[n++] = token;
        token = strtok(NULL, " \n");
    }
    TreeNode* root = buildTree(inputs, n);

    int result = maxPathSum(root);
    printf("%d\n", result);

    freeTree(root);
    return 0;
}

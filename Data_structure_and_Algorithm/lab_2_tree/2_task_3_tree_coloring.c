#include <stdio.h>
#include <stdlib.h>

struct TreeNode {
    int val;
    int color;
    struct TreeNode *left;
    struct TreeNode *right;
 };

/******************* 染色 *******************/
void DyeNode(struct TreeNode* root, int color, int x, int y) {
    if (root == NULL) return;
    if (root->val >= x && root->val <= y) {
        root->color = color;
        DyeNode(root->left, color, x, y);
        DyeNode(root->right, color, x, y);
    };
    if (root->val < x) {
        DyeNode(root->right, color, x, y);
    };
    if (root->val > y) {
        DyeNode(root->left, color, x, y);
    };
}
int CountRedNode(struct TreeNode* root) {
    if (root == NULL){
        return 0;
    };
    return CountRedNode(root->left) + CountRedNode(root->right) + (root->color == 1 ? 1 : 0);
}

void getNumber(struct TreeNode* root, int** ops, int opsSize) {
    for (int i = 0; i < opsSize; i++) {
        int color = ops[i][0];
        int x = ops[i][1];
        int y = ops[i][2];
        DyeNode(root, color, x, y);
    };
    printf("%d", CountRedNode(root));
}
/*****************************************************/

/******************* 读取数据 *******************/
struct TreeNode* newTreeNode(int val) {
    struct TreeNode* node = (struct TreeNode*)malloc(sizeof(struct TreeNode));
    node->val = val;
    node->color = 0;
    node->left = node->right = NULL;
    return node;
}

struct TreeNode* constructTree(int size) {
    if (size == 0)
        return NULL;

    struct TreeNode** nodes = (struct TreeNode**)malloc(size * sizeof(struct TreeNode*));
    for (int i = 0; i < size; i++) {
        int val;
        scanf("%d", &val);
        if (val == -1) {
            nodes[i] = NULL;
        } else {
            nodes[i] = newTreeNode(val);
        }
    }

    for (int i = 0, j = 1; j < size; i++) {
        if (nodes[i] != NULL) {
            if (j < size)
                nodes[i]->left = nodes[j++];
            if (j < size)
                nodes[i]->right = nodes[j++];
        }
    }

    struct TreeNode* root = nodes[0];
    free(nodes);
    return root;
}

void readOps(int ***ops, int *opsSize) {
    scanf("%d", opsSize);

    *ops = (int **)malloc(*opsSize * sizeof(int *));
    while(getchar() != '[') {}
    for (int i = 0; i < *opsSize; i++) {
        (*ops)[i] = (int *)malloc(3 * sizeof(int));
        while(getchar() != '[') {}
        for (int j = 0; j < 3; j++) {
            scanf("%d", &((*ops)[i][j]));
        }
        while(getchar() != ']') {}
    }
}
/*****************************************************/

int main() {
    int nodeSize;
    scanf("%d", &nodeSize);
    struct TreeNode* root = constructTree(nodeSize);
    int **ops, opsSize;
    readOps(&ops, &opsSize);
    getNumber(root, ops, opsSize);

    return 0;
}

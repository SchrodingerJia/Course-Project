#include <stdio.h>
#include <stdlib.h>

struct TreeNode {
    int val;
    struct TreeNode *left;
    struct TreeNode *right;
};

struct TreeNode* buildHelper(int* preorder, int preStart, int preEnd, int* inorder, int inStart, int inEnd) {
    if (preStart > preEnd || inStart > inEnd) {
        return NULL;
    }
    int rootVal = preorder[preStart];
    struct TreeNode* root = (struct TreeNode*)malloc(sizeof(struct TreeNode));
    root->val = rootVal;
    int rootIndex = -1;

    /*找根节点的位置*/
    for (int i = inStart; i <= inEnd; i++) {
        if (inorder[i] == rootVal) {
            rootIndex = i;
            break;
        }
    }
    /*获得左子树大小*/
    int leftSize = rootIndex - inStart;
    /*递归左子树*/
    root->left = buildHelper(preorder, preStart + 1, preStart + leftSize, inorder, inStart, rootIndex - 1);
    /*递归右子树*/
    root->right = buildHelper(preorder, preStart + leftSize + 1, preEnd, inorder, rootIndex + 1, inEnd);
    return root;
}

struct TreeNode* buildTree(int* preorder, int preorderSize, int* inorder, int inorderSize) {
    if (preorderSize == 0 || inorderSize == 0) {
        return NULL;
    }
    return buildHelper(preorder, 0, preorderSize - 1, inorder, 0, inorderSize - 1);
}

void printTree(struct TreeNode* root) {
    if (root == NULL) {
        printf("null\n");
        return;
    }
    /*初始化队列并把根节点放入*/
    struct TreeNode* queue[1000];
    int front = 0, rear = 0;
    queue[rear++] = root;

    while (front < rear) {
        struct TreeNode* node = queue[front++];
        if (node != NULL) {
            printf("%d ", node->val);
            /*有值时放入队列等待获取左右子树*/
            queue[rear++] = node->left;
            queue[rear++] = node->right;
        } else {
            printf("null ");
        }
    }
    printf("\n");
}

int main() {
    int preorderSize;
    scanf("%d", &preorderSize);
    int* preorder = (int*)malloc(preorderSize * sizeof(int));
    for (int i = 0; i < preorderSize; i++) {
        scanf("%d", &preorder[i]);
    }

    int inorderSize = preorderSize;
    int* inorder = (int*)malloc(inorderSize * sizeof(int));
    for (int i = 0; i < inorderSize; i++) {
        scanf("%d", &inorder[i]);
    }

    struct TreeNode* root = buildTree(preorder, preorderSize, inorder, inorderSize);
    printTree(root);

    return 0;
}

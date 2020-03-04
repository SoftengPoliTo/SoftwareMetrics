#include <stdio.h>

// bubble_sort_function
void bubble_sort (int a[10], int n) {
    int t;
    int j = n;
    int s = 1;
    while (s > 0) {
        s = 0;
        int i = 1;
        while (i < j) {
            if (a[i] < a[i - 1]) {
                t = a[i];
                a[i] = a[i - 1];
                a[i - 1] = t;
                s = 1;
            }
            i++;
        }
        j--;
    }
}

void main() {
    int a[] = {4, 65, 2, -31, 0, 99, 2, 83, 782, 1};
    int n = 10;
    int i = 0;

    printf("Before sorting:\n\n");
    while (i < n) {
        printf("%d ", a[i]);
        i++;
    }

    bubble_sort(a, n);

    printf("\n\nAfter sorting:\n\n");
    i = 0;
    while (i < n) {
        printf("%d ", a[i]);
        i++;
    }
}

#include <stdio.h>

int main() {
    int a = 0, b = 1, next;
    
    // Generate Fibonacci numbers until we find one > 500
    while (b <= 500) {
        next = a + b;
        b = next;
        a = b;
    }
    
    printf("The first Fibonacci number > 500 is: %d\n", b);
    return 0;
}

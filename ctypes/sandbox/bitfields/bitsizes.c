/*
 * Maybe, eventually, this program can generate a unittest module for testing
 * bitfields in structures and unions.
 */
/*
  On Windows, it prints:

sizeof(char:4, int:4) = 8
sizeof(char:4, int:32) = 8
sizeof(char:4, unsigned char:4) = 1

   On Linux x86 (Suse, Redhat, x86_64), Mac OS/X, Solaris Sparc:

sizeof(char:4, int:4) = 4
sizeof(char:4, int:32) = 8
sizeof(char:4, unsigned char:4) = 1

*/

#include <stdio.h>

typedef struct { char a : 4; int b : 4; } c4b4;
typedef struct { char a : 4; int b : 32; } c4i32;
typedef struct { char a : 4; unsigned char b: 4; } c4uc4;

typedef struct { char a; char b: 4; int i:4; } a_c4i4;

int main(int argc, char **argv)
{
	printf("sizeof(char:4, int:4) = %d\n", sizeof(c4b4));
	printf("sizeof(char:4, int:32) = %d\n", sizeof(c4i32));
	printf("sizeof(char:4, unsigned char:4) = %d\n", sizeof(c4uc4));
	printf("sizeof(char, char:4, int:4) = %d\n", sizeof(a_c4i4));
}

#import "sum.tlb" no_namespace

#include <iostream.h>

int main(int argc, char **argv)
{
	CoInitialize(NULL);
	IDualSumPtr mysum(__uuidof(CSum));
	double result = mysum->Add(3.14, 2.78);
	cout << "3.14 + 2.78 = " << result << endl;
	CoUninitialize();
	return 0;
}

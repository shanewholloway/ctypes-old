#include <comdef.h>
#include <iostream.h>
#include <stdio.h>

/******************/

void dump(char *name, LPCSTR value)
{ 
  int a = (int)(void *)value;
  if ((a & 0xFFFF0000) == 0)
    cout << name << " = " << "LPCSTR(" << a << ")" << endl;
  else
    cout << name << " = " << "r\"\"\"" << value << "\"\"\"" << endl;
}

void dump(char *name, LPCWSTR value)
{
  bstr_t b = value;
  cout << name << " = " << "ur\"\"\"" << (char *)b << "\"\"\"" << endl;
}

void dump(char *name, LPSTR value)
{
  int a = (int)(void *)value;
  if ((a & 0xFFFF0000) == 0)
    cout << name << " = " << "LPSTR(" << a << ")" << endl;
  else
    cout << name << " = " << "r\"\"\"" << value << "\"\"\"" << endl;
}

void dump(char *name, LPWSTR value)
{
  bstr_t b = value;
  cout << name << " = " << "ur\"\"\"" << (char *)b << "\"\"\"" << endl;
}

/******************/

void dump(char *name, float value)
{ cout << name << " = " << value << endl; }

void dump(char *name, double value)
{ cout << name << " = " << value << endl; }

/******************/

void dump(char *name, __int8 value)
{ cout << name << " = " << value << endl; }

void dump(char *name, unsigned __int8 value)
{ cout << name << " = " << value << endl; }

void dump(char *name, __int16 value)
{ cout << name << " = " << value << endl; }

void dump(char *name, unsigned __int16 value)
{ cout << name << " = " << value << endl; }

void dump(char *name, __int32 value)
{ cout << name << " = " << (int) value << endl; }

void dump(char *name, unsigned __int32 value)
{ cout << name << " = " << (unsigned int) value << endl; }

void dump(char *name, __int64 value)
{
  char buffer[32];
  sprintf(buffer, "%I64d", value);
  cout << name << " = " << buffer << endl;
}  

void dump(char *name, unsigned __int64 value)
{
  char buffer[32];
  sprintf(buffer, "%I64u", value);
  cout << name << " = " << buffer << endl;
}

/******************/

void dump(char *name, char value)
{ cout << name << " = chr(" << (int)value << ")" << endl; }

void dump(char *name, short int value)
{ cout << name << " = " << value << endl; }

void dump(char *name, unsigned short int value)
{ cout << name << " = " << value << endl; }

void dump(char *name, int value)
{ cout << name << " = " << value << endl; }

void dump(char *name, unsigned int value)
{ cout << name << " = " << value << endl; }

void dump(char *name, long value)
{ cout << name << " = " << value << endl; }

void dump(char *name, unsigned long value)
{ cout << name << " = " << value << endl; }

/******************/

void dump(char *name, HWND value)
{ cout << name << " = HWND(" << (int)value << ")" << endl; }

/* is HKEY signed or unsigned? */
void dump(char *name, HKEY value)
{ cout << name << " = HKEY(" << (int)value << ")" << endl; }

void dump(char *name, GUID value)
{
  wchar_t guid[64];
  bstr_t b;
  StringFromGUID2(value, guid, sizeof(guid));
  b = guid;
  cout << name << " = GUID(\"" << (char *)b << ")\"" << endl;
}

void dump(char *name, void *value)
{ cout << name << " = VOIDP(" << value << ")" << endl; }

//void *
//HDDEDATA
//CERT_INFO


/******************
 This catches all remaining cases - writes a comment to the output.
 XXX Unfortunately, it also catches enum, and I don't know enough C++
 to avoid that...

 So maybe it's better to comment this all out...
*/

/*
template < class T> void dump(char *name, T value)
{ cout << "# " << name << " = " << value << endl; }
*/

/******************/

#define DUMP(sym) dump(#sym, sym)


[Setup]
AppName=gccxml
AppVerName=gccxml-20041208
DefaultDirName={pf}\gccxml
DefaultGroupName=gccxml
Compression=lzma
;;Compression=None
SolidCompression=yes
LicenseFile="C:\sf\gccxml\GCC_XML\Copyright.txt"
InfoBeforeFile=snapshot.txt

[Files]
Source: "C:\sf\gccxml\GCC_XML\Copyright.txt"; DestDir: "{app}\doc"; Flags: ignoreversion
Source: "C:\sf\buildgcc\bin\release\snapshot.txt"; DestDir: "{app}\doc"; Destname: README.txt; Flags: ignoreversion

Source: "C:\sf\buildgcc\bin\release\gccxml.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "C:\sf\buildgcc\bin\release\gccxml_cc1plus.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "C:\sf\buildgcc\bin\release\vcInstallPatch.exe"; DestDir: "{app}\install"; Flags: ignoreversion
Source: "C:\sf\buildgcc\bin\release\vcInstall.exe"; DestDir: "{app}\install"; Flags: ignoreversion

Source: "C:\sf\gccxml\GCC_XML\VcInstall\*.patch"; DestDir: "{app}\install"; Flags: ignoreversion
Source: "C:\sf\gccxml\GCC_XML\VcInstall\vcCat.exe"; DestName: cat.exe; DestDir: "{app}\install"; Flags: ignoreversion
Source: "C:\sf\gccxml\GCC_XML\VcInstall\vcPatch.exe"; DestName: patch.exe; DestDir: "{app}\install"; Flags: ignoreversion
Source: "config"; DestDir: "{app}\bin";

[Icons]
Name: {group}\Uninstall gccxml; Filename: {uninstallexe}; Comment: Click to uninstall gccxml

[Run]
Filename: "{app}\install\vcInstall.exe"; WorkingDir: "{app}\install"; Parameters: ". ..\bin"

[UninstallDelete]
Type: files; Name: {app}\bin\config
Type: filesandordirs; Name: {app}\bin\Vc6
Type: filesandordirs; Name: {app}\bin\Vc7
Type: filesandordirs; Name: {app}\bin\Vc71

[Registry]
Root: HKLM; Subkey: "Software\gccxml"; ValueType: string; ValueName: "loc"; ValueData: {app}; Flags: uninsdeletekey

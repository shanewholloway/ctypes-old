[Setup]
AppName=gccxml

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
AppVerName=gccxml-20050318
OutputBaseFileName=gccxml-20050318-setup
InfoBeforeFile=snapshot.txt
;AppVerName=gccxml-20050318-vctk
;OutputBaseFileName=gccxml-20050318-vctk-setup
;InfoBeforeFile=snapshot-vctk.txt

DefaultDirName={pf}\gccxml
DefaultGroupName=gccxml
Compression=lzma
SolidCompression=yes
LicenseFile="C:\sf\gccxml\GCC_XML\Copyright.txt"
OutputDir="c:\inout"

[Files]
Source: "C:\sf\gccxml\GCC_XML\Copyright.txt"; DestDir: "{app}\doc"; Flags: ignoreversion

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Source: "snapshot.txt"; DestDir: "{app}\doc"; Destname: README.txt; Flags: ignoreversion
;Source: "snapshot-vctk.txt"; DestDir: "{app}\doc"; Destname: README.txt; Flags: ignoreversion

Source: "C:\sf\buildgcc6\bin\minsizerel\gccxml.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
Source: "C:\sf\buildgcc6\bin\minsizerel\gccxml_cc1plus.exe"; DestDir: "{app}\bin"; Flags: ignoreversion
;Source: "C:\sf\buildgcc6\bin\minsizerel\vcInstallPatch.exe"; DestName: "patch.exe"; DestDir: "{app}\install"; Flags: ignoreversion
Source: "C:\sf\buildgcc6\bin\minsizerel\vcInstall.exe"; DestDir: "{app}\install"; Flags: ignoreversion

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

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;Type: filesandordirs; Name: {app}\bin\WS2003PlatformSDK

[Registry]
Root: HKLM; Subkey: "Software\gccxml"; ValueType: string; ValueName: "loc"; ValueData: {app}; Flags: uninsdeletekey

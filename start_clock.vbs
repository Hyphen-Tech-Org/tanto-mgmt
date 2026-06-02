' Launches the analog clock without showing a console window.
' Double-click this file to run.
Option Explicit
Dim fso, shell, dir
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = dir
' pythonw.exe runs without a console. 3rd arg 0 = hidden window.
shell.Run "pythonw.exe " & Chr(34) & dir & "\clock_qt.py" & Chr(34), 0, False

@echo off
python .\buildsystem\generateVersionHeaderFile.py Engine\src\Engine\Core\Version.h .\Version.lua

@echo on
.\vendor\premake\premake5.exe vs2022

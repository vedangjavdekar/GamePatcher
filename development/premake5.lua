include "Version.lua"
include "Dependencies.lua"

workspace "Shooter"
   configurations { "Debug", "Release","Shipping" }
   architecture "x86_64"

versionPath = "version%{Version.Major}_%{Version.Minor}/" 
projectLocation = "%{wks.location}/build/%{prj.name}"
basedir = "%{wks.location}/"
outputdir = "%{cfg.buildcfg}"
targetPath = basedir .. "bin/" .. versionPath .. outputdir
objectPath = basedir .. "bin-int/".. versionPath .. outputdir 
debugPath =  basedir 

group "Dependencies"
   include "Engine/vendor/raylib"
group ""

group "Core"
   include "Engine"
group ""

group "Applications"
   include "Game"
group ""
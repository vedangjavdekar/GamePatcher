project "Engine"
    kind "StaticLib"
    language "C++"
    cppdialect "C++17"

    targetdir(targetPath)
    objdir(objectPath)
    location(projectLocation)

    dependson {
       "raylib"
    }

    links{
        "raylib"
    }

    files { 
        "src/**.h",
        "src/**.cpp"
    }

    pchheader "epch.h"
	pchsource "src/epch.cpp"

    defines{
        "BUILD_LIBTYPE_SHARED"
    }

    includedirs {
        "src",
        "%{IncludeDirs.raylib}",
        "%{IncludeDirs.spdlog}"
    }

    filter "configurations:Debug"
        defines { "DEBUG" }
        symbols "On"

    filter "configurations:Release"
        defines { "NDEBUG" }
        optimize "On"
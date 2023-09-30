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
        defines { "BUILD_DEBUG" }
        symbols "On"

    filter "configurations:Release"
        defines { "BUILD_RELEASE" }
        optimize "On"

    filter "configurations:Shipping"
        defines { "BUILD_SHIPPING" }
        optimize "On"
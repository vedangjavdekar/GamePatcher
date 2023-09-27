project "Game"
    kind "ConsoleApp"
    language "C++"
    cppdialect "C++17"

    targetdir(targetPath)
    objdir(objectPath)
    debugdir(debugPath)
    location(projectLocation)

    dependson {
       "Engine"
    }

    links{
        "Engine",
    }

    files { 
        "src/**.h",
        "src/**.cpp"
    }

    includedirs {
        "src",
        "%{wks.location}/Engine/src",
		"%{IncludeDirs.spdlog}",
		"%{IncludeDirs.raylib}",
    }

    filter "configurations:Debug"
        defines { "DEBUG" }
        symbols "On"

    filter "configurations:Release"
        defines { "NDEBUG" }
        optimize "On"
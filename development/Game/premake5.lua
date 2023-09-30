project "Game"
    kind "ConsoleApp"
    language "C++"
    cppdialect "C++17"

    targetdir(targetPath)
    objdir(objectPath)
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
        defines { "BUILD_DEBUG" }
        symbols "On"

    filter "configurations:Release"
        defines { "BUILD_RELEASE" }
        optimize "On"

    filter "configurations:Shipping"
        defines { "BUILD_SHIPPING" }
        optimize "On"
        postbuildcommands{
            "{COPYDIR} %{wks.location}/assets ".. targetPath .. "/assets" 
        }
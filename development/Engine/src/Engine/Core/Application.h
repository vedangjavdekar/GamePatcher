#pragma once
#include "Engine/Core/Base.h"
#include "Engine/Core/Window.h"

#include <string>

int main(int argc, char** argv);

namespace Engine
{
    class Application
    {
    public:
        Application();
        virtual ~Application();

        void Quit();

        static Application& Get() { return *s_Instance; }
        
        Window& GetWindow() { return *m_Window; }

        const char* GetApplicationBasePath()const { return m_AppBasePath.c_str(); }

    protected:
        virtual void OnInit() = 0;
        virtual void OnUpdate(const float dt) = 0;
        virtual void OnDraw() = 0;
        virtual void OnShutdown() = 0;

    private:
        void Run();

    protected:
        std::string m_AppBasePath;

        bool m_Running = false;

        Scope<Window> m_Window;

    private:
        static Application* s_Instance;
        friend int ::main(int argc, char** argv);
    };

    // To be defined in CLIENT
    Application* CreateApplication();
}
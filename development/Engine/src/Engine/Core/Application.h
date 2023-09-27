#pragma once
#include "Engine/Core/Base.h"
#include "Engine/Core/Window.h"

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

    private:
        void Run();

    private:
        bool m_Running = false;

        Scope<Window> m_Window;

    private:
        static Application* s_Instance;
        friend int ::main(int argc, char** argv);
    };

    // To be defined in CLIENT
    Application* CreateApplication();
}
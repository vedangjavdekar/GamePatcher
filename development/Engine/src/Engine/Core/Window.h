#pragma once

#include "raylib.h"

namespace Engine
{
    struct WindowProps
    {
        const char* Title;
        uint32_t Width;
        uint32_t Height;
        bool FullScreen;
        bool ExitOnEscape;

        WindowProps(const uint32_t width = 1280, const uint32_t height = 720, const char* title = "Engine")
            :Width(width), Height(height), Title(title)
        {
#ifdef NDEBUG
            FullScreen = true;
            ExitOnEscape = false;
#else
            FullScreen = false;
            ExitOnEscape = true;
#endif
        }
    };


    class Window
    {
    public:
        static const uint32_t GAME_SCREEN_WIDTH;
        static const uint32_t GAME_SCREEN_HEIGHT;

    public:
        Window(const WindowProps& props = WindowProps());
        virtual ~Window();

        bool ShouldClose() const;

        void Update();
        
        void BeginDraw();
        void EndDraw();

        void Display();

        void SetFullscreen(bool fullscreen);

        Vector2 GetMousePosWorld() const;
    protected:
        WindowProps m_Props;

        RenderTexture2D m_Canvas;

    private:
        float m_Scale;
    };
}
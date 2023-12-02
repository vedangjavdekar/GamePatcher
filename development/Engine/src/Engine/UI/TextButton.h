#pragma once
#include <string>
#include "raylib.h"

namespace Engine
{
    struct ButtonStyle
    {
        Color Normal = GRAY;
        Color Hovered = ORANGE;
        Color Pressed = DARKGRAY;
    };

    struct TextStyle
    {
        Color Normal = BLACK;
        Color Hovered = WHITE;
        Color Pressed = WHITE;
    };

    class TextButton
    {
    private:
        enum class ButtonState
        {
            Normal,
            Hovered,
            Pressed
        };

    public:
        TextButton(const char *text = "Button",
                   int fontsize = 24,
                   Rectangle buttonRect = {0, 0, 200, 60},
                   ButtonStyle buttonStyle = ButtonStyle(),
                   TextStyle textStyle = TextStyle(),
                   bool adjustForOverflow = false,
                   Vector4 padding = {0, 0, 0, 0});

        void SetText(const std::string &newText, const int fontSize);
        void SetPosition(Vector2 newPosition);

        ButtonStyle &GetButtonStyle();

        TextStyle &GetTextStyle();

        void SetButtonRect(const Rectangle &NewButtonDimensions);

        void Draw();

        bool IsClicked();

    protected:
        void CalculateLayout();

    private:
        std::string m_Text;
        int m_FontSize;
        Vector4 m_Padding; // t, l, b, r
        bool m_AdjustForOverflow;

        Rectangle m_TextRect;
        Rectangle m_ButtonRect;

        ButtonStyle m_ButtonStyle;
        TextStyle m_TextStyle;

        ButtonState m_ButtonState = ButtonState::Normal;
    };

}
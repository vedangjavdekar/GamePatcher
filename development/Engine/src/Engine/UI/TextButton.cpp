#include <epch.h>

#include "TextButton.h"
#include <math.h>
#include "Engine/Core/Application.h"
#include "Engine/Core/Window.h"

namespace Engine
{
    TextButton::TextButton(const char *text,
                           int fontsize,
                           Rectangle buttonRect,
                           ButtonStyle buttonStyle,
                           TextStyle textStyle,
                           bool adjustForOverflow,
                           Vector4 padding)
        : m_Text(text), m_FontSize(fontsize), m_ButtonRect(buttonRect), m_ButtonStyle(buttonStyle), m_TextStyle(textStyle), m_AdjustForOverflow(adjustForOverflow), m_Padding(padding)
    {
        CalculateLayout();
    }

    void TextButton::SetText(const std::string &newText, const int fontSize)
    {
        m_Text = newText;
        m_FontSize = fontSize;

        CalculateLayout();
    }

    void TextButton::SetPosition(Vector2 newPosition)
    {
        m_ButtonRect.x = newPosition.x;
        m_ButtonRect.y = newPosition.y;

        CalculateLayout();
    }

    ButtonStyle &TextButton::GetButtonStyle()
    {
        return m_ButtonStyle;
    }

    TextStyle &TextButton::GetTextStyle()
    {
        return m_TextStyle;
    }

    void TextButton::SetButtonRect(const Rectangle &NewButtonDimensions)
    {
        m_ButtonRect = NewButtonDimensions;

        CalculateLayout();
    }

    void TextButton::Draw()
    {
        switch (m_ButtonState)
        {
        case ButtonState::Normal:
            DrawRectangleRec(m_ButtonRect, m_ButtonStyle.Normal);
            DrawText(m_Text.c_str(), (int)m_TextRect.x, (int)m_TextRect.y, m_FontSize, m_TextStyle.Normal);
            break;
        case ButtonState::Hovered:
            DrawRectangleRec(m_ButtonRect, m_ButtonStyle.Hovered);
            DrawText(m_Text.c_str(), (int)m_TextRect.x, (int)m_TextRect.y, m_FontSize, m_TextStyle.Hovered);
            break;
        case ButtonState::Pressed:
            DrawRectangleRec(m_ButtonRect, m_ButtonStyle.Pressed);
            DrawText(m_Text.c_str(), (int)m_TextRect.x, (int)m_TextRect.y, m_FontSize, m_TextStyle.Pressed);
            break;
        default:
            break;
        }
    }

    bool TextButton::IsClicked()
    {
        Window &appWindow = Application::Get().GetWindow();
        Vector2 mousePos = appWindow.GetMousePosWorld();

        if (CheckCollisionPointRec(mousePos, m_ButtonRect))
        {
            if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT))
            {
                m_ButtonState = ButtonState::Pressed;
            }
            else if (m_ButtonState == ButtonState::Pressed)
            {
                if (IsMouseButtonReleased(MOUSE_BUTTON_LEFT))
                {
                    m_ButtonState = ButtonState::Normal;
                    return true;
                }
            }
            else
            {
                m_ButtonState = ButtonState::Hovered;
            }
        }
        else
        {
            m_ButtonState = ButtonState::Normal;
        }

        return false;
    }

    void TextButton::CalculateLayout()
    {
        Font defaultFont = GetFontDefault();

        Vector2 textSize{(float)MeasureText(m_Text.c_str(), (int)m_FontSize), (float)m_FontSize};

        m_TextRect.width = textSize.x;
        m_TextRect.height = textSize.y;

        if (m_AdjustForOverflow)
        {
            m_ButtonRect.width = std::fmaxf(m_ButtonRect.width, m_TextRect.width + m_Padding.y + m_Padding.w);
            m_ButtonRect.height = std::fmaxf(m_ButtonRect.height, m_TextRect.height + m_Padding.x + m_Padding.z);
        }

        m_TextRect.x = m_ButtonRect.x + 0.5f * (m_ButtonRect.width - textSize.x);
        m_TextRect.y = m_ButtonRect.y + 0.5f * (m_ButtonRect.height - textSize.y);
    }

}

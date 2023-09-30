#include <epch.h>
#include "Engine/Core/Application.h"
#include <string>
#include "raymath.h"

#include "VersionText.h"

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
		TextButton(const char* text = "Button",
			int fontsize = 24,
			Rectangle buttonRect = { 0,0,200,60 },
			ButtonStyle buttonStyle = ButtonStyle(),
			TextStyle textStyle = TextStyle(),
			bool adjustForOverflow = false,
			Vector4 padding = {0,0,0,0})
			:m_Text(text)
			, m_FontSize(fontsize)
			, m_ButtonRect(buttonRect)
			, m_ButtonStyle(buttonStyle)
			, m_TextStyle(textStyle)
			, m_AdjustForOverflow(adjustForOverflow)
			, m_Padding(padding)
		{
			CalculateLayout();
		}

		void SetText(const std::string& newText, const int fontSize)
		{
			m_Text = newText;
			m_FontSize = fontSize;

			CalculateLayout();
		}
		
		void SetPosition(Vector2 newPosition)
		{
			m_ButtonRect.x = newPosition.x;
			m_ButtonRect.y = newPosition.y;

			CalculateLayout();
		}

		ButtonStyle& GetButtonStyle()
		{
			return m_ButtonStyle;
		}

		TextStyle& GetTextStyle()
		{
			return m_TextStyle;
		}

		void SetButtonRect(const Rectangle& NewButtonDimensions)
		{
			m_ButtonRect = NewButtonDimensions;

			CalculateLayout();
		}

		void Draw()
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

		bool IsClicked()
		{
			Window& appWindow = Application::Get().GetWindow();
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

	protected:
		void CalculateLayout()
		{
			Font defaultFont = GetFontDefault();

			Vector2 textSize{ (float)MeasureText(m_Text.c_str(), (int)m_FontSize), (float)m_FontSize };


			m_TextRect.width = textSize.x;
			m_TextRect.height = textSize.y;

			if (m_AdjustForOverflow)
			{
				m_ButtonRect.width = std::max(m_ButtonRect.width, m_TextRect.width + m_Padding.y + m_Padding.w);
				m_ButtonRect.height = std::max(m_ButtonRect.height, m_TextRect.height + m_Padding.x + m_Padding.z);
			}

			m_TextRect.x = m_ButtonRect.x + 0.5f * (m_ButtonRect.width - textSize.x);
			m_TextRect.y = m_ButtonRect.y + 0.5f * (m_ButtonRect.height- textSize.y);
		}

	private:
		std::string m_Text;
		int m_FontSize;
		Vector4 m_Padding;// t, l, b, r
		bool m_AdjustForOverflow;

		Rectangle m_TextRect;
		Rectangle m_ButtonRect;
		
		ButtonStyle m_ButtonStyle;
		TextStyle m_TextStyle;

		ButtonState m_ButtonState = ButtonState::Normal;

	};

	Application* Application::s_Instance = nullptr;

	Application::Application()
		:m_Running(true)
	{
		s_Instance = this;

		std::string appDir(GetApplicationDirectory());

#ifndef BUILD_SHIPPING
		size_t binPos = appDir.find("bin");
		if (binPos != std::string::npos)
		{
			m_AppBasePath = appDir.substr(0, binPos);
		}
#else
		m_AppBasePath = appDir;
#endif

	}

	Application::~Application()
	{
	}

	void Application::Quit()
	{
		m_Running = false;
	}

	void Application::Run()
	{
		WindowProps windowProps;
		windowProps.FullScreen = false;
		windowProps.ExitOnEscape = true;
        m_Window = CreateScope<Window>(windowProps);

		VersionText versionText;

		TextButton button("Fullscreen", 32, { 10,50,200,64 }, ButtonStyle(), TextStyle(), false, { 10,10,10,10 });
		
		bool fullScreen = false;


		std::string imagePath = m_AppBasePath + "assets/RTS/Crate.png";
		Image image = LoadImage(imagePath.c_str());
		Texture2D texture = LoadTextureFromImage(image);          // Image converted to texture, GPU memory (VRAM)
		UnloadImage(image);   // Once image has been converted to texture and uploaded to VRAM, it can be unloaded from RAM

        // Main game loop
        while (!m_Window->ShouldClose())    // Detect window close button or ESC key
        {
			m_Window->Update();
			
			if (button.IsClicked())
			{
				fullScreen = !fullScreen;
				m_Window->SetFullscreen(fullScreen);
			}

			m_Window->BeginDraw();

			button.Draw();

			DrawTexture(texture, Window::GAME_SCREEN_WIDTH/ 2 - texture.width / 2, Window::GAME_SCREEN_HEIGHT/ 2 - texture.height / 2, WHITE);

			versionText.Draw();
			m_Window->EndDraw();
			m_Window->Display();
        }

	}

}
#include <epch.h>
#include "Engine/Core/VersionText.h"
#include "Engine/Core/Version.h"
#include "Engine/Core/Window.h"


namespace Engine
{
	const size_t VersionTextFontSize = 32;
	const Color VersionTextColor = Color{ 0, 0, 0, 128 };


	VersionText::VersionText()
	{
		m_TextSize = MeasureTextEx(GetFontDefault(), VERSION_STRING, VersionTextFontSize, 0);
	}

	void VersionText::Draw()
	{
		Vector2 textPosition{ 0,Engine::Window::GAME_SCREEN_HEIGHT - m_TextSize.y };
		DrawText(VERSION_STRING, (int)textPosition.x, (int)textPosition.y, VersionTextFontSize, VersionTextColor);
	}
}
#pragma once
#include "raylib.h"

namespace Engine
{
	class VersionText
	{
	public:
		VersionText();

		void Draw();
	private:
		Vector2 m_TextSize;
	};
}
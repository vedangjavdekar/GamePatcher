#include <epch.h>
#include "raymath.h"

#include "Engine/Core/Window.h"

namespace Engine
{
	const uint32_t Window::GAME_SCREEN_WIDTH = 1920;
	const uint32_t Window::GAME_SCREEN_HEIGHT = 1080;

	Window::Window(const WindowProps& props)
		:m_Props(props),
		m_Scale(1.0f)
	{
		SetConfigFlags(FLAG_VSYNC_HINT);
		InitWindow(props.Width, props.Height, props.Title);

		SetWindowMinSize(GAME_SCREEN_WIDTH/2, GAME_SCREEN_HEIGHT/2);
		SetTargetFPS(60);

		m_Canvas = LoadRenderTexture(GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT);
		SetTextureFilter(m_Canvas.texture, TEXTURE_FILTER_BILINEAR);

		if (props.FullScreen)
		{
			const int display = GetCurrentMonitor();
			// if we are not full screen, set the window size to match the monitor we are on
			SetWindowSize(GetMonitorWidth(display), GetMonitorHeight(display));
			// toggle the state
			ToggleFullscreen();
		}
		else
		{
			if (!props.ExitOnEscape)
			{
				SetExitKey(0);
			}
		}
	}

	Window::~Window()
	{
		UnloadRenderTexture(m_Canvas);
		CloseWindow();
	}

	bool Window::ShouldClose() const
	{
		return WindowShouldClose();
	}

	void Window::Update()
	{
		m_Scale = std::fmin((float)GetScreenWidth() / GAME_SCREEN_WIDTH, (float)GetScreenHeight() / GAME_SCREEN_HEIGHT);
	}

	void Window::BeginDraw()
	{
		BeginTextureMode(m_Canvas);
		ClearBackground(RAYWHITE);
	}

	void Window::EndDraw()
	{
		EndTextureMode();
	}

	void Window::Display()
	{
		BeginDrawing();
		ClearBackground(BLACK);     // Clear screen background

		const float scaledWidth = GAME_SCREEN_WIDTH * m_Scale;
		const float scaledHeight = GAME_SCREEN_HEIGHT * m_Scale;

		// Draw render texture to screen, properly scaled
		DrawTexturePro(
			m_Canvas.texture, //Texture
			Rectangle{ 0.0f, 0.0f, (float)m_Canvas.texture.width, (float)-m_Canvas.texture.height }, // SrcRect
			Rectangle{
				0.5f * (GetScreenWidth() - scaledWidth) ,
				0.5f * (GetScreenHeight() - scaledHeight),
				scaledWidth,
				scaledHeight
			}, // DstRect
			Vector2{ 0, 0 }, // Origin
			0.0f, // Rotation
			WHITE); // Tint

		EndDrawing();
	}

	void Window::SetFullscreen(bool fullscreen)
	{
		if (fullscreen)
		{
			if (!IsWindowFullscreen())
			{
				int display = GetCurrentMonitor();
				// if we are not full screen, set the window size to match the monitor we are on
				SetWindowSize(GetMonitorWidth(display), GetMonitorHeight(display));
				ToggleFullscreen();
			}
		}
		else
		{
			if (IsWindowFullscreen())
			{
				ToggleFullscreen();
				// if we are full screen, then go back to the windowed size
				SetWindowSize(m_Props.Width, m_Props.Height);
			}
		}
	}

	Vector2 Window::GetMousePosWorld() const
	{
		// Update virtual mouse (clamped mouse value behind game screen)
		const Vector2 mouse = GetMousePosition();

		const float scaledWidth = GAME_SCREEN_WIDTH * m_Scale;
		const float scaledHeight = GAME_SCREEN_HEIGHT * m_Scale;

		Vector2 virtualMouse = { 0 };
		virtualMouse.x = (mouse.x - 0.5f * (GetScreenWidth() - scaledWidth)) / m_Scale;
		virtualMouse.y = (mouse.y - 0.5f * (GetScreenHeight() - scaledHeight)) / m_Scale;

		virtualMouse = Vector2Clamp(
			virtualMouse,
			Vector2{ 0, 0 },
			Vector2{ (float)GAME_SCREEN_WIDTH, (float)GAME_SCREEN_HEIGHT }
		);
		return virtualMouse;
	}
}
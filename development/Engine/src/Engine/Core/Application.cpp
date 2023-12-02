#include <epch.h>
#include "Engine/Core/Application.h"
#include <string>
#include "raymath.h"

#include "VersionText.h"
#include "Version.h"
#include "Engine/UI/TextButton.h"

namespace Engine
{
	Application *Application::s_Instance = nullptr;

	Application::Application()
		: m_Running(true)
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

		TextButton button("Fullscreen", 32, {10, 50, 200, 64}, ButtonStyle(), TextStyle(), false, {10, 10, 10, 10});

		bool fullScreen = false;

		OnInit();
		
		// Main game loop
		while (!m_Window->ShouldClose()) // Detect window close button or ESC key
		{
			m_Window->Update();

			if (button.IsClicked())
			{
				fullScreen = !fullScreen;
				m_Window->SetFullscreen(fullScreen);
			}

			OnUpdate(GetFrameTime());

			m_Window->BeginDraw();

			button.Draw();

			OnDraw();
			
			versionText.Draw();
			m_Window->EndDraw();
			m_Window->Display();
		}

		OnShutdown();
	}

}
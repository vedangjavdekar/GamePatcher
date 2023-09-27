#pragma once
#include "Engine/Core/Base.h"
#include "Engine/Core/Application.h"

extern Engine::Application* Engine::CreateApplication();

int main(int argc, char** argv)
{
	Engine::Log::Init();

	auto app = Engine::CreateApplication();
	app->Run();
	delete app;
}
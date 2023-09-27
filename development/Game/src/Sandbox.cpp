#include <Engine.h>
#include "Engine/Core/EntryPoint.h"

class Sandbox : public Engine::Application
{
public:
	Sandbox() {	}
	virtual ~Sandbox() { }
};

Engine::Application* Engine::CreateApplication()
{
	return new Sandbox();
}

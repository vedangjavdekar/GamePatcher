#include <Engine.h>
#include "Engine/Core/EntryPoint.h"
#include "Engine/Core/Version.h"

class Sandbox final: public Engine::Application
{
public:
	Sandbox() {	}
	virtual ~Sandbox() { }
protected:
	void OnInit() override
	{
		// TODO: Refactor
		std::string imagePath;

		if constexpr(Engine::MAJOR_VERSION == 1 && Engine::MINOR_VERSION == 1)
		{
			imagePath = m_AppBasePath + "assets/RTS/Crate_1_1.png";
		}
		else
		{
			imagePath = m_AppBasePath + "assets/RTS/Crate_1_0.png";
		}

		Image image = LoadImage(imagePath.c_str());
		m_Texture = LoadTextureFromImage(image); 
		UnloadImage(image);								 
	}
	
	void OnUpdate(const float dt) override
	{

	}

	void OnDraw() override
	{
		DrawTexture(m_Texture, 300, 300, WHITE);
	}

	void OnShutdown()override
	{
		UnloadTexture(m_Texture);
	}

private:
	Texture2D m_Texture;

};

Engine::Application* Engine::CreateApplication()
{
	return new Sandbox();
}

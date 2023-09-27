#pragma once

#include "Engine/Core/Base.h"

// This ignores all warnings raised inside External headers
#pragma warning(push, 0)
#include <spdlog/spdlog.h>
#include <spdlog/fmt/ostr.h>
#pragma warning(pop)

namespace Engine
{
	class Log
	{
	public:
		static void Init();

		static Ref<spdlog::logger>& GetCoreLogger() { return s_CoreLogger; }
		static Ref<spdlog::logger>& GetClientLogger() { return s_ClientLogger; }
	private:
		static Ref<spdlog::logger> s_CoreLogger;
		static Ref<spdlog::logger> s_ClientLogger;
	};

}

// Core log macros
#define ECORE_LOG(...)    ::Engine::Log::GetCoreLogger()->trace(__VA_ARGS__)
#define ECORE_INFO(...)     ::Engine::Log::GetCoreLogger()->info(__VA_ARGS__)
#define ECORE_WARN(...)     ::Engine::Log::GetCoreLogger()->warn(__VA_ARGS__)
#define EHZ_CORE_ERROR(...)    ::Engine::Log::GetCoreLogger()->error(__VA_ARGS__)
#define EHZ_CORE_CRITICAL(...) ::Engine::Log::GetCoreLogger()->critical(__VA_ARGS__)

// Client log macros
#define E_LOG(...)         ::Engine::Log::GetClientLogger()->trace(__VA_ARGS__)
#define E_INFO(...)          ::Engine::Log::GetClientLogger()->info(__VA_ARGS__)
#define E_WARN(...)          ::Engine::Log::GetClientLogger()->warn(__VA_ARGS__)
#define E_ERROR(...)         ::Engine::Log::GetClientLogger()->error(__VA_ARGS__)
#define E_CRITICAL(...)      ::Engine::Log::GetClientLogger()->critical(__VA_ARGS__)
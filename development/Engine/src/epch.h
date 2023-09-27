#pragma once

#ifndef NOMINMAX
    // See github.com/skypjack/entt/wiki/Frequently-Asked-Questions#warning-c4003-the-min-the-max-and-the-macro
    #define NOMINMAX
#endif

#include "raylib.h"

#include "Engine/Core/PlatformDefines.h"

#include <iostream>
#include <memory>
#include <utility>
#include <algorithm>
#include <functional>

#include <string>
#include <sstream>
#include <array>
#include <vector>
#include <unordered_map>
#include <unordered_set>

#include "Engine/Core/Base.h"
#include "Engine/Core/Log.h"

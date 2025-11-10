# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-11-09

### 🚨 Breaking Changes
- **Major API simplification** - Complete rewrite for cleaner, more intuitive routing
- Decorator renamed from `@view()` to `@route()` for clarity
- Views now return `ft.View` objects directly instead of lists of controls
- **Removed `@ft.component` requirement** - Views are now simple functions
- Removed `ViewProxy` and dynamic view property updates via `on_load`
- `on_load` function signature simplified - no longer accepts `page` or `view` parameters
- View properties (appbar, bgcolor, etc.) now set directly in the returned `ft.View` object

### Added
- **Stack navigation with "+" prefix** - Use `+/route` to stack views, `/route` to replace stack
  - Example: `push_route("+/products")` stacks the view, `push_route("/")` replaces entire stack
- Automatic state wrapping for reactive updates - state method calls now trigger re-renders automatically
- Better state isolation per route instance - each parameterized route (e.g., `/user/123`) gets its own state
- Enhanced loading state management with `loading_routes` and `loaded_routes` tracking
- `RouterState` class for centralized router state management
- Improved error handling in `on_load` functions with detailed error logging

### Changed
- Views are now simple functions returning `ft.View` objects (no decorator wrappers needed)
- Simplified initialization - no more `initialize_with_route()` complexity
- Route matching logic optimized for better performance
- State management now uses automatic method wrapping for reactivity
- `on_load` parameters are now positional based on function signature order
- Cleaner separation between route pattern and actual route instances

### Removed
- `ViewProxy` class - view properties no longer modifiable in `on_load`
- `view_kwargs_cache` - view properties now set directly in view functions
- Complex initialization logic - simplified to single state initialization
- `page` and `view` parameters from `on_load` function signature
- `@ft.component` requirement for view functions

### Improved
- **Dramatically simplified API** - easier to learn and use
- Better performance with optimized state management
- More predictable behavior with explicit stack vs replace navigation
- Cleaner code structure with less boilerplate
- Enhanced debugging with detailed console logging
- More intuitive mental model - views are just functions that return views

### Migration Guide from 0.2.x

#### 1. Update decorator name
```python
# Before (0.2.x)
from flet_stack import view

@view("/")
@ft.component
def home_view():
    return [ft.Text("Home")]

# After (0.3.0)
from flet_stack import route

@route("/")
def home_view():
    return ft.View(
        controls=[ft.Text("Home")]
    )
```

#### 2. Return ft.View objects instead of control lists
```python
# Before (0.2.x)
@view("/profile", appbar=ft.AppBar())
@ft.component
def profile_view():
    return [
        ft.Text("Profile"),
        ft.Button("Click me")
    ]

# After (0.3.0)
@route("/profile")
def profile_view():
    return ft.View(
        appbar=ft.AppBar(),
        controls=[
            ft.Text("Profile"),
            ft.Button("Click me")
        ]
    )
```

#### 3. Update navigation to use stack syntax
```python
# Before (0.2.x)
asyncio.create_task(ft.context.page.push_route("/products"))

# After (0.3.0) - Stack navigation
asyncio.create_task(ft.context.page.push_route("+/products"))

# After (0.3.0) - Replace navigation
asyncio.create_task(ft.context.page.push_route("/"))
```

#### 4. Update on_load signatures
```python
# Before (0.2.x)
async def load_user(state, view, user_id):
    state.user = fetch_user(user_id)
    view.appbar = ft.AppBar(title=ft.Text(state.user['name']))

# After (0.3.0)
async def load_user(state, user_id):
    state.user = fetch_user(user_id)
    # Set appbar in the view function instead
```

#### 5. Remove @ft.component decorator
```python
# Before (0.2.x)
@view("/counter", state_class=CounterState)
@ft.component
def counter_view(state):
    return [ft.Text(f"Count: {state.count}")]

# After (0.3.0)
@route("/counter", state_class=CounterState)
def counter_view(state):
    return ft.View(
        controls=[ft.Text(f"Count: {state.count}")]
    )
```

## [0.2.3] - 2025-10-19

### Added
- Support for dynamic view property updates via view parameter in on_load functions
- `ViewProxy` class to allow modifying view properties (appbar, bgcolor, etc.) during loading
- `view_kwargs_cache` in `AppModel` to store updated view properties per route instance

### Changed
- `on_load` functions can now accept a view parameter to modify view properties dynamically
- View properties can be updated based on loaded data (e.g., setting appbar title from API response)

### Improved
- Enhanced flexibility for views that need to update their appearance based on loaded data
- Better separation between initial view configuration and runtime modifications

## [0.2.2] - 2025-10-16

### Fixed
- Remove appending `view_kwargs` in loading view

## [0.2.1] - 2025-10-16

### Added
- Support for custom initial routes via `page.route`
- `initialize_with_route()` method in `AppModel` for explicit route initialization
- `initialized` flag to track route initialization state
- Better support for authentication flows and deep linking

### Fixed
- Initial route was always defaulting to `/` regardless of `page.route` setting
- Routes list initialization now respects the page's initial route
- Proper `on_load` trigger for custom initial routes

### Improved
- Documentation updated with examples for setting initial routes
- Enhanced initialization logic to prevent route duplication on startup

## [0.2.0] - 2025-10-16

### 🚨 Breaking Changes
- **Complete architecture rewrite** to use Flet's new component system
- Requires **Flet >= 0.70.0.dev6281** (new component architecture)
- Views must now use `@ft.component` decorator
- State classes must use `@ft.observable` and `@dataclass`
- Navigation changed from `page.go()` to `ft.context.page.push_route()`
- Main app initialization changed from `ft.run(main)` to using `page.render_views(FletStack)`
- Removed automatic `ft.run()` patching - now uses explicit `FletStack` component

### Added
- `FletStack` component for managing view stack and routing
- Integration with Flet's `@ft.observable` for reactive state management
- Integration with Flet's `@ft.component` decorator
- `AppModel` class for managing routing state
- Support for `ft.context.page` in view components
- Better view stack management with proper back navigation
- Improved route state persistence across navigation
- Enhanced 404 handling with component architecture
- `render_view_for_route()` helper function for view rendering

### Changed
- View functions now return lists of controls instead of Column/Container
- State management now uses observable dataclasses
- Navigation now uses `asyncio.create_task(ft.context.page.push_route())`
- Loading indicators now properly integrate with component lifecycle
- Route matching improved for better performance
- View registration simplified with cleaner decorator pattern
- State initialization moved to observable dataclass defaults

### Improved
- Performance improvements with component-based rendering
- Better separation of concerns between routing and view logic
- More predictable state management with observables
- Cleaner API surface with explicit `FletStack` component
- Enhanced type hints and documentation

## [0.1.0] - 2025-10-06

### Added
- Initial release of flet-stack
- `@view()` decorator for route definition
- Automatic view stacking from URL paths
- State management with `state_class` parameter
- Async loading support with `on_load` parameter
- URL parameter extraction (e.g., `/user/{id}`)
- Automatic loading indicators during async operations
- Support for custom view properties via `**view_kwargs`
- Automatic routing via patched `ft.run()`
- 404 handling for undefined routes
- Prevention of duplicate route processing

### Features
- Decorator-based routing
- Automatic view stack creation from nested paths
- Built-in state management
- Support for both sync and async `on_load` functions
- Flexible parameter injection for view functions
- Regex-based route matching with named groups

[0.3.0]: https://github.com/fasilwdr/flet-stack/releases/tag/v0.3.0
[0.2.3]: https://github.com/fasilwdr/flet-stack/releases/tag/v0.2.3
[0.2.2]: https://github.com/fasilwdr/flet-stack/releases/tag/v0.2.2
[0.2.1]: https://github.com/fasilwdr/flet-stack/releases/tag/v0.2.1
[0.2.0]: https://github.com/fasilwdr/flet-stack/releases/tag/v0.2.0
[0.1.0]: https://github.com/fasilwdr/flet-stack/releases/tag/v0.1.0
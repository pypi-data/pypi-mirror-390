import asyncio
import inspect
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any, Tuple, Set
import flet as ft

# Global registry to store route mappings
# Now stores tuple of (view_function, state_class, on_load_function)
_route_registry: Dict[str, Tuple[Callable, Optional[type], Optional[Callable]]] = {}


def match_route(pattern: str, actual_route: str) -> Optional[Dict[str, str]]:
    """
    Match a route pattern against an actual route.
    Returns dict of parameters if match, None otherwise.

    Example:
        pattern: '/blogs/{blog_id}'
        actual_route: '/blogs/43'
        returns: {'blog_id': '43'}
    """
    pattern_parts = pattern.split('/')
    route_parts = actual_route.split('/')

    if len(pattern_parts) != len(route_parts):
        return None

    params = {}
    for pattern_part, route_part in zip(pattern_parts, route_parts):
        if pattern_part.startswith('{') and pattern_part.endswith('}'):
            # This is a parameter
            param_name = pattern_part[1:-1]
            params[param_name] = route_part
        elif pattern_part != route_part:
            # Static parts don't match
            return None

    return params


def find_matching_route(actual_route: str) -> Optional[Tuple[str, Dict[str, str]]]:
    """
    Find a matching route pattern for the actual route.
    Returns tuple of (pattern, params) if found, None otherwise.
    """
    # First try exact match (for routes without parameters)
    if actual_route in _route_registry:
        return (actual_route, {})

    # Then try pattern matching
    for pattern in _route_registry.keys():
        params = match_route(pattern, actual_route)
        if params is not None:
            return (pattern, params)

    return None


def route(path: str, state_class: Optional[type] = None, on_load: Optional[Callable] = None):
    """
    Decorator to register a view function for a specific route.

    Args:
        path: The route path (e.g., '/', '/store', '/blogs/{blog_id}')
              Can include URL parameters in curly braces
        state_class: Optional state class to instantiate and pass to the view function
        on_load: Optional function to call before rendering the view.
                 Can be sync or async.
                 Signature: on_load(state, param1, param2, ...) if state_class provided
                           on_load(param1, param2, ...) if no state_class
                 While on_load executes, a loading view will be displayed.

    Example with parameters:
        @route('/blogs/{blog_id}', state_class=BlogState, on_load=load_blog)
        def blog_view(blog_id, state):
            return ft.View(...)

        def load_blog(state, blog_id):
            state.title = f"Blog {blog_id}"
    """

    def decorator(func: Callable):
        _route_registry[path] = (func, state_class, on_load)
        return func

    return decorator


def get_404_view(route: str) -> ft.View:
    """Returns a 404 view for routes that are not found."""
    return ft.View(
        route=route,
        appbar=ft.AppBar(),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Icon(ft.Icons.ERROR_OUTLINE, size=100, color=ft.Colors.RED_400),
            ft.Text("404 - Page Not Found", size=32, weight=ft.FontWeight.BOLD),
        ]
    )


def get_loading_view(route: str) -> ft.View:
    """Returns a loading view while on_load is executing."""
    return ft.View(
        route=route,
        controls=[ft.ProgressRing()],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )


@ft.observable
@dataclass
class RouterState:
    """State management for the router."""
    current_route: str
    view_stack: List[str] = field(default_factory=list)
    # Store state instances for each route instance (actual route with param values as key)
    # E.g., '/blogs/43' and '/blogs/44' will have separate state instances
    route_states: Dict[str, Any] = field(default_factory=dict)
    # Track which routes are currently loading (actual route as key)
    loading_routes: Set[str] = field(default_factory=set)
    # Track which routes have completed their on_load (actual route as key)
    loaded_routes: Set[str] = field(default_factory=set)
    # Version counter to trigger re-renders when route states change
    state_version: int = 0

    def route_change(self, e: ft.RouteChangeEvent):
        """Handle route change events."""
        new_route = e.route
        is_stack_navigation = new_route.startswith("+")

        # Strip the '+' prefix for actual route lookup
        actual_route = new_route[1:] if is_stack_navigation else new_route

        print(f"Route changed to: {actual_route} (stack: {is_stack_navigation})")

        if is_stack_navigation:
            # Append to stack
            if actual_route not in self.view_stack:
                self.view_stack.append(actual_route)
        else:
            # Replace entire stack
            self.view_stack = [actual_route]

        self.current_route = actual_route

        # Update page route without the '+'
        if ft.context.page.route != actual_route:
            ft.context.page.route = actual_route

    async def view_popped(self, e: ft.ViewPopEvent):
        """Handle view pop events (back button)."""
        print("View popped")

        if len(self.view_stack) > 1:
            # Remove the current view
            self.view_stack.pop()
            # Navigate to the previous view
            previous_route = self.view_stack[-1]
            await ft.context.page.push_route(previous_route)

    def get_or_create_state(self, route_path: str, state_class: Optional[type]) -> Optional[Any]:
        """Get existing state or create new state for a route."""
        if state_class is None:
            return None

        if route_path not in self.route_states:
            # Create new state instance
            state_instance = state_class()

            # Wrap the state instance to trigger re-renders on method calls
            wrapped_state = self._wrap_state(state_instance)
            self.route_states[route_path] = wrapped_state

        return self.route_states[route_path]

    def _wrap_state(self, state_instance: Any) -> Any:
        """Wrap a state instance to trigger version increments on method calls."""
        # Store the original instance
        original_instance = state_instance

        # Get all methods from the state class
        state_class = type(state_instance)

        # Wrap each method to increment version after execution
        for attr_name in dir(state_instance):
            # Skip private attributes and non-callables
            if attr_name.startswith('_'):
                continue

            attr = getattr(state_instance, attr_name)
            if callable(attr) and not attr_name.startswith('__'):
                # Create a wrapper function
                def make_wrapper(original_method):
                    def wrapper(*args, **kwargs):
                        result = original_method(*args, **kwargs)
                        # Increment version to trigger re-render
                        self.state_version += 1
                        return result

                    return wrapper

                # Replace the method with the wrapped version
                setattr(state_instance, attr_name, make_wrapper(attr))

        return state_instance


@ft.component
def FletStack():
    """
    Main routing component that manages view navigation.

    This component handles:
    - Route registration via @route decorator
    - URL parameters (e.g., /blogs/{blog_id})
    - Stack navigation (routes with '+' prefix)
    - Replace navigation (routes without '+' prefix)
    - 404 handling for unknown routes
    - State management for routes with state_class (separate state per route instance)
    - on_load hooks for route initialization
    """
    # Initialize state with current page route
    initial_route = ft.context.page.route or "/"
    state, set_state = ft.use_state(RouterState(
        current_route=initial_route,
        view_stack=[initial_route]
    ))

    # Subscribe to page events
    ft.context.page.on_route_change = state.route_change
    ft.context.page.on_view_pop = state.view_popped

    async def execute_on_load(
            route_path: str,
            on_load_func: Callable,
            route_state: Optional[Any],
            params: Dict[str, str]
    ):
        """Execute the on_load function for a route with URL parameters."""
        if route_path in state.loaded_routes:
            return  # Already loaded

        # Mark as loading
        state.loading_routes.add(route_path)
        state.state_version += 1
        ft.context.page.update()

        try:
            # Get function signature
            sig = inspect.signature(on_load_func)
            param_names = list(sig.parameters.keys())

            # Build arguments list
            args = []

            # If state_class is provided, state is the first parameter
            if route_state is not None and len(param_names) > 0:
                args.append(route_state)
                # Remaining parameters are URL parameters (in order they appear in signature)
                for param_name in param_names[1:]:
                    if param_name in params:
                        args.append(params[param_name])
            else:
                # All parameters are URL parameters (in order they appear in signature)
                for param_name in param_names:
                    if param_name in params:
                        args.append(params[param_name])

            # Execute on_load (handle both sync and async)
            if asyncio.iscoroutinefunction(on_load_func):
                await on_load_func(*args)
            else:
                # Sync function - run in thread pool to avoid blocking UI
                await asyncio.to_thread(on_load_func, *args)

        except Exception as e:
            print(f"Error in on_load for route {route_path}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Mark as loaded and no longer loading
            state.loaded_routes.add(route_path)
            if route_path in state.loading_routes:
                state.loading_routes.remove(route_path)
            state.state_version += 1
            ft.context.page.update()

    # Check for routes that need on_load execution
    for route_path in state.view_stack:
        match_result = find_matching_route(route_path)

        if match_result is not None:
            pattern, params = match_result
            view_func, state_class, on_load_func = _route_registry[pattern]

            # If route has on_load and hasn't been loaded or is not loading
            if (on_load_func is not None and
                    route_path not in state.loaded_routes and
                    route_path not in state.loading_routes):
                # Get or create state for this route instance (use actual route path as key)
                route_state = state.get_or_create_state(route_path, state_class)

                # Execute on_load asynchronously
                asyncio.create_task(execute_on_load(route_path, on_load_func, route_state, params))

    # Build views based on current stack
    views = []

    for route_path in state.view_stack:
        match_result = find_matching_route(route_path)

        if match_result is not None:
            pattern, params = match_result
            view_func, state_class, on_load_func = _route_registry[pattern]

            # Check if route is currently loading OR needs to be loaded
            if on_load_func is not None and (
                route_path in state.loading_routes or
                route_path not in state.loaded_routes
            ):
                # Show loading view while on_load executes
                views.append(get_loading_view(route_path))
            else:
                # Get or create state for this route instance (use actual route path as key)
                route_state = state.get_or_create_state(route_path, state_class)

                # Get function signature to determine parameter order
                sig = inspect.signature(view_func)
                param_names = list(sig.parameters.keys())

                # Build arguments for view function
                args = []

                # State comes first (if it exists)
                if route_state is not None:
                    args.append(route_state)
                    # Remaining parameters are URL parameters (in order they appear in signature)
                    for param_name in param_names[1:]:  # Skip first param which is state
                        if param_name in params:
                            args.append(params[param_name])
                else:
                    # All parameters are URL parameters (in order they appear in signature)
                    for param_name in param_names:
                        if param_name in params:
                            args.append(params[param_name])

                # Call the view function
                view = view_func(*args)

                # Ensure the view has the correct route set
                if hasattr(view, 'route'):
                    view.route = route_path
                views.append(view)
        else:
            # Route not found, show 404
            views.append(get_404_view(route_path))

    return views
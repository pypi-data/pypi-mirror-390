# function_collection = set()
# from collections.abc import Callable
# from typing import Any

# _showcases: dict[Callable, list[tuple[Any, str | Any]]] = {}


# def showcase(*fixtures, name: str | None = None) -> Callable:
#     """
#     Register example fixtures for component preview and testing.

#     Usage:
#         @showcase(example_post)
#         @showcase(minimal_post, name="minimal")
#         def post(post: blog_models.Post):
#             return section(...)[...]

#     The decorator enables:
#     - Automatic test generation
#     - Interactive component galleries
#     - Documentation with live examples
#     """

#     def decorator(func: Callable) -> Callable:
#         if func not in _showcases:
#             _showcases[func] = []

#         for fixture in fixtures:
#             _showcases[func].append((fixture, name))

#         # Attach metadata for introspection
#         if not hasattr(func, "__showcases__"):
#             func.__showcases__ = []
#         func.__showcases__.extend(fixtures)

#         return func

#     # Support both @showcase(fixture) and @showcase
#     if len(fixtures) == 1 and callable(fixtures[0]) and name is None:
#         # Called as @showcase without parens
#         func = fixtures[0]
#         return func

#     return decorator


# @showcase()
# def example_function():
#     pass

import sys
import types
import unittest


sublime = types.ModuleType("sublime")
sublime.DRAW_NO_OUTLINE = 0
sublime_plugin = types.ModuleType("sublime_plugin")
sublime_plugin.WindowCommand = type("WindowCommand", (), {})
sublime_plugin.EventListener = type("EventListener", (), {})
sys.modules["sublime"] = sublime
sys.modules["sublime_plugin"] = sublime_plugin

import highlighter


class View:
  def __init__(self, window=None):
    self._window = window
    self.regions = []

  def window(self):
    return self._window

  def find_all(self, pattern):
    return [(0, 4)]

  def add_regions(self, key, regions, scope, icon, flags):
    self.regions.append((key, regions, scope, icon, flags))


class Window:
  def __init__(self, view):
    self.view = view

  def views(self):
    return [self.view]


class HighlighterEventTests(unittest.TestCase):
  def setUp(self):
    highlighter.colors_by_scope.clear()
    highlighter.colors_by_scope["scope"] = "word"
    self.listener = highlighter.HighlighterCommand()

  def test_modified_view_without_window_is_ignored(self):
    view = View()

    self.listener.on_modified(view)

    self.assertEqual(view.regions, [])

  def test_activated_view_without_window_is_ignored(self):
    view = View()

    self.listener.on_activated(view)

    self.assertEqual(view.regions, [])

  def test_modified_view_with_window_is_highlighted(self):
    view = View()
    view._window = Window(view)

    self.listener.on_modified(view)

    self.assertEqual(view.regions, [("word", [(0, 4)], "scope", "dot", 0)])


if __name__ == "__main__":
  unittest.main()

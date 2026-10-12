import importlib
import re
import sys
import types
import unittest
from unittest.mock import Mock


sublime = types.ModuleType("sublime")
sublime.DRAW_NO_OUTLINE = 0
sublime.load_settings = Mock()
sublime.status_message = Mock()
sublime_plugin = types.ModuleType("sublime_plugin")


class WindowCommand:
  def __init__(self, window):
    self.window = window


sublime_plugin.WindowCommand = WindowCommand
sublime_plugin.EventListener = type("EventListener", (), {})
sys.modules["sublime"] = sublime
sys.modules["sublime_plugin"] = sublime_plugin

import highlighter


class View:
  def __init__(self, text="word", window=None):
    self.text = text
    self._window = window
    self.selection = [(0, 4)]
    self.regions = {}
    self.draw_calls = []

  def window(self):
    return self._window

  def sel(self):
    return self.selection

  def substr(self, region):
    return self.text[region[0]:region[1]]

  def word(self, region):
    for match in re.finditer(r"\w+", self.text):
      if match.start() <= region[0] < match.end():
        return match.span()
    return region

  def select(self, text):
    start = self.text.index(text)
    self.selection = [(start, start + len(text))]

  def find_all(self, pattern):
    return [match.span() for match in re.finditer(pattern, self.text)]

  def add_regions(self, key, regions, scope, icon, flags):
    payload = (key, regions, scope, icon, flags)
    self.regions[key] = payload
    self.draw_calls.append(payload)

  def erase_regions(self, key):
    self.regions.pop(key, None)


class Window:
  def __init__(self, *views):
    self._views = list(views)
    for view in views:
      view._window = self

  def active_view(self):
    return self._views[0] if self._views else None

  def views(self):
    return self._views


class HighlighterTests(unittest.TestCase):
  def setUp(self):
    highlighter.colors_by_scope.clear()
    sublime.load_settings.reset_mock()
    sublime.load_settings.side_effect = None
    sublime.load_settings.return_value = {}
    sublime.status_message.reset_mock()
    self.listener = highlighter.HighlighterCommand()

  def load_palette(self, extras=None):
    if extras is not None:
      sublime.load_settings.return_value = {"extra_scopes": extras}
    highlighter.plugin_loaded()

  def toggle(self, window, text, color=None):
    window.active_view().select(text)
    highlighter.TextHighlighterToggleCommand(window).run(color=color)

  def test_import_does_not_load_settings(self):
    sublime.load_settings.side_effect = AssertionError("settings unavailable during import")
    importlib.reload(highlighter)
    self.assertEqual(list(highlighter.colors_by_scope.items()), [])
    sublime.load_settings.assert_not_called()
    sublime.load_settings.side_effect = None
    self.load_palette()
    view = View()
    self.toggle(Window(view), "word")
    self.assertEqual(view.regions["word"],
                     ("word", [(0, 4)], "markup.changed.git_gutter", "dot", 0))

  def test_default_palette_allocates_in_existing_order(self):
    self.load_palette()
    view = View("w01 w02 w03 w04 w05 w06 w07 w08 w09")
    window = Window(view)
    for text in ("w01", "w02", "w03", "w04", "w05", "w06", "w07", "w08", "w09"):
      self.toggle(window, text)
    self.assertEqual([(payload[0], payload[2]) for payload in view.draw_calls], [
      ("w01", "markup.changed.git_gutter"),
      ("w02", "support.class"),
      ("w03", "markup.deleted.git_gutter"),
      ("w04", "markup.inserted.git_gutter"),
      ("w05", "constant.numeric"),
      ("w06", "constant.character.escape"),
      ("w07", "variable"),
      ("w08", "string"),
      ("w09", "comment"),
    ])
    sublime.load_settings.assert_called_once_with("TextHighlighter.sublime-settings")

  def test_more_than_nine_scopes_render_across_views_and_recycle(self):
    self.load_palette(["text_highlighter.cyan", "text_highlighter.magenta"])
    first = View("w01 w02 w03 w04 w05 w06 w07 w08 w09 w10 w11 w12")
    second = View("w10 w11 w12")
    window = Window(first, second)
    for text in ("w01", "w02", "w03", "w04", "w05", "w06", "w07", "w08", "w09", "w10", "w11"):
      self.toggle(window, text)
    self.assertEqual(first.regions["w10"],
                     ("w10", [(36, 39)], "text_highlighter.cyan", "dot", 0))
    self.assertEqual(first.regions["w11"],
                     ("w11", [(40, 43)], "text_highlighter.magenta", "dot", 0))
    self.assertEqual(second.regions["w10"],
                     ("w10", [(0, 3)], "text_highlighter.cyan", "dot", 0))
    self.assertEqual(highlighter.colors_by_scope["text_highlighter.cyan"], "w10")
    self.toggle(window, "w10", color="unknown.scope")
    self.assertNotIn("w10", first.regions)
    self.assertNotIn("w10", second.regions)
    self.toggle(window, "w12")
    self.assertEqual(second.regions["w12"],
                     ("w12", [(8, 11)], "text_highlighter.cyan", "dot", 0))
    self.assertEqual(highlighter.colors_by_scope["text_highlighter.cyan"], "w12")

  def test_extra_scope_can_be_selected_explicitly(self):
    self.load_palette(["text_highlighter.cyan"])
    view = View("word word")
    self.toggle(Window(view), "word", color="text_highlighter.cyan")
    self.assertEqual(view.regions["word"],
                     ("word", [(0, 4), (5, 9)], "text_highlighter.cyan", "dot", 0))
    self.assertEqual(highlighter.colors_by_scope["text_highlighter.cyan"], "word")
    self.assertIsNone(highlighter.colors_by_scope["markup.changed.git_gutter"])

  def test_duplicate_scopes_keep_first_occurrence_and_capacity(self):
    self.load_palette(["support.class", "custom.first", "custom.first", "custom.second"])
    view = View("w01 w02 w03 w04 w05 w06 w07 w08 w09 w10 w11 w12")
    window = Window(view)
    for text in ("w01", "w02", "w03", "w04", "w05", "w06", "w07", "w08", "w09", "w10", "w11", "w12"):
      self.toggle(window, text)
    self.assertEqual(view.regions["w02"], ("w02", [(4, 7)], "support.class", "dot", 0))
    self.assertEqual(view.regions["w10"], ("w10", [(36, 39)], "custom.first", "dot", 0))
    self.assertEqual(view.regions["w11"], ("w11", [(40, 43)], "custom.second", "dot", 0))
    self.assertNotIn("w12", view.regions)
    sublime.status_message.assert_called_once_with(
      "TextHighlighter: All scopes are in use. Clear a highlight or add extra_scopes and restart Sublime Text.")

  def test_invalid_settings_fall_back_to_defaults(self):
    for extras in ("custom.scope", None, {}, 42, [""], ["   "], [False], ["custom.scope", 7]):
      with self.subTest(extras=extras):
        highlighter.colors_by_scope.clear()
        sublime.status_message.reset_mock()
        sublime.load_settings.return_value = {"extra_scopes": extras}
        highlighter.plugin_loaded()
        view = View()
        self.toggle(Window(view), "word")
        self.assertEqual(view.regions["word"],
                         ("word", [(0, 4)], "markup.changed.git_gutter", "dot", 0))
        self.assertEqual(len(highlighter.colors_by_scope), 9)
        sublime.status_message.assert_called_once_with(
          "TextHighlighter: extra_scopes must be a list of nonempty scope strings. Using default scopes.")

  def test_unknown_explicit_scope_does_not_create_orphan_regions(self):
    self.load_palette()
    view = View("word next")
    window = Window(view)
    self.toggle(window, "word")
    for invalid in ("unknown.scope", "", ["support.class"], 7):
      self.toggle(window, "next", color=invalid)
    self.assertEqual(view.regions,
                     {"word": ("word", [(0, 4)], "markup.changed.git_gutter", "dot", 0)})
    self.assertEqual(highlighter.colors_by_scope["markup.changed.git_gutter"], "word")
    sublime.status_message.assert_called_with(
      "TextHighlighter: Unknown scope. Add it to extra_scopes and restart Sublime Text.")

  def test_occupied_explicit_scope_keeps_existing_highlight(self):
    self.load_palette(["custom.scope"])
    view = View("word next")
    window = Window(view)
    self.toggle(window, "word", color="custom.scope")
    self.toggle(window, "next", color="custom.scope")
    self.assertEqual(view.regions, {"word": ("word", [(0, 4)], "custom.scope", "dot", 0)})
    self.assertEqual(highlighter.colors_by_scope["custom.scope"], "word")
    sublime.status_message.assert_called_once_with(
      "TextHighlighter: Scope is already in use. Clear its highlight or choose another scope.")
    highlighter.TextHighlighterClearAllCommand(window).run()
    self.assertEqual(view.regions, {})

  def test_exhaustion_reports_status_and_preserves_highlights(self):
    self.load_palette()
    view = View("w01 w02 w03 w04 w05 w06 w07 w08 w09 w10")
    window = Window(view)
    for text in ("w01", "w02", "w03", "w04", "w05", "w06", "w07", "w08", "w09", "w10"):
      self.toggle(window, text)
    self.assertEqual(len(view.regions), 9)
    self.assertEqual(view.regions["w09"], ("w09", [(32, 35)], "comment", "dot", 0))
    self.assertNotIn("w10", view.regions)
    sublime.status_message.assert_called_once_with(
      "TextHighlighter: All scopes are in use. Clear a highlight or add extra_scopes and restart Sublime Text.")

  def test_clear_all_frees_extra_scopes_across_views(self):
    self.load_palette(["custom.scope"])
    first, second = View("word next"), View("word next")
    window = Window(first, second)
    self.toggle(window, "word", color="custom.scope")
    self.toggle(window, "next")
    highlighter.TextHighlighterClearAllCommand(window).run()
    self.assertEqual(first.regions, {})
    self.assertEqual(second.regions, {})
    self.assertTrue(all(value is None for value in highlighter.colors_by_scope.values()))
    self.toggle(window, "next", color="custom.scope")
    self.assertEqual(second.regions["next"], ("next", [(5, 9)], "custom.scope", "dot", 0))

  def test_events_refresh_extra_scopes_without_reallocating(self):
    self.load_palette(["custom.scope"])
    view = View()
    window = Window(view)
    self.toggle(window, "word", color="custom.scope")
    view.text = "word word"
    self.listener.on_modified(view)
    self.assertEqual(view.regions["word"],
                     ("word", [(0, 4), (5, 9)], "custom.scope", "dot", 0))
    next_view = View("word")
    next_view._window = window
    window._views.append(next_view)
    self.listener.on_activated(next_view)
    self.assertEqual(next_view.regions["word"], ("word", [(0, 4)], "custom.scope", "dot", 0))
    self.assertEqual(highlighter.colors_by_scope["custom.scope"], "word")
    self.toggle(window, "word")
    self.assertEqual(view.regions, {})
    self.assertEqual(next_view.regions, {})

  def test_repeated_plugin_loaded_preserves_assignments(self):
    self.load_palette(["custom.scope"])
    view = View()
    window = Window(view)
    self.toggle(window, "word", color="custom.scope")
    sublime.load_settings.return_value = {"extra_scopes": ["replacement.scope"]}
    highlighter.plugin_loaded()
    self.listener.on_modified(view)
    self.assertEqual(view.regions["word"], ("word", [(0, 4)], "custom.scope", "dot", 0))
    self.assertEqual(highlighter.colors_by_scope["custom.scope"], "word")
    self.assertNotIn("replacement.scope", highlighter.colors_by_scope)
    sublime.load_settings.assert_called_once_with("TextHighlighter.sublime-settings")

  def test_modified_view_without_window_is_ignored(self):
    self.load_palette()
    view = View()
    self.listener.on_modified(view)
    self.assertEqual(view.regions, {})

  def test_activated_view_without_window_is_ignored(self):
    self.load_palette()
    view = View()
    self.listener.on_activated(view)
    self.assertEqual(view.regions, {})

  def test_modified_view_with_window_is_highlighted(self):
    self.load_palette()
    view = View()
    self.toggle(Window(view), "word")
    self.listener.on_modified(view)
    self.assertEqual(view.regions["word"],
                     ("word", [(0, 4)], "markup.changed.git_gutter", "dot", 0))

  def test_no_selection_uses_word_under_cursor(self):
    self.load_palette()
    view = View()
    view.selection = [(1, 1)]
    highlighter.TextHighlighterToggleCommand(Window(view)).run()
    self.assertEqual(view.regions["word"],
                     ("word", [(0, 4)], "markup.changed.git_gutter", "dot", 0))

  def test_empty_selection_and_missing_view_do_not_consume_scope(self):
    self.load_palette()
    highlighter.TextHighlighterToggleCommand(Window()).run()
    empty = View("")
    empty.selection = [(0, 0)]
    highlighter.TextHighlighterToggleCommand(Window(empty)).run()
    empty.selection = []
    highlighter.TextHighlighterToggleCommand(Window(empty)).run()
    view = View()
    self.toggle(Window(view), "word")
    self.assertEqual(view.regions["word"],
                     ("word", [(0, 4)], "markup.changed.git_gutter", "dot", 0))


if __name__ == "__main__":
  unittest.main()

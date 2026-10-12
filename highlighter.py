import sublime
import sublime_plugin

import re
from collections import OrderedDict

DEFAULT_SCOPES = (
  'markup.changed.git_gutter',
  'support.class',
  'markup.deleted.git_gutter',
  'markup.inserted.git_gutter',
  'constant.numeric',
  'constant.character.escape',
  'variable',
  'string',
  'comment',
  'keyword',
  'entity.name.function',
  'entity.name.tag',
  'markup.heading',
)
colors_by_scope = OrderedDict()

class TextHighlighterToggleCommand(sublime_plugin.WindowCommand):
  def run(self, color=None):
    active_view = self.window.active_view()
    if active_view is None:
      return
    selected_region = active_view.sel()
    if not selected_region:
      return
    sel_string = active_view.substr(selected_region[0])

    # Get word on cursor if any region isn't selected.
    if not sel_string:
      word_region = active_view.word(selected_region[0])
      sel_string = active_view.substr(word_region)

    if not sel_string:
      return

    views = self.window.views()
    if is_highlighted(self.window, sel_string):
      color = find_used_color(self.window, sel_string)
      colors_by_scope[color] = None
      for view in views:
        eraser(view, sel_string)
    else:
      if color is not None:
        if not isinstance(color, str) or color not in colors_by_scope:
          sublime.status_message('TextHighlighter: Unknown scope. Add it to extra_scopes and restart Sublime Text.')
          return
        if colors_by_scope[color] is not None:
          sublime.status_message('TextHighlighter: Scope is already in use. Clear its highlight or choose another scope.')
          return
        if has_color_collision(color):
          sublime.status_message('TextHighlighter: Color is already in use. Clear its highlight or choose another scope.')
          return
      else:
        color = find_usable_color()
        if color is None:
          sublime.status_message('TextHighlighter: No distinct highlight colors are available. Clear a highlight or add extra_scopes with distinct foregrounds and restart Sublime Text.')
          return
      colors_by_scope[color] = sel_string
      for view in views:
        highlighter(view, sel_string, color)


class TextHighlighterClearAllCommand(sublime_plugin.WindowCommand):
  def run(self):
    views = self.window.views()

    for color, sel_string in colors_by_scope.items():
      colors_by_scope[color] = None
      if sel_string is not None:
        for view in views:
          eraser(view, sel_string)


class HighlighterCommand(sublime_plugin.EventListener):
  def on_activated(self, view):
    highlightAll(view)

  def on_modified(self, view):
    highlightAll(view)

def highlightAll(view):
  window = view.window()
  if window is None:
    return
  views = window.views()

  for view in views:
    for color, sel_string in colors_by_scope.items():
      if color and sel_string:
        highlighter(view, sel_string, color)

def highlighter(view, sel_string, color):
  regions = find_all(view, sel_string)
  if color and regions:
    view.add_regions(
      sel_string,
      regions,
      color,
      'dot',
      sublime.DRAW_NO_OUTLINE
      )

def eraser(view, sel_string):
  view.erase_regions(sel_string)

def find_all(view, sel_string):
  return view.find_all(re.escape(sel_string))

def is_highlighted(window, sel_string):
  global colors_by_scope

  highlighted = False
  for key, value in colors_by_scope.items():
    if value == sel_string:
      highlighted = True
      break
  return highlighted

def find_used_color(window, sel_string):
  global colors_by_scope

  color = None
  for key, value in colors_by_scope.items():
    if value == sel_string:
      color = key
  return color

def has_color_collision(candidate_scope):
  for window in sublime.windows():
    for view in window.views():
      foreground = view.style_for_scope(candidate_scope)['foreground']
      for scope, text in colors_by_scope.items():
        if text is not None and view.style_for_scope(scope)['foreground'] == foreground:
          return True
  return False

def find_usable_color():
  for scope, text in colors_by_scope.items():
    if text is None and not has_color_collision(scope):
      return scope
  return None

def plugin_loaded():
  if colors_by_scope:
    return colors_by_scope

  settings = sublime.load_settings('TextHighlighter.sublime-settings')
  extra_scopes = settings.get('extra_scopes', [])
  if not isinstance(extra_scopes, list) or any(
      not isinstance(scope, str) or not scope.strip() for scope in extra_scopes):
    sublime.status_message('TextHighlighter: extra_scopes must be a list of nonempty scope strings. Using default scopes.')
    extra_scopes = []

  for scope in list(DEFAULT_SCOPES) + extra_scopes:
    colors_by_scope[scope] = None

  return colors_by_scope

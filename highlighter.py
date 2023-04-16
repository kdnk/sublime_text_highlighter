import sublime
import sublime_plugin

import re
from collections import OrderedDict

class TextHighlighterToggleCommand(sublime_plugin.WindowCommand):
  # TODO: run this command when new tab is opened
  def run(self, color=None):
    active_view = self.window.active_view()
    selected_region = active_view.sel()
    sel_string = active_view.substr(selected_region[0])

    # Get word on cursor if any region isn't selected.
    if not sel_string:
      word_region = active_view.word(selected_region[0])
      sel_string = active_view.substr(word_region)

    views = self.window.views()
    if is_highlighted(self.window, sel_string):
      color = find_used_color(self.window, sel_string)
      for view in views:
        eraser(view, sel_string, color)
    else:
      if not color:
          color = find_usable_color(self.window, sel_string)
      for view in views:
        highlighter(view, sel_string, color)


class TextHighlighterClearAllCommand(sublime_plugin.WindowCommand):
  def run(self):
    window =self.window
    views = self.window.views()

    for sel_string in colors_by_scope.values():
      if sel_string:
        color = find_used_color(window, sel_string)
        if color:
          for view in views:
              eraser(view, sel_string, color)


class HighlighterCommand(sublime_plugin.EventListener):
  def on_activated(self, view):
    highlightAll(view)

  def on_modified(self, view):
    highlightAll(view)

def highlightAll(view):
  window = view.window()
  views = window.views()

  for view in views:
    for color, sel_string in colors_by_scope.items():
      if color and sel_string:
        highlighter(view, sel_string, color)

def highlighter(view, sel_string, color):
  global colors_by_scope
  window = view.window()

  regions = find_all(view, sel_string)
  if color and regions:
    if not colors_by_scope[color]:
      colors_by_scope[color] = sel_string

    view.add_regions(
      sel_string,
      regions,
      color,
      'dot',
      sublime.DRAW_NO_OUTLINE
      )

def eraser(view, sel_string, color):
  global colors_by_scope
  window = view.window()

  regions = find_all(view, sel_string)
  colors_by_scope[color] = None

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

def find_usable_color(window, sel_string):
  global colors_by_scope

  color = None
  for key, value in colors_by_scope.items():
    if not value:
      color = key
      break
  return color

def plugin_loaded():
  global colors_by_scope

  if 'colors_by_scope' in globals(): # Return colors_by_scope if colors_by_scope is already exists.
    return colors_by_scope

  colors_by_scope = OrderedDict() # TODO: Make color configurable
  colors_by_scope['markup.changed.git_gutter'] = None # vivid purple
  colors_by_scope['support.class'] = None # yellow
  colors_by_scope['markup.deleted.git_gutter'] = None # vivid pink
  colors_by_scope['markup.inserted.git_gutter'] = None # vivid green
  colors_by_scope['constant.numeric'] = None # orange
  colors_by_scope['constant.character.escape'] = None # light blue
  colors_by_scope['variable'] = None # red
  colors_by_scope['string'] = None # light green
  colors_by_scope['comment'] = None # glay

  return colors_by_scope

plugin_loaded()

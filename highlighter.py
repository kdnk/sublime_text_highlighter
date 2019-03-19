import sublime
import sublime_plugin

import re
from collections import OrderedDict

class TextHighlighterToggleCommand(sublime_plugin.WindowCommand):
  def __init__(self, window):
    super().__init__(window)
    if not window.project_data():
      window.set_project_data(init_color())

  # TODO: run this command when new tab is opened
  def run(self):
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
      color = find_usable_color(self.window, sel_string)
      for view in views:
        highlighter(view, sel_string, color)

class TextHighlighterClearAllCommand(sublime_plugin.WindowCommand):
  def run(self):
    window =self.window
    views = self.window.views()
    colors_by_scope = window.project_data()
    for sel_string in colors_by_scope.values():
      if sel_string:
        color = find_used_color(window, sel_string)
        if color:
          for view in views:
              eraser(view, sel_string, color)

class HighlighterCommand(sublime_plugin.EventListener):
  def on_modified(self, view):
    window = view.window()
    colors_by_scope = window.project_data()
    views = window.views()
    for view in views:
      for color, sel_string in colors_by_scope.items():
        if color and sel_string:
          highlighter(view, sel_string, color)

def highlighter(view, sel_string, color):
  window = view.window()
  colors_by_scope = window.project_data()
  regions = find_all(view, sel_string)
  if color and regions:
    if not colors_by_scope[color]:
      colors_by_scope[color] = sel_string
      window.set_project_data(colors_by_scope)
    view.add_regions(
      sel_string,
      regions,
      color,
      'dot',
      sublime.DRAW_NO_OUTLINE
      )

def eraser(view, sel_string, color):
  window = view.window()
  colors_by_scope = window.project_data()

  regions = find_all(view, sel_string)
  colors_by_scope[color] = None
  window.set_project_data(colors_by_scope)
  view.erase_regions(sel_string)

def find_all(view, sel_string):
  return view.find_all(re.escape(sel_string))

def is_highlighted(window, sel_string):
  colors_by_scope = window.project_data()

  highlighted = False
  for key, value in colors_by_scope.items():
    if value == sel_string:
      highlighted = True
      break
  return highlighted

def find_used_color(window, sel_string):
  colors_by_scope = window.project_data()
  color = None
  for key, value in colors_by_scope.items():
    if value == sel_string:
      color = key
  return color

def find_usable_color(window, sel_string):
  colors_by_scope = window.project_data()
  color = None
  for key, value in colors_by_scope.items():
    if not value:
      color = key
      break
  return color

def init_color():
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


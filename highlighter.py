import sublime
import sublime_plugin

from collections import OrderedDict

COLORS_BY_SCOPE = OrderedDict()
COLORS_BY_SCOPE['string'] = None
COLORS_BY_SCOPE['entity.name.class'] = None
COLORS_BY_SCOPE['variable.parameter'] = None
COLORS_BY_SCOPE['invalid.deprecated'] = None
COLORS_BY_SCOPE['invalid'] = None
COLORS_BY_SCOPE['support.function'] = None

class HighlighterToggleCommand(sublime_plugin.WindowCommand):
  def run(self):
    active_view = self.window.active_view()
    selected_region = active_view.sel()
    sel_string = active_view.substr(selected_region[0])

    views = self.window.views()
    if is_highlighted(sel_string):
      for view in views:
        # erase
        regions = find_regexes(view, sel_string)
        color = find_used_color(sel_string)
        COLORS_BY_SCOPE[color] = None
        view.erase_regions(sel_string)
    else:
      for view in views:
        # highlight
        regions = find_regexes(view, sel_string)
        color = find_usable_color(sel_string)
        if color:
          COLORS_BY_SCOPE[color] = sel_string
          view.add_regions(sel_string, regions, color, 'circle')

def find_regexes(view, sel_string):
  return view.find_all(sel_string)

def is_highlighted(sel_string):
  highlighted = False
  for key, value in COLORS_BY_SCOPE.items():
    if value == sel_string:
      highlighted = True
      break
  return highlighted

def find_used_color(sel_string):
  color = None
  for key, value in COLORS_BY_SCOPE.items():
    if value == sel_string:
      color = key
  return color

def find_usable_color(sel_string):
  color = ''
  for key, value in COLORS_BY_SCOPE.items():
    if not value:
      color = key
      break
  return color


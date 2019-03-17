import sublime
import sublime_plugin

from collections import OrderedDict

COLORS_BY_SCOPE = OrderedDict()
COLORS_BY_SCOPE['string'] = False
COLORS_BY_SCOPE['entity.name.class'] = False
COLORS_BY_SCOPE['variable.parameter'] = False
COLORS_BY_SCOPE['invalid.deprecated'] = False
COLORS_BY_SCOPE['invalid'] = False
COLORS_BY_SCOPE['support.function'] = False

class SelectAreaCommand(sublime_plugin.WindowCommand):
  def run(self):
    active_view = self.window.active_view()
    selected_region = active_view.sel()
    sel_string = active_view.substr(selected_region[0])

    views = self.window.views()
    for view in views:
      regions = find_regexes(view, sel_string)
      color = find_color()
      view.add_regions(sel_string, regions, color, 'circle')

class EraseHighlightCommand(sublime_plugin.WindowCommand):
  def run(self):
    active_view = self.window.active_view()
    selected_region = active_view.sel()
    sel_string = active_view.substr(selected_region[0])

    views = self.window.views()
    for view in views:
      view.erase_regions(sel_string)

def find_regexes(view, sel_string):
  return view.find_all(sel_string)

def find_color():
  color = ""
  for key, value in COLORS_BY_SCOPE.items():
    if value == False:
      COLORS_BY_SCOPE[key] = True
      color = key
      break
  return color


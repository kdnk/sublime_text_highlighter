import sublime
import sublime_plugin


class SelectAreaCommand(sublime_plugin.WindowCommand):
  def run(self):
    active_view = self.window.active_view()
    selected_region = active_view.sel()
    sel_string = active_view.substr(selected_region[0])

    views = self.window.views()
    for view in views:
      regions = find_regexes(view, sel_string)
      view.add_regions(sel_string, regions, 'keyword', 'circle')

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

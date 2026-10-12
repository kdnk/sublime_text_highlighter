# TextHighlighter

![](https://user-images.githubusercontent.com/15260226/54765330-a61a4900-4c3c-11e9-99b4-8fd7a41c2be0.gif)

Requires Sublime Text 3.1 or later. [Sublime Text 3.1](https://www.sublimetext.com/3) added the `View.style_for_scope` API used to compare highlight colors.

## How to install

- Type `Add Repository` into command palette
- `Install Package`
- Choose `Text Highlighter`

## Keybinding

### with NeoVintageous https://github.com/NeoVintageous/NeoVintageous

```
vnoremap <leader>j :TextHighlighterToggle<CR>
snoremap <leader>j :TextHighlighterToggle<CR>
nnoremap <leader>j :TextHighlighterToggle<CR>
nnoremap <leader>c :TextHighlighterClearAll<CR>
```

### normal keymap

Put settings like below to your keybinding file.

```
{ "keys": ["ctrl+super+j"], "command": "text_highlighter_toggle" }
// use specific color as below
{ "keys": ["ctrl+super+j"], "command": "text_highlighter_toggle", "args": { "color": "markup.changed.git_gutter"} }

{ "keys": ["ctrl+super+h"], "command": "text_highlighter_clear_all" }
```

### Default scope candidates

`[ markup.changed.git_gutter, support.class, markup.deleted.git_gutter, markup.inserted.git_gutter, constant.numeric, constant.character.escape, variable, string, comment, keyword, entity.name.function, entity.name.tag, markup.heading ]`

The active color schemes determine how many distinct highlight colors these scopes provide. Scope assignments are shared across windows. Automatic allocation checks scopes in the listed order. It skips occupied scopes and scopes whose foreground matches an existing highlight in any open view across all windows. TextHighlighter compares each pair of scopes within the same view.

The original nine scopes keep their order. `keyword`, `entity.name.function`, `entity.name.tag`, and `markup.heading` provide more candidates when the color scheme gives them distinct foregrounds.

### Add more highlight colors

Use `extra_scopes` and color scheme rules to add arbitrary highlight colors. Choose foregrounds that differ from the colors of other highlights in each view.

1. Open **Preferences > Browse Packages**.
2. Create `User/TextHighlighter.sublime-settings` with the following settings.

   ```json
   {
     "extra_scopes": [
       "text_highlighter.cyan",
       "text_highlighter.magenta"
     ]
   }
   ```

3. For an active `.sublime-color-scheme`, open the command palette and run **UI: Customize Color Scheme**.
4. Add the following entries to the user override's `rules` array. Keep any existing rules.

   ```json
   {
     "rules": [
       {
         "scope": "text_highlighter.cyan",
         "foreground": "#00BCD4"
       },
       {
         "scope": "text_highlighter.magenta",
         "foreground": "#E040FB"
       }
     ]
   }
   ```

5. Save both files and restart Sublime Text.

If the customization command is unavailable, create a `.sublime-color-scheme` file in `Packages/User` with the active scheme's filename. Sublime merges the user file's rules with the active scheme. See [color scheme customization](https://www.sublimetext.com/docs/color_schemes.html#customization).

Custom scopes follow the default candidates. Their allocation order depends on which candidates provide distinct colors in every open view across all windows. Add more scope names and color scheme rules for more colors. Changes to `extra_scopes` take effect after restarting Sublime Text.

[`add_regions`](https://www.sublimetext.com/docs/api_reference.html#sublime.View.add_regions) uses a scope's foreground color to draw highlights. Set `foreground` to the desired highlight color. Different scope names can display the same color if their scheme rules resolve to the same foreground. Scopes without matching rules can also share the scheme's default foreground. TextHighlighter compares the resolved colors with [`style_for_scope`](https://www.sublimetext.com/docs/api_reference.html#sublime.View.style_for_scope) before allocating a scope.

To select an added scope explicitly, use the existing `color` argument.

```json
{ "keys": ["ctrl+super+j"], "command": "text_highlighter_toggle", "args": { "color": "text_highlighter.cyan" } }
```

Each configured scope supports one simultaneously highlighted string. The number of available distinct colors can be smaller than the number of configured scopes. Toggling a highlighted string frees its scope, regardless of the supplied `color` argument.

When adding a new string, an unknown or occupied explicit scope displays a status message and keeps existing highlights. TextHighlighter also refuses an explicit scope if its foreground matches an existing highlight in any open view across all windows. When no distinct colors remain, clear a highlight or add scopes with distinct foregrounds and restart.

Each allocation reads the current color schemes. A scheme change or a newly opened view does not reassign existing highlights. If existing highlights share a color after a scheme change or in a new view, clear the highlights and apply them again.

`extra_scopes` must be a list of nonempty scope strings. Duplicate names count once and retain their first position. Invalid settings display a status message and use the default candidates.

## Inspired

Inspired by https://github.com/ryu1kn/vscode-text-marker

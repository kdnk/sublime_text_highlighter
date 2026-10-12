# TextHighlighter

![](https://user-images.githubusercontent.com/15260226/54765330-a61a4900-4c3c-11e9-99b4-8fd7a41c2be0.gif)

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

### Available colors by scope

`[ markup.changed.git_gutter, support.class, markup.deleted.git_gutter, markup.inserted.git_gutter, constant.numeric, constant.character.escape, variable, string, comment ] `

### Add more highlight colors

The nine default scopes remain available. Add scopes with `extra_scopes` to highlight more than nine different strings at once.

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

The tenth highlighted string uses `text_highlighter.cyan`. The eleventh uses `text_highlighter.magenta`. Add more scope names and color scheme rules for more colors. Palette changes take effect after restarting Sublime Text.

The active color scheme controls the actual colors. [`add_regions`](https://www.sublimetext.com/docs/api_reference.html#sublime.View.add_regions) uses a scope's foreground color to draw highlights. Set `foreground` to the desired highlight color. Different scope names can display the same color if their scheme rules resolve to the same foreground.

To select an added scope explicitly, use the existing `color` argument.

```json
{ "keys": ["ctrl+super+j"], "command": "text_highlighter_toggle", "args": { "color": "text_highlighter.cyan" } }
```

Each configured scope supports one simultaneously highlighted string. Toggling a highlighted string frees its scope, regardless of the supplied `color` argument. When adding a new string, an unknown or occupied explicit scope leaves existing highlights unchanged and displays a status message. When all scopes are in use, clear a highlight or add scopes and restart.

`extra_scopes` must be a list of nonempty scope strings. Duplicate names count once and retain their first position. Invalid settings display a status message and use the nine default scopes.

## Inspired

Inspired by https://github.com/ryu1kn/vscode-text-marker

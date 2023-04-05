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

## Inspired

Inspired by https://github.com/ryu1kn/vscode-text-marker

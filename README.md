# TextHighlighter

## Keybinding

### with NeoVintageous https://github.com/NeoVintageous/NeoVintageous

```
vnoremap <leader>j :TextHighlighterToggle<CR>
snoremap <leader>j :TextHighlighterToggle<CR>
nnoremap <leader>j :TextHighlighterToggle<CR>
nnoremap <leader>c :TextHighlighterClearAll<CR>
```

### normal keymap

Put settings like blow to your keybinding file.

```
{ "keys": ["ctrl+super+j"], "command": "text_highlighter_toggle" }
{ "keys": ["ctrl+super+h"], "command": "text_highlighter_clear_all" }
```

## Inspired

Inspired by https://github.com/ryu1kn/vscode-text-marker

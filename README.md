# nblib

Tool to manage and organize Jupyter notebooks. Organize notebooks chapters by
markdown headers levels and by files. Together with fzf allow easy search and reuse
snippets between notebooks. Two scripts are included:

- `nblib.py` - python module scanning for files and providing data for fzf.
Scanning shall be done manually by simply calling the script without any arguments.
It will scan all subfolders starting from current and will store results in
`./conf/nblib.json`. To preview the file directly you can use very handy
viewer: `jless`
- `nblib_fzf.sh` - simply bash script preparing data for fzf. Allow easy searching
and preview and then copy to clipboard code or markdown.

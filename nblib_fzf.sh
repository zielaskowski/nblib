#!/bin/bash

copy_code(){
	# the first arg is uuid
	nblib --preview --id="$1" --what=code | xclip -n -selection clipboard
	notify-send "Copied code to clipboard"
}
export -f copy_code

copy_markdown(){
	# the first arg is uuid
	nblib --preview --id="$1" --what=markdown | xclip -n -selection clipboard
	notify-send "Copied markdown to clipboard"
}
export -f copy_markdown

preview(){
	code=$(nblib --preview --id="$1" --what=code)
	markdown=$(nblib --preview --id="$1" --what=markdown)
	printf "\e[1;34m---markdown---\e[0m\n" # bold blue
	echo "$markdown"
	echo
	printf "\e[1;34m---code---\e[0m\n"
	echo "$code"
}
export -f preview


# Get the data file from the main inventory script.
export DATA_FILE
DATA_FILE=$(nblib --view)

# If the data string is empty exit gracefully.
if [ -z "$DATA_FILE" ]; then
    echo "No data available."
    exit 0
fi

data_to_display(){
	printf "$DATA_FILE" |\
	column -t -s$'\t'
}
export -f data_to_display


data_to_display \
| fzf --delimiter='[ ]{2,}' \
      --ansi \
      --with-nth=1,2,3 \
      --preview 'bash -c '\''preview "$1"'\'' _ {3}' \
      --border='horizontal' \
      --border-label="ctrl-c to copy code | ctrl-m to copy markdown" \
      --border-label-pos=-1:bottom \
      --bind 'ctrl-c:execute-silent(bash -c '\''copy_code "$1"'\'' _ {3})' \
      --bind 'ctrl-m:execute-silent(bash -c '\''copy_markdown "$1"'\'' _ {3})'





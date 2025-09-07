#/bin/bash

files_to_be_deleted=(
    demo.pdf
    demo.html
    demo_with_outline.pdf
    outline_errors.json
    package.json
    package-lock.json
)

rm -f "${files_to_be_deleted[@]}"


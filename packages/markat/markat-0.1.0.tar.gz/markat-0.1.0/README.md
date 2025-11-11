## markat

`mkat` is a tiny CLI that prints a nested Markdown subsection using a dotted
path syntax. Each dotted segment refers to the n-th heading for a particular
depth (defaulting to `##`, `###`, `####`, ...):

```
# syntax
2.3.2  -> second `##`, third `###` inside it, second `####` inside that
```

### Features
- Dotted selection syntax (`2.3.2` = 2nd `##`, 3rd `###`, 2nd `####`).
- Colorized output that highlights the breadcrumb path plus the raw section.
- `--plain`/`-p` flag for piping the exact Markdown without headers/colors.
- `--color/--no-color` switches to override auto-detection when needed.
- `--base-level` flag to align the first index with your preferred heading depth.

### Usage

```
uv sync
uv run mkat example.md 2.1.2        # colorful header + section text
uv run mkat example.md 2.1.2 -p     # plain Markdown only
uv run mkat docs/spec.md 1 --color  # force-enable color when piping
```

Ship a Markdown file like `example.md` (included) to experiment with the dotted
paths. Add `--base-level 1` if your top-level headings start with `#` instead of `##`.

### Testing

```
python -m unittest discover
```

The test suite covers path parsing, section selection, and the CLI presentation
helpers.

# difflint

A code review catches most problems, but the small mechanical ones slip
through anyway: a line with trailing whitespace, a merge conflict marker
someone forgot to remove, a line that got way too long. `difflint` checks
the *added* lines of a diff for that kind of thing, so you can run it in a
pre-commit hook or CI step before a human has to notice it by eye.

It only looks at unified diff text - the output of `git diff`, `diff -u`,
or a `.patch` file - and only flags lines on the new side of a hunk. It
does not check whole files, and it does not know anything about a
particular language's syntax.

## Usage

Pipe a diff in from git:

```
git diff | difflint
```

Check a saved patch file directly:

```
difflint changes.patch
```

Check several files, or mix files with `-` to also read stdin:

```
difflint one.patch two.patch
```

Sample output:

```
src/app.py:42: [trailing-whitespace] trailing whitespace
src/app.py:57: [conflict-marker] unresolved merge conflict marker
src/utils.py:12: [line-too-long] line exceeds 100 characters
```

The exit code is `1` if any findings were reported and `0` otherwise, so it
plugs into a CI step or a pre-commit hook without extra glue.

## Rules

| id                    | what it flags                                   |
|-----------------------|--------------------------------------------------|
| `trailing-whitespace` | an added line ending in spaces or tabs           |
| `conflict-marker`     | a `<<<<<<<`, `=======`, or `>>>>>>>` marker left in an added line |
| `line-too-long`       | an added line longer than the limit (default 100, set with `--max-line-length`) |

## Requirements

Python 3.9 or newer. No third-party dependencies.

## Development

Tests use the standard library's `unittest` and live under `tests/`:

```
python -m unittest discover
```

## Status

Early. The rule set is intentionally small right now - see the roadmap for
what's planned next.

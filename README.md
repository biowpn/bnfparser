# BNF Parser

Simple [BNF](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form) grammar parser. Parse BNF grammar into machine-friendly Context-Free Grammar notation. Support some extensions such as regular-expression-like syntax.


## Usage

```
# Lexing
words = bnfparser.lexer.lex(src: str, long: bool)

# Parsing
rules, nt_map = bnfparser.parser.parse(words)
```

The result `rules` is a list of production rules:

```
[rule1, rule2, ...]
```

Each rule is a 2-tuple: a non-terminal identified by a negative integer and a subsitution as a list of symbols:

```
(-1, ['(', -1, ')'])
```

Each symbol in the subsitution can be either a non-terminal or a terminal (a literal string).

The starting non-terminal is always -1.

If `long` is True, then the parser will preserve long terminals instead of breaking them down into single characters (some simple lexing is performed).

`nt_map` is a mapping from terminal id (the negative integer) to terminal name. Note that some extra terminals might be generated if regular syntax was used, and they will be named like "temp-%d".

## Command Line Usage

Run `python -m bnfparser -h` to see usage.

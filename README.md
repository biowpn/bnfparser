# BNF Parser

Simple [BNF](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form) grammar parser. Parse BNF grammar into machine-friendly Context-Free Grammar notation. Support some extensions such as regular-expression-like syntax.


## Usage

```
rules, nt_map = bnfparser.parse(src: str, long: bool)
```

`rules` is a list of transition rules:

```
[rule1, rule2, ...]
```

Each rule is a 2-tuple: a non-terminal represented by an integer, and a list of subsitutionals:

```
(0, ['(', 0, ')'])
```

Each subsitutional can be either a non-terminal (an integer) or a terminal (a single-character string).

If `long` is True, then the parser will preserve long terminals instead of breaking them down into single characters (some simple lexing is performed).

`nt_map` is a mapping from terminal name to terminal id (its integer representation in the parsing output). Note that some extra terminals might be generated if regular syntax was used, therefore **not all terminals have original names**.

## Command Line Usage

Original BNF ([examples/dna.bnf](./examples/dna.bnf)):

```
<DNA> ::= <DNA> <Nucleotide> | <Nucleotide>

<Nucleotide> ::= 'A' | 'G' | 'C' | 'T'
```

Command:

```
python -m bnfparser .\examples\dna.bnf -t
```

Output:

```
<DNA> ::= <DNA> <Nucleotide>
<DNA> ::= <Nucleotide>
<Nucleotide> ::= A
<Nucleotide> ::= G
<Nucleotide> ::= C
<Nucleotide> ::= T
```

Command:

```
python -m bnfparser .\examples\dna.bnf -t -f json
```

Output (equivalent to):

```
[
    ["<DNA>", ["<DNA>", "<Nucleotide>"]],
    ["<DNA>", ["<DNA>"]],
    ["<Nucleotide>", ["A"]],
    ["<Nucleotide>", ["G"]],
    ["<Nucleotide>", ["C"]],
    ["<Nucleotide>", ["T"]]
]
```

For all available options, run with `-h`.

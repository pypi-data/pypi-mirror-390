# `polars-xml`

This is a very simple Polars plugin that allows querying xml in a string column with [XPath](https://en.wikipedia.org/wiki/XPath).

It has just one function, `xpath`, which accepts an expression and a valid xpath statement.

```py
import polars as pl
import polars_xml as px

rows = []
for i in range(1000):
    sample_xml = f"""
    <foo>
        <bar quux="hello from quux {i}">hello from bar {i}</bar>
        <baz xyzzy="hello from xyzzy {i}">hello from baz {i}</baz>
    </foo>
    """
    rows.append(
        {
            "index": i,
            "xml_data": sample_xml,
        }
    )

df = pl.DataFrame(rows).select(
    index=pl.col("index"),
    bar=px.xpath(pl.col("xml_data"), "//foo//bar"),
    baz=px.xpath(pl.col("xml_data"), "//foo//baz"),
    quux=px.xpath(pl.col("xml_data"), "//foo//bar/@quux"),
    xyzzy=px.xpath(pl.col("xml_data"), "//foo//baz/@xyzzy"),
    missing=px.xpath(pl.col("xml_data"), "//foo//wow"),
)

print(df)
```

```
shape: (1_000, 6)
┌───────┬────────────────────────┬────────────────────────┬─────────────────────────┬──────────────────────────┬───────────┐
│ index ┆ bar                    ┆ baz                    ┆ quux                    ┆ xyzzy                    ┆ missing   │
│ ---   ┆ ---                    ┆ ---                    ┆ ---                     ┆ ---                      ┆ ---       │
│ i64   ┆ list[str]              ┆ list[str]              ┆ list[str]               ┆ list[str]                ┆ list[str] │
╞═══════╪════════════════════════╪════════════════════════╪═════════════════════════╪══════════════════════════╪═══════════╡
│ 0     ┆ ["hello from bar 0"]   ┆ ["hello from baz 0"]   ┆ ["hello from quux 0"]   ┆ ["hello from xyzzy 0"]   ┆ []        │
│ 1     ┆ ["hello from bar 1"]   ┆ ["hello from baz 1"]   ┆ ["hello from quux 1"]   ┆ ["hello from xyzzy 1"]   ┆ []        │
│ 2     ┆ ["hello from bar 2"]   ┆ ["hello from baz 2"]   ┆ ["hello from quux 2"]   ┆ ["hello from xyzzy 2"]   ┆ []        │
│ 3     ┆ ["hello from bar 3"]   ┆ ["hello from baz 3"]   ┆ ["hello from quux 3"]   ┆ ["hello from xyzzy 3"]   ┆ []        │
│ 4     ┆ ["hello from bar 4"]   ┆ ["hello from baz 4"]   ┆ ["hello from quux 4"]   ┆ ["hello from xyzzy 4"]   ┆ []        │
│ …     ┆ …                      ┆ …                      ┆ …                       ┆ …                        ┆ …         │
│ 995   ┆ ["hello from bar 995"] ┆ ["hello from baz 995"] ┆ ["hello from quux 995"] ┆ ["hello from xyzzy 995"] ┆ []        │
│ 996   ┆ ["hello from bar 996"] ┆ ["hello from baz 996"] ┆ ["hello from quux 996"] ┆ ["hello from xyzzy 996"] ┆ []        │
│ 997   ┆ ["hello from bar 997"] ┆ ["hello from baz 997"] ┆ ["hello from quux 997"] ┆ ["hello from xyzzy 997"] ┆ []        │
│ 998   ┆ ["hello from bar 998"] ┆ ["hello from baz 998"] ┆ ["hello from quux 998"] ┆ ["hello from xyzzy 998"] ┆ []        │
│ 999   ┆ ["hello from bar 999"] ┆ ["hello from baz 999"] ┆ ["hello from quux 999"] ┆ ["hello from xyzzy 999"] ┆ []        │
└───────┴────────────────────────┴────────────────────────┴─────────────────────────┴──────────────────────────┴───────────┘
```

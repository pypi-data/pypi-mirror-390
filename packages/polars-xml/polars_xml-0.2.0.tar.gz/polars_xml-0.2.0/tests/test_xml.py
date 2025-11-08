import polars as pl
import polars_xml as px
from polars.testing import assert_frame_equal


def _sample_df() -> pl.DataFrame:
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

    return pl.DataFrame(rows)


def test_parse_xml():
    sample = _sample_df()

    result = sample.select(
        index=pl.col("index"),
        bar=px.xpath(pl.col("xml_data"), "//foo//bar").list.first(),
        baz=px.xpath(pl.col("xml_data"), "//foo//baz").list.first(),
        quux=px.xpath(pl.col("xml_data"), "//foo//bar/@quux").list.first(),
        xyzzy=px.xpath(pl.col("xml_data"), "//foo//baz/@xyzzy").list.first(),
        missing=px.xpath(pl.col("xml_data"), "//foo//wow").list.first(),
        foo_children=px.xpath(pl.col("xml_data"), "//foo/*").list.sort(),
    )

    expected = sample.select(
        index=pl.col("index"),
        bar="hello from bar " + pl.col("index").cast(pl.String),
        baz="hello from baz " + pl.col("index").cast(pl.String),
        quux="hello from quux " + pl.col("index").cast(pl.String),
        xyzzy="hello from xyzzy " + pl.col("index").cast(pl.String),
        missing=pl.lit(None).cast(pl.String),
        foo_children=pl.concat_list(
            [
                "hello from bar " + pl.col("index").cast(pl.String),
                "hello from baz " + pl.col("index").cast(pl.String),
            ]
        ),
    )

    assert_frame_equal(expected, result)


if __name__ == "__main__":
    test_parse_xml()

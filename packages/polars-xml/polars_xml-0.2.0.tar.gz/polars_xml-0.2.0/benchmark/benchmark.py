import polars as pl
import polars_xml as px


def create_sample_xml(i: int) -> str:
    res = f'<foo foo_index="{i}" doodad_name="foo">'

    for j in range(20):
        res += f'<bar bar_index="{j}" doodad_name="bar">hello from bar {i}, {j}</bar>'

    for k in range(30):
        res += f'<baz baz_index="{k}" doodad_name="baz">'

        for l in range(5):
            res += f'<quux quux_index="{l}" doodad_name="quux">hello from quux {i}, {k}, {l}</quux>'
        res += "</baz>"
    res += "</foo>"

    return res


def _sample_df() -> pl.DataFrame:
    rows = []
    for i in range(10_000):
        rows.append(
            {
                "index": i,
                "xml_data": create_sample_xml(i),
            }
        )

    return pl.DataFrame(rows)


if __name__ == "__main__":
    df_sample = _sample_df()

    lf_benchmark = (
        df_sample.lazy()
        .with_columns(
            specific_quux=px.xpath(
                pl.col("xml_data"), '//foo/baz[@baz_index="29"]/quux[@quux_index="4"]'
            ).list.first()
        )
        .with_columns(
            all_quux_list=px.xpath(pl.col("xml_data"), "//foo/baz/quux"),
        )
        .with_columns(
            all_bar_no_list=px.xpath(
                pl.col("xml_data"), "//foo/bar | //foo/baz"
            ).list.first()
        )
    )

    res, bench = lf_benchmark.profile(no_optimization=True)

    print(res)
    print(
        bench.with_columns(
            duration=(
                pl.duration(microseconds=pl.col("end"))
                - pl.duration(microseconds=pl.col("start"))
            ),
        )
        .with_columns(average_duration=pl.col("duration") / len(df_sample))
        .with_columns(pl.col(["duration", "average_duration"]).dt.to_string("polars"))
    )

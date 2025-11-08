use polars::datatypes::DataType;
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;

#[derive(Deserialize)]
struct XPathKwargs {
	xpath: String,
}

fn xpath_str_list<'a>(
	input: &'a str,
	xpath: &str,
) -> PolarsResult<Vec<String>> {
	let package = sxd_document::parser::parse(input)
		.map_err(|e| polars_err!(ComputeError: "{}", e))?;
	let document = package.as_document();
	let output = sxd_xpath::evaluate_xpath(&document, xpath)
		.map_err(|e| polars_err!(ComputeError: "{}", e))?;

	match output {
		sxd_xpath::Value::Nodeset(nodeset) => Ok(
			nodeset
				.into_iter()
				.map(|node| node.string_value())
				.collect(),
		),

		other => Ok(vec![format!("{}", other.into_string())]),
	}
}

fn list_dtype(input_fields: &[Field]) -> PolarsResult<Field> {
	let list_of_strings_dtype = DataType::List(Box::new(DataType::String));
	polars_plan::dsl::FieldsMapper::new(input_fields)
		.with_dtype(list_of_strings_dtype)
}

#[polars_expr(output_type_func=list_dtype)]
fn xpath(inputs: &[Series], kwargs: XPathKwargs) -> PolarsResult<Series> {
	let ca = inputs[0].str()?;
	let mut builder =
		ListStringChunkedBuilder::new(ca.name().clone(), ca.len(), 1);
	ca.iter().for_each(|value| {
		if let Some(value) = value {
			let result = xpath_str_list(value, &kwargs.xpath).ok();
			if let Some(result) = result {
				builder.append_values_iter(result.iter().map(|v| v.as_str()));
				return;
			}
		}
		builder.append_null();
	});
	Ok(builder.finish().into_series())
}

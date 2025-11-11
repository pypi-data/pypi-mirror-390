# json_tabulator

A simple query language for extracting tables from JSON-like objects.

Working with tabular data is much easier than working with nested documents. json_tabulator helps to extract tables from JSON-like objects in a simple, declarative manner. All further processing is left to the many powerful tools that exist for working with tables, such as Spark or Pandas.


## Installation

Install from pypi:

```shell
pip install json_tabulator
```

## Quickstart

The `json_tabulator` module provides tools to extract a JSON document into a set of related tables. Let's start with a simple document

```python
data = {
    'id': 'doc-1',
    'table': [
        {'id': 1, 'name': 'row-1'},
        {'id': 2, 'name': 'row-2'}
    ]
}
```

The document consists of a document-level value `id` as well as a nested sub-table `table`. We want to extract it into a single table, with the global value folded into the table.

To do this, we write a query that defines the conversion into a table like this:

```python
from json_tabulator import tabulate

query = tabulate({
    'document_id': 'id',
    'row_id': 'table[*].id',
    'row_name': 'table[*].name'
})

rows = query.get_rows(data)
```

This returns an iterator of rows, where each row is a dict `{<column_name>: <value>}`:

```python
>>> list(rows)
[
    {'document_id': 'doc-1', 'row_id': 1, 'row_name': 'row-1'},
    {'document_id': 'doc-1', 'row_id': 2, 'row_name': 'row-2'}
]
```

### Path Syntax

The syntax for path expressions is very similar to a subset of JSON Path. A path consists of an optional root element `'$'` followed by a path that specifies what is to be extracted. The child operator `.` and subscripts `[1], ['a'], [*]` can be used for arrays or dicts.

#### Dict key

Can be any string. Key values can be quoted with single or double quotes. Within quoted strings, the quote character must be doubled to escape it. For example, `"say \"hello\""` is interpreted as `say "hello"`.

Keys _must_ be quoted if
* they contain any of the characters `* $ . ' " [] ()`, or if
* they start with a digit
* they are used in a subscript, e.g. `$["child"]` is valid, but `$[child]` is not.

#### Subscripts

Subscripts are entered as `[]`. Allowed subscript values are

* Non-negative numbers representing array indices, e.g. `$[123]`
* Quoted dict keys, e.g. `$['a']`
* Wildcards, e.g. `$[*]`

Subscripts can be entered with or without a period, e.g. `$[*]` and `$.[*]` are both valid.

#### Wildcard `*`

An asterisk `*` is interpreted as a wildcard. Iterates over dict values or array items. Note that wildcards _must_ be entered explicitly, there is no implicit iteration over arrays. Use either `$[*]` or `$.*`.

Note that in contrast to JSON path, the wildcard can be used for dicts and arrays regardless of whether subscript is used.

#### Functions

Functions are notated in parentheses. All available functions can only appear at the end of a path, separated by a `.`. Example: `$.*.(path)`.

##### Structural Queries

There are two functions that query document structure:

* `(index)` returns the index that corresponds to the preceding wildcard
* `(path)` returns the full path up to the preceding wildcard

They _must_ be placed directly after a wildcard and must be at the end of the path. For example `*.(index)` is valid, but `a.(index)` and `*.(index).b` are not.

The output of `(path)` is unique for all rows extracted from the document.

##### Inline Arrays

The function `(inline <relative-path>)` allows to return multiple values in a single row as an inline array. The argument `<relative-path>` follows the same rules as other paths with the exception that the initial `$` is forbidden.

For example, the query `$.a[*].(inline b[*].c)` finds all elements that match the path `$.a[*].b[*].c` but aggregates them into lists, one per each match of `$.a[*]`.

### Data Extraction

#### Query Semantics

Values for all attributes in a query are combined into individual rows. Attributes from different parts of the document are combined by "joining" on the lowest common ancestor.

For this reason, all wildcards for all attributes must lie on a common path. Violating this condition would lead to implicit cross joins and the associated data blow-up.

For example, the paths `$.a[*]` and `$.b[*]` cannot be combined because the wildcards are not on the same path. On the other hand, `$.a` and `$.b[*].c` can be combined.

Queries are analysed and compiled independently of the data to be queried.

If you think you need to get a combination of attributes that is not allowed, think again. If you still think so just run multiple queries and do the join afterwards.

#### Returned values

All extracted values are returned as-is with no further conversion. Returned values are not limited to atomic types, dicts and lists are also allowed.

By default, all requested attributes are returned, the value `None` is used if an attribute cannot be found in the data. When the `omit_missing_attributes` flag is set in `tabulate`, each row only contains keys that are found in the data, allowing for downstream error-handling.

## Related Projects

- [jsontable](https://pypi.org/project/jsontable/) has the same purpose but is not maintained.
- [jsonpath-ng](https://github.com/bridgecrewio/jsonpath-ng) and other jsonpath implementation are much more flexible but more cumbersome to extract nested tables.

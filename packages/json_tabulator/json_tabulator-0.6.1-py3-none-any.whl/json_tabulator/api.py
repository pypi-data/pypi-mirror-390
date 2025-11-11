from dataclasses import dataclass
import typing as typ
from .expression import Expression
from .query import QueryPlan
from .parser import parse_expression


@dataclass
class Attribute:
    name: str
    expression: Expression

    @property
    def path(self):
        """Return query path expression."""
        return self.expression.to_string()


@dataclass
class Tabulator:
    """JSON tabulator query.

    Attributes:
        attributes: Output attributes.
        omit_missing_attributes: Control handling of attributes that are not found in the data.
    """
    attributes: list[Attribute]
    _plan: QueryPlan
    omit_missing_attributes: bool

    @property
    def names(self) -> list[str]:
        """Returns the names of all attributes."""
        return [a.name for a in self.attributes]

    def get_rows(self, data: typ.Any) -> typ.Generator[dict[str, typ.Any], None, None]:
        """Run query against Python object.

        Yields:
            dict[str, typ.Any]: Row generator.
        """
        return self._plan.execute(data, omit_missing_attributes=self.omit_missing_attributes)


def tabulate(
        attributes: dict[str, str],
        omit_missing_attributes: bool = False
) -> Tabulator:
    """Create a new query.

    Args:
        attributes: A dict mapping attribute names to path expressions.
        omit_missing_attributes: Controls output for attributes that are not found.
            If False (default), attributes are set to `None`.
            If True, the keys are omitted on row level.

    Returns:
        A `Tabulator` object that represents the query. The query can be run against data
        by calling `Tabulator.get_rows(data)`.

    Raises:
        InvalidExpression: If path expression contains invalid syntax.
        IncompatiblePaths: If requested paths are not compatible due to requesting
            data that requires an implicit cross join.
    """
    if isinstance(attributes, dict):
        attributes = [
            Attribute(name, expression=parse_expression(expr))
            for name, expr in attributes.items()
        ]
    else:
        raise ValueError(f'Query not understood: {attributes}')
    plan = QueryPlan.from_dict({a.name: a.expression for a in attributes})
    return Tabulator(attributes, plan, omit_missing_attributes=omit_missing_attributes)

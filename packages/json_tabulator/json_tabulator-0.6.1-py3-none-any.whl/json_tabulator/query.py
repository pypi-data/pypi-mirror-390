import typing as tp
from dataclasses import dataclass
from collections import defaultdict

from .expression import Expression, STAR, INDEX, PATH, Inline, is_function
from .exceptions import IncompatiblePaths


def nested_get(data, keys) -> tuple[tp.Any, bool]:
    res = data
    for k in keys:
        if isinstance(res, dict):
            if k not in res:
                return None, False
            res = res[k]
        elif isinstance(res, list):
            if not isinstance(k, int) or k >= len(res):
                return None, False
            res = res[k]
    return res, True


@dataclass
class QueryPlan:
    path: Expression
    extracts: dict[Expression, dict[str, tuple]]

    @classmethod
    def from_dict(cls, query: dict[str, Expression]) -> 'QueryPlan':
        steps = defaultdict(dict)
        query_path = Expression()
        for name, expr in query.items():
            table = expr.get_table()

            if not table.coincides_with(query_path):
                raise IncompatiblePaths(f'Illegal query: Paths {table} and {query_path} are not compatible.')

            query_path = max(query_path, table, key=len)
            tail = expr[len(table):]
            if is_function(tail):
                func = tail[-1]
                if isinstance(func, Inline):
                    steps[table][name] = (*tail[:-1], InlineQueryPlan.from_expression(func.expression))
                else:
                    steps[table][name] = func
            else:
                steps[table][name] = tuple(tail)

        return cls(path=query_path, extracts=steps)

    def execute(self, data, omit_missing_attributes: bool):
        def _extract(data, item, path) -> tuple[tp.Any, bool]:
            if isinstance(item, tuple):
                if item and isinstance(item[-1], InlineQueryPlan):
                    d, success = nested_get(data, item[:-1])
                    return item[-1].execute(d), success
                else:
                    return nested_get(data, item)
            elif item == INDEX:
                return path[-1], True
            elif item == PATH:
                return Expression(path).to_string(), True

        def _recurse(data, head, tail, path, extract):
            if head in self.extracts:
                extract = dict(extract)
                for name, item in self.extracts[head].items():
                    value, success = _extract(data, item, path)
                    if success or not omit_missing_attributes:
                        extract[name] = value
            if tail:
                current, *tail = tail
                head = head + (current,)
                if current == STAR and isinstance(data, list):
                    for idx, item in enumerate(data):
                        yield from _recurse(item, head, tail, path + (idx,), extract)
                elif current == STAR and isinstance(data, dict):
                    for idx, item in data.items():
                        yield from _recurse(item, head, tail, path + (idx,), extract)
                elif isinstance(current, str) and isinstance(data, dict):
                    yield from _recurse(data.get(current), head, tail, path + (current,), extract)
                elif isinstance(current, int) and isinstance(data, list) and current < len(data):
                    yield from _recurse(data[current], head, tail, path + (current,), extract)
            else:
                yield extract

        yield from _recurse(data, Expression(), self.path, (), {})


@dataclass
class InlineQueryPlan:
    plan: QueryPlan

    @classmethod
    def from_expression(cls, expr: Expression):
        return cls(plan=QueryPlan.from_dict({'_': expr}))

    def execute(self, data) -> list:
        print(data)
        return [row['_'] for row in self.plan.execute(data, omit_missing_attributes=True) if '_' in row]


from parsy import string, regex, eof, alt, seq, forward_declaration, ParseError
from .expression import Expression, STAR, INDEX, PATH, Inline
from .exceptions import InvalidExpression


dot = string('.').then(eof.should_fail('expression to continue'))
star = string('*').result(STAR)
root = string('$').result([])
forbidden = ''.join(['"', "'", '\\.', '\\$', '\\*', '\\[\\]', '\\(\\)'])
lparen = string('(')
rparen = string(')')
lbracket = string('[')
rbracket = string(']')


def make_quoted_member(q: str):
    def unquote(s: str) -> str: return s.replace('\\' + q, q)
    return string(q) >> regex(f'(\\\\{q}|[^{q}])+').map(unquote) << string(q)


unquoted_member = regex(f'[^{forbidden}0-9][^{forbidden}]*')
quoted_member = (make_quoted_member('"') | make_quoted_member("'"))
number = regex(r'\d+').map(int)
whitespace = regex(r'\s*')
func_index =  lparen >> string('index').result(INDEX) << rparen
func_path = lparen >> string('path').result(PATH) << rparen
relative_expression = forward_declaration()
func_inline = lparen >> string('inline') >> whitespace >> relative_expression.map(lambda x: Inline(Expression(x))) << rparen
function = alt(func_index, func_path, func_inline)

subscript = lbracket >> alt(number, quoted_member, star) << rbracket

relative_initial_segment = alt(
    unquoted_member,
    quoted_member,
    subscript,
    star,
)
initial_segment = alt(root, relative_initial_segment)

inner_segment = alt(
    dot >> unquoted_member,
    dot >> quoted_member,
    dot >> star,
    dot >> function,
    dot.optional() >> subscript
)


def concat_list(*args):
    res = []
    for a in args:
        if isinstance(a, list):
            res += a
        else:
            res.append(a)
    return res


relative_expression.become(seq(relative_initial_segment, inner_segment.many()).combine(concat_list))
expression = seq(initial_segment, inner_segment.many()).combine(concat_list)


def parse_expression(string: str) -> Expression:
    try:
        res = Expression(expression.parse(string))
    except ParseError:
        raise InvalidExpression(string)

    for i, part in enumerate(res):
        if part in (PATH, INDEX):
            if i < len(res) - 1:
                raise InvalidExpression(string)
            if i == 0 or res[i - 1] != STAR:
                raise InvalidExpression(string)
        elif isinstance(part, Inline):
            if i < len(res) - 1:
                raise InvalidExpression(string)

    return res

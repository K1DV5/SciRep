'''
module procedure

does the calculations needed, sets the appropriate variables in the main
module and returns the procedure of the calculations
'''

import ast  # to know which steps are needed
from .document import DICT, color
from .parsing import latexify, eqn, DEFAULT_MAT_SIZE, UNIT_PF, PARENS

# units that are not base units
DERIVED = {
    'N': 'kg*m/s**2',
    'Pa': 'kg/(m*s**2)',
    'J': 'kg*m**2/s**2',
    'W': 'kg*m**2/s**3',
    'Hz': '_/s',
}
DERIVED = {u: ast.parse(DERIVED[u]).body[0].value for u in DERIVED}


def _calculate(expr, steps, mat_size):
    '''carryout the necesary calculations and assignments'''

    result = [
        latexify(expr, mat_size=mat_size),
        latexify(expr, subs=True, mat_size=mat_size),
        latexify(eval(expr, DICT), mat_size)
    ]

    if steps:
        return [result[s] for s in steps]
    # remove repeated steps (retaining order)
    return list(dict.fromkeys(result))


def _assort_input(input_str):
    '''look above'''

    # only split once, because the # char is used for notes below
    input_parts = [part.strip() for part in input_str.strip().split('#', 1)]
    if len(input_parts) == 1:
        additionals = ''
        equation = input_str
    else:
        equation = input_parts[0]
        additionals = input_parts[1]

    if '=' in equation:
        eq_place = equation.rfind('=')
        while True:
            if all([equation[eq_place:].count(p[0]) == equation[eq_place:].count(p[1])
                    for p in PARENS]):
                break
            else:
                eq_place = equation.rfind('=', 0, eq_place)
        var_name = equation[:eq_place].strip()
        expression = equation[eq_place + 1:].strip()
    else:
        print(color('ERROR:', 'red'),
              'This is not an equation.')
        exit()

    unp_vars = [n.id
                for n in ast.walk(ast.parse(var_name).body[0])
                if isinstance(n, ast.Name)]

    steps = []
    mat_size = DEFAULT_MAT_SIZE
    unit = ''
    mode = 'default'
    vert = True
    note = ''

    if additionals:
        for a in [a.strip() for a in additionals.split(',')]:
            if a.isdigit():
                steps = [int(num) - 1 for num in a]
            # only the first # is used to split the line (see above) so others
            elif a.startswith('#'):
                note = a[1:]
            elif a.startswith('m') and a[1:].isdigit():
                if len(a) == 2:
                    mat_size = int(a[1])
                else:
                    mat_size = (int(a[1]), int(a[2]))
            elif a == '$':
                mode = 'inline'
            elif a == '$$':
                mode = 'display'
            elif a == '|':
                vert = True
            elif a == '-':
                vert = False
            else:
                try:
                    compile(a, '', 'eval')
                    unit = a
                except SyntaxError:
                    print('            ', color('WARNING:', 'yellow'),
                          f"Unknown option '{a}' found, ignoring...")

    if note:
        note = f'\\quad\\text{{{note}}}'

    return var_name, unp_vars, expression, unit, steps, mat_size, mode, vert, note


def cal(input_str: str) -> str:
    '''
    evaluate all the calculations, carry out the appropriate assignments,
    and return all the procedures

    '''
    var_name, unp_vars, expr, unit, steps, mat_size, mode, vert, note = _assort_input(
        input_str)
    result = _calculate(expr, steps, mat_size)
    var_lx = latexify(var_name)
    # detect if the user is trying to give a different unit and give warning
    if unit:
        # in their dict forms
        compared = [UnitHandler(True).visit(ast.parse(unit).body[0].value),
                    UnitHandler(False).visit(ast.parse(expr).body[0].value)]
        # when the calculated already has a unit
        compared = [compared, [compared[1], [{}, {}]]]
        # if it is detected, warn the user but accept it anyway
        if not are_equivalent(*compared[1]) and not are_equivalent(*compared[0]):
            print('            ', color('WARNING:', 'yellow'),
                  'The input unit is not equivalent to the calculated one.',
                  color('Overriding...', 'yellow'))
    else:
        unit = unitize(expr)
    if unit and unit != '_':
        unit_lx = f" \, \mathrm{{{latexify(unit, div_symbol='/')}}}"
    else:
        unit_lx = ''
    result[-1] += unit_lx + note

    if mode == 'inline':
        displ = False
    elif mode == 'display':
        displ = True
    else:
        if len(steps) == 1 and steps[0] == 0:
            displ = False
        else:
            displ = True

    procedure = [f'{var_lx} = {result[0]}']
    for step in result[1:]:
        procedure.append('    = ' + step)

    output = eqn(*procedure, norm=False, disp=displ, vert=vert)

    # carry out normal op in main script
    exec(input_str, DICT)
    # for later unit retrieval
    for var in unp_vars:
        exec(f'{var}{UNIT_PF} = "{unit}"', DICT)

    return output


class UnitHandler(ast.NodeVisitor):
    '''
    simplify the given expression as a combination of units
    '''

    def __init__(self, norm=False):
        self.norm = norm

    def visit_Name(self, n):
        if self.norm:
            unit = n
        else:
            if n.id + UNIT_PF in DICT:
                un = DICT[n.id + UNIT_PF]
            else:
                un = '_'
            unit = ast.parse(un).body[0].value
        if isinstance(unit, ast.Name):
            if unit.id in DERIVED:
                unit = DERIVED[unit.id]
            elif hasattr(n, 'upper') and not n.upper:
                return [{}, {unit.id: 1}]
            else:
                return [{unit.id: 1}, {}]
        unit.upper = n.upper if hasattr(n, 'upper') else True
        # store and temporarily disregard the state self.norm
        prev_norm = self.norm
        self.norm = True
        l = self.visit(unit)
        # revert to the previous state
        self.norm = prev_norm
        return l

    def visit_Call(self, n):
        if isinstance(n.func, ast.Attribute):
            func = n.func.attr
        elif isinstance(n.func, ast.Name):
            func = n.func.id
        else:
            func = self.visit(n.func)
        if func == 'sqrt':
            return self.visit(ast.BinOp(left=n.args[0], op=ast.Pow(), right=ast.Num(n=1/2)))
        return [{}, {}]

    def visit_BinOp(self, n):
        if hasattr(n, 'upper') and not n.upper:
            upper = False
        else:
            upper = True
        n.left.upper = upper
        left = self.visit(n.left)
        if isinstance(n.op, ast.Pow):
            if isinstance(n.right, ast.BinOp):
                if isinstance(n.right.left, ast.Num) and isinstance(n.right, ast.Num):
                    if isinstance(n.right.op, ast.Add):
                        p = n.right.left.n + n.right.n
                    elif isinstance(n.right.op, ast.Sub):
                        p = n.right.left.n - n.right.n
                    elif isinstance(n.right.op, ast.Mult):
                        p = n.right.left.n * n.right.n
                    elif isinstance(n.right.op, ast.Div):
                        p = n.right.left.n / n.right.n
                    elif isinstance(n.right.op, ast.Pow):
                        p = n.right.left.n ** n.right.n
            elif isinstance(n.right, ast.UnaryOp):
                if isinstance(n.right.operand, ast.Num):
                    if isinstance(n.right.op, ast.USub):
                        p = - n.right.operand.n
                    elif isinstance(n.right.op, ast.UAdd):
                        p = n.right.operand.n
            elif isinstance(n.right, ast.Num):
                p = n.right.n
            for u in left[0]:
                left[0][u] *= p
            for u in left[1]:
                left[1][u] *= p
            return left
        elif isinstance(n.op, ast.Mult):
            n.right.upper = upper
            right = self.visit(n.right)
            for u in right[0]:
                if u in left[0]:
                    left[0][u] += right[0][u]
                else:
                    left[0][u] = right[0][u]
            for u in right[1]:
                if u in left[1]:
                    left[1][u] += right[1][u]
                else:
                    left[1][u] = right[1][u]
            return left
        elif isinstance(n.op, ast.Div):
            n.right.upper = not upper
            right = self.visit(n.right)
            for u in right[0]:
                if u in left[0]:
                    left[0][u] += right[0][u]
                else:
                    left[0][u] = right[0][u]
            for u in right[1]:
                if u in left[1]:
                    left[1][u] += right[1][u]
                else:
                    left[1][u] = right[1][u]
            return left
        elif isinstance(n.op, ast.Add) or isinstance(n.op, ast.Sub):
            n.right.upper = upper
            left = reduce(left)
            right = reduce(self.visit(n.right))
            if are_equivalent(left, right):
                return left
            print('            ', color('WARNING:', 'yellow'),
                  'The units of the two sides are not equivalent.')
            return [{}, {}]

    def visit_UnaryOp(self, n):
        return self.visit(n.operand)

    def generic_visit(self, n):
        return [{}, {}]


def unitize(s: str) -> str:
    '''
    look for units of the variable names in the expression, cancel-out units
    that can be canceled out and return an expression of units that can be
    converted into latex using latexify
    '''

    def unit_handler(pu, norm):
        return UnitHandler(norm).visit(pu)
    ls = reduce(unit_handler(ast.parse(s).body[0].value, False))

    # the var names that are of units in the main dict that are not _
    in_use = {DICT[u] for u in DICT
              if u.endswith(UNIT_PF) and DICT[u] != '_'}
    # var names in in_use whose values contain one of the DERIVED units
    in_use = [u for u in in_use
              if any([n.id in DERIVED
                      for n in [n for n in ast.walk(ast.parse(u).body[0].value)
                                if isinstance(n, ast.Name)]])]
    # search in reverse order to choose the most recently used unit
    in_use.reverse()
    # if this unit is equivalent to one of them, return that
    for unit in in_use:
        if are_equivalent(unit_handler(ast.parse(unit).body[0].value, True), ls):
            return unit

    upper = "*".join([u if ls[0][u] == 1 else f'{u}**{ls[0][u]}'
                      for u in ls[0]])
    lower = "*".join([u if ls[1][u] == 1 else f'{u}**{ls[1][u]}'
                      for u in ls[1]])

    s_upper = f'({upper})' if ls[0] else "_"
    s_lower = f'/({lower})' if ls[1] else ""
    return s_upper + s_lower


def are_equivalent(unit1: dict, unit2: dict) -> bool:
    '''
    return True if the units are equivalent, False otherwise
    '''

    unit1, unit2 = reduce(unit1), reduce(unit2)
    conditions = [
        # the numerators have the same elements
        set(unit1[0]) == set(unit2[0]) and \
        # each item's value (power) is the same in both
        all([unit1[0][e] == unit2[0][e] for e in unit1[0]]),
        # the denominators have the same elements
        set(unit1[1]) == set(unit2[1]) and \
        # and each item's value (power) is the same in both
        all([unit1[1][e] == unit2[1][e] for e in unit1[1]]),
    ]

    return all(conditions)


def reduce(ls: list) -> list:
    '''
    cancel out units that appear in both the numerator and denominator, those
    that have no name (_) and those with power of 0
    '''
    upper = {**ls[0]}
    lower = {**ls[1]}
    for u in ls[0]:
        if u in ls[1]:
            if upper[u] > lower[u]:
                upper[u] -= lower[u]
                del lower[u]
            elif upper[u] < lower[u]:
                lower[u] -= upper[u]
                del upper[u]
            else:
                del upper[u]
                del lower[u]
    for u in {**upper}:
        if upper[u] == 0 or u == '_':
            del upper[u]
    for u in {**lower}:
        if lower[u] == 0 or u == '_':
            del lower[u]
    return [upper, lower]

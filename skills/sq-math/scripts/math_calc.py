#!/usr/bin/env python3
import argparse
import ast
import math

try:
    import sympy as sp
except Exception:
    sp = None


def fail(msg):
    print(msg)
    raise SystemExit(1)


def require_sympy():
    if sp is None:
        fail("sympy 未安装，无法执行该操作。请先安装: pip install sympy")


def main():
    p = argparse.ArgumentParser(description="sq-math calculator")
    p.add_argument("--expr")
    p.add_argument("--solve")
    p.add_argument("--diff")
    p.add_argument("--integrate")
    p.add_argument("--var", default="x")
    p.add_argument("--a")
    p.add_argument("--b")
    p.add_argument("--det")
    args = p.parse_args()

    if args.expr:
        if sp is not None:
            v = sp.simplify(sp.sympify(args.expr))
            print(v)
            return
        # sympy 不在时，提供基础安全表达式计算
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        allowed.update({"abs": abs, "round": round})
        print(eval(args.expr, {"__builtins__": {}}, allowed))
        return

    if args.solve:
        require_sympy()
        x = sp.symbols(args.var)
        eq = sp.sympify(args.solve)
        ans = sp.solve(sp.Eq(eq, 0), x)
        print(ans)
        return

    if args.diff:
        require_sympy()
        x = sp.symbols(args.var)
        expr = sp.sympify(args.diff)
        print(sp.diff(expr, x))
        return

    if args.integrate:
        require_sympy()
        x = sp.symbols(args.var)
        expr = sp.sympify(args.integrate)
        if args.a is not None and args.b is not None:
            print(sp.integrate(expr, (x, sp.sympify(args.a), sp.sympify(args.b))))
        else:
            print(sp.integrate(expr, x))
        return

    if args.det:
        require_sympy()
        m = ast.literal_eval(args.det)
        print(sp.Matrix(m).det())
        return

    fail("请至少提供一个参数，如 --expr 或 --solve")


if __name__ == "__main__":
    main()

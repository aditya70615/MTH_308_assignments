#!/usr/bin/env python3
"""mth308lib command-line interface

Provides quick access to core numerical methods from the terminal once the
package is installed (``pip install .``).

Examples
--------
Root-finding with bisection::

    mth308 root --method bisection --func "x**2-2" --a 0 --b 2

Numerical integration::

    mth308 integrate --method simpsons --expr "math.sin(x)" --a 0 --b 3.14159 --n 500

ODE solving with RK4::

    mth308 ode --method rk4 --ode "x + y" --x0 0 --y0 1 --h 0.1 --steps 20

Each sub-command has ``-h`` for detailed help, e.g. ``mth308 root -h``.
"""
from __future__ import annotations

import argparse
import math
import sys
import textwrap
from types import SimpleNamespace
from typing import Callable, Sequence, Tuple

# Import library primitives --------------------------------------------------
from mth308 import (
    # Root-finding
    bisection_method,
    regula_falsi,
    modified_regula_falsi,
    newton_raphson,
    secant_method,
    # Linear algebra (place-holders for future expansion)
    # gaussian_elimination, gauss_seidel, jacobi, sor_solver, lu_doolittle,
    # lu_crout, power_method,
    # Integration
    trapezoidal_rule,
    simpsons_one_third,
    # ODEs
    euler_method,
    rk4,
)

# ---------------------------------------------------------------------------
#                           Utility helpers
# ---------------------------------------------------------------------------

def _safe_eval(expr: str, **kwargs):
    """Evaluate *expr* allowing only names present in *kwargs* + ``math``.

    This prevents arbitrary code execution while still supporting typical math
    expressions like ``sin(x)``.
    """
    allowed_names = {"math": math, **kwargs}
    code = compile(expr, "<expr>", "eval")
    for name in code.co_names:
        if name not in allowed_names:
            raise ValueError(f"'{name}' is not an allowed identifier in the expression.")
    return eval(code, allowed_names)


def _parse_f_of_x(expr: str) -> Callable[[float], float]:
    """Return *f(x)* callable from an *expr* string."""
    return lambda x: _safe_eval(expr, x=x)


def _parse_f_of_x_y(expr: str) -> Callable[[float, float], float]:
    """Return *f(x, y)* callable from an *expr* string."""
    return lambda x, y: _safe_eval(expr, x=x, y=y)


# ---------------------------------------------------------------------------
#                         Command implementations
# ---------------------------------------------------------------------------

def _cmd_root(args: argparse.Namespace) -> None:
    f = _parse_f_of_x(args.func)
    meth = args.method
    kwargs = dict(tol=args.tol, max_iter=args.max_iter)
    if meth == "bisection":
        root, it, ok = bisection_method(f, args.a, args.b, **kwargs)
    elif meth == "regula_falsi":
        root, it, ok = regula_falsi(f, args.a, args.b, **kwargs)
    elif meth == "modified_regula_falsi":
        root, it, ok = modified_regula_falsi(f, args.a, args.b, **kwargs)
    elif meth == "newton":
        root, it, ok = newton_raphson(f, args.x0, **kwargs)
    elif meth == "secant":
        root, it, ok = secant_method(f, args.x0, args.x1, **kwargs)
    else:  # pragma: no cover
        raise ValueError("Unsupported root-finding method.")

    print(f"Root: {root}  |  iterations: {it}  |  converged: {ok}")


def _cmd_integrate(args: argparse.Namespace) -> None:
    f = _parse_f_of_x(args.expr)
    if args.method == "trapezoidal":
        res = trapezoidal_rule(f, args.a, args.b, args.n)
    elif args.method == "simpsons":
        res = simpsons_one_third(f, args.a, args.b, args.n)
    else:  # pragma: no cover
        raise ValueError("Unsupported integration method.")
    print(f"Integral ≈ {res}")


def _cmd_ode(args: argparse.Namespace) -> None:
    f = _parse_f_of_x_y(args.ode)
    if args.method == "euler":
        xs, ys = euler_method(f, args.x0, args.y0, args.h, args.steps)
    elif args.method == "rk4":
        xs, ys = rk4(f, args.x0, args.y0, args.h, args.steps)
    else:  # pragma: no cover
        raise ValueError("Unsupported ODE method.")

    for x, y in zip(xs, ys):
        print(f"x = {x:.6g}\ty = {y:.6g}")


# ---------------------------------------------------------------------------
#                                 Main
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mth308",
        description="Command-line interface for numerical methods implemented in mth308lib.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """Examples:\n"
            "  mth308 root --method bisection --func 'x**2-2' --a 0 --b 2\n"
            "  mth308 integrate --method simpsons --expr 'math.sin(x)' --a 0 --b 3.1415 --n 1000\n"
            "  mth308 ode --method rk4 --ode 'x + y' --x0 0 --y0 1 --h 0.1 --steps 10\n"  # noqa: E501
        ),
    )
    sub = p.add_subparsers(dest="command", required=True)

    # ---------------- Root-finding ----------------
    pr = sub.add_parser("root", help="Root-finding algorithms")
    pr.add_argument("--method", required=True,
                    choices=["bisection", "regula_falsi", "modified_regula_falsi", "newton", "secant"],
                    help="Algorithm to use.")
    pr.add_argument("--func", required=True, help="Function in x, e.g. 'x**3 - x - 2'.")
    pr.add_argument("--a", type=float, help="Lower bound (bracketing methods).")
    pr.add_argument("--b", type=float, help="Upper bound (bracketing methods).")
    pr.add_argument("--x0", type=float, help="Initial guess (Newton/Secant).")
    pr.add_argument("--x1", type=float, help="Second guess (Secant).")
    pr.add_argument("--tol", type=float, default=1e-8, help="Tolerance for convergence.")
    pr.add_argument("--max-iter", type=int, default=100, help="Maximum iterations.")
    pr.set_defaults(func=_cmd_root)

    # ---------------- Integration ----------------
    pi = sub.add_parser("integrate", help="Numerical integration")
    pi.add_argument("--method", required=True, choices=["trapezoidal", "simpsons"], help="Rule to use.")
    pi.add_argument("--expr", required=True, help="Integrand expression in x, e.g. 'math.exp(-x**2)'.")
    pi.add_argument("--a", type=float, required=True, help="Lower limit of integration.")
    pi.add_argument("--b", type=float, required=True, help="Upper limit of integration.")
    pi.add_argument("--n", type=int, default=100, help="Number of sub-intervals (even for Simpson).")
    pi.set_defaults(func=_cmd_integrate)

    # ---------------- ODEs ----------------
    po = sub.add_parser("ode", help="First-order ODE solvers")
    po.add_argument("--method", required=True, choices=["euler", "rk4"], help="Solver to use.")
    po.add_argument("--ode", required=True, help="RHS f(x, y), e.g. 'x + y'.")
    po.add_argument("--x0", type=float, required=True, help="Initial x.")
    po.add_argument("--y0", type=float, required=True, help="Initial y.")
    po.add_argument("--h", type=float, default=0.1, help="Step size.")
    po.add_argument("--steps", type=int, default=10, help="Number of steps.")
    po.set_defaults(func=_cmd_ode)

    return p


def main(argv: Sequence[str] | None = None) -> None:  # entry point for ``console_scripts``
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()

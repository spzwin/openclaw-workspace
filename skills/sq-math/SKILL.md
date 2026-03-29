---
name: sq-math
description: 数学运算技能，支持算术、代数方程、函数求值、微积分与矩阵计算。用于用户提出“帮我算一下”“解方程”“求导/积分”“矩阵运算”等数学任务时，优先通过内置脚本稳定计算并返回结果。
---

# sq-math

执行数学计算并输出清晰结果。

## 快速用法

- 算术与表达式：运行 `python3 scripts/math_calc.py --expr "(23*17+9)/4"`
- 方程求解：运行 `python3 scripts/math_calc.py --solve "x**2-5*x+6" --var x`
- 求导：运行 `python3 scripts/math_calc.py --diff "sin(x)*x**2" --var x`
- 定积分：运行 `python3 scripts/math_calc.py --integrate "x**2" --var x --a 0 --b 3`
- 矩阵行列式：运行 `python3 scripts/math_calc.py --det "[[1,2],[3,4]]"`

## 约束

- 优先使用脚本给出可复现结果，避免口算。
- 输入无效时直接返回可执行的修正示例。
- 输出保持简洁：结果 + 关键步骤（如有）。

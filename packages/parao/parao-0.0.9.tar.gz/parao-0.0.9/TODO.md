
# Union or tuple[type] for
- Coder.typ 
- Arg key element
- Shorthand key element

# multi values
- for multi triggered actions
- via merge method on Param, used in Arguments._solve_values

# fix RecusiveActions repetitions
- if recusion encounters an RecursiveAct the is currently planned, consider it done ?!
  - only withing the directly upcoming contiguous block of RecursiveActs using the same parameter

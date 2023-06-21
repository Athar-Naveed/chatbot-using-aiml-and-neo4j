
def callCalculate(name,exp):
    if "calculate" in exp:
        exp = exp[9:]
        return eval(exp)
    else:
        exp = exp[5:]
        return eval(exp)

def soma(a: float, b: float) -> float:
    """Retorna a soma de dois números."""
    return a + b

def subtrai(a: float, b: float) -> float:
    """Retorna a subtração entre dois números."""
    return a - b

def media(valores: list[float]) -> float:
    """Calcula a média de uma lista de números."""
    if not valores:
        return 0
    return sum(valores) / len(valores)

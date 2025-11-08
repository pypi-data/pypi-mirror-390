def imc(peso: float, altura: float) -> float:
    """Calcula o Índice de Massa Corporal (IMC)."""
    if altura <= 0:
        raise ValueError("Altura deve ser maior que zero.")
    return peso / (altura ** 2)

def classificar_imc(imc: float) -> str:
    """Classifica o IMC segundo a OMS."""
    if imc < 18.5:
        return "Abaixo do peso"
    elif imc < 25:
        return "Peso normal"
    elif imc < 30:
        return "Sobrepeso"
    else:
        return "Obesidade"

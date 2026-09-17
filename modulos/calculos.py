def calcular_imc(peso: float, altura: float) -> float:
    """Calcula o Índice de Massa Corporal (IMC)."""
    if altura <= 0:
        return 0.0
    return round(peso / (altura ** 2), 2)


def classificar_imc(imc: float) -> str:
    """Classifica o IMC de acordo com a OMS."""
    if imc < 18.5:
        return "Abaixo do Peso"
    elif 18.5 <= imc < 25.0:
        return "Peso Normal"
    elif 25.0 <= imc < 30.0:
        return "Sobrepeso"
    elif 30.0 <= imc < 35.0:
        return "Obesidade Grau I"
    elif 35.0 <= imc < 40.0:
        return "Obesidade Grau II"
    else:
        return "Obesidade Grau III"


def calcular_peso_ideal(altura: float) -> float:
    """Calcula o peso ideal recomendado baseado no ponto médio de eutrofia (IMC 21.75)."""
    if altura <= 0:
        return 0.0
    return round(21.75 * (altura ** 2), 1)


def somar_totais_diarios(dieta: dict):
    """Soma o valor energético e os macronutrientes do plano diário."""
    total_kcal = 0.0
    total_prot = 0.0
    total_carb = 0.0
    total_gord = 0.0

    for refeicao, alimentos in dieta.items():
        for item in alimentos:
            total_kcal += item.get("energia_kcal", 0.0)
            total_prot += item.get("proteina_g", 0.0)
            total_carb += item.get("carboidrato_g", 0.0)
            total_gord += item.get("lipideos_g", 0.0)

    return (
        round(total_kcal, 1),
        round(total_prot, 1),
        round(total_carb, 1),
        round(total_gord, 1)
    )
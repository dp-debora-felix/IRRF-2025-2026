import streamlit as st

# -----------------------------
# Funções de cálculo
# -----------------------------

# Faixas INSS 2025 (limite superior, alíquota)
INSS_FAIXAS = [
    (1518.00, 0.075),
    (2793.88, 0.09),
    (4190.83, 0.12),
    (8157.41, 0.14),
]

# Faixas IRRF 2025 (limite superior, alíquota, parcela a deduzir)
IRRF_FAIXAS = [
    (2428.80, 0.00, 0.00),
    (2826.65, 0.075, 182.16),
    (3751.05, 0.15, 394.16),
    (4664.68, 0.225, 675.49),
    (float("inf"), 0.275, 908.73),
]

DESCONTO_SIMPLIFICADO = 607.20
DEDUCAO_DEPENDENTE = 189.59

def reducao_2026(salario: float) -> float:
    return 978.62 - (0.133145 * salario)

def calcular_inss_2025(salario: float) -> float:
    total = 0.0
    prev_limite = 0.0
    for limite, aliq in INSS_FAIXAS:
        if salario > prev_limite:
            faixa_valor = min(salario, limite) - prev_limite
            total += faixa_valor * aliq
            prev_limite = limite
    return round(total, 2)

def calcular_irrf_2025(salario: float, dependentes: int):
    inss = calcular_inss_2025(salario)
    ded_dependentes = dependentes * DEDUCAO_DEPENDENTE

    deducoes_legais = inss + ded_dependentes
    deducoes_simplificado = DESCONTO_SIMPLIFICADO

    if deducoes_legais > deducoes_simplificado:
        base = max(0.0, salario - inss - ded_dependentes)
        regime = "Deduções legais"
    else:
        base = max(0.0, salario - DESCONTO_SIMPLIFICADO)
        regime = "Desconto simplificado"

    for limite, aliq, ded in IRRF_FAIXAS:
        if base <= limite:
            imposto = max(0.0, base * aliq - ded)
            return round(imposto, 2), inss, base, regime, aliq, ded

    aliq, ded = IRRF_FAIXAS[-1][1], IRRF_FAIXAS[-1][2]
    imposto = max(0.0, base * aliq - ded)
    return round(imposto, 2), inss, base, regime, aliq, ded

def calcular_irrf_2026(salario: float, irrf_2025: float) -> float:
    if salario <= 5000.00:
        return 0.0
    elif salario <= 7350.00:
        reducao = reducao_2026(salario)
        return round(max(0.0, irrf_2025 - min(irrf_2025, reducao)), 2)
    else:
        return irrf_2025

# -----------------------------
# Interface Streamlit
# -----------------------------

st.set_page_config(page_title="Simulador IRRF", page_icon="💼", layout="centered")
st.image("minha_foto.png")

st.title("💼 Simulador IRRF 2025 × 2026")
st.caption("Desenvolvido por Débora Felix • dp.deborafelix@gmail.com")

st.subheader("📥 Dados de entrada")
salario = st.number_input("Salário bruto mensal (R$)", min_value=0.0, value=6000.0, step=50.0, format="%.2f")
dependentes = st.number_input("Número de dependentes", min_value=0, value=0, step=1)
incluir_13 = st.checkbox("Incluir 13º salário na economia anual", value=True)

# 🔥 Botão que recalcula sempre com os valores atuais
if st.button("🧮 Calcular IRRF"):
    irrf_2025, inss, base, regime, aliq, ded = calcular_irrf_2025(salario, dependentes)
    irrf_2026 = calcular_irrf_2026(salario, irrf_2025)
    economia_mensal = round(irrf_2025 - irrf_2026, 2)
    economia_anual = round(economia_mensal * (13 if incluir_13 else 12), 2)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📅 IRRF 2025")
        st.metric("Valor calculado", f"R$ {irrf_2025:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.caption(f"Regime: {regime}")
    with col2:
        st.subheader("📅 IRRF 2026")
        st.metric("Valor calculado", f"R$ {irrf_2026:,.2f}".replace(",", "X").replace(".", ",").replace("X", ","))

    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("📈 Economia mensal")
        st.metric("Diferença", f"R$ {economia_mensal:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col4:
        st.subheader("📊 Economia anual")
        st.metric("Total", f"R$ {economia_anual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    with st.expander("🔍 Detalhamento do cálculo"):
        st.write(f"- INSS: R$ {inss:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.write(f"- Base de cálculo do IR: R$ {base:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.write(f"- Faixa aplicada: {aliq*100:.1f}%")
        st.write(f"- Parcela a deduzir: R$ {ded:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.caption("Ferramenta informativa. Regras 2026 dependem de aprovação final e regulamentação.")
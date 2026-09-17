import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def criar_pdf_plano(
    nome_paciente,
    sexo,
    idade,
    peso,
    altura,
    imc,
    classificacao,
    peso_ideal,
    restricoes,
    dieta,
    total_kcal,
    total_prot,
    total_carb,
    total_gord,
):
    """Gera o relatório em PDF assinado pela Dra. Andressa Santos usando ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    elements = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.HexColor("#059669"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "HeaderSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15,
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=6,
    )

    elements.append(Paragraph("NutriDAY — Plano Alimentar", title_style))
    elements.append(
        Paragraph(
            "Dra. Andressa Santos — Nutricionista Clínica", subtitle_style
        )
    )

    restricao_txt = (
        str(restricoes).strip()
        if restricoes and str(restricoes).strip()
        else "Nenhuma relatada"
    )
    dados_paciente = (
        f"<b>Paciente:</b> {nome_paciente} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Sexo:</b> {sexo} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Idade:</b> {idade} anos<br/>"
        f"<b>Peso Atual:</b> {float(peso):.1f}kg &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Altura:</b> {float(altura):.2f}m &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>IMC:</b> {float(imc):.2f} ({classificacao}) &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Peso Ideal:</b> {float(peso_ideal):.1f}kg<br/>"
        f"<b>Alergias / Restrições Alimentares:</b> {restricao_txt}"
    )
    elements.append(Paragraph(dados_paciente, styles["Normal"]))
    elements.append(Spacer(1, 15))

    tem_alimentos = False
    if isinstance(dieta, dict):
        for refeicao, alimentos in dieta.items():
            if alimentos:
                tem_alimentos = True
                elements.append(Paragraph(str(refeicao), section_style))

                dados_tabela = [
                    [
                        "Alimento",
                        "Qtd (g)",
                        "Kcal",
                        "Prot (g)",
                        "Carb (g)",
                        "Gord (g)",
                    ]
                ]
                for item in alimentos:
                    dados_tabela.append([
                        str(item.get("nome", "")),
                        f"{float(item.get('quantidade_g', 0)):.0f}g",
                        f"{float(item.get('energia_kcal', 0)):.1f}",
                        f"{float(item.get('proteina_g', 0)):.1f}",
                        f"{float(item.get('carboidrato_g', 0)):.1f}",
                        f"{float(item.get('lipideos_g', 0)):.1f}",
                    ])

                t = Table(dados_tabela, colWidths=[200, 60, 60, 60, 60, 60])
                t.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#f1f5f9"),
                        ),
                        (
                            "TEXTCOLOR",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#0f172a"),
                        ),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.HexColor("#e2e8f0"),
                        ),
                    ])
                )
                elements.append(t)
                elements.append(Spacer(1, 10))

    if not tem_alimentos:
        elements.append(
            Paragraph(
                "Nenhum alimento cadastrado no plano alimentar.",
                styles["Italic"],
            )
        )

    elements.append(Spacer(1, 15))
    resumo_texto = (
        f"<b>Balanço Nutricional Diário:</b> {float(total_kcal):.1f} kcal"
        f" &nbsp;|&nbsp; Proteínas: {float(total_prot):.1f}g &nbsp;|&nbsp;"
        f" Carboidratos: {float(total_carb):.1f}g &nbsp;|&nbsp; Lipídeos:"
        f" {float(total_gord):.1f}g"
    )
    elements.append(Paragraph(resumo_texto, styles["Normal"]))

    elements.append(Spacer(1, 40))
    elements.append(
        Paragraph(
            "________________________________________________",
            ParagraphStyle("Line", parent=styles["Normal"], alignment=1),
        )
    )
    elements.append(
        Paragraph(
            "<b>Dra. Andressa Santos</b><br/>Nutricionista Responsável",
            ParagraphStyle("Sign", parent=styles["Normal"], alignment=1),
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
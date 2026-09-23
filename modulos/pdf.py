import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

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
    modalidade="",
    fator_sel="",
    objetivo="",
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    story = []
    styles = getSampleStyleSheet()

    # Estilos com visual verde-água e lilás
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#2EC4B6"),
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#4A5568"),
        fontName="Helvetica",
        spaceAfter=12,
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#9B51E0"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2D3748"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    # 1. Cabeçalho
    story.append(Paragraph("NutriDAY — Plano Alimentar", title_style))
    story.append(
        Paragraph("Prescrição Nutricional | Dra. Andressa Santos", subtitle_style)
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2EC4B6"), spaceAfter=12))

    # 2. Perfil do Paciente e Exercícios
    dados_paciente = [
        [
            Paragraph(f"<b>Paciente:</b> {nome_paciente}", normal_style),
            Paragraph(f"<b>Idade:</b> {idade} anos", normal_style),
            Paragraph(f"<b>Sexo:</b> {sexo}", normal_style),
        ],
        [
            Paragraph(f"<b>Peso:</b> {peso} kg", normal_style),
            Paragraph(f"<b>Altura:</b> {altura} m", normal_style),
            Paragraph(f"<b>IMC:</b> {imc:.1f} kg/m² ({classificacao})", normal_style),
        ],
        [
            Paragraph(f"<b>Modalidade / Treino:</b> {modalidade or 'Não informada'}", normal_style),
            Paragraph(f"<b>Atividade:</b> {fator_sel or 'N/A'}", normal_style),
            Paragraph(f"<b>Objetivo:</b> {objetivo or 'N/A'}", normal_style),
        ],
    ]

    if restricoes:
        dados_paciente.append([
            Paragraph(f"<b>Observações / Restrições:</b> {restricoes}", normal_style),
            "", "",
        ])

    t_paciente = Table(dados_paciente, colWidths=[200, 160, 160])
    t_paciente.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAF9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#EFE6FA")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EFE6FA")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("SPAN", (0, 3), (2, 3)) if restricoes else ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(t_paciente)
    story.append(Spacer(1, 12))

    # 3. Refeições com Subtotais
    story.append(Paragraph("Prescrição de Refeições", section_style))

    for ref_nome, itens in dieta.items():
        if not itens:
            continue

        story.append(Paragraph(f"<b>{ref_nome}</b>", ParagraphStyle("RefTitle", parent=normal_style, fontSize=10, textColor=colors.HexColor("#2EC4B6"), fontName="Helvetica-Bold", spaceBefore=6)))

        data_ref = [[
            Paragraph("Alimento", table_header_style),
            Paragraph("Qtd (g)", table_header_style),
            Paragraph("Kcal", table_header_style),
            Paragraph("Prot (g)", table_header_style),
            Paragraph("Carb (g)", table_header_style),
            Paragraph("Gord (g)", table_header_style),
        ]]

        ref_kcal, ref_prot, ref_carb, ref_gord = 0.0, 0.0, 0.0, 0.0

        for item in itens:
            ref_kcal += item.get("energia_kcal", 0.0)
            ref_prot += item.get("proteina_g", 0.0)
            ref_carb += item.get("carboidrato_g", 0.0)
            ref_gord += item.get("lipideos_g", 0.0)

            data_ref.append([
                Paragraph(item["nome"], normal_style),
                Paragraph(str(item["quantidade_g"]), normal_style),
                Paragraph(f"{item['energia_kcal']:.1f}", normal_style),
                Paragraph(f"{item['proteina_g']:.1f}", normal_style),
                Paragraph(f"{item['carboidrato_g']:.1f}", normal_style),
                Paragraph(f"{item['lipideos_g']:.1f}", normal_style),
            ])

        # Subtotal da refeição
        data_ref.append([
            Paragraph("<b>Subtotal da Refeição</b>", normal_style),
            Paragraph("-", normal_style),
            Paragraph(f"<b>{ref_kcal:.1f}</b>", normal_style),
            Paragraph(f"<b>{ref_prot:.1f}</b>", normal_style),
            Paragraph(f"<b>{ref_carb:.1f}</b>", normal_style),
            Paragraph(f"<b>{ref_gord:.1f}</b>", normal_style),
        ])

        t_ref = Table(data_ref, colWidths=[200, 60, 65, 65, 65, 65])
        t_ref.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2EC4B6")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EFE6FA")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("PADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(t_ref)
        story.append(Spacer(1, 8))

    # 4. Total Geral do Dia
    story.append(Spacer(1, 6))
    story.append(Paragraph("Resumo Nutricional Diário (Total Geral)", section_style))

    data_total = [
        [
            Paragraph("Energia Total", table_header_style),
            Paragraph("Proteínas", table_header_style),
            Paragraph("Carboidratos", table_header_style),
            Paragraph("Gorduras", table_header_style),
        ],
        [
            Paragraph(f"<b>{total_kcal:.1f} kcal</b>", normal_style),
            Paragraph(f"<b>{total_prot:.1f} g</b>", normal_style),
            Paragraph(f"<b>{total_carb:.1f} g</b>", normal_style),
            Paragraph(f"<b>{total_gord:.1f} g</b>", normal_style),
        ],
    ]

    t_total = Table(data_total, colWidths=[130, 130, 130, 130])
    t_total.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#9B51E0")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAF9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#9B51E0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EFE6FA")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ])
    )
    story.append(t_total)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
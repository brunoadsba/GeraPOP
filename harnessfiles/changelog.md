# Changelog — Harness de UX/UI (GeraPOP)

Formato: `[YYYY-MM-DD] area · issue_id · o que mudou · arquivo(s)`

[2026-08-09] tema · design-system · Paleta do mockup telas-recriadas.html aplicada aos tokens light/dark: accent teal (PRIMARY/ACCENT/SWITCH), hero índigo→roxo (HERO_G1/G2), superfícies em 3 níveis (BG/SURFACE/INPUT_BG) e novos tokens ACCENT_DIM, DANGER, DANGER_DIM, OPTIONAL, OPTIONAL_DIM, PRIMARY_TEXT · gerapop/ui/theme.py

[2026-08-09] tema · design-system · CSS do mockup: sidebar com item de navegação ativo em accent-dim, hero com eyebrow mono + h1 1.7rem, KPIs com números maiores, stepper com estado "current" (anel accent), chips do preview em fonte mono com borda, banner de aviso com borda accent, seções do preview com eyebrow mono (substitui h2 com border-bottom), tabelas com label em negrito 140px + valor muted + linha inferior apenas, cards radius 10px, badge pendente com cores danger · gerapop/ui/theme.css

[2026-08-09] formulario · design-system · Badge OBRIGATÓRIO/OPCIONAL com cores danger/optional dim + fonte mono; hint de exemplo migrado do inline para tooltip nativo (help=) nos campos com label visível (identificação, objetivo, escopo, consulta) via novo helper _flag_help · gerapop/ui/form_sections.py

[2026-08-09] home · design-system · Stepper marca a primeira etapa pendente como "current" (anel accent) · gerapop/ui/home.py

[2026-08-09] preview · design-system · Seções do POP em modo leitura usam eyebrow mono accent no lugar do h2 com border-bottom · gerapop/ui/preview.py

[2026-08-09] config · design-system · Tema nativo do Streamlit alinhado à paleta (primaryColor teal, fundos claros novos) · .streamlit/config.toml

[2026-08-09] preview · design-system · Gap dos chips de metadados do hero aumentado (0.4 → 0.6rem) · gerapop/ui/theme.css

[2026-08-09] tema · design-system · Botões (primários e secundários) com radius 10px, alinhados aos cards branded do dashboard · gerapop/ui/theme.css

[2026-08-09] config · design-system · toolbarMode minimal oculta o chrome do Streamlit Cloud (botão "Deploy") · .streamlit/config.toml

[2026-08-09] sidebar · design-system · Toggle "Tema escuro" movido para o rodapé da sidebar (após a navegação) com separador — nova função render_theme_toggle() · gerapop/ui/theme.py, gerapop/ui/main.py, gerapop/ui/theme.css

[2026-08-09] preview · espacamento · Seções com separador border-top fino + respiro de 32px antes de cada eyebrow; tabelas com margem maior acima/abaixo (Definições/Campos/Revisões) · gerapop/ui/theme.css

[2026-08-09] layout · responsivo · Container de conteúdo com max-width clamp(720px, 88%, 1160px) + padding clamp(1rem, 4vw, 2.5rem), substituindo o centered fixo do Streamlit em telas largas · gerapop/ui/theme.css

[2026-08-09] pdf · aviso · Tags <b> do aviso escapadas como texto literal: _aviso_table usava _paragraph (que escapa tudo) sobre markup do próprio código; corrigido com Paragraph direto + _escape apenas do conteúdo. Blindagem extra: objetivo, escopo, títulos de seção e "Campos obrigatórios" agora escapam dados de usuário · gerapop/services/pdf/builder.py

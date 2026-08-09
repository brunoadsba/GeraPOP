# Design System — GeraPOP (CODEBA)

> Os tokens abaixo são o que dá pra observar nos screenshots atuais, não os valores reais de
> `theme.py`. Antes de tratar como fonte de verdade, confirme os hex reais nos placeholders
> `__VAR__` do tema e substitua esta tabela.

## Paleta (a confirmar contra `theme.py`)
| Token | Uso | Observado nos screenshots |
|---|---|---|
| `__SURFACE__` | fundo geral (dark) | navy quase preto |
| `__HERO_G1__` / `__HERO_G2__` | gradiente do hero | azul-índigo → roxo-azulado |
| `__ACCENT__` | teal institucional CODEBA | não aparece com destaque nas telas atuais — checar se está sendo usado em algum componente ou só existe no token |
| `__BORDER__` | bordas de card | cinza-escuro sutil |
| `__TEXT__` / `__MUTED__` | texto principal / secundário | branco / cinza-claro |

## Tipografia
- Títulos de seção (Objetivo, Escopo, Definições) e o H1 do hero usam peso/tamanho parecidos —
  falta hierarquia visual clara entre nível de página e nível de seção.
- Corpo de texto tem bom contraste sobre o fundo escuro.

## Componentes e problemas observados nas capturas atuais

### Hero (preview do POP)
- Bom contraste branco sobre gradiente.
- Chips de metadados (código, versão, data, área) ficam colados entre si — aumentar `gap`.

### Sidebar
- Logo CODEBA + bandeira do Brasil ocupam espaço vertical considerável sem padding consistente
  com o resto da sidebar (radio de navegação logo abaixo, colado).
- Toggle "Tema escuro" não tem agrupamento visual com a navegação — considerar separador ou
  mover para o rodapé da sidebar.

### Formulário
- Badge (OBRIGATÓRIO/OPCIONAL) + descrição aparecem ACIMA do label do campo, e o label vem
  logo antes do input. Ordem de leitura fica: badge → descrição → label → input — label e
  descrição competem pelo mesmo papel. Considerar usar o `help=` nativo do Streamlit pro texto
  descritivo (ícone de tooltip) e deixar só o label + badge visíveis por padrão.
- Botões "Iniciar simulação" e "Carregar modelo" usam o estilo default do Streamlit, destoando
  visualmente dos cards branded do dashboard.

### Dashboard
- KPIs (número grande + label em caixa alta) são bem escaneáveis — manter esse padrão.
- Stepper com etapas concluídas em verde é claro; validar se a etapa "pulada" no meio da
  sequência (numeração não-linear) é intencional ou é bug de estado.
- O botão "Deploy" no canto superior direito é o chrome padrão do Streamlit Cloud, não é da
  marca — fora do escopo de UI do app em si, mas se incomodar visualmente dá pra ocultar via
  `client.toolbarMode = "minimal"` no `.streamlit/config.toml`.

## Checklist de aceite para qualquer mudança visual
- [ ] Funciona em light e dark
- [ ] Contraste texto/fundo ≥ WCAG AA (4.5:1 para texto normal, 3:1 para texto grande)
- [ ] Espaçamento consistente com o resto da tela (não um valor mágico isolado)
- [ ] Não quebra nenhum dos 72 testes AppTest
- [ ] Legível na largura mínima que o Streamlit usa (não assumir viewport fixo)

# Harness de UX/UI — GeraPOP × DeepSeek

## O que é
Loop automatizado: screenshot da tela rodando → crítica por um modelo com visão → correção pelo
DeepSeek (via OpenCode) → testes → repete. Existe porque o DeepSeek (deepseek-chat /
deepseek-reasoner) não processa imagem — ele nunca vê o screenshot, só o `critique.json` em
texto, escrito por um modelo com visão.

## Setup
1. `uv add requests` (ou `pip install requests --break-system-packages`) no ambiente do projeto.
2. Garanta que `chromium` (ou `google-chrome`) está no PATH. Teste: `chromium --version`.
3. Copie `config.example.json` para `config.json` e preencha:
   - `critic.url` / `critic.api_key` / `critic.model`: endpoint do modelo com visão que você já
     tem configurado (por exemplo o Gemini que você já ligou no OpenCode Zen).
   - `editor.command_template`: o comando exato que invoca o OpenCode com o DeepSeek no seu
     ambiente. Rode `opencode --help` e ajuste — o comando de exemplo é um chute razoável, não
     um comando testado.
   - `pages`: URL de cada tela. **Atenção**: a navegação do GeraPOP é via `st.sidebar.radio`
     (estado de sessão), não necessariamente refletida na URL. Se `?page=form` não mudar a tela
     de fato, você tem duas saídas:
     a. adicionar leitura de `st.query_params` no `main.py` para sincronizar a navegação com a
        URL (mudança pequena, compensa só para habilitar este harness); ou
     b. rodar uma instância Streamlit por tela, clicando manualmente até o estado certo antes de
        cada rodada de screenshot (mais manual, funciona sem tocar em código).
4. Suba o app: `streamlit run gerapop/ui/main.py` (porta 8599, como nos seus screenshots).

## Rodar
```
python harness/ui_loop.py --pages home,form --iterations 3 --score-threshold 8.5
```

## Segurança
- O script dá `git commit` de snapshot antes de cada edição do DeepSeek. Se os 72 testes
  quebrarem depois, ele reverte sozinho (`git reset --hard HEAD~1`).
- Use `--no-git-safety` só se você mesmo for revisar cada iteração manualmente.
- O script nunca dá push nem toca em `fluxo-sev/` — isso está fixado no `AGENTS.md`, mantenha
  assim se editar o prompt.

## Saída
- `harness/shots/`: screenshots de cada iteração, por página.
- `harness/critique_itN.json`: crítica bruta de cada rodada.
- `harness/changelog.md`: log acumulado do que foi mudado, por severidade.

## Limitações conhecidas
- `--virtual-time-budget` no Chromium ajuda, mas não garante que o Streamlit (que renderiza via
  websocket) terminou de desenhar antes do screenshot. Se as imagens saírem "picadas"
  (spinner, skeleton), aumente o valor ou migre para Playwright com `wait_for_selector` — dá mais
  controle, mas adiciona uma dependência que hoje o projeto não tem (o `obsoleto/ambiente-fronend.md`
  menciona QA visual manual via chromium headless, sem Playwright integrado).
- O crítico "alucina" às vezes, como qualquer LLM — trate `critique.json` como sugestão, não
  verdade absoluta. O `AGENTS.md` já instrui o DeepSeek a só mexer em P0/P1 por rodada,
  justamente para limitar o dano de uma crítica ruim.
- Este harness assume DeepSeek sem visão. Se você estiver usando uma variante com visão
  (deepseek-vl2 ou equivalente), dá pra simplificar o fluxo e cortar o papel do "crítico"
  separado — mas eu não confirmaria isso sem checar a doc atual do modelo que você tem
  configurado no OpenCode.

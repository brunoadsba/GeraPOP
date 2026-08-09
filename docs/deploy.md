# Deploy do GeraPOP

Duas formas de publicar o GeraPOP para o setor usar:

| Opção | Persistência do histórico/rascunho | Esforço |
|-------|-----------------------------------|---------|
| **A. Streamlit Community Cloud** | **Efêmera** (perde dados a cada restart/redeploy) | Baixo — sem servidor |
| **B. Docker com volume** | **Persistente** (`./data:/app/data` no host) | Médio — precisa de um servidor |

> Recomendação: o Community Cloud é ótimo para pilotar com a equipe por um tempo.
> Quando o histórico de POPs gerados passar a ser parte do trabalho diário, migrar
> para Docker com volume (ou adicionar um armazenamento externo).

---

## Opção A — Streamlit Community Cloud

Pré-requisitos:

- Repositório deste projeto no GitHub (público ou privado).
- Conta no [share.streamlit.io](https://share.streamlit.io) (entra com o GitHub).

Passo a passo:

1. **Publique o código no GitHub** e faça push da branch desejada.
2. Acesse <https://share.streamlit.io> e faça login com o GitHub.
3. Clique em **New app**.
4. Em **Deploy a public app from GitHub**:
   - **Repository**: selecione `seu-usuario/gerapop`.
   - **Branch**: `main` (ou a branch de produção).
   - **Main file path**: `app.py`.
5. Clique em **Advanced settings**:
   - **Python version**: `3.11`.
   - Não é necessário configurar secrets (o app não usa).
6. Clique em **Deploy**.
7. Aguarde o build (instala `requirements.txt` e roda `pip install -e .`). O app
   estará disponível em `https://<app>.streamlit.app`.

Atualizações: a cada push para a branch configurada o Cloud re-deploya
automaticamente.

### Aviso: persistência é efêmera no Cloud

O filesystem do Community Cloud é **descartável**. Tudo o que o app grava em
disco — o histórico em `data/pops/`, o rascunho (`data/draft.json`) e os
backups em `data/backups/` — **é perdido** quando o app:

- entra em *idle timeout* e é reiniciado,
- é atualizado por um novo push (redeploy),
- é pausado/reiniciado manualmente.

Na prática, no Cloud:

- O **rascunho** funciona apenas dentro da mesma sessão ativa.
- O **histórico de POPs** não sobrevive a reinícios — use o botão
  **"Baixar backup (.zip)"** (no histórico) ou baixe os `.docx`/`.json` para
  guardar fora do app.
- O app lê `GERAPOP_DATA_DIR` (default `data/`) se quiser apontar o storage
  para outro diretório efêmero — não resolve a efemeridade.

Se o setor precisar reter o histórico de forma confiável, use a Opção B.

---

## Opção B — Docker com volume (persistência real)

Pré-requisitos: um servidor/máquina com Docker e Docker Compose.

```bash
make docker-run          # ou: docker compose up --build
```

O `docker-compose.yml` monta `./data:/app/data` como volume, então **histórico,
rascunho e backups ficam gravados no host** e sobrevivem a reinícios e
re-deploys. O serviço roda com `restart: unless-stopped` (sobe sozinho após
reinício da máquina).

O app fica em `http://<servidor>:8501`.

Notas:

- Para mudar o diretório de dados: `GERAPOP_DATA_DIR` no serviço, apontando
  para um caminho dentro do volume.
- Para acesso externo seguro, coloque um proxy reverso (ex.: Nginx + TLS) na
  frente da porta 8501.

---

## Segurança (ambas as opções)

- O GeraPOP **não tem login**. Qualquer pessoa com a URL pode criar, editar e
  baixar POPs.
- No Community Cloud, a URL do app é pública. Para uso restrito ao setor,
  prefira a Opção B numa rede interna, ou adicione autenticação numa versão
  futura.
- O histórico fica em texto claro no disco do servidor — sem dados sensíveis
  além dos próprios POPs.

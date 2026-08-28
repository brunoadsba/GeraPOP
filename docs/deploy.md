# Deploy do GeraPOP

Duas formas de publicar o GeraPOP:

| Opção | Persistência | Esforço |
|-------|-------------|---------|
| **A. Fly.io** (recomendado) | **Persistente** (volume montado em `/data`) | Baixo — CLI `fly deploy` |
| **B. Docker local** | **Persistente** (`./data:/app/data` no host) | Médio — precisa de um servidor |

---

## Opção A — Fly.io (recomendado)

Pré-requisitos:

- Conta no [fly.io](https://fly.io) (plano gratuito inclui 3 VMs shared-cpu-1x).
- CLI `flyctl` instalado (`curl -L https://fly.io/install.sh | sh`).
- Repositório atualizado no GitHub.

### Primeiro deploy

```bash
# 1. Autenticar
fly auth login

# 2. Criar o app (nome definido no fly.toml)
fly apps create gerapop

# 3. Criar volume persistente (1 GB na região GRU — São Paulo)
fly volumes create gerapop_data --region gru --size 1

# 4. Fazer o deploy (build remoto)
fly deploy

# 5. (Opcional) Alimentar a biblioteca com POPs iniciais
fly ssh console -C "python scripts/seed_pops.py"
```

O app ficará disponível em `https://gerapop.fly.dev`.

### Configuração (`fly.toml`)

O arquivo `fly.toml` na raiz define:

- **Região:** `gru` (São Paulo — menor latência para o Brasil)
- **VM:** `shared-cpu-1x` com 512 MB RAM
- **Volume:** `gerapop_data` montado em `/data` (histórico + rascunho + biblioteca)
- **Auto-stop:** máquina suspende quando ociosa (economia de créditos)
- **HTTPS:** forçado automaticamente pelo Fly.io

### Variáveis de ambiente

Definidas em `[env]` no `fly.toml`:

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `PORT` | `8000` | Porta interna do uvicorn |
| `GERAPOP_DATA_DIR` | `/data` | Diretório de dados (dentro do volume) |
| `GERAPOP_LIBRARY_DIR` | `/data/biblioteca` | Biblioteca oficial (dentro do volume) |

### Atualizações

```bash
git push origin main
fly deploy
```

### Fontes Calibri (opcional)

Por padrão, os PDFs usam Helvetica no container Linux. Para usar Calibri (padrão CODEBA):

1. Copiar `calibri.ttf`, `calibrib.ttf`, `calibrii.ttf`, `calibriz.ttf` para o diretório do projeto
2. Adicionar ao Dockerfile:
   ```dockerfile
   COPY fonts/ /usr/share/fonts/truetype/calibri/
   ```
3. Redesploiar com `fly deploy`

---

## Opção B — Docker local com volume

Pré-requisitos: servidor/máquina com Docker e Docker Compose.

```bash
make docker-run          # ou: docker compose up --build
```

O `docker-compose.yml` monta `./data:/app/data` como volume. Histórico, rascunho e backups ficam gravados no host. Serviço roda com `restart: unless-stopped`.

O app fica em `http://<servidor>:8000`.

Notas:

- Para acesso externo seguro, coloque um proxy reverso (Nginx + TLS) na frente.
- As variáveis `GERAPOP_DATA_DIR` e `GERAPOP_LIBRARY_DIR` podem ser definidas no `docker-compose.yml`.

---

## Segurança (ambas as opções)

- O GeraPOP **não tem login**. Qualquer pessoa com a URL pode criar, editar e baixar POPs.
- No Fly.io, a URL é pública (`https://gerapop.fly.dev`). Para uso restrito, adicione autenticação numa versão futura.
- O histórico fica em texto claro no disco — sem dados sensíveis além dos próprios POPs.

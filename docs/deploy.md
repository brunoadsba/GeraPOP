# Deploy do GeraPOP — Nuvem Free (sem cartão)

> Fly.io (`fly.toml` GRU) está **bloqueado sem cartão** (`fly apps create` exige billing). Este guia foca em alternativas **100% free sem cartão**.

| Opção | Custo sem cartão | Persistência | Esforço | URL |
|-------|------------------|--------------|---------|-----|
| **A. Koyeb** (recomendado) | ✅ Free Hobby sem cartão | Efêmera* | Baixo — GitHub auto-deploy | `https://<app>.koyeb.app` |
| **B. HuggingFace Spaces (Docker)** | ✅ Free sem cartão | Efêmera* | Baixo — push para HF | `https://huggingface.co/spaces/<user>/gerapop` |
| **C. Cloudflare Tunnel** | ✅ Free sem cartão | Persistente (host local) | Baixo — já validado | `https://wedding-inherited-strong-fixes.trycloudflare.com` |
| **D. Docker local** | ✅ | Persistente (`./data:/app/data`) | Médio | `http://<servidor>:8000` |

\* Plataformas free sem volume perdem `data/` em redeploy. Use `GET /api/backup` ou `python -m gerapop.backup` regularmente. Biblioteca oficial pode ser versionada via `data/pops/` → commit manual se desejado.

---

## Opção A — Koyeb (substituto direto do Fly, sem cartão)

Suporta `Dockerfile` nativo, região `gru` disponível, detecta `PORT` do `Dockerfile`.

```bash
# 1. Criar conta em koyeb.com (GitHub login, sem cartão no Hobby)
# 2. No painel: Create App → GitHub → brunoadsba/GeraPOP → branch main
# 3. Builder: Dockerfile (auto)
# 4. Variables:
#    PORT=8000
#    GERAPOP_DATA_DIR=/data
#    GERAPOP_LIBRARY_DIR=/data/biblioteca
# 5. Deploy
```

Exposta em `https://<nome>.koyeb.app`. Auto-deploy a cada `git push origin main`.

Notas:
- Sem volume no Hobby: dados efêmeros. Para piloto, baixar backup zip após cada sessão.
- Se liberar volume pago futuramente, montar `/data` igual ao `fly.toml`.

---

## Opção B — HuggingFace Spaces (Docker SDK) — garantido sem cartão

Ideal para demo pública. Espaços Docker são gratuitos sem cartão (públicos).

1. Criar Space em `huggingface.co/new-space` → SDK `Docker` → Blank
2. Adicionar remote:
```bash
git remote add hf https://huggingface.co/spaces/<user>/gerapop
git push hf main
```
3. HF usa `PORT=7860`. O `Dockerfile` já respeita `${PORT:-8000}`, então funciona sem alteração.
4. Space fica em `https://<user>-gerapop.hf.space`

Exige `README.md` com `sdk: docker` no Space (não no repo principal). Dados também efêmeros.

---

## Opção C — Cloudflare Tunnel (`cloudflared`) — produção imediata já validada

Já testado: `wedding-inherited-strong-fixes.trycloudflare.com` (1s estável). Zero cartão, zero hosting — apenas expõe seu `docker compose` local.

```bash
# Docker já rodando
make docker-run  # gerapop-gerapop:8000 healthy

# Túnel efêmero (sem conta)
cloudflared tunnel --url http://localhost:8000
# saída: https://<hash>.trycloudflare.com

# Túnel com conta free (URL estável, opcional)
cloudflared tunnel login
cloudflared tunnel create gerapop
cloudflared tunnel route dns gerapop gerapop.seudominio.com
cloudflared tunnel run gerapop --url http://localhost:8000
```

Alternativa `ngrok` free (`b83e-...ngrok-free.app` 0.5s) funciona mas URL muda a cada restart; custom `gerapop-codeba` só no plano pago (`ERR_NGROK_313`).

Atalho já criado: `~/ligar-gerapop.sh` + `~/.local/share/applications/gerapop.desktop` sobe `docker compose` + túnel.

Recomendado para piloto interno CODEBA sem depender de terceiros.

---

## Opção D — Docker local com volume (persistente)

```bash
make docker-run  # ou: docker compose up --build
```

`docker-compose.yml` monta `./data:/app/data` + `./POP - Procedimento Operacional Padrão:/app/POP - Procedimento Operacional Padrão` com `restart: unless-stopped`. Histórico e rascunho persistem no host. Para acesso externo, combine com Opção C.

Variáveis podem ser definidas no `docker-compose.yml`:
```yaml
environment:
  - PORT=8000
  - GERAPOP_DATA_DIR=/app/data
```

---

## Fly.io — bloqueado (referência)

`fly.toml` (app `gerapop`, `primary_region = gru`, `shared-cpu-1x/512MB`, `gerapop_data:/data`) permanece no repo para migração futura, mas `fly deploy`/`fly apps create` exigem cartão. Não usar até liberar billing.

```bash
fly auth login
fly apps create gerapop      # bloqueado: exige cartão
fly volumes create gerapop_data --region gru --size 1
fly deploy
fly ssh console -C "python scripts/seed_pops.py"
```

---

## Segurança (todas as opções)

- GeraPOP **não tem login**. Qualquer pessoa com a URL pode criar/editar/baixar POPs.
- URLs públicas free (Koyeb/HF/Tunnel) são públicas — para uso restrito, adicione auth em `backend/main.py` numa v2.
- Histórico em texto claro no disco — sem dados sensíveis além dos POPs.

---

## Checklist rápido free-cloud

- [ ] Escolha A/B/C. Para piloto CODEBA hoje: **C (cloudflared)** é instantâneo e já validado.
- [ ] `docker build` local passa (`71 pytest + tsc + vite 38.67kB`)
- [ ] Após deploy, `GET /api/health` responde 200
- [ ] Testar `POST /api/generate` + download `.docx`/`.pdf` + backup zip
- [ ] Documentar URL pública no `memory.md` (local, ignorado)

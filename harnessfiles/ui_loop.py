#!/usr/bin/env python3
"""
Harness de melhoria de UX/UI para o GeraPOP, orientado a DeepSeek (via OpenCode CLI).

Loop: screenshot -> critica (modelo com visao) -> edicao (DeepSeek/OpenCode) -> testes -> repete.

DeepSeek (deepseek-chat / deepseek-reasoner) nao processa imagem. Por isso o harness separa
dois papeis:
  - CRITIC: modelo com visao (ex: Gemini, ja configurado no seu OpenCode Zen) que olha o
    screenshot e escreve um critique.json.
  - EDITOR: DeepSeek, que so le texto (critique.json + design_system.md) e edita codigo.

Uso:
  python harness/ui_loop.py --pages home,form --iterations 3 --score-threshold 8.5

Requer: chromium (ou google-chrome) no PATH, app Streamlit ja rodando, git inicializado
(para o safety-net de commit/revert), uv + pytest + ruff configurados no projeto.
"""
import argparse
import base64
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests

HARNESS_DIR = Path(__file__).parent
SHOTS_DIR = HARNESS_DIR / "shots"
CHANGELOG = HARNESS_DIR / "changelog.md"


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def take_screenshot(url: str, out_path: Path, browser_bin: str, width=1440, height=1000) -> Path:
    """Screenshot headless via Chromium. Streamlit e uma SPA (websocket) - usa
    virtual-time-budget para dar tempo do app renderizar antes da captura. Nao e garantia
    total: se sair spinner/skeleton na imagem, aumente o valor ou migre para Playwright com
    wait_for_selector (ver harness/README.md)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        browser_bin,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={width},{height}",
        "--virtual-time-budget=4000",
        f"--screenshot={out_path}",
        url,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    if not out_path.exists():
        raise RuntimeError(f"Screenshot nao foi gerado: {out_path}")
    return out_path


def run_tests() -> bool:
    result = subprocess.run(["uv", "run", "pytest", "-q"], capture_output=True, text=True)
    print(result.stdout[-2000:])
    if result.returncode != 0:
        print(result.stderr[-2000:], file=sys.stderr)
    return result.returncode == 0


def run_lint() -> None:
    subprocess.run(["ruff", "check", "--fix", "."], check=False)


def call_critic(cfg: dict, screenshot_path: Path, design_system: str, page_name: str) -> dict:
    """Chama o modelo com visao configurado (endpoint compativel com o formato de chat
    completions da OpenAI, content multimodal). Ajuste conforme seu provedor real."""
    with open(screenshot_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    prompt_template = (HARNESS_DIR / "critic_prompt.md").read_text(encoding="utf-8")
    prompt = prompt_template.replace("{{PAGE_NAME}}", page_name).replace(
        "{{DESIGN_SYSTEM}}", design_system
    )

    payload = {
        "model": cfg["critic"]["model"],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                ],
            }
        ],
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(
        cfg["critic"]["url"],
        headers={"Authorization": f"Bearer {cfg['critic']['api_key']}"},
        json=payload,
        timeout=90,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def call_editor(cfg: dict, critique_path: Path, design_system_path: Path) -> None:
    """Invoca o OpenCode CLI com o DeepSeek configurado. Ajuste o template de comando em
    config.json -> editor.command_template conforme a versao instalada do OpenCode
    (`opencode --help` no seu ambiente) - o default aqui e um chute razoavel, nao testado."""
    template = cfg["editor"]["command_template"]
    cmd = template.format(
        critique=str(critique_path),
        design_system=str(design_system_path),
        agents=str(HARNESS_DIR.parent / "AGENTS.md"),
    )
    print(f"[editor] {cmd}")
    subprocess.run(cmd, shell=True, check=False)


def git_snapshot(msg: str) -> None:
    subprocess.run(["git", "add", "-A"], check=False)
    subprocess.run(["git", "commit", "-m", msg], check=False)


def git_revert_last() -> None:
    subprocess.run(["git", "reset", "--hard", "HEAD~1"], check=False)


def append_changelog(entries: list) -> None:
    ts = datetime.now().strftime("%Y-%m-%d")
    lines = []
    for e in entries:
        lines.append(
            f"[{ts}] {e.get('area', '?')} \u00b7 {e.get('id', '?')} \u00b7 "
            f"{e.get('description', '')} \u00b7 sev={e.get('severity', '?')}"
        )
    with open(CHANGELOG, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HARNESS_DIR / "config.json"))
    ap.add_argument("--pages", default="home", help="ex: home,form,preview")
    ap.add_argument("--iterations", type=int, default=3)
    ap.add_argument("--score-threshold", type=float, default=8.5)
    ap.add_argument("--no-git-safety", action="store_true")
    args = ap.parse_args()

    cfg = load_config(args.config)
    design_system = Path(cfg["design_system_path"]).read_text(encoding="utf-8")
    pages = {p: cfg["pages"][p] for p in args.pages.split(",")}

    for it in range(1, args.iterations + 1):
        print(f"\n=== Iteracao {it}/{args.iterations} ===")
        all_critiques = []
        for page_name, url in pages.items():
            shot = SHOTS_DIR / f"{page_name}_it{it}.png"
            take_screenshot(url, shot, cfg.get("browser_bin", "chromium"))
            critique = call_critic(cfg, shot, design_system, page_name)
            critique["page"] = page_name
            all_critiques.append(critique)
            print(f"[{page_name}] score={critique.get('score')} issues={len(critique.get('issues', []))}")

        critique_path = HARNESS_DIR / f"critique_it{it}.json"
        critique_path.write_text(
            json.dumps(all_critiques, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        min_score = min(c.get("score", 0) for c in all_critiques)
        if min_score >= args.score_threshold:
            print(f"Score minimo {min_score} >= threshold {args.score_threshold}. Encerrando.")
            break

        if not args.no_git_safety:
            git_snapshot(f"harness: snapshot antes da iteracao {it}")

        call_editor(cfg, critique_path, Path(cfg["design_system_path"]))

        if not run_tests():
            print("Testes quebraram apos a edicao.")
            if not args.no_git_safety:
                print("Revertendo para o snapshot anterior.")
                git_revert_last()
            else:
                print("Sem git safety - revise manualmente antes de continuar.")
            continue

        run_lint()
        all_issues = [i for c in all_critiques for i in c.get("issues", [])]
        append_changelog(all_issues)

    print("\nHarness finalizado. Confira harness/changelog.md e rode a UI manualmente antes de commitar de vez.")


if __name__ == "__main__":
    main()

import { useEffect, useMemo, useReducer, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  checkCode,
  deletePop,
  downloadDocx,
  generatePop,
  getPop,
  listPops,
  previewDocx,
  previewPdf,
  triggerDownload,
} from '../api/client';
import { ConsultaSection } from '../components/Form/ConsultaSection';
import { DefinicoesSection } from '../components/Form/DefinicoesSection';
import { IdentificacaoSection } from '../components/Form/IdentificacaoSection';
import { ObjetivoEscopoSection } from '../components/Form/ObjetivoEscopoSection';
import { ProcedimentoSection } from '../components/Form/ProcedimentoSection';
import { RegrasSection } from '../components/Form/RegrasSection';
import { History } from '../components/History/History';
import { Accordion } from '../components/ui/Accordion';
import { Button } from '../components/ui/Button';
import {
  IconCheckCircle,
  IconDownload,
  IconEye,
  IconFileText,
  IconSave,
  IconTrash,
  IconZap,
} from '../components/ui/Icons';
import { Modal } from '../components/ui/Modal';
import { showToast } from '../components/ui/Toast';
import { useDraft } from '../hooks/useDraft';
import { reducer } from '../hooks/usePopForm';
import type { DraftPayload, PopData, PopListItem } from '../types/pop';
import { emptyPop } from '../types/pop';

interface NavState {
  carregar?: PopData;
  novo_pop?: { nome: string; objetivo: string };
  editar_id?: string;
}

const validateLocal = (pop: ReturnType<typeof emptyPop>): string[] => {
  const errors: string[] = [];
  if (!pop.nome_pop) errors.push('Nome do POP é obrigatório.');
  if (!pop.codigo) errors.push('Código é obrigatório.');
  if (!pop.area) errors.push('Área é obrigatória.');
  if (!pop.objetivo) errors.push('Objetivo é obrigatório.');
  return errors;
};

function calcProgress(pop: PopData): number {
  const fields = [pop.nome_pop, pop.codigo, pop.area, pop.objetivo];
  const filled = fields.filter((f) => f && f.trim().length > 0).length;
  return Math.round((filled / fields.length) * 100);
}

export function FormPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const navState = location.state as NavState | null;
  const [state, dispatch] = useReducer(reducer, undefined, emptyPop);
  const [erros, setErros] = useState<string[]>([]);
  const [erroDuplicado, setErroDuplicado] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [gerando, setGerando] = useState(false);
  const [gerado, setGerado] = useState<{ pop_id: string; filename: string } | null>(null);
  const [loadedFromId, setLoadedFromId] = useState<string | null>(null);
  const [confirmandoExclusao, setConfirmandoExclusao] = useState<PopListItem | null>(null);
  const aplicadoDraft = useRef(false);

  const logo = '/logo-codeba-topo.png';

  const { isSaving, lastSavedTime, saveNow, discard } = useDraft({
    state,
    loadedFromId,
    enabled: !carregando && !gerado,
  });

  const progress = useMemo(() => calcProgress(state), [state]);

  const navExplicita =
    Boolean(navState?.carregar) || Boolean(navState?.novo_pop) || Boolean(navState?.editar_id);

  useEffect(() => {
    if (navExplicita) return;
    const onDraftLoaded = (event: Event) => {
      if (aplicadoDraft.current) return;
      const payload = (event as CustomEvent<DraftPayload>).detail;
      if (!payload?.form) return;
      aplicadoDraft.current = true;
      dispatch({ type: 'LOAD_POP', pop: { ...emptyPop(), ...payload.form } });
      setLoadedFromId(payload.loaded_from_id ?? null);
    };
    document.addEventListener('gerapop:draft:loaded', onDraftLoaded);
    return () => document.removeEventListener('gerapop:draft:loaded', onDraftLoaded);
  }, [navExplicita]);

  useEffect(() => {
    if (navState?.carregar) {
      dispatch({ type: 'LOAD_POP', pop: navState.carregar });
      setCarregando(false);
      return;
    }
    if (navState?.novo_pop) {
      dispatch({ type: 'RESET' });
      dispatch({ type: 'SET_FIELD', field: 'nome_pop', value: navState.novo_pop.nome });
      dispatch({ type: 'SET_FIELD', field: 'objetivo', value: navState.novo_pop.objetivo });
      setCarregando(false);
      return;
    }
    if (navState?.editar_id) {
      getPop(navState.editar_id)
        .then((pop) => {
          setLoadedFromId(navState.editar_id ?? null);
          dispatch({ type: 'LOAD_POP', pop });
        })
        .catch(() => undefined)
        .finally(() => setCarregando(false));
      return;
    }
    setCarregando(false);
  }, [navState]);

  useEffect(() => {
    if (!state.codigo?.trim()) return;
    const timer = setTimeout(() => {
      checkCode(state.codigo, loadedFromId ? [loadedFromId] : [])
        .then((duplicado) => {
          if (duplicado) {
            setErroDuplicado(
              `O código ${state.codigo} já é usado pelo POP '${duplicado.nome_pop}' (criado em ${duplicado.created_at}). Use um código diferente ou carregue o POP existente para editá-lo.`,
            );
          } else {
            setErroDuplicado(null);
          }
        })
        .catch(() => undefined);
    }, 400);
    return () => clearTimeout(timer);
  }, [state.codigo, loadedFromId]);

  const handleManualSave = async () => {
    await saveNow();
    if (loadedFromId || validateLocal(state).length === 0) {
      try {
        const result = await generatePop(state, loadedFromId ? [loadedFromId] : []);
        if (!loadedFromId) {
          setLoadedFromId(result.pop_id);
        }
      } catch {
        // Ignore backend validation error during manual draft save
      }
    }
    showToast('Alterações salvas com sucesso!', 'success');
  };

  const gerar = async () => {
    setGerando(true);
    setErros([]);
    setErroDuplicado(null);
    try {
      const errors = validateLocal(state);
      if (errors.length) {
        setErros(errors);
        showToast('Corrija os campos obrigatórios antes de gerar.', 'error');
        return;
      }
      const result = await generatePop(state, loadedFromId ? [loadedFromId] : []);
      setGerado(result);
      setLoadedFromId(result.pop_id);
      discard();
      showToast('POP gerado com sucesso!', 'success');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erro ao gerar o POP.';
      if (message.includes('código')) {
        setErroDuplicado(message);
      } else {
        setErros([message]);
      }
      showToast(message, 'error');
    } finally {
      setGerando(false);
    }
  };

  const baixarGerado = async (tipo: 'docx' | 'pdf') => {
    if (!gerado) return;
    const nome = tipo === 'pdf' ? gerado.filename.replace(/\.docx$/, '.pdf') : gerado.filename;
    try {
      if (tipo === 'docx') {
        const blob = await downloadDocx(gerado.pop_id);
        triggerDownload(blob, nome);
      } else {
        const blob = await previewPdf(state);
        triggerDownload(blob, nome);
      }
      showToast(`Arquivo ${tipo.toUpperCase()} baixado.`, 'success');
    } catch {
      try {
        const blob = tipo === 'docx' ? await previewDocx(state) : await previewPdf(state);
        triggerDownload(blob, nome);
      } catch {
        showToast('Não foi possível preparar o arquivo.', 'error');
      }
    }
  };

  const carregarDoHistorico = (id: string) => {
    setLoadedFromId(id);
    getPop(id).then((pop) => {
      dispatch({ type: 'LOAD_POP', pop });
      setGerado(null);
      showToast('POP carregado para edição.', 'info');
    });
  };

  const handleExcluir = (id: string) => {
    listPops()
      .then((all) => setConfirmandoExclusao(all.find((r) => r.id === id) ?? null))
      .catch(() => undefined);
  };

  const excluirConfirmado = async () => {
    if (!confirmandoExclusao) return;
    try {
      await deletePop(confirmandoExclusao.id);
      showToast('POP excluído.', 'success');
    } catch {
      showToast('Não foi possível excluir o POP.', 'error');
    }
    if (loadedFromId === confirmandoExclusao.id) setLoadedFromId(null);
    setConfirmandoExclusao(null);
    onDelCache();
  };

  const onDelCache = () => {
    dispatch({ type: 'RESET' });
    setGerado(null);
    discard();
  };

  return (
    <>
      {/* Cabeçalho compacto com Logo da CODEBA no topo à esquerda */}
      <div className="form-header-card">
        <div className="form-header-main">
          <div className="form-header-brand">
            <div className="form-logo-box">
              <img src={logo} alt="CODEBA" className="form-codeba-logo" />
            </div>
            <div className="form-header-titles">
              <h1 className="form-page-title">
                <IconFileText size={20} />
                Formulário — GeraPOP
              </h1>
              <p className="form-page-subtitle">
                Preencha os campos e gere o documento POP formatado (.docx).
              </p>
            </div>
          </div>
          <div className="form-header-status-side">
            {isSaving ? (
              <span className="draft-indicator">⏳ Salvando rascunho…</span>
            ) : lastSavedTime ? (
              <span className="draft-indicator">
                <IconCheckCircle size={12} /> Rascunho salvo às {lastSavedTime}
              </span>
            ) : null}
          </div>
        </div>
      </div>

      {carregando ? (
        <div className="dash-loading">
          <span className="spinner" />
          Carregando…
        </div>
      ) : (
        <>
          <div className="form-workspace">
            {/* Barra de Progresso Superior */}
            <div className="form-progress-strip">
              <div
                className="form-progress-fill"
                style={{ width: `${progress}%` }}
                role="progressbar"
                aria-valuenow={progress}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label="Progresso do preenchimento"
              />
            </div>

            {/* Bloco Superior: Identificação + Metadados + Histórico de Revisões */}
            <div className="form-card form-top-card">
              <IdentificacaoSection state={state} dispatch={dispatch} />
            </div>

            {/* Seções em Fluxo Completo e Confortável */}
            <div className="form-sections-stack">
              <Accordion title="Objetivo e Escopo" defaultOpen={true}>
                <ObjetivoEscopoSection state={state} dispatch={dispatch} />
              </Accordion>

              <Accordion
                title="Definições"
                badge={`${state.definicoes.filter((d) => d.termo).length}`}
                defaultOpen={false}
              >
                <DefinicoesSection state={state} dispatch={dispatch} />
              </Accordion>

              <Accordion
                title="Procedimento"
                badge={`${state.secoes.length} seções`}
                defaultOpen={true}
              >
                <ProcedimentoSection state={state} dispatch={dispatch} />
              </Accordion>

              <Accordion
                title="Regras e Restrições"
                badge={`${state.regras.filter(Boolean).length}`}
                defaultOpen={false}
              >
                <RegrasSection state={state} dispatch={dispatch} />
              </Accordion>

              <Accordion title="Consulta e Relatórios" defaultOpen={false}>
                <ConsultaSection state={state} dispatch={dispatch} />
              </Accordion>
            </div>
          </div>

          {erros.length > 0 ? (
            <div className="alert alert-error">
              {erros.map((erro) => (
                <div key={erro}>{erro}</div>
              ))}
            </div>
          ) : null}
          {erroDuplicado ? <div className="alert alert-error">{erroDuplicado}</div> : null}
          {gerado ? (
            <div className="alert alert-success">
              <IconCheckCircle size={16} />
              POP gerado com sucesso.
            </div>
          ) : null}

          <div className="form-actions">
            <Button icon={<IconSave size={15} />} onClick={handleManualSave} disabled={isSaving}>
              Salvar rascunho
            </Button>
            <Button
              icon={<IconEye size={15} />}
              onClick={() => navigate('/preview/rascunho/atual', { state: { pop: state } })}
            >
              Visualizar Prévia
            </Button>
            <Button variant="primary" icon={<IconZap size={15} />} onClick={gerar} loading={gerando}>
              Gerar POP (.docx)
            </Button>
            {gerado ? (
              <>
                <Button icon={<IconDownload size={14} />} onClick={() => baixarGerado('docx')}>
                  Baixar POP (.docx)
                </Button>
                <Button icon={<IconDownload size={14} />} onClick={() => baixarGerado('pdf')}>
                  Baixar POP (.pdf)
                </Button>
              </>
            ) : null}
          </div>

          <History onCarregar={carregarDoHistorico} onExcluir={handleExcluir} />
        </>
      )}

      <Modal
        open={confirmandoExclusao !== null}
        title="Confirmar exclusão"
        onClose={() => setConfirmandoExclusao(null)}
        footer={
          <>
            <Button variant="ghost" onClick={() => setConfirmandoExclusao(null)}>
              Cancelar
            </Button>
            <Button variant="danger" icon={<IconTrash size={14} />} onClick={excluirConfirmado}>
              Sim, excluir
            </Button>
          </>
        }
      >
        Excluir permanentemente <strong>{confirmandoExclusao?.nome_pop}</strong> (
        {confirmandoExclusao?.codigo || 'sem código'})? Essa ação não pode ser desfeita.
      </Modal>
    </>
  );
}
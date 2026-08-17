import { useEffect, useReducer, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
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
import { RevisoesSection } from '../components/Form/RevisoesSection';
import { History } from '../components/History/History';
import { Simulacao } from '../components/Simulation/Simulacao';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
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

export function FormPage() {
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
  const { discard } = useDraft({ state, loadedFromId, enabled: !carregando && !gerado });

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

  useDraft({ state, loadedFromId, enabled: !carregando && !gerado });

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

  const gerar = async () => {
    setGerando(true);
    setErros([]);
    setErroDuplicado(null);
    try {
      const errors = validateLocal(state);
      if (errors.length) {
        setErros(errors);
        return;
      }
      const result = await generatePop(state, loadedFromId ? [loadedFromId] : []);
      setGerado(result);
      setLoadedFromId(result.pop_id);
      discard();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erro ao gerar o POP.';
      if (message.includes('código')) {
        setErroDuplicado(message);
      } else {
        setErros([message]);
      }
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
    } catch {
      try {
        const blob = tipo === 'docx' ? await previewDocx(state) : await previewPdf(state);
        triggerDownload(blob, nome);
      } catch {
        alert('Não foi possível preparar o arquivo.');
      }
    }
  };

  const carregarDoHistorico = (id: string) => {
    setLoadedFromId(id);
    getPop(id).then((pop) => {
      dispatch({ type: 'LOAD_POP', pop });
      setGerado(null);
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
    } catch {
      alert('Não foi possível excluir o POP.');
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
      <div className="page-header">
        <h1>📝 Formulário — GeraPOP</h1>
        <p className="subtitle">Preencha os campos e gere o documento POP formatado (.docx).</p>
      </div>

      {carregando ? (
        <p style={{ color: 'var(--muted)' }}>Carregando…</p>
      ) : (
        <>
          <Simulacao dispatch={dispatch} />

          <div className="form-card">
            <IdentificacaoSection state={state} dispatch={dispatch} />
            <ObjetivoEscopoSection state={state} dispatch={dispatch} />
            <DefinicoesSection state={state} dispatch={dispatch} />
            <ProcedimentoSection state={state} dispatch={dispatch} />
            <RegrasSection state={state} dispatch={dispatch} />
            <ConsultaSection state={state} dispatch={dispatch} />
            <RevisoesSection state={state} dispatch={dispatch} />
          </div>

          {erros.length > 0 ? (
            <div className="alert alert-error">
              {erros.map((erro) => (
                <div key={erro}>{erro}</div>
              ))}
            </div>
          ) : null}
          {erroDuplicado ? <div className="alert alert-error">{erroDuplicado}</div> : null}
          {gerado ? <div className="alert alert-success">POP gerado com sucesso.</div> : null}

          <div className="form-actions">
            <Button variant="primary" onClick={gerar} loading={gerando}>
              Gerar POP (.docx)
            </Button>
            {gerado ? (
              <>
                <Button onClick={() => baixarGerado('docx')}>Baixar POP (.docx)</Button>
                <Button onClick={() => baixarGerado('pdf')}>Baixar POP (.pdf)</Button>
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
            <Button variant="danger" onClick={excluirConfirmado}>
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
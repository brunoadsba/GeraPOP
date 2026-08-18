import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import {
  downloadDocx,
  downloadPdf,
  getFluxoPop,
  getPop,
  previewDocx,
  previewPdf,
  triggerDownload,
} from '../api/client';
import { Button } from '../components/ui/Button';
import { IconArrowLeft, IconDownload, IconEdit } from '../components/ui/Icons';
import { showToast } from '../components/ui/Toast';
import type { PopData } from '../types/pop';

export function PreviewPage() {
  const { type, ref } = useParams<{ type: string; ref: string }>();
  const navigate = useNavigate();
  const [pop, setPop] = useState<PopData | null>(null);
  const [naoEncontrado, setNaoEncontrado] = useState(false);

  const location = useLocation();
  const statePop = (location.state as { pop?: PopData } | null)?.pop;

  useEffect(() => {
    if (statePop) {
      setPop(statePop);
      return;
    }
    if (!ref) return;

    const promise = type === 'fluxo' ? getFluxoPop(ref) : getPop(ref);
    promise
      .then((data) => {
        if (data) {
          setPop(data);
        } else {
          setNaoEncontrado(true);
        }
      })
      .catch(() => setNaoEncontrado(true));
  }, [type, ref, statePop]);

  useEffect(() => {
    if (!pop) return;
    document.title = `${pop.nome_pop || 'POP'} — GeraPOP`;
    return () => {
      document.title = 'GeraPOP — CODEBA';
    };
  }, [pop]);

  const handleEditar = () => {
    if (type === 'salvo' && ref) {
      navigate('/formulario', { state: { editar_id: ref } });
    } else if (type === 'fluxo' && ref) {
      navigate('/formulario', { state: { carregar: pop } });
    } else if (pop) {
      navigate('/formulario', { state: { carregar: pop } });
    } else {
      navigate('/formulario');
    }
  };

  const baixar = async (tipo: 'docx' | 'pdf') => {
    if (!pop) return;
    const basename = `${pop.codigo}_${slugify(pop.nome_pop)}.docx`;
    const nome = tipo === 'pdf' ? basename.replace(/\.docx$/, '.pdf') : basename;
    try {
      let blob: Blob;
      if (type === 'salvo' && ref) {
        blob = tipo === 'docx' ? await downloadDocx(ref) : await downloadPdf(ref);
      } else {
        blob = tipo === 'docx' ? await previewDocx(pop) : await previewPdf(pop);
      }
      triggerDownload(blob, nome);
      showToast(`Arquivo ${tipo.toUpperCase()} baixado.`, 'success');
    } catch {
      showToast('Não foi possível baixar o arquivo.', 'error');
    }
  };

  if (naoEncontrado) {
    return (
      <div className="page-header">
        <h1>POP não encontrado</h1>
        <Button icon={<IconArrowLeft size={14} />} onClick={() => navigate('/')}>
          Voltar ao painel
        </Button>
      </div>
    );
  }

  if (!pop) {
    return (
      <div className="dash-loading">
        <span className="spinner" />
        Carregando…
      </div>
    );
  }

  let passoGlobal = 0;

  return (
    <>
      <div className="preview-actions">
        <Button variant="ghost" icon={<IconArrowLeft size={14} />} onClick={() => navigate('/')}>
          Voltar ao painel
        </Button>
        <Button icon={<IconEdit size={14} />} onClick={handleEditar}>
          Editar POP
        </Button>
        <Button icon={<IconDownload size={14} />} onClick={() => baixar('docx')}>
          Baixar .docx
        </Button>
        <Button icon={<IconDownload size={14} />} onClick={() => baixar('pdf')}>
          Baixar .pdf
        </Button>
      </div>

      <div className="preview-hero">
        <h1>{pop.nome_pop || 'POP sem título'}</h1>
        <div className="preview-chips">
          <span className="preview-chip">{pop.codigo || 'sem código'}</span>
          <span className="preview-chip">v{pop.versao}</span>
          <span className="preview-chip">{pop.data}</span>
          <span className="preview-chip">{pop.area || 'sem área'}</span>
        </div>
      </div>

      {pop.aviso ? <div className="preview-aviso">{pop.aviso}</div> : null}

      {pop.objetivo ? (
        <>
          <div className="preview-eyebrow">Objetivo</div>
          <p>{pop.objetivo}</p>
        </>
      ) : null}

      {pop.escopo ? (
        <>
          <div className="preview-eyebrow">Escopo e Pré-condições</div>
          <p>{pop.escopo}</p>
        </>
      ) : null}

      {definicoesUteis(pop).length > 0 ? (
        <>
          <div className="preview-eyebrow">Definições</div>
          <Tabela linhas={definicoesUteis(pop)} />
        </>
      ) : null}

      {pop.secoes.length > 0 ? (
        <>
          <div className="preview-eyebrow">Procedimento</div>
          {pop.secoes.map((secao, indice) => {
            const passos = secao.passos.filter(Boolean);
            const campos = secao.campos.filter((c) => c.campo);
            if (!secao.titulo) return null;
            return (
              <div key={indice}>
                <h3 className="preview-h3">
                  {indice + 1}. {secao.titulo}
                </h3>
                {passos.map((passo, i) => {
                  passoGlobal++;
                  return (
                    <div className="preview-passo" key={i}>
                      <span className="preview-passo-num">{passoGlobal}</span>
                      {passo}
                    </div>
                  );
                })}
                {campos.length > 0 ? (
                  <>
                    <div className="preview-h2">Campos de registro:</div>
                    <Tabela linhas={campos.map((c) => [c.campo, c.descricao])} />
                  </>
                ) : null}
              </div>
            );
          })}
        </>
      ) : null}

      {pop.regras.filter(Boolean).length > 0 ? (
        <>
          <div className="preview-eyebrow">Regras e Restrições</div>
          {pop.regras.filter(Boolean).map((regra, i) => (
            <div className="preview-regra" key={i}>
              {regra}
            </div>
          ))}
        </>
      ) : null}

      {pop.consulta ? (
        <>
          <div className="preview-eyebrow">Consulta e Relatórios</div>
          <p>{pop.consulta}</p>
        </>
      ) : null}

      {pop.revisoes.filter((r) => r.revisao).length > 0 ? (
        <>
          <div className="preview-eyebrow">Histórico de Revisões</div>
          <Tabela
            linhas={pop.revisoes
              .filter((r) => r.revisao)
              .map((r) => [r.revisao, `${r.data} — ${r.descricao}`])}
          />
        </>
      ) : null}
    </>
  );
}

function Tabela({ linhas }: { linhas: [string, string][] }) {
  return (
    <table className="preview-table">
      <tbody>
        {linhas.map(([chave, valor], i) => (
          <tr key={i}>
            <td>{chave}</td>
            <td>{valor}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function definicoesUteis(pop: PopData) {
  return pop.definicoes
    ? pop.definicoes.filter((d) => d.termo).map((d) => [d.termo, d.definicao] as [string, string])
    : [];
}

function slugify(texto: string): string {
  return (texto || '').replace(/[^\w.-]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 30);
}
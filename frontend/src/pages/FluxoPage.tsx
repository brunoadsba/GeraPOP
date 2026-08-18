import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getFluxo,
  getFluxoPop,
  previewDocx,
  previewPdf,
  triggerDownload,
} from '../api/client';
import { CardGrid } from '../components/Dashboard/CardGrid';
import { Button } from '../components/ui/Button';
import {
  IconCheckCircle,
  IconClock,
  IconDownload,
  IconEdit,
  IconEye,
  IconPlus,
  IconTarget,
} from '../components/ui/Icons';
import { showToast } from '../components/ui/Toast';
import type { Fluxo, FluxoNo, PopData } from '../types/pop';

export function FluxoPage() {
  const navigate = useNavigate();
  const [fluxo, setFluxo] = useState<Fluxo | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [filtro, setFiltro] = useState<'todos' | 'concluidos' | 'pendentes'>('todos');

  useEffect(() => {
    getFluxo()
      .then(setFluxo)
      .catch(() => undefined)
      .finally(() => setCarregando(false));
  }, []);

  const baixarPop = async (pop: PopData, filename: string, tipo: 'docx' | 'pdf') => {
    try {
      const blob = tipo === 'docx' ? await previewDocx(pop) : await previewPdf(pop);
      const nome = tipo === 'pdf' ? filename.replace(/\.docx$/, '.pdf') : filename;
      triggerDownload(blob, nome);
      showToast(`Arquivo ${tipo.toUpperCase()} baixado com sucesso.`, 'success');
    } catch {
      showToast('Não foi possível gerar o arquivo.', 'error');
    }
  };

  const criarPop = (no: FluxoNo) => {
    navigate('/formulario', { state: { novo_pop: { nome: no.rotulo, objetivo: no.descricao } } });
  };

  const editarPopFluxo = (no: FluxoNo) => {
    if (!no.pop_ref) return;
    getFluxoPop(no.pop_ref).then((pop) => {
      if (pop) navigate('/formulario', { state: { carregar: pop } });
    });
  };

  if (carregando) {
    return (
      <div className="dash-loading">
        <span className="spinner" />
        Carregando esteira do Fluxo SEV…
      </div>
    );
  }

  if (!fluxo) {
    return (
      <div className="page-header">
        <h1>Fluxo SEV</h1>
        <div className="alert alert-warning">Não foi possível carregar o fluxo SEV.</div>
      </div>
    );
  }

  const concluidos = fluxo.nos.filter((no) => no.pop_ref).sort((a, b) => a.etapa - b.etapa);
  const pendentes = fluxo.nos.filter((no) => !no.pop_ref).sort((a, b) => a.etapa - b.etapa);

  const listaFiltrada =
    filtro === 'concluidos' ? concluidos : filtro === 'pendentes' ? pendentes : fluxo.nos;

  return (
    <>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.8rem' }}>
          <div>
            <h1>
              <IconTarget size={24} />
              Fluxo SEV — {fluxo.titulo}
            </h1>
            <p className="subtitle">{fluxo.descricao}</p>
          </div>
          <Button
            variant="primary"
            icon={<IconPlus size={15} />}
            onClick={() => navigate('/formulario')}
          >
            Novo POP
          </Button>
        </div>
      </div>

      {/* Abas de filtro */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.2rem', flexWrap: 'wrap' }}>
        <Button
          variant={filtro === 'todos' ? 'primary' : 'default'}
          size="sm"
          onClick={() => setFiltro('todos')}
        >
          Todas as Etapas ({fluxo.nos.length})
        </Button>
        <Button
          variant={filtro === 'concluidos' ? 'primary' : 'default'}
          size="sm"
          icon={<IconCheckCircle size={13} />}
          onClick={() => setFiltro('concluidos')}
        >
          Com POP ({concluidos.length})
        </Button>
        <Button
          variant={filtro === 'pendentes' ? 'primary' : 'default'}
          size="sm"
          icon={<IconClock size={13} />}
          onClick={() => setFiltro('pendentes')}
        >
          Pendentes ({pendentes.length})
        </Button>
      </div>

      <section className="dash-section">
        {listaFiltrada.length === 0 ? (
          <p className="dash-empty">Nenhuma etapa encontrada com o filtro selecionado.</p>
        ) : (
          <CardGrid>
            {listaFiltrada.map((no) =>
              no.pop_ref ? (
                <CardEtapaConcluida
                  key={no.id}
                  no={no}
                  onVer={() => navigate(`/preview/fluxo/${no.pop_ref}`)}
                  onEditar={() => editarPopFluxo(no)}
                  onBaixar={baixarPop}
                />
              ) : (
                <CardEtapaPendente key={no.id} no={no} onCriar={() => criarPop(no)} />
              ),
            )}
          </CardGrid>
        )}
      </section>
    </>
  );
}

function CardEtapaConcluida({
  no,
  onVer,
  onEditar,
  onBaixar,
}: {
  no: FluxoNo;
  onVer: () => void;
  onEditar: () => void;
  onBaixar: (pop: PopData, filename: string, tipo: 'docx' | 'pdf') => void;
}) {
  const [pop, setPop] = useState<PopData | null>(null);
  useEffect(() => {
    if (no.pop_ref) getFluxoPop(no.pop_ref).then(setPop).catch(() => undefined);
  }, [no.pop_ref]);

  return (
    <div className="dash-card">
      <div className="dash-card-head">
        <span className="dash-card-title">
          {no.etapa}. {no.rotulo}
        </span>
        <span className="dash-chip gerado">Etapa {no.etapa}</span>
      </div>
      <div className="dash-card-caption">{no.descricao}</div>
      {pop ? (
        <div className="dash-card-actions">
          <Button icon={<IconEye size={14} />} onClick={onVer}>
            Visualizar
          </Button>
          <Button
            icon={<IconDownload size={14} />}
            onClick={() =>
              onBaixar(
                pop,
                pop.codigo ? `${pop.codigo}_${slug(pop.nome_pop)}.docx` : 'pop.docx',
                'docx',
              )
            }
          >
            .docx
          </Button>
          <Button
            icon={<IconDownload size={14} />}
            onClick={() =>
              onBaixar(
                pop,
                pop.codigo ? `${pop.codigo}_${slug(pop.nome_pop)}.docx` : 'pop.docx',
                'pdf',
              )
            }
          >
            .pdf
          </Button>
          <Button icon={<IconEdit size={14} />} onClick={onEditar}>
            Editar
          </Button>
        </div>
      ) : (
        <p className="dash-empty">Carregando dados da etapa…</p>
      )}
    </div>
  );
}

function CardEtapaPendente({ no, onCriar }: { no: FluxoNo; onCriar: () => void }) {
  return (
    <div className="dash-card">
      <div className="dash-card-head">
        <span className="dash-card-title">
          {no.etapa}. {no.rotulo}
        </span>
        <span className="dash-chip pendente">Pendente</span>
      </div>
      <div className="dash-card-caption">{no.descricao}</div>
      <div className="dash-card-actions">
        <Button variant="primary" icon={<IconPlus size={14} />} onClick={onCriar}>
          Criar POP desta etapa
        </Button>
      </div>
    </div>
  );
}

function slug(nome: string): string {
  return nome.replace(/[^\w.-]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 30);
}

import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  deletePop,
  downloadDocx,
  downloadPdf,
  getFluxo,
  getFluxoPop,
  listPops,
  previewDocx,
  previewPdf,
  triggerDownload,
} from '../api/client';
import { CardGrid } from '../components/Dashboard/CardGrid';
import { Hero } from '../components/Dashboard/Hero';
import { KpiGrid } from '../components/Dashboard/KpiGrid';
import { Stepper } from '../components/Dashboard/Stepper';
import { Button } from '../components/ui/Button';
import {
  IconDownload,
  IconEdit,
  IconEye,
  IconFileText,
  IconClock,
  IconFolder,
  IconPin,
  IconPlus,
  IconTrash,
} from '../components/ui/Icons';
import { Modal } from '../components/ui/Modal';
import { showToast } from '../components/ui/Toast';
import type { Fluxo, FluxoNo, PopData, PopListItem } from '../types/pop';

const MODELO_REF = 'pop-desembarque';

export function HomePage() {
  const navigate = useNavigate();
  const [fluxo, setFluxo] = useState<Fluxo | null>(null);
  const [salvos, setSalvos] = useState<PopListItem[]>([]);
  const [confirmando, setConfirmando] = useState<PopListItem | null>(null);
  const [carregando, setCarregando] = useState(true);

  const carregar = useCallback(() => {
    Promise.all([getFluxo(), listPops()])
      .then(([fluxoData, pops]) => {
        setFluxo(fluxoData);
        setSalvos(pops);
      })
      .catch(() => undefined)
      .finally(() => setCarregando(false));
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

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

  const baixarSalvo = async (record: PopListItem, tipo: 'docx' | 'pdf') => {
    try {
      const blob = tipo === 'docx' ? await downloadDocx(record.id) : await downloadPdf(record.id);
      const nome = tipo === 'pdf' ? record.filename.replace(/\.docx$/, '.pdf') : record.filename;
      triggerDownload(blob, nome);
      showToast(`Arquivo ${tipo.toUpperCase()} baixado com sucesso.`, 'success');
    } catch {
      showToast('Não foi possível baixar o arquivo.', 'error');
    }
  };

  const confirmarExclusao = async () => {
    if (!confirmando) return;
    try {
      await deletePop(confirmando.id);
      showToast('POP excluído com sucesso.', 'success');
    } catch {
      showToast('Não foi possível excluir o POP.', 'error');
    }
    setConfirmando(null);
    carregar();
  };

  if (carregando) {
    return (
      <div className="dash-loading">
        <span className="spinner" />
        Carregando…
      </div>
    );
  }

  if (!fluxo) {
    return (
      <div className="page-header">
        <h1>
          <IconFileText size={24} />
          Início
        </h1>
        <div className="alert alert-warning">
          Não foi possível carregar o fluxo SEV. Use o menu 'Formulário' para criar um POP avulso.
        </div>
      </div>
    );
  }

  const pendentes = fluxo.nos
    .filter((no) => !no.pop_ref)
    .sort((a, b) => a.etapa - b.etapa);
  const gerados = fluxo.nos
    .filter((no) => no.pop_ref)
    .sort((a, b) => a.etapa - b.etapa);
  const total = fluxo.nos.length;
  const concluido = total ? Math.round((gerados.length / total) * 100) : 0;

  const kpis = [
    { icone: '📋', valor: String(total), rotulo: 'Etapas' },
    { icone: '📄', valor: String(salvos.length), rotulo: 'POPs gerados' },
    { icone: '⏳', valor: String(pendentes.length), rotulo: 'Pendentes' },
    { icone: '✅', valor: `${concluido}%`, rotulo: 'Concluído' },
  ];

  const criarPop = (no: FluxoNo) => {
    navigate('/formulario', { state: { novo_pop: { nome: no.rotulo, objetivo: no.descricao } } });
  };

  const editarPopFluxo = (no: FluxoNo) => {
    if (!no.pop_ref) return;
    getFluxoPop(no.pop_ref).then((pop) => {
      if (pop) navigate('/formulario', { state: { carregar: pop } });
    });
  };

  return (
    <>
      <Hero titulo={fluxo.titulo} descricao={fluxo.descricao} />
      <KpiGrid kpis={kpis} />
      <Stepper nos={fluxo.nos} />

      <section className="dash-section">
        <h2 className="dash-section-title">
          <IconPin size={18} />
          Modelo de referência
        </h2>
        <CardGrid>
          <ModeloCard onVer={() => {
            getFluxoPop(MODELO_REF).then((pop) => {
              if (pop) navigate('/formulario', { state: { carregar: pop } });
            });
          }} onBaixar={baixarPop} />
        </CardGrid>
      </section>

      <section className="dash-section">
        <h2 className="dash-section-title">
          <IconFileText size={18} />
          Etapas com POP ({gerados.length}/{total})
        </h2>
        {gerados.length === 0 ? (
          <p className="dash-empty">Nenhuma etapa do fluxo possui POP vinculado ainda.</p>
        ) : (
          <CardGrid>
            {gerados.map((no) => (
              <CardEtapaGerada
                key={no.id}
                no={no}
                onVer={() => navigate(`/preview/fluxo/${no.pop_ref}`)}
                onEditar={() => editarPopFluxo(no)}
                onBaixar={baixarPop}
              />
            ))}
          </CardGrid>
        )}
      </section>

      <section className="dash-section">
        <h2 className="dash-section-title">
          <IconClock size={18} />
          POPs pendentes ({pendentes.length})
        </h2>
        {pendentes.length === 0 ? (
          <p className="dash-empty">Todas as etapas do fluxo já possuem POP.</p>
        ) : (
          <CardGrid>
            {pendentes.map((no) => (
              <CardEtapaPendente key={no.id} no={no} onCriar={() => criarPop(no)} />
            ))}
          </CardGrid>
        )}
      </section>

      <section className="dash-section">
        <h2 className="dash-section-title">
          <IconFolder size={18} />
          POPs salvos no app ({salvos.length})
        </h2>
        {salvos.length === 0 ? (
          <p className="dash-empty">Nenhum POP salvo ainda. Gere um POP no formulário.</p>
        ) : (
          <CardGrid>
            {salvos.map((record) => (
              <CardSalvo
                key={record.id}
                record={record}
                onVer={() => navigate(`/preview/salvo/${record.id}`)}
                onEditar={() => navigate('/formulario', { state: { editar_id: record.id } })}
                onBaixar={baixarSalvo}
                onExcluir={() => setConfirmando(record)}
              />
            ))}
          </CardGrid>
        )}
      </section>

      <Modal
        open={confirmando !== null}
        title="Confirmar exclusão"
        onClose={() => setConfirmando(null)}
        footer={
          <>
            <Button variant="ghost" onClick={() => setConfirmando(null)}>
              Cancelar
            </Button>
            <Button variant="danger" icon={<IconTrash size={14} />} onClick={confirmarExclusao}>
              Sim, excluir
            </Button>
          </>
        }
      >
        Excluir permanentemente <strong>{confirmando?.nome_pop}</strong> (
        {confirmando?.codigo || 'sem código'})? Essa ação não pode ser desfeita.
      </Modal>
    </>
  );
}

function ModeloCard({
  onVer,
  onBaixar,
}: {
  onVer: () => void;
  onBaixar: (pop: PopData, filename: string, tipo: 'docx' | 'pdf') => void;
}) {
  const [pop, setPop] = useState<PopData | null>(null);
  useEffect(() => {
    getFluxoPop(MODELO_REF).then(setPop).catch(() => undefined);
  }, []);
  if (!pop) return null;
  return (
    <div className="dash-card">
      <div className="dash-card-head">
        <span className="dash-card-title">{pop.nome_pop}</span>
        <span className="dash-chip gerado">{pop.codigo}</span>
      </div>
      <div className="dash-card-caption">
        Exemplo completo de POP preenchido, validado contra o modelo OpenPort.
      </div>
      <div className="dash-card-actions">
        <Button icon={<IconEye size={14} />} onClick={onVer}>Ver modelo no formulário</Button>
        <Button icon={<IconDownload size={14} />} onClick={() => onBaixar(pop, pop.codigo ? `${pop.codigo}_${slug(pop.nome_pop)}.docx` : 'modelo.docx', 'docx')}>
          .docx
        </Button>
      </div>
    </div>
  );
}

function CardEtapaGerada({
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
        <span className="dash-card-title">{no.rotulo}</span>
        <span className="dash-chip gerado">{no.etapa}</span>
      </div>
      <div className="dash-card-caption">{no.descricao}</div>
      {pop ? (
        <div className="dash-card-actions">
          <Button icon={<IconEye size={14} />} onClick={onVer}>Visualizar POP</Button>
          <Button icon={<IconDownload size={14} />} onClick={() => onBaixar(pop, pop.codigo ? `${pop.codigo}_${slug(pop.nome_pop)}.docx` : 'pop.docx', 'docx')}>
            .docx
          </Button>
          <Button icon={<IconDownload size={14} />} onClick={() => onBaixar(pop, pop.codigo ? `${pop.codigo}_${slug(pop.nome_pop)}.docx` : 'pop.docx', 'pdf')}>
            .pdf
          </Button>
          <Button icon={<IconEdit size={14} />} onClick={onEditar}>Editar POP</Button>
        </div>
      ) : (
        <p className="dash-empty">POP referenciado não encontrado.</p>
      )}
    </div>
  );
}

function CardEtapaPendente({ no, onCriar }: { no: FluxoNo; onCriar: () => void }) {
  return (
    <div className="dash-card">
      <div className="dash-card-head">
        <span className="dash-card-title">{no.rotulo}</span>
        <span className="dash-chip pendente">{no.etapa}</span>
      </div>
      <div className="dash-card-caption">{no.descricao}</div>
      <div className="dash-card-actions">
        <Button variant="primary" icon={<IconPlus size={14} />} onClick={onCriar}>
          Criar POP
        </Button>
      </div>
    </div>
  );
}

function CardSalvo({
  record,
  onVer,
  onEditar,
  onBaixar,
  onExcluir,
}: {
  record: PopListItem;
  onVer: () => void;
  onEditar: () => void;
  onBaixar: (record: PopListItem, tipo: 'docx' | 'pdf') => void;
  onExcluir: () => void;
}) {
  return (
    <div className="dash-card">
      <div className="dash-card-head">
        <span className="dash-card-title">{record.nome_pop}</span>
        <span className="dash-chip gerado">{record.codigo || '—'}</span>
      </div>
      <div className="dash-card-caption">
        {record.created_at ? formatData(record.created_at) : ''}
      </div>
      <div className="dash-card-actions">
        <Button icon={<IconEye size={14} />} onClick={onVer}>Visualizar</Button>
        <Button icon={<IconDownload size={14} />} onClick={() => onBaixar(record, 'docx')}>.docx</Button>
        <Button icon={<IconDownload size={14} />} onClick={() => onBaixar(record, 'pdf')}>.pdf</Button>
        <Button icon={<IconEdit size={14} />} onClick={onEditar}>Editar</Button>
        <Button variant="danger" icon={<IconTrash size={14} />} onClick={onExcluir}>
          Excluir
        </Button>
      </div>
    </div>
  );
}

function slug(nome: string): string {
  return nome.replace(/[^\w.-]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 30);
}

function formatData(iso: string): string {
  try {
    return new Date(iso).toLocaleString('pt-BR');
  } catch {
    return iso.slice(0, 19).replace('T', ' ');
  }
}

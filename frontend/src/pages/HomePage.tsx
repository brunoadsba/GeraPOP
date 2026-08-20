import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { downloadDocx, downloadPdf, listPops, triggerDownload } from '../api/client';
import { CardGrid } from '../components/Dashboard/CardGrid';
import { KpiGrid } from '../components/Dashboard/KpiGrid';
import { Button } from '../components/ui/Button';
import {
  IconDownload,
  IconEye,
  IconFileText,
  IconFolder,
  IconPlus,
} from '../components/ui/Icons';
import { showToast } from '../components/ui/Toast';
import type { PopListItem } from '../types/pop';

export function HomePage() {
  const navigate = useNavigate();
  const [salvos, setSalvos] = useState<PopListItem[]>([]);
  const [carregando, setCarregando] = useState(true);

  const carregar = useCallback(() => {
    setCarregando(true);
    listPops()
      .then(setSalvos)
      .catch(() => undefined)
      .finally(() => setCarregando(false));
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  const { criadosHoje, ultimos7 } = useMemo(() => {
    const agora = new Date();
    const inicioHoje = new Date(agora.getFullYear(), agora.getMonth(), agora.getDate());
    const inicio7 = new Date(inicioHoje);
    inicio7.setDate(inicio7.getDate() - 6);
    let criadosHoje = 0;
    let ultimos7 = 0;
    for (const record of salvos) {
      const criado = new Date(record.created_at);
      if (isNaN(criado.getTime())) continue;
      if (criado >= inicioHoje) criadosHoje += 1;
      if (criado >= inicio7) ultimos7 += 1;
    }
    return { criadosHoje, ultimos7 };
  }, [salvos]);

  const kpis = [
    { icone: '📄', valor: String(salvos.length), rotulo: 'POPs salvos' },
    { icone: '🕐', valor: String(criadosHoje), rotulo: 'Criados hoje' },
    { icone: '🗓️', valor: String(ultimos7), rotulo: 'Últimos 7 dias' },
  ];

  const recentes = salvos.slice(0, 6);

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

  return (
    <>
      <div className="page-header">
        <h1>
          <IconFileText size={24} />
          Início
        </h1>
        <p className="subtitle">Visão geral dos seus Procedimentos Operacionais Padrão.</p>
      </div>

      {carregando ? (
        <div className="dash-loading">
          <span className="spinner" />
          Carregando…
        </div>
      ) : (
        <>
          <KpiGrid kpis={kpis} />

          <section className="dash-section">
            <h2 className="dash-section-title">
              <IconFolder size={18} />
              Ações rápidas
            </h2>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <Button
                variant="primary"
                icon={<IconPlus size={15} />}
                onClick={() => navigate('/formulario')}
              >
                Novo POP
              </Button>
              <Button
                icon={<IconFolder size={15} />}
                onClick={() => navigate('/pops')}
              >
                Ir para a biblioteca
              </Button>
            </div>
          </section>

          <section className="dash-section">
            <h2 className="dash-section-title">
              <IconFolder size={18} />
              Recentes ({recentes.length})
            </h2>
            {recentes.length === 0 ? (
              <p className="dash-empty">
                Nenhum POP salvo ainda. Comece criando um novo POP pelo botão acima.
              </p>
            ) : (
              <CardGrid>
                {recentes.map((record) => (
                  <div className="dash-card" key={record.id}>
                    <div className="dash-card-head">
                      <span className="dash-card-title">{record.nome_pop}</span>
                      <span className="dash-chip gerado">{record.codigo || '—'}</span>
                    </div>
                    <div className="dash-card-caption">
                      {formatData(record.created_at)}
                    </div>
                    <div className="dash-card-actions">
                      <Button icon={<IconEye size={14} />} onClick={() => navigate(`/preview/salvo/${record.id}`)}>
                        Visualizar
                      </Button>
                      <Button icon={<IconDownload size={14} />} onClick={() => baixarSalvo(record, 'docx')}>.docx</Button>
                      <Button icon={<IconDownload size={14} />} onClick={() => baixarSalvo(record, 'pdf')}>.pdf</Button>
                    </div>
                  </div>
                ))}
              </CardGrid>
            )}
          </section>
        </>
      )}
    </>
  );
}

function formatData(iso: string): string {
  try {
    return new Date(iso).toLocaleString('pt-BR');
  } catch {
    return iso.slice(0, 19).replace('T', ' ');
  }
}
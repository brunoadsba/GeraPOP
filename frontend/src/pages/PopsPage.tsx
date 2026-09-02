import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  attachPop,
  deletePop,
  downloadBackup,
  downloadDocx,
  downloadPdf,
  listPops,
  triggerDownload,
} from '../api/client';
import { CardGrid } from '../components/Dashboard/CardGrid';
import { Button } from '../components/ui/Button';
import {
  IconArchive,
  IconDownload,
  IconEdit,
  IconEye,
  IconFolder,
  IconPlus,
  IconSearch,
  IconTrash,
  IconUpload,
} from '../components/ui/Icons';
import { Modal } from '../components/ui/Modal';
import { showToast } from '../components/ui/Toast';
import type { PopListItem } from '../types/pop';

export function PopsPage() {
  const navigate = useNavigate();
  const [pops, setPops] = useState<PopListItem[]>([]);
  const [busca, setBusca] = useState('');
  const [carregando, setCarregando] = useState(true);
  const [confirmando, setConfirmando] = useState<PopListItem | null>(null);
  const [anexarAberto, setAnexarAberto] = useState(false);
  const [anexarCodigo, setAnexarCodigo] = useState('');
  const [anexarNome, setAnexarNome] = useState('');
  const [anexarFile, setAnexarFile] = useState<File | null>(null);
  const [anexando, setAnexando] = useState(false);

  const carregar = () => {
    setCarregando(true);
    listPops()
      .then(setPops)
      .catch(() => undefined)
      .finally(() => setCarregando(false));
  };

  useEffect(() => {
    carregar();
  }, []);

  const filtrados = useMemo(() => {
    if (!busca.trim()) return pops;
    const termo = busca.toLowerCase();
    return pops.filter(
      (p) =>
        p.nome_pop.toLowerCase().includes(termo) ||
        p.codigo.toLowerCase().includes(termo) ||
        p.filename.toLowerCase().includes(termo),
    );
  }, [pops, busca]);

  const baixar = async (id: string, filename: string, tipo: 'docx' | 'pdf') => {
    try {
      const blob = tipo === 'docx' ? await downloadDocx(id) : await downloadPdf(id);
      const nome = tipo === 'pdf' ? filename.replace(/\.docx$/, '.pdf') : filename;
      triggerDownload(blob, nome);
      showToast(`Arquivo ${tipo.toUpperCase()} baixado.`, 'success');
    } catch {
      showToast('Não foi possível baixar o arquivo.', 'error');
    }
  };

  const baixarBackup = async () => {
    try {
      const blob = await downloadBackup();
      const nome = `gerapop_backup_${new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)}.zip`;
      triggerDownload(blob, nome);
      showToast('Backup (.zip) baixado com sucesso.', 'success');
    } catch {
      showToast('Não foi possível gerar o backup.', 'error');
    }
  };

  const excluirConfirmado = async () => {
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

  const handleAnexar = async () => {
    if (!anexarCodigo.trim() || !anexarNome.trim() || !anexarFile) {
      showToast('Preencha código, nome e selecione o arquivo.', 'error');
      return;
    }
    if (anexarFile.size > 10 * 1024 * 1024) {
      showToast('Arquivo muito grande (máx 10MB).', 'error');
      return;
    }
    const ext = anexarFile.name.split('.').pop()?.toLowerCase();
    if (ext !== 'docx' && ext !== 'pdf') {
      showToast('Apenas .docx ou .pdf são aceitos.', 'error');
      return;
    }
    setAnexando(true);
    try {
      const res = await attachPop(anexarCodigo.trim(), anexarNome.trim(), anexarFile);
      showToast(`POP ${res.codigo} anexado: ${res.nome_pop}`, 'success');
      setAnexarAberto(false);
      setAnexarCodigo('');
      setAnexarNome('');
      setAnexarFile(null);
      carregar();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Falha ao anexar POP.';
      showToast(msg, 'error');
    } finally {
      setAnexando(false);
    }
  };

  return (
    <>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.8rem' }}>
          <div>
            <h1>
              <IconFolder size={24} />
              Meus POPs (Biblioteca)
            </h1>
            <p className="subtitle">
              Todos os Procedimentos Operacionais Padrão criados e salvos no sistema.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <Button
              variant="ghost"
              icon={<IconUpload size={14} />}
              onClick={() => setAnexarAberto(true)}
            >
              Anexar POP externo
            </Button>
            <Button
              variant="ghost"
              icon={<IconArchive size={14} />}
              onClick={baixarBackup}
            >
              Baixar backup (.zip)
            </Button>
            <Button
              variant="primary"
              icon={<IconPlus size={15} />}
              onClick={() => navigate('/formulario', { state: { novo_pop: { nome: '', objetivo: '' } } })}
            >
              Novo POP
            </Button>
          </div>
        </div>
      </div>

      <div className="pops-search-bar" style={{ marginBottom: '1.6rem', display: 'flex', gap: '0.8rem', alignItems: 'center', maxWidth: '520px', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: '1 1 280px', minWidth: 0 }}>
          <input
            type="text"
            className="input"
            placeholder="Buscar por nome do POP ou código…"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            style={{ paddingLeft: '2.4rem', height: '42px', borderRadius: '12px' }}
            aria-label="Buscar POPs"
          />
          <div style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', opacity: 0.55, color: 'var(--muted)' }}>
            <IconSearch size={16} />
          </div>
        </div>
        <span style={{ fontSize: '0.8rem', color: 'var(--muted)', whiteSpace: 'nowrap' }}>
          {filtrados.length} de {pops.length} POPs
        </span>
        {busca ? (
          <Button variant="ghost" size="sm" onClick={() => setBusca('')}>
            Limpar
          </Button>
        ) : null}
      </div>

      {carregando ? (
        <div className="dash-skeleton-grid" aria-busy="true" aria-label="Carregando POPs">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="skeleton skeleton-card" style={{ animationDelay: `${i * 0.06}s` }} />
          ))}
        </div>
      ) : filtrados.length === 0 ? (
        <div className="dash-empty dash-empty-premium" role="status" aria-live="polite">
          <div className="dash-empty-illustration" aria-hidden="true">
            <IconFolder size={32} />
          </div>
          {busca ? (
            <>
              <h3 className="dash-empty-title">Nenhum resultado para “{busca}”</h3>
              <p className="dash-empty-desc">Tente ajustar os termos da busca ou limpar o filtro para ver todos os POPs.</p>
              <Button variant="ghost" icon={<IconSearch size={14} />} onClick={() => setBusca('')}>
                Limpar busca
              </Button>
            </>
          ) : (
            <>
              <h3 className="dash-empty-title">Sua biblioteca está vazia</h3>
              <p className="dash-empty-desc">Crie seu primeiro POP em menos de 3 minutos com o formulário guiado. O documento sai no padrão CODEBA pronto para exportar.</p>
              <Button
                variant="primary"
                icon={<IconPlus size={15} />}
                onClick={() => navigate('/formulario', { state: { novo_pop: { nome: '', objetivo: '' } } })}
              >
                Criar primeiro POP
              </Button>
            </>
          )}
        </div>
      ) : (
        <CardGrid>
          {filtrados.map((record) => (
            <div className="dash-card" key={record.id}>
              <div className="dash-card-head">
                <span className="dash-card-title">{record.nome_pop}</span>
                {record.codigo ? <span className="dash-chip">{record.codigo}</span> : null}
              </div>
              <div className="dash-card-caption">
                {record.created_at
                  ? new Date(record.created_at).toLocaleString('pt-BR', {
                      dateStyle: 'short',
                      timeStyle: 'medium',
                    })
                  : 'Data não informada'}
              </div>
              <div className="dash-card-actions">
                <Button
                  icon={<IconEye size={14} />}
                  onClick={() => navigate(`/preview/salvo/${record.id}`)}
                >
                  Visualizar
                </Button>
                <Button
                  icon={<IconDownload size={14} />}
                  onClick={() => baixar(record.id, record.filename, 'docx')}
                >
                  .docx
                </Button>
                <Button
                  icon={<IconDownload size={14} />}
                  onClick={() => baixar(record.id, record.filename, 'pdf')}
                >
                  .pdf
                </Button>
                <Button
                  icon={<IconEdit size={14} />}
                  onClick={() => navigate('/formulario', { state: { editar_id: record.id } })}
                >
                  Editar
                </Button>
                <Button
                  variant="danger"
                  icon={<IconTrash size={14} />}
                  onClick={() => setConfirmando(record)}
                >
                  Excluir
                </Button>
              </div>
            </div>
          ))}
        </CardGrid>
      )}

      <Modal
        open={confirmando !== null}
        title="Confirmar exclusão"
        onClose={() => setConfirmando(null)}
        footer={
          <>
            <Button variant="ghost" onClick={() => setConfirmando(null)}>
              Cancelar
            </Button>
            <Button variant="danger" icon={<IconTrash size={14} />} onClick={excluirConfirmado}>
              Sim, excluir
            </Button>
          </>
        }
      >
        Excluir permanentemente o POP <strong>{confirmando?.nome_pop}</strong> (
        {confirmando?.codigo || 'sem código'})? Essa ação não pode ser desfeita.
      </Modal>

      <Modal
        open={anexarAberto}
        title="Anexar POP externo"
        onClose={() => !anexando && setAnexarAberto(false)}
        footer={
          <>
            <Button variant="ghost" onClick={() => setAnexarAberto(false)} disabled={anexando}>
              Cancelar
            </Button>
            <Button variant="primary" icon={<IconUpload size={14} />} onClick={handleAnexar} disabled={anexando}>
              {anexando ? 'Anexando...' : 'Anexar'}
            </Button>
          </>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <p style={{ fontSize: '0.85rem', color: 'var(--muted)', margin: 0 }}>
            Para POPs criados fora do GeraPOP (Word/PDF manual). O arquivo será salvo na biblioteca oficial.
          </p>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Código *</span>
            <input
              className="input"
              placeholder="POP-OPE-003"
              value={anexarCodigo}
              onChange={(e) => setAnexarCodigo(e.target.value.toUpperCase())}
              style={{ height: '40px' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Nome do POP *</span>
            <input
              className="input"
              placeholder="Ex: PROGRAMAÇÃO DE CARGA"
              value={anexarNome}
              onChange={(e) => setAnexarNome(e.target.value)}
              style={{ height: '40px' }}
            />
          </label>
          <label style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>Arquivo .docx ou .pdf * (máx 10MB)</span>
            <input
              type="file"
              accept=".docx,.pdf"
              onChange={(e) => setAnexarFile(e.target.files?.[0] ?? null)}
              style={{ fontSize: '0.85rem' }}
            />
            {anexarFile ? (
              <span style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>
                Selecionado: {anexarFile.name} ({(anexarFile.size / 1024).toFixed(1)} KB)
              </span>
            ) : null}
          </label>
        </div>
      </Modal>
    </>
  );
}

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  downloadBackup,
  downloadDocx,
  downloadPdf,
  listPops,
  triggerDownload,
} from '../../api/client';
import { Button } from '../ui/Button';
import { IconArchive, IconDownload, IconEye, IconTrash, IconUpload } from '../ui/Icons';
import { showToast } from '../ui/Toast';
import type { PopListItem } from '../../types/pop';

interface HistoryProps {
  onCarregar: (id: string) => void;
  onExcluir: (id: string) => void;
}

export function History({ onCarregar, onExcluir }: HistoryProps) {
  const navigate = useNavigate();
  const [records, setRecords] = useState<PopListItem[]>([]);
  const [selected, setSelected] = useState<string>('');

  useEffect(() => {
    listPops().then(setRecords).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!selected && records.length) setSelected(records[0].id);
  }, [records, selected]);

  if (records.length === 0) {
    return <p className="dash-empty">Nenhum POP salvo ainda. Gere um POP para vê-lo aqui.</p>;
  }

  const baixar = async (id: string, tipo: 'docx' | 'pdf') => {
    const record = records.find((r) => r.id === id);
    if (!record) return;
    try {
      const blob = tipo === 'docx' ? await downloadDocx(id) : await downloadPdf(id);
      const nome = tipo === 'pdf' ? record.filename.replace(/\.docx$/, '.pdf') : record.filename;
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
      showToast('Backup baixado com sucesso.', 'success');
    } catch {
      showToast('Não foi possível gerar o backup.', 'error');
    }
  };

  return (
    <div className="history-box">
      <h2 className="section-title">Histórico de POPs gerados</h2>
      <div className="history-select-row">
        <select
          className="select"
          aria-label="POP salvo"
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
        >
          {records.map((record) => (
            <option key={record.id} value={record.id}>
              {formatLabel(record)}
            </option>
          ))}
        </select>
      </div>
      <div className="dash-card-actions">
        <Button icon={<IconDownload size={14} />} onClick={() => baixar(selected, 'docx')}>Baixar .docx</Button>
        <Button icon={<IconDownload size={14} />} onClick={() => baixar(selected, 'pdf')}>Baixar .pdf</Button>
        <Button icon={<IconEye size={14} />} onClick={() => navigate(`/preview/salvo/${selected}`)}>Visualizar</Button>
        <Button icon={<IconUpload size={14} />} onClick={() => onCarregar(selected)}>Carregar para editar</Button>
        <Button variant="danger" icon={<IconTrash size={14} />} onClick={() => onExcluir(selected)}>
          Excluir
        </Button>
      </div>
      <div style={{ marginTop: '1rem' }}>
        <Button variant="ghost" icon={<IconArchive size={14} />} onClick={baixarBackup}>
          Baixar backup (.zip)
        </Button>
      </div>
    </div>
  );
}

function formatLabel(record: PopListItem): string {
  const data = record.created_at?.slice(0, 19).replace('T', ' ') || '';
  return `${data} — ${record.codigo || 'POP'} — ${record.nome_pop.slice(0, 40)}`;
}
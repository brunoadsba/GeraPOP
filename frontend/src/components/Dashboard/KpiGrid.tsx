import { useEffect, useRef, useState } from 'react';
import { IconClipboard, IconFileText, IconClock, IconCheck } from '../ui/Icons';

interface Kpi {
  icone: string;
  valor: string;
  rotulo: string;
}

interface KpiGridProps {
  kpis: Kpi[];
}

const KPI_ICONS: Record<string, React.ReactNode> = {
  'Etapas': <IconClipboard size={18} />,
  'Com POP': <IconFileText size={18} />,
  'Etapas com POP': <IconFileText size={18} />,
  'POPs gerados': <IconFileText size={18} />,
  'Pendentes': <IconClock size={18} />,
  'Concluído': <IconCheck size={18} />,
};

function AnimatedValue({ value }: { value: string }) {
  const [display, setDisplay] = useState(value);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const num = parseInt(value, 10);
    if (isNaN(num) || value.includes('%')) {
      setDisplay(value);
      return;
    }
    // Simple count-up
    const duration = 600;
    const start = 0;
    const startTime = performance.now();

    function step(now: number) {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setDisplay(String(Math.round(start + (num - start) * eased)));
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }, [value]);

  return <div className="dash-kpi-value" ref={ref}>{display}</div>;
}

export function KpiGrid({ kpis }: KpiGridProps) {
  return (
    <div className="dash-kpis">
      {kpis.map((kpi) => (
        <div className="dash-kpi" key={kpi.rotulo}>
          <div className="dash-kpi-icon" aria-hidden="true">
            {KPI_ICONS[kpi.rotulo] ?? <IconClipboard size={18} />}
          </div>
          {kpi.valor.includes('%') ? (
            <div className="dash-kpi-value">{kpi.valor}</div>
          ) : (
            <AnimatedValue value={kpi.valor} />
          )}
          <div className="dash-kpi-label">{kpi.rotulo}</div>
        </div>
      ))}
    </div>
  );
}

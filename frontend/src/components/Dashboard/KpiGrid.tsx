interface Kpi {
  icone: string;
  valor: string;
  rotulo: string;
}

interface KpiGridProps {
  kpis: Kpi[];
}

export function KpiGrid({ kpis }: KpiGridProps) {
  return (
    <div className="dash-kpis">
      {kpis.map((kpi) => (
        <div className="dash-kpi" key={kpi.rotulo}>
          <div className="dash-kpi-icon" aria-hidden="true">
            {kpi.icone}
          </div>
          <div className="dash-kpi-value">{kpi.valor}</div>
          <div className="dash-kpi-label">{kpi.rotulo}</div>
        </div>
      ))}
    </div>
  );
}

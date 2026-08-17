import type { FluxoNo } from '../../types/pop';

interface StepperProps {
  nos: FluxoNo[];
}

export function Stepper({ nos }: StepperProps) {
  const ordenados = [...nos].sort((a, b) => a.etapa - b.etapa);
  let viuPendente = false;

  return (
    <div className="dash-steps" role="list" aria-label="Etapas do fluxo">
      {ordenados.map((no) => {
        const done = Boolean(no.pop_ref);
        let estado = '';
        if (done) {
          estado = 'done';
        } else if (!viuPendente) {
          estado = 'current';
          viuPendente = true;
        }
        return (
          <div className={`dash-step ${estado}`.trim()} key={no.id} role="listitem" title={no.rotulo}>
            <div className="dash-dot">{done ? '✓' : String(no.etapa)}</div>
            <div className="dash-step-label">{no.rotulo}</div>
          </div>
        );
      })}
    </div>
  );
}

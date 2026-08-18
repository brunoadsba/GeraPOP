import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/Button';
import { IconPlus } from '../ui/Icons';

interface HeroProps {
  titulo: string;
  descricao: string;
}

export function Hero({ titulo, descricao }: HeroProps) {
  const navigate = useNavigate();

  return (
    <div className="dash-hero">
      <span className="dash-badge">Fluxo SEV</span>
      <h1>{titulo}</h1>
      <p>{descricao}</p>
      <div className="dash-hero-actions">
        <Button
          icon={<IconPlus size={16} />}
          onClick={() => navigate('/formulario', { state: { novo_pop: { nome: '', objetivo: '' } } })}
        >
          Novo POP
        </Button>
      </div>
    </div>
  );
}

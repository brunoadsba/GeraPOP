interface HeroProps {
  titulo: string;
  descricao: string;
}

export function Hero({ titulo, descricao }: HeroProps) {
  return (
    <div className="dash-hero">
      <span className="dash-badge">Fluxo SEV</span>
      <h1>{titulo}</h1>
      <p>{descricao}</p>
    </div>
  );
}

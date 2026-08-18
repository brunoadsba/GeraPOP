import { NavLink } from 'react-router-dom';
import { useTheme } from '../../hooks/useTheme';
import { IconHome, IconFileText, IconSun, IconMoon } from '../ui/Icons';

export function Sidebar() {
  const { isDark, toggle } = useTheme();
  const logo = isDark ? '/logo-codeba-branca.png' : '/logo-codeba.png';

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img src={logo} alt="CODEBA" />
      </div>
      <nav className="sidebar-nav" aria-label="Navegação principal">
        <NavLink to="/" end className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
          <span className="nav-link-icon" aria-hidden="true">
            <IconHome size={18} />
          </span>
          <span className="nav-link-label">Início</span>
        </NavLink>
        <NavLink
          to="/formulario"
          className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
        >
          <span className="nav-link-icon" aria-hidden="true">
            <IconFileText size={18} />
          </span>
          <span className="nav-link-label">Formulário</span>
        </NavLink>
      </nav>
      <div className="sidebar-footer">
        <button
          className="theme-toggle"
          onClick={toggle}
          aria-pressed={isDark}
          title="Alternar tema claro/escuro"
        >
          {isDark ? <IconSun size={15} /> : <IconMoon size={15} />}
          {isDark ? 'Tema claro' : 'Tema escuro'}
        </button>
        <span className="sidebar-version">GeraPOP v1.1</span>
      </div>
    </aside>
  );
}

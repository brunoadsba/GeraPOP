import { Route, Routes } from 'react-router-dom';
import { Sidebar } from './components/Layout/Sidebar';
import { ToastContainer } from './components/ui/Toast';
import { FluxoPage } from './pages/FluxoPage';
import { FormPage } from './pages/FormPage';
import { HomePage } from './pages/HomePage';
import { PopsPage } from './pages/PopsPage';
import { PreviewPage } from './pages/PreviewPage';

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="app-main">
        <div className="app-container">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/fluxo" element={<FluxoPage />} />
            <Route path="/pops" element={<PopsPage />} />
            <Route path="/formulario" element={<FormPage />} />
            <Route path="/preview/:type/:ref" element={<PreviewPage />} />
          </Routes>
        </div>
      </main>
      <ToastContainer />
    </div>
  );
}

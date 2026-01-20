import { useNavigate } from "react-router-dom";
import "./Success.css";

export default function Success() {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/");
  }

  return (
    <div className="success-container">
      <div className="success-card">
        <div className="success-emoji">🎉</div>
        
        <div className="success-header">
          <h1>Parabéns!</h1>
          <p className="success-subtitle">Você está logado com sucesso</p>
        </div>

        <p className="success-message">Bem-vindo ao nosso sistema. Você tem acesso total a todos os recursos.</p>
        
        <button onClick={handleLogout} className="success-button">
          Sair da Conta
        </button>

        <div className="footer-text">
          © 2026 Login System. Todos os direitos reservados.
        </div>
      </div>
    </div>
  );
}

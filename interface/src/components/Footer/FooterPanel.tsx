import * as React from 'react';
import './FooterPanel.css';

export const FooterPanel = () => {
  const [isLlmMode, setIsLlmMode] = React.useState<boolean>(() => {
    const saved = localStorage.getItem('llm-mode');
    const initialMode = saved === 'true';
    
    // Отправляем начальное состояние при загрузке
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('mode-change', { 
        detail: { mode: initialMode ? 'llm' : 'standard' }
      }));
    }, 0);
    
    return initialMode;
  });

  const handleToggle = () => {
    const newMode = !isLlmMode;
    setIsLlmMode(newMode);
    
    localStorage.setItem('llm-mode', newMode.toString());
    
    if (newMode) {
      document.body.classList.add('llm-mode-active');
      document.body.classList.remove('standard-mode-active');
    } else {
      document.body.classList.add('standard-mode-active');
      document.body.classList.remove('llm-mode-active');
    }
    
    window.dispatchEvent(new CustomEvent('mode-change', { 
      detail: { mode: newMode ? 'llm' : 'standard' }
    }));
  };

  return (
    <div className="footer-container">
      <div className="mode-toggle-wrapper">
        <div className="toggle-control">
          <button
            className={`llm-toggle-btn ${isLlmMode ? 'llm-active' : ''}`}
            onClick={handleToggle}
            aria-label={isLlmMode ? 'Переключить в стандартный режим' : 'Переключить в LLM режим'}
            title={isLlmMode ? 'LLM режим включен' : 'Стандартный режим'}
          >
            <div className="toggle-slider">
              <div className="toggle-knob">
                <span className="knob-icon">
                  {isLlmMode ? '🤖' : '📊'}
                </span>
              </div>
            </div>
            <span className="toggle-state">
              {isLlmMode ? 'AI Вкл' : 'AI Выкл'}
            </span>
          </button>
        </div>
      </div>
      
      <span className="copyright-text">
        Авторское право © Intelligent Semantic Systems LLC, Все права защищены
      </span>
    </div>
  );
};
import { useYandexAuth } from '@hooks/useYandexAuth';
import React from 'react';

const YandexAuthButton: React.FC = () => {
  const { handleYandexAuth, isLoading, error } = useYandexAuth();

  return (
    <div>
      <button
        onClick={handleYandexAuth}
        disabled={isLoading}
        style={{
          backgroundColor: '#ffcc00',
          color: '#000',
          border: 'none',
          padding: '10px 20px',
          borderRadius: '4px',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          fontSize: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontWeight: 'bold'
        }}
      >
        {isLoading ? (
          'Загрузка...'
        ) : (
          <>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24">
              <text x="2" y="17" fontSize="16" fontFamily="Arial" fill="red">Я</text>
            </svg>
            Войти через Яндекс
          </>
        )}
      </button>
      {error && (
        <div style={{ color: 'red', marginTop: '10px' }}>
          {error}
        </div>
      )}
    </div>
  );
};

export default YandexAuthButton;

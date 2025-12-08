import { useEffect, useState } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { call_create_author_agent } from '@api/sc/agents/googleAuthAgent';
import { generateSessionId, setCookie } from '@hooks/useGoogleAuth';

export const YandexCallback = () => {
  const history = useHistory();
  const location = useLocation();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const handleYandexCode = async (code: string) => {
    try {
      const newSessionId = generateSessionId();
      console.log('Generate auth session:', newSessionId);
      setCookie('auth_session', newSessionId, 7);
      setSessionId(newSessionId);
      
      await call_create_author_agent(
        code, 
        newSessionId, 
        "action_create_yandex_author"
      );

      history.push('/');
      
    } catch (error) {
      console.error('Get error with auth:', error);
      setError('Authentication failed');
      setTimeout(() => {
        history.push('/login');
      }, 3000);
    }
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const code = urlParams.get('code');
    
    if (code) {
      handleYandexCode(code);
      const cleanUrl = window.location.pathname;
      window.history.replaceState({}, '', cleanUrl);
    } else {
      history.replace('/');
    }
  }, [location.search]);

  if (error) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        flexDirection: 'column'
      }}>
        <div style={{ color: 'red', marginBottom: '20px' }}>{error}</div>
        <div>Redirecting to login page...</div>
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh'
    }}>
      <div>Processing Yandex authentication...</div>
    </div>
  );
};

export default YandexCallback;
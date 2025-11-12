import { call_create_google_user_agent } from '@api/sc/agents/googleAuthAgent';
import { useState, useCallback, useEffect } from 'react';

// generate random session
const generateSessionId = (): string => {
  return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
};

const setCookie = (name: string, value: string, days: number = 7) => {
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
};

export const getCookie = (name: string): string | null => {
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
  }
  return null;
};


export const useGoogleAuth = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);


  useEffect(() => {
    // set session if exists
    const existingSession = getCookie('google_session');
    if (existingSession) {
      setSessionId(existingSession);
      console.log('Get existing google session:', existingSession);
    }
  }, []);

  const handleGoogleCode = async (code: string) => {
    try {
      const newSessionId = generateSessionId();
      // create new session
      console.log('Generate google session:', newSessionId);
      setCookie('google_session', newSessionId, 7);
      setSessionId(newSessionId);
      await call_create_google_user_agent(code, newSessionId);

    } catch (error) {
      console.error('Get error with google auth:', error);
    }
  };

  useEffect(() => {
    // try to find query param "code" in url
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (code) {      
      // generate session and call create user agent
      handleGoogleCode(code);
      window.history.replaceState({}, '', '/');
    }
  }, []);

  

  const handleGoogleAuth = useCallback(() => {
    setIsLoading(true);
    setError(null);
    // use oauth2.0 technology
    // send request to google(get code param)
    const clientId = process.env.GOOGLE_CLIENT_ID;
    const redirectUri = 'http://localhost:3033';
    const scopes = ['email', 'profile', 'https://www.googleapis.com/auth/calendar'];
    const responseType = 'code';
    
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${clientId}` +
      `&redirect_uri=${encodeURIComponent(redirectUri)}` +
      `&response_type=${responseType}` +
      `&scope=${encodeURIComponent(scopes.join(' '))}` +
      `&access_type=offline` +
      `&prompt=consent`;

    window.location.href = authUrl;
  }, []);

  return {
    handleGoogleAuth,
    isLoading,
    error,
  };
};
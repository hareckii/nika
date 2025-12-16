import { useState, useCallback, useEffect } from 'react';

export const useYandexAuth = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleYandexAuth = useCallback(() => {
    setIsLoading(true);
    setError(null);

    const clientId = process.env.YANDEX_CLIENT_ID;
    const redirectUri = 'http://localhost:3033/auth/yandex/callback';

    const scopes = [
      'login:email',
      'login:info',
      'cloud_api:disk.read',
      'cloud_api:disk.write',
      'cloud_api:disk.app_folder',
      'cloud_api:disk.info',
      'login:avatar',
    ];

    const responseType = 'code';

    const authUrl = `https://oauth.yandex.ru/authorize?` +
      `client_id=${clientId}` +
      `&redirect_uri=${encodeURIComponent(redirectUri)}` +
      `&response_type=${responseType}` +
      `&force_confirm=yes` +
      `&scope=${encodeURIComponent(scopes.join(' '))}`;

    window.location.href = authUrl;
  }, []);

  return {
    handleYandexAuth,
    isLoading,
    error,
  };
};

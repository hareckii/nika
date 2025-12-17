import { useCallback, useEffect, useState, Fragment } from 'react';
import { Wrapper, ChatWrapper, SCgViewerWrapper } from "./styled";
import { Message } from '@components/Chat/Message';
import { Chat } from '@components/Chat';
import { Date } from '@components/Chat/Date';
import { ScAddr } from 'ts-sc-client';
import { resolveUserAgent } from '@agents/resolveUserAgent';
import { useChat } from '@hooks/useChat';
import { SC_WEB_URL } from "@constants";

// Хук для получения состояния режима
const useLlmMode = () => {
  const [isLlmMode, setIsLlmMode] = useState<boolean>(() => {
    return localStorage.getItem('llm-mode') === 'true';
  });

  useEffect(() => {
    const handleModeChange = (event: CustomEvent) => {
      setIsLlmMode(event.detail.mode === 'llm');
    };

    window.addEventListener('mode-change', handleModeChange as EventListener);
    
    // Также проверяем изменения в localStorage (если из другой вкладки)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'llm-mode') {
        setIsLlmMode(e.newValue === 'true');
      }
    };

    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('mode-change', handleModeChange as EventListener);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  return isLlmMode;
};

export const Demo = () => {
    const [user, setUser] = useState<ScAddr | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const isLlmMode = useLlmMode(); // Используем хук

    const { 
        initChat, 
        sendMessage, 
        isAgentAnswer, 
        onFetching, 
        messages, 
        chatRef 
    } = useChat(user, isLlmMode);
    
    const onSend = useCallback(
        async (text: string) => {
            if (!user){
                const new_user = await resolveUserAgent();
                if (new_user)
                setUser(new_user)
            }
            if (!user) return;
            
            // Используем режим при отправке сообщения
            if (isLlmMode) {
                console.log('Отправка в LLM режиме');
                // Здесь может быть специфичная логика для LLM режима
            } else {
                console.log('Отправка в стандартном режиме');
            }
            
            await sendMessage(user, text);
            await initChat([user]);
        },
        [user, sendMessage, isLlmMode], // Добавляем isLlmMode в зависимости
    );

    const url = SC_WEB_URL + '/?sys_id=answer_structure&scg_structure_view_only=true';

    useEffect(() => {
        let isMounted = true;
        
        const initialize = async () => {
            setIsLoading(true);
            try {
                const user = await resolveUserAgent();
                
                if (!isMounted) return;
                
                if (user) {
                    setUser(user);
                    
                    await initChat([user]);
                    
                } else {
                    console.warn('User not resolved');
                }

            } catch (error) {
                console.error('Initialization error:', error);
            } finally {
                if (isMounted) {
                    setIsLoading(false);
                }
            }
        };
        
        initialize();
        
        return () => { isMounted = false; };
    }, [initChat, isLlmMode]);

    return (
        <Wrapper>
            {isLlmMode && (
                <div style={{
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    background: 'linear-gradient(to right, #8b6358, #9A7469)',
                    color: 'white',
                    padding: '5px 10px',
                    borderRadius: '15px',
                    fontSize: '12px',
                    zIndex: 1000
                }}>
                    🤖 AI Режим
                </div>
            )}
            
            <ChatWrapper>
                <Chat
                    ref={chatRef}
                    isLoading={isLoading}
                    onSend={onSend}
                    onFetching={onFetching}
                    isAgentAnswer={isAgentAnswer}
                >
                    {messages.map((item, ind) => {
                        const prevItem = messages[ind - 1];
                        const showDate = item.date !== prevItem?.date;
                        return (
                            <Fragment key={item.id}>
                                {showDate && <Date date={item.date} />}
                                <Message
                                    isLeft={!!user && !item.author.equal(user)}
                                    time={item.time}
                                    isLoading={item.isLoading}
                                >
                                    {typeof item.text === 'string' ? (
                                        <div dangerouslySetInnerHTML={{__html: item.text}} />
                                    ) : (
                                        <div>{item.text}</div>
                                    )}
                                </Message>
                            </Fragment>
                        );
                    })}
                </Chat>
            </ChatWrapper>
            <SCgViewerWrapper>
                {/* Можно менять URL в зависимости от режима */}
                <iframe 
                    src={url + (isLlmMode ? '&mode=llm' : '')} 
                    style={{
                        width: '100%', 
                        height: '100%', 
                        border: 0, 
                        borderRadius: '15px',
                        // Меняем стили в зависимости от режима
                        filter: isLlmMode ? 'sepia(0.3)' : 'none'
                    }}
                />
            </SCgViewerWrapper>
        </Wrapper>
    );
};
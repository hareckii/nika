import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { createGlobalStyle } from 'styled-components';

import { store } from '@store';

import { App } from './App';

const GlobalStyle = createGlobalStyle`
  body {
    margin: 0;
    display: flex;
    font-family: 'Roboto', sans-serif;
    /* For firefox full height */
    height: 100%;
  }
  #content {
    flex-grow: 1;
    display: flex;
  }
  * {
    box-sizing: border-box;
  }
`;

function deleteAllCookies() {
    const cookies = document.cookie.split(";");

    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
    }
}

const isCallbackPage = window.location.pathname.includes('/auth/yandex/callback');

if (!isCallbackPage) {
    console.log("Cookies and localStorage cleaning initiated");
    deleteAllCookies();
    localStorage.clear();
    sessionStorage.clear();
} else {
    console.log("Not deleting cookies during auth callback");
}

ReactDOM.render(
    <Provider store={store}>
        <BrowserRouter>
            <GlobalStyle />
            <App />
        </BrowserRouter>
    </Provider>,
    document.getElementById('content'),
);

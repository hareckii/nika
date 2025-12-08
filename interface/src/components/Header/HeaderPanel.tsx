import { routes } from '@constants';
import { NavLink } from 'react-router-dom';
import YandexAuthButton from './YandexAuthButton';

export const HeaderPanel = () => {
    return (
        <div className="header">
            <h1 className="header-logo-text">NIKA</h1>
            <YandexAuthButton/>
            <div className="nav-container">
                <ul className="nav">
                    <li>
                        <NavLink exact to={routes.MAIN}>Главная</NavLink>
                    </li>
                    <li>
                        <NavLink to={routes.ABOUT}>О нас</NavLink>
                    </li>
                </ul>
            </div>
        </div>
    );
}

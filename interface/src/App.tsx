import { lazy, useEffect, useState} from "react";
import { Route, Redirect } from "react-router-dom";
import { loadingComponent } from '@components/LoadingComponent';
import { routes } from '@constants';

import 'antd/dist/antd.css';
import './assets/main.css';

import { Layout } from 'antd';

import { HeaderPanel } from "@components/Header";
import { FooterPanel } from "@components/Footer";
import { fetchColorValue } from "@api/sc/agents/fetchColorValueAgent";

const { Header, Content, Footer } = Layout;

const Demo = loadingComponent(lazy(() => import('@pages/Demo')));
const About = loadingComponent(lazy(() => import('@pages/About')));

const DemoRoutes = () => (
    <>
        <Route exact path={routes.MAIN} component={Demo} />
    </>
);

const AboutRoutes = () => (
    <>
        <Route path={routes.ABOUT}>
            <About />
        </Route>
    </>
);

export const App = () => {
    const [headerBgColor, setHeaderBgColor] = useState<string>('#39494C');
    const [mainBgColor, setMainBgColor] = useState<string>('#fcfafa');
    const [footerBgColor, setFooterBgColor] = useState<string>('#39494C');
    
    const funcChange = [setHeaderBgColor, setMainBgColor, setFooterBgColor]

    useEffect(() => {
        fetchColorValue(funcChange);
    }, []);

    const headerStyles = {
        background: headerBgColor,
    };
    
    const mainStyles = {
        background: mainBgColor,
    };

    const footerStyles = {
        background: footerBgColor,
    };

    return (
        <Layout>
            <Header style={headerStyles}>
                <HeaderPanel />
            </Header>
            <Content style={mainStyles}>
                <DemoRoutes />
                <AboutRoutes />
            </Content>
            <Footer style={footerStyles}>
                <FooterPanel />
            </Footer>
        </Layout>
    );
};

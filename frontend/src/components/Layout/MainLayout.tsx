import React, { useState } from 'react';
import { Layout, Menu, Button } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  ShoppingCartOutlined,
  ShopOutlined,
  InboxOutlined,
  BarChartOutlined,
  SettingOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../auth/AuthContext';

const { Sider, Content, Header } = Layout;

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  
  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
    { key: '/orders', icon: <ShoppingCartOutlined />, label: 'Заказы' },
    { key: '/products', icon: <ShopOutlined />, label: 'Товары' },
    { key: '/warehouse', icon: <InboxOutlined />, label: 'Склад' },
    { key: '/finance', icon: <BarChartOutlined />, label: 'Финансы' },
    { key: '/settings', icon: <SettingOutlined />, label: 'Настройки' },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div style={{ 
          height: 32, 
          margin: 16, 
          background: 'rgba(255, 255, 255, 0.3)',
          borderRadius: 4,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontWeight: 'bold'
        }}>
          {collapsed ? 'F' : 'FMS'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ 
          background: '#fff', 
          padding: '0 16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ margin: 0 }}>FMS - Fulfillment Management System</h2>
          <Button 
            type="primary" 
            danger 
            icon={<LogoutOutlined />}
            onClick={handleLogout}
          >
            Выход
          </Button>
        </Header>
        <Content style={{ margin: '16px', padding: 24, background: '#fff', borderRadius: 8 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;

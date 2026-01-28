import React from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { useAuth } from '../auth/AuthContext';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values: { email: string; password: string }) => {
    try {
      await login(values.email, values.password);
      message.success('Вход выполнен успешно');
      navigate('/');
    } catch (error: any) {
      message.error(error?.response?.data?.detail || 'Неверные учетные данные');
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card 
        title={<div style={{ textAlign: 'center', fontSize: 24, fontWeight: 'bold' }}>FMS Login</div>} 
        style={{ width: 400 }}
      >
        <Form onFinish={onFinish} layout="vertical" size="large">
          <Form.Item 
            name="email" 
            label="Email" 
            rules={[
              { required: true, message: 'Пожалуйста, введите email' },
              { type: 'email', message: 'Введите корректный email' }
            ]}
          >
            <Input placeholder="email@example.com" />
          </Form.Item>
          <Form.Item 
            name="password" 
            label="Пароль" 
            rules={[{ required: true, message: 'Пожалуйста, введите пароль' }]}
          >
            <Input.Password placeholder="Введите пароль" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              Войти
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Login;

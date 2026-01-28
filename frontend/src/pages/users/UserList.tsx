import React from 'react';
import { Table, Button, Space, Tag, Card } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const mockUsers = [
  { 
    id: '1', 
    email: 'admin@fms.local', 
    full_name: 'Администратор Системы',
    phone: '+79991234567',
    role: 'admin',
    is_active: true,
    tenant: 'ООО "Тест"'
  },
  { 
    id: '2', 
    email: 'manager@example.com', 
    full_name: 'Иванов Иван Иванович',
    phone: '+79997654321',
    role: 'manager',
    is_active: true,
    tenant: 'ООО "Тест"'
  },
  { 
    id: '3', 
    email: 'warehouse@example.com', 
    full_name: 'Петров Петр Петрович',
    phone: '+79991111111',
    role: 'warehouse',
    is_active: true,
    tenant: 'ИП Иванов'
  },
  { 
    id: '4', 
    email: 'inactive@example.com', 
    full_name: 'Сидоров Сидор Сидорович',
    phone: '+79992222222',
    role: 'manager',
    is_active: false,
    tenant: 'ООО "Тест"'
  },
];

const roleColors: Record<string, string> = {
  admin: 'red',
  manager: 'blue',
  warehouse: 'green',
  picker: 'orange',
};

const roleNames: Record<string, string> = {
  admin: 'Администратор',
  manager: 'Менеджер',
  warehouse: 'Склад',
  picker: 'Сборщик',
};

const UserList: React.FC = () => {
  const navigate = useNavigate();

  const columns = [
    { 
      title: 'Email', 
      dataIndex: 'email', 
      key: 'email',
      sorter: (a: any, b: any) => a.email.localeCompare(b.email),
    },
    { 
      title: 'ФИО', 
      dataIndex: 'full_name', 
      key: 'full_name',
      sorter: (a: any, b: any) => a.full_name.localeCompare(b.full_name),
    },
    { 
      title: 'Телефон', 
      dataIndex: 'phone', 
      key: 'phone',
    },
    { 
      title: 'Роль', 
      dataIndex: 'role', 
      key: 'role',
      render: (role: string) => (
        <Tag color={roleColors[role] || 'default'}>
          {roleNames[role] || role}
        </Tag>
      ),
    },
    { 
      title: 'Арендатор', 
      dataIndex: 'tenant', 
      key: 'tenant',
    },
    { 
      title: 'Статус', 
      dataIndex: 'is_active', 
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Активен' : 'Неактивен'}
        </Tag>
      ),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button onClick={() => navigate(`/users/${record.id}`)}>Открыть</Button>
          <Button onClick={() => console.log('Edit', record.id)}>Редактировать</Button>
        </Space>
      ),
    },
  ];

  return (
    <Card 
      title="Пользователи" 
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/users/new')}>Новый пользователь</Button>}
    >
      <Table 
        dataSource={mockUsers} 
        columns={columns} 
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default UserList;

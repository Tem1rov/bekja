import React from 'react';
import { Table, Button, Space, Tag, Card } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const mockTenants = [
  { 
    id: '1', 
    name: 'ООО "Тест"', 
    inn: '1234567890', 
    email: 'test@example.com',
    phone: '+79991234567',
    legal_address: 'г. Москва, ул. Тестовая, д. 1',
    storage_rate: 10.50,
    processing_rate: 5.25,
    is_active: true
  },
  { 
    id: '2', 
    name: 'ИП Иванов', 
    inn: '0987654321', 
    email: 'ivanov@example.com',
    phone: '+79997654321',
    legal_address: 'г. СПб, пр. Невский, д. 10',
    storage_rate: 12.00,
    processing_rate: 6.00,
    is_active: true
  },
  { 
    id: '3', 
    name: 'ООО "Неактивный"', 
    inn: '1111111111', 
    email: 'inactive@example.com',
    phone: '+79991111111',
    legal_address: 'г. Казань, ул. Примерная, д. 5',
    storage_rate: 8.00,
    processing_rate: 4.00,
    is_active: false
  },
];

const TenantList: React.FC = () => {
  const navigate = useNavigate();

  const columns = [
    { 
      title: 'Название', 
      dataIndex: 'name', 
      key: 'name',
      sorter: (a: any, b: any) => a.name.localeCompare(b.name),
    },
    { 
      title: 'ИНН', 
      dataIndex: 'inn', 
      key: 'inn',
    },
    { 
      title: 'Email', 
      dataIndex: 'email', 
      key: 'email',
    },
    { 
      title: 'Телефон', 
      dataIndex: 'phone', 
      key: 'phone',
    },
    { 
      title: 'Ставка хранения', 
      dataIndex: 'storage_rate', 
      key: 'storage_rate',
      render: (rate: number) => `${rate.toFixed(2)} ₽/м³/день`,
      sorter: (a: any, b: any) => a.storage_rate - b.storage_rate,
    },
    { 
      title: 'Ставка обработки', 
      dataIndex: 'processing_rate', 
      key: 'processing_rate',
      render: (rate: number) => `${rate.toFixed(2)} ₽/заказ`,
      sorter: (a: any, b: any) => a.processing_rate - b.processing_rate,
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
          <Button onClick={() => navigate(`/tenants/${record.id}`)}>Открыть</Button>
          <Button onClick={() => console.log('Edit', record.id)}>Редактировать</Button>
        </Space>
      ),
    },
  ];

  return (
    <Card 
      title="Арендаторы" 
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/tenants/new')}>Новый арендатор</Button>}
    >
      <Table 
        dataSource={mockTenants} 
        columns={columns} 
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default TenantList;

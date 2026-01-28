import React from 'react';
import { Table, Button, Space, Tag, Card } from 'antd';
import { PlusOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const mockIntegrations = [
  { 
    id: '1', 
    name: 'Wildberries', 
    type: 'marketplace',
    status: 'active',
    last_sync: '2024-01-15 10:30:00',
    orders_synced: 150,
    products_synced: 500,
    tenant: 'ООО "Тест"'
  },
  { 
    id: '2', 
    name: 'Ozon', 
    type: 'marketplace',
    status: 'active',
    last_sync: '2024-01-15 09:15:00',
    orders_synced: 200,
    products_synced: 300,
    tenant: 'ООО "Тест"'
  },
  { 
    id: '3', 
    name: 'Яндекс.Маркет', 
    type: 'marketplace',
    status: 'inactive',
    last_sync: '2024-01-10 14:20:00',
    orders_synced: 50,
    products_synced: 100,
    tenant: 'ИП Иванов'
  },
  { 
    id: '4', 
    name: '1C: Управление торговлей', 
    type: 'erp',
    status: 'active',
    last_sync: '2024-01-15 11:00:00',
    orders_synced: 0,
    products_synced: 1000,
    tenant: 'ООО "Тест"'
  },
];

const typeColors: Record<string, string> = {
  marketplace: 'blue',
  erp: 'green',
  crm: 'purple',
  shipping: 'orange',
};

const typeNames: Record<string, string> = {
  marketplace: 'Маркетплейс',
  erp: 'ERP система',
  crm: 'CRM система',
  shipping: 'Доставка',
};

const IntegrationList: React.FC = () => {
  const navigate = useNavigate();

  const columns = [
    { 
      title: 'Название', 
      dataIndex: 'name', 
      key: 'name',
      sorter: (a: any, b: any) => a.name.localeCompare(b.name),
    },
    { 
      title: 'Тип', 
      dataIndex: 'type', 
      key: 'type',
      render: (type: string) => (
        <Tag color={typeColors[type] || 'default'}>
          {typeNames[type] || type}
        </Tag>
      ),
    },
    { 
      title: 'Статус', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => (
        <Tag 
          color={status === 'active' ? 'green' : 'red'}
          icon={status === 'active' ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
        >
          {status === 'active' ? 'Активна' : 'Неактивна'}
        </Tag>
      ),
    },
    { 
      title: 'Последняя синхронизация', 
      dataIndex: 'last_sync', 
      key: 'last_sync',
    },
    { 
      title: 'Заказов синхронизировано', 
      dataIndex: 'orders_synced', 
      key: 'orders_synced',
      sorter: (a: any, b: any) => a.orders_synced - b.orders_synced,
    },
    { 
      title: 'Товаров синхронизировано', 
      dataIndex: 'products_synced', 
      key: 'products_synced',
      sorter: (a: any, b: any) => a.products_synced - b.products_synced,
    },
    { 
      title: 'Арендатор', 
      dataIndex: 'tenant', 
      key: 'tenant',
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button onClick={() => navigate(`/integrations/${record.id}`)}>Настроить</Button>
          <Button onClick={() => console.log('Sync', record.id)}>Синхронизировать</Button>
        </Space>
      ),
    },
  ];

  return (
    <Card 
      title="Интеграции" 
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/integrations/new')}>Новая интеграция</Button>}
    >
      <Table 
        dataSource={mockIntegrations} 
        columns={columns} 
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default IntegrationList;

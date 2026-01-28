import React from 'react';
import { Table, Button, Space, Tag, Card } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const mockTariffs = [
  { 
    id: '1', 
    name: 'Базовый тариф', 
    tenant: 'ООО "Тест"',
    storage_rate: 10.50,
    processing_rate: 5.25,
    packaging_rate: 2.00,
    is_active: true,
    valid_from: '2024-01-01',
    valid_to: '2024-12-31'
  },
  { 
    id: '2', 
    name: 'Премиум тариф', 
    tenant: 'ИП Иванов',
    storage_rate: 12.00,
    processing_rate: 6.00,
    packaging_rate: 2.50,
    is_active: true,
    valid_from: '2024-01-01',
    valid_to: '2024-12-31'
  },
  { 
    id: '3', 
    name: 'Эконом тариф', 
    tenant: 'ООО "Тест"',
    storage_rate: 8.00,
    processing_rate: 4.00,
    packaging_rate: 1.50,
    is_active: false,
    valid_from: '2023-01-01',
    valid_to: '2023-12-31'
  },
];

const TariffList: React.FC = () => {
  const navigate = useNavigate();

  const columns = [
    { 
      title: 'Название', 
      dataIndex: 'name', 
      key: 'name',
      sorter: (a: any, b: any) => a.name.localeCompare(b.name),
    },
    { 
      title: 'Арендатор', 
      dataIndex: 'tenant', 
      key: 'tenant',
    },
    { 
      title: 'Хранение', 
      dataIndex: 'storage_rate', 
      key: 'storage_rate',
      render: (rate: number) => `${rate.toFixed(2)} ₽/м³/день`,
      sorter: (a: any, b: any) => a.storage_rate - b.storage_rate,
    },
    { 
      title: 'Обработка', 
      dataIndex: 'processing_rate', 
      key: 'processing_rate',
      render: (rate: number) => `${rate.toFixed(2)} ₽/заказ`,
      sorter: (a: any, b: any) => a.processing_rate - b.processing_rate,
    },
    { 
      title: 'Упаковка', 
      dataIndex: 'packaging_rate', 
      key: 'packaging_rate',
      render: (rate: number) => `${rate.toFixed(2)} ₽/заказ`,
    },
    { 
      title: 'Период действия', 
      key: 'period',
      render: (_: any, record: any) => `${record.valid_from} - ${record.valid_to}`,
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
          <Button onClick={() => navigate(`/finance/tariffs/${record.id}`)}>Открыть</Button>
          <Button onClick={() => console.log('Edit', record.id)}>Редактировать</Button>
        </Space>
      ),
    },
  ];

  return (
    <Card 
      title="Тарифы" 
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/finance/tariffs/new')}>Новый тариф</Button>}
    >
      <Table 
        dataSource={mockTariffs} 
        columns={columns} 
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default TariffList;

import React from 'react';
import { Table, Button, Space, Tag, Card } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const mockWarehouses = [
  { 
    id: '1', 
    name: 'Склад А', 
    address: 'г. Москва, ул. Складская, д. 1',
    total_cells: 1000,
    occupied_cells: 750,
    free_cells: 250,
    utilization: 75,
    tenant: 'ООО "Тест"'
  },
  { 
    id: '2', 
    name: 'Склад Б', 
    address: 'г. СПб, пр. Складской, д. 10',
    total_cells: 500,
    occupied_cells: 300,
    free_cells: 200,
    utilization: 60,
    tenant: 'ИП Иванов'
  },
  { 
    id: '3', 
    name: 'Склад В', 
    address: 'г. Казань, ул. Складная, д. 5',
    total_cells: 2000,
    occupied_cells: 1800,
    free_cells: 200,
    utilization: 90,
    tenant: 'ООО "Тест"'
  },
];

const WarehouseList: React.FC = () => {
  const navigate = useNavigate();

  const columns = [
    { 
      title: 'Название', 
      dataIndex: 'name', 
      key: 'name',
      sorter: (a: any, b: any) => a.name.localeCompare(b.name),
    },
    { 
      title: 'Адрес', 
      dataIndex: 'address', 
      key: 'address',
    },
    { 
      title: 'Всего ячеек', 
      dataIndex: 'total_cells', 
      key: 'total_cells',
      sorter: (a: any, b: any) => a.total_cells - b.total_cells,
    },
    { 
      title: 'Занято', 
      dataIndex: 'occupied_cells', 
      key: 'occupied_cells',
      sorter: (a: any, b: any) => a.occupied_cells - b.occupied_cells,
    },
    { 
      title: 'Свободно', 
      dataIndex: 'free_cells', 
      key: 'free_cells',
      sorter: (a: any, b: any) => a.free_cells - b.free_cells,
    },
    { 
      title: 'Загрузка', 
      dataIndex: 'utilization', 
      key: 'utilization',
      render: (utilization: number) => (
        <Tag color={utilization > 80 ? 'red' : utilization > 60 ? 'orange' : 'green'}>
          {utilization}%
        </Tag>
      ),
      sorter: (a: any, b: any) => a.utilization - b.utilization,
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
          <Button onClick={() => navigate(`/warehouse/${record.id}`)}>Открыть</Button>
          <Button onClick={() => navigate(`/warehouse/${record.id}/inventory`)}>Инвентаризация</Button>
        </Space>
      ),
    },
  ];

  return (
    <Card 
      title="Склады" 
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/warehouse/new')}>Новый склад</Button>}
    >
      <Table 
        dataSource={mockWarehouses} 
        columns={columns} 
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default WarehouseList;

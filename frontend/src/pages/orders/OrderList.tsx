import React from 'react';
import { Table, Button, Space, Tag, Card } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const mockOrders = [
  { id: '1', order_number: 'ORD-001', status: 'new', total_amount: 5000, customer_name: 'Иванов И.И.', created_at: '2024-01-15 10:00' },
  { id: '2', order_number: 'ORD-002', status: 'picking', total_amount: 12000, customer_name: 'Петров П.П.', created_at: '2024-01-14 15:30' },
  { id: '3', order_number: 'ORD-003', status: 'shipped', total_amount: 8500, customer_name: 'Сидоров С.С.', created_at: '2024-01-13 09:20' },
  { id: '4', order_number: 'ORD-004', status: 'confirmed', total_amount: 3200, customer_name: 'Козлов К.К.', created_at: '2024-01-12 14:15' },
  { id: '5', order_number: 'ORD-005', status: 'delivered', total_amount: 15000, customer_name: 'Новikov Н.Н.', created_at: '2024-01-11 11:45' },
];

const statusColors: Record<string, string> = {
  new: 'blue',
  confirmed: 'cyan',
  picking: 'orange',
  packed: 'purple',
  shipped: 'green',
  delivered: 'green',
  cancelled: 'red',
};

const statusNames: Record<string, string> = {
  new: 'Новый',
  confirmed: 'Подтвержден',
  picking: 'Сборка',
  packed: 'Упакован',
  shipped: 'Отправлен',
  delivered: 'Доставлен',
  cancelled: 'Отменен',
};

const OrderList: React.FC = () => {
  const navigate = useNavigate();

  const columns = [
    { 
      title: 'Номер', 
      dataIndex: 'order_number', 
      key: 'order_number',
      sorter: (a: any, b: any) => a.order_number.localeCompare(b.order_number),
    },
    { 
      title: 'Клиент', 
      dataIndex: 'customer_name', 
      key: 'customer_name',
      sorter: (a: any, b: any) => a.customer_name.localeCompare(b.customer_name),
    },
    { 
      title: 'Статус', 
      dataIndex: 'status', 
      key: 'status',
      render: (status: string) => <Tag color={statusColors[status]}>{statusNames[status] || status}</Tag>
    },
    { 
      title: 'Сумма', 
      dataIndex: 'total_amount', 
      key: 'total_amount',
      render: (amount: number) => `${amount.toLocaleString()} ₽`,
      sorter: (a: any, b: any) => a.total_amount - b.total_amount,
    },
    { 
      title: 'Дата создания', 
      dataIndex: 'created_at', 
      key: 'created_at',
      sorter: (a: any, b: any) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button onClick={() => navigate(`/orders/${record.id}`)}>Открыть</Button>
        </Space>
      ),
    },
  ];

  return (
    <Card 
      title="Заказы" 
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/orders/new')}>Новый заказ</Button>}
    >
      <Table dataSource={mockOrders} columns={columns} rowKey="id" pagination={{ pageSize: 10 }} />
    </Card>
  );
};

export default OrderList;

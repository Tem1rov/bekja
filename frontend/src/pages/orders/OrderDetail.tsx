import React from 'react';
import { Card, Descriptions, Tag, Button, Space, Table } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeftOutlined } from '@ant-design/icons';

const mockOrder = {
  id: '1',
  order_number: 'ORD-001',
  status: 'picking',
  customer_name: 'Иванов Иван Иванович',
  customer_phone: '+79991234567',
  customer_email: 'ivanov@example.com',
  delivery_address: 'г. Москва, ул. Тестовая, д. 1, кв. 10',
  delivery_method: 'courier',
  total_amount: 5000,
  cost_of_goods: 3000,
  marketplace_fee: 500,
  shipping_cost: 500,
  storage_cost: 100,
  processing_cost: 200,
  packaging_cost: 100,
  other_costs: 100,
  margin: 500,
  created_at: '2024-01-15 10:00:00',
  confirmed_at: '2024-01-15 10:15:00',
  items: [
    { id: '1', product_sku: 'SKU-001', product_name: 'Товар 1', quantity: 2, price: 2000, cost_price: 1200 },
    { id: '2', product_sku: 'SKU-002', product_name: 'Товар 2', quantity: 1, price: 1000, cost_price: 600 },
  ],
};

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

const OrderDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const itemColumns = [
    { title: 'SKU', dataIndex: 'product_sku', key: 'product_sku' },
    { title: 'Товар', dataIndex: 'product_name', key: 'product_name' },
    { title: 'Количество', dataIndex: 'quantity', key: 'quantity' },
    { 
      title: 'Цена', 
      dataIndex: 'price', 
      key: 'price',
      render: (price: number) => `${price.toLocaleString()} ₽`
    },
    { 
      title: 'Себестоимость', 
      dataIndex: 'cost_price', 
      key: 'cost_price',
      render: (price: number) => `${price.toLocaleString()} ₽`
    },
    { 
      title: 'Сумма', 
      key: 'total',
      render: (_: any, record: any) => `${(record.price * record.quantity).toLocaleString()} ₽`
    },
  ];

  return (
    <div>
      <Card
        title={
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/orders')}>
              Назад
            </Button>
            <span>Заказ {mockOrder.order_number}</span>
          </Space>
        }
        extra={
          <Tag color={statusColors[mockOrder.status]}>
            {statusNames[mockOrder.status] || mockOrder.status}
          </Tag>
        }
      >
        <Descriptions title="Информация о заказе" bordered column={2}>
          <Descriptions.Item label="Номер заказа">{mockOrder.order_number}</Descriptions.Item>
          <Descriptions.Item label="Статус">
            <Tag color={statusColors[mockOrder.status]}>
              {statusNames[mockOrder.status] || mockOrder.status}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Клиент">{mockOrder.customer_name}</Descriptions.Item>
          <Descriptions.Item label="Телефон">{mockOrder.customer_phone}</Descriptions.Item>
          <Descriptions.Item label="Email">{mockOrder.customer_email}</Descriptions.Item>
          <Descriptions.Item label="Способ доставки">{mockOrder.delivery_method}</Descriptions.Item>
          <Descriptions.Item label="Адрес доставки" span={2}>
            {mockOrder.delivery_address}
          </Descriptions.Item>
          <Descriptions.Item label="Дата создания">{mockOrder.created_at}</Descriptions.Item>
          <Descriptions.Item label="Дата подтверждения">{mockOrder.confirmed_at || '-'}</Descriptions.Item>
        </Descriptions>

        <Card title="Товары" style={{ marginTop: 16 }}>
          <Table
            dataSource={mockOrder.items}
            columns={itemColumns}
            rowKey="id"
            pagination={false}
          />
        </Card>

        <Card title="Финансы" style={{ marginTop: 16 }}>
          <Descriptions bordered column={2}>
            <Descriptions.Item label="Сумма заказа">{mockOrder.total_amount.toLocaleString()} ₽</Descriptions.Item>
            <Descriptions.Item label="Себестоимость товаров">{mockOrder.cost_of_goods.toLocaleString()} ₽</Descriptions.Item>
            <Descriptions.Item label="Комиссия маркетплейса">{mockOrder.marketplace_fee.toLocaleString()} ₽</Descriptions.Item>
            <Descriptions.Item label="Доставка">{mockOrder.shipping_cost.toLocaleString()} ₽</Descriptions.Item>
            <Descriptions.Item label="Хранение">{mockOrder.storage_cost.toLocaleString()} ₽</Descriptions.Item>
            <Descriptions.Item label="Обработка">{mockOrder.processing_cost.toLocaleString()} ₽</Descriptions.Item>
            <Descriptions.Item label="Упаковка">{mockOrder.packaging_cost.toLocaleString()} ₽</Descriptions.Item>
            <Descriptions.Item label="Прочие расходы">{mockOrder.other_costs.toLocaleString()} ₽</Descriptions.Item>
            <Descriptions.Item label="Маржа" span={2}>
              <strong>{mockOrder.margin.toLocaleString()} ₽</strong>
            </Descriptions.Item>
          </Descriptions>
        </Card>
      </Card>
    </div>
  );
};

export default OrderDetail;

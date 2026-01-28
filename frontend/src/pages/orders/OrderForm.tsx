import React from 'react';
import { Form, Input, Select, Button, Card, Space, Table } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

const OrderForm: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [items, setItems] = useState<any[]>([]);

  const onFinish = (values: any) => {
    console.log('Order values:', values, items);
    // TODO: Отправка данных на сервер
    navigate('/orders');
  };

  const addItem = () => {
    setItems([...items, { id: Date.now(), product_sku: '', quantity: 1, price: 0 }]);
  };

  const removeItem = (id: number) => {
    setItems(items.filter(item => item.id !== id));
  };

  const updateItem = (id: number, field: string, value: any) => {
    setItems(items.map(item => item.id === id ? { ...item, [field]: value } : item));
  };

  const itemColumns = [
    {
      title: 'SKU товара',
      dataIndex: 'product_sku',
      key: 'product_sku',
      render: (_: any, record: any) => (
        <Input
          value={record.product_sku}
          onChange={(e) => updateItem(record.id, 'product_sku', e.target.value)}
          placeholder="SKU-001"
        />
      ),
    },
    {
      title: 'Количество',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (_: any, record: any) => (
        <Input
          type="number"
          value={record.quantity}
          onChange={(e) => updateItem(record.id, 'quantity', parseInt(e.target.value) || 1)}
          min={1}
          style={{ width: '100%' }}
        />
      ),
    },
    {
      title: 'Цена',
      dataIndex: 'price',
      key: 'price',
      render: (_: any, record: any) => (
        <Input
          type="number"
          value={record.price}
          onChange={(e) => updateItem(record.id, 'price', parseFloat(e.target.value) || 0)}
          min={0}
          style={{ width: '100%' }}
        />
      ),
    },
    {
      title: 'Сумма',
      key: 'total',
      render: (_: any, record: any) => `${(record.quantity * record.price).toLocaleString()} ₽`,
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: any) => (
        <Button
          icon={<DeleteOutlined />}
          danger
          onClick={() => removeItem(record.id)}
        />
      ),
    },
  ];

  return (
    <Card title="Новый заказ">
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
      >
        <Form.Item
          name="customer_name"
          label="ФИО клиента"
          rules={[{ required: true, message: 'Введите ФИО клиента' }]}
        >
          <Input placeholder="Иванов Иван Иванович" />
        </Form.Item>

        <Form.Item
          name="customer_phone"
          label="Телефон"
          rules={[{ required: true, message: 'Введите телефон' }]}
        >
          <Input placeholder="+79991234567" />
        </Form.Item>

        <Form.Item
          name="customer_email"
          label="Email"
        >
          <Input type="email" placeholder="customer@example.com" />
        </Form.Item>

        <Form.Item
          name="delivery_address"
          label="Адрес доставки"
          rules={[{ required: true, message: 'Введите адрес доставки' }]}
        >
          <Input.TextArea rows={2} placeholder="г. Москва, ул. Тестовая, д. 1, кв. 10" />
        </Form.Item>

        <Form.Item
          name="delivery_method"
          label="Способ доставки"
          rules={[{ required: true, message: 'Выберите способ доставки' }]}
        >
          <Select placeholder="Выберите способ доставки">
            <Select.Option value="courier">Курьер</Select.Option>
            <Select.Option value="pickup">Самовывоз</Select.Option>
            <Select.Option value="post">Почта</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item label="Товары">
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={addItem}
            style={{ width: '100%', marginBottom: 16 }}
          >
            Добавить товар
          </Button>
          <Table
            dataSource={items}
            columns={itemColumns}
            rowKey="id"
            pagination={false}
            size="small"
          />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" disabled={items.length === 0}>
              Создать заказ
            </Button>
            <Button onClick={() => navigate('/orders')}>
              Отмена
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default OrderForm;

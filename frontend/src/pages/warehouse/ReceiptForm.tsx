import React from 'react';
import { Form, Input, InputNumber, Select, Button, Card, Space, Table } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

const ReceiptForm: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [items, setItems] = useState<any[]>([]);

  const onFinish = (values: any) => {
    console.log('Receipt values:', values, items);
    // TODO: Отправка данных на сервер
    navigate('/warehouse/inventory');
  };

  const addItem = () => {
    setItems([...items, { id: Date.now(), product_sku: '', quantity: 1, cell: '' }]);
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
        <InputNumber
          value={record.quantity}
          onChange={(value) => updateItem(record.id, 'quantity', value)}
          min={1}
          style={{ width: '100%' }}
        />
      ),
    },
    {
      title: 'Ячейка',
      dataIndex: 'cell',
      key: 'cell',
      render: (_: any, record: any) => (
        <Input
          value={record.cell}
          onChange={(e) => updateItem(record.id, 'cell', e.target.value)}
          placeholder="A-01-01"
        />
      ),
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
    <Card title="Приемка товара">
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
      >
        <Form.Item
          name="warehouse_id"
          label="Склад"
          rules={[{ required: true, message: 'Выберите склад' }]}
        >
          <Select placeholder="Выберите склад">
            <Select.Option value="1">Склад А</Select.Option>
            <Select.Option value="2">Склад Б</Select.Option>
            <Select.Option value="3">Склад В</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="supplier"
          label="Поставщик"
        >
          <Input placeholder="Название поставщика" />
        </Form.Item>

        <Form.Item
          name="document_number"
          label="Номер документа"
        >
          <Input placeholder="Номер накладной" />
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
              Сохранить приемку
            </Button>
            <Button onClick={() => navigate('/warehouse/inventory')}>
              Отмена
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ReceiptForm;

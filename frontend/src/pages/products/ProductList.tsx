import React from 'react';
import { Table, Button, Space, Tag, Card, Input } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

const mockProducts = [
  { 
    id: '1', 
    sku: 'SKU-001', 
    name: 'Товар 1',
    barcode: '1234567890123',
    category: 'Электроника',
    price: 5000,
    cost_price: 3000,
    stock: 150,
    reserved: 20,
    available: 130,
    unit: 'шт',
    tenant: 'ООО "Тест"'
  },
  { 
    id: '2', 
    sku: 'SKU-002', 
    name: 'Товар 2',
    barcode: '1234567890124',
    category: 'Одежда',
    price: 2500,
    cost_price: 1500,
    stock: 80,
    reserved: 10,
    available: 70,
    unit: 'шт',
    tenant: 'ООО "Тест"'
  },
  { 
    id: '3', 
    sku: 'SKU-003', 
    name: 'Товар 3',
    barcode: '1234567890125',
    category: 'Бытовая техника',
    price: 15000,
    cost_price: 10000,
    stock: 25,
    reserved: 5,
    available: 20,
    unit: 'шт',
    tenant: 'ИП Иванов'
  },
];

const ProductList: React.FC = () => {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState('');

  const filteredProducts = mockProducts.filter(product => 
    product.name.toLowerCase().includes(searchText.toLowerCase()) ||
    product.sku.toLowerCase().includes(searchText.toLowerCase()) ||
    product.barcode.includes(searchText)
  );

  const columns = [
    { 
      title: 'SKU', 
      dataIndex: 'sku', 
      key: 'sku',
      sorter: (a: any, b: any) => a.sku.localeCompare(b.sku),
    },
    { 
      title: 'Название', 
      dataIndex: 'name', 
      key: 'name',
      sorter: (a: any, b: any) => a.name.localeCompare(b.name),
    },
    { 
      title: 'Штрихкод', 
      dataIndex: 'barcode', 
      key: 'barcode',
    },
    { 
      title: 'Категория', 
      dataIndex: 'category', 
      key: 'category',
    },
    { 
      title: 'Цена', 
      dataIndex: 'price', 
      key: 'price',
      render: (price: number) => `${price.toLocaleString()} ₽`,
      sorter: (a: any, b: any) => a.price - b.price,
    },
    { 
      title: 'Себестоимость', 
      dataIndex: 'cost_price', 
      key: 'cost_price',
      render: (price: number) => `${price.toLocaleString()} ₽`,
    },
    { 
      title: 'Остаток', 
      dataIndex: 'stock', 
      key: 'stock',
      render: (stock: number, record: any) => (
        <span>
          {stock} {record.unit}
          {record.reserved > 0 && (
            <Tag color="orange" style={{ marginLeft: 8 }}>
              Резерв: {record.reserved}
            </Tag>
          )}
        </span>
      ),
      sorter: (a: any, b: any) => a.stock - b.stock,
    },
    { 
      title: 'Доступно', 
      dataIndex: 'available', 
      key: 'available',
      render: (available: number, record: any) => (
        <Tag color={available > 0 ? 'green' : 'red'}>
          {available} {record.unit}
        </Tag>
      ),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button onClick={() => navigate(`/products/${record.id}`)}>Открыть</Button>
          <Button onClick={() => navigate(`/products/${record.id}/edit`)}>Редактировать</Button>
        </Space>
      ),
    },
  ];

  return (
    <Card 
      title="Товары" 
      extra={
        <Space>
          <Input
            placeholder="Поиск по названию, SKU или штрихкоду"
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 300 }}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/products/new')}>
            Новый товар
          </Button>
        </Space>
      }
    >
      <Table 
        dataSource={filteredProducts} 
        columns={columns} 
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default ProductList;

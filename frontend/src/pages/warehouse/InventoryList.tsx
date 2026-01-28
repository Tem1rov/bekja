import React from 'react';
import { Table, Button, Space, Tag, Card, Input } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

const mockInventory = [
  { 
    id: '1', 
    product_sku: 'SKU-001', 
    product_name: 'Товар 1',
    cell: 'A-01-01',
    quantity: 150,
    reserved: 20,
    available: 130,
    last_movement: '2024-01-15 10:30',
    warehouse: 'Склад А'
  },
  { 
    id: '2', 
    product_sku: 'SKU-002', 
    product_name: 'Товар 2',
    cell: 'A-01-02',
    quantity: 80,
    reserved: 10,
    available: 70,
    last_movement: '2024-01-14 15:20',
    warehouse: 'Склад А'
  },
  { 
    id: '3', 
    product_sku: 'SKU-003', 
    product_name: 'Товар 3',
    cell: 'B-02-05',
    quantity: 25,
    reserved: 5,
    available: 20,
    last_movement: '2024-01-13 09:15',
    warehouse: 'Склад Б'
  },
];

const InventoryList: React.FC = () => {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState('');

  const filteredInventory = mockInventory.filter(item => 
    item.product_name.toLowerCase().includes(searchText.toLowerCase()) ||
    item.product_sku.toLowerCase().includes(searchText.toLowerCase()) ||
    item.cell.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns = [
    { 
      title: 'SKU', 
      dataIndex: 'product_sku', 
      key: 'product_sku',
      sorter: (a: any, b: any) => a.product_sku.localeCompare(b.product_sku),
    },
    { 
      title: 'Товар', 
      dataIndex: 'product_name', 
      key: 'product_name',
      sorter: (a: any, b: any) => a.product_name.localeCompare(b.product_name),
    },
    { 
      title: 'Ячейка', 
      dataIndex: 'cell', 
      key: 'cell',
      sorter: (a: any, b: any) => a.cell.localeCompare(b.cell),
    },
    { 
      title: 'Количество', 
      dataIndex: 'quantity', 
      key: 'quantity',
      render: (quantity: number, record: any) => (
        <span>
          {quantity} шт
          {record.reserved > 0 && (
            <Tag color="orange" style={{ marginLeft: 8 }}>
              Резерв: {record.reserved}
            </Tag>
          )}
        </span>
      ),
      sorter: (a: any, b: any) => a.quantity - b.quantity,
    },
    { 
      title: 'Доступно', 
      dataIndex: 'available', 
      key: 'available',
      render: (available: number) => (
        <Tag color={available > 0 ? 'green' : 'red'}>
          {available} шт
        </Tag>
      ),
    },
    { 
      title: 'Склад', 
      dataIndex: 'warehouse', 
      key: 'warehouse',
    },
    { 
      title: 'Последнее движение', 
      dataIndex: 'last_movement', 
      key: 'last_movement',
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button onClick={() => navigate(`/warehouse/inventory/${record.id}`)}>Детали</Button>
          <Button onClick={() => navigate(`/warehouse/receipt?product=${record.product_sku}`)}>Приемка</Button>
        </Space>
      ),
    },
  ];

  return (
    <Card 
      title="Инвентаризация"
      extra={
        <Input
          placeholder="Поиск по товару, SKU или ячейке"
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ width: 300 }}
        />
      }
    >
      <Table 
        dataSource={filteredInventory} 
        columns={columns} 
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default InventoryList;

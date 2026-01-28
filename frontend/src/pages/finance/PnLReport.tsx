import React from 'react';
import { Card, Table, DatePicker, Select, Button, Space, Statistic, Row, Col } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

const mockPnLData = [
  {
    id: '1',
    period: '2024-01',
    revenue: 500000,
    cost_of_goods: 300000,
    marketplace_fee: 50000,
    shipping_cost: 40000,
    storage_cost: 10000,
    processing_cost: 20000,
    packaging_cost: 10000,
    other_costs: 10000,
    total_costs: 450000,
    profit: 50000,
    margin: 10,
  },
  {
    id: '2',
    period: '2024-02',
    revenue: 600000,
    cost_of_goods: 360000,
    marketplace_fee: 60000,
    shipping_cost: 48000,
    storage_cost: 12000,
    processing_cost: 24000,
    packaging_cost: 12000,
    other_costs: 12000,
    total_costs: 540000,
    profit: 60000,
    margin: 10,
  },
];

const PnLReport: React.FC = () => {
  const columns = [
    {
      title: 'Период',
      dataIndex: 'period',
      key: 'period',
      sorter: (a: any, b: any) => a.period.localeCompare(b.period),
    },
    {
      title: 'Выручка',
      dataIndex: 'revenue',
      key: 'revenue',
      render: (value: number) => `${value.toLocaleString()} ₽`,
      sorter: (a: any, b: any) => a.revenue - b.revenue,
    },
    {
      title: 'Себестоимость',
      dataIndex: 'cost_of_goods',
      key: 'cost_of_goods',
      render: (value: number) => `${value.toLocaleString()} ₽`,
    },
    {
      title: 'Комиссия маркетплейса',
      dataIndex: 'marketplace_fee',
      key: 'marketplace_fee',
      render: (value: number) => `${value.toLocaleString()} ₽`,
    },
    {
      title: 'Доставка',
      dataIndex: 'shipping_cost',
      key: 'shipping_cost',
      render: (value: number) => `${value.toLocaleString()} ₽`,
    },
    {
      title: 'Хранение',
      dataIndex: 'storage_cost',
      key: 'storage_cost',
      render: (value: number) => `${value.toLocaleString()} ₽`,
    },
    {
      title: 'Обработка',
      dataIndex: 'processing_cost',
      key: 'processing_cost',
      render: (value: number) => `${value.toLocaleString()} ₽`,
    },
    {
      title: 'Упаковка',
      dataIndex: 'packaging_cost',
      key: 'packaging_cost',
      render: (value: number) => `${value.toLocaleString()} ₽`,
    },
    {
      title: 'Прочие расходы',
      dataIndex: 'other_costs',
      key: 'other_costs',
      render: (value: number) => `${value.toLocaleString()} ₽`,
    },
    {
      title: 'Итого расходы',
      dataIndex: 'total_costs',
      key: 'total_costs',
      render: (value: number) => <strong>{value.toLocaleString()} ₽</strong>,
    },
    {
      title: 'Прибыль',
      dataIndex: 'profit',
      key: 'profit',
      render: (value: number) => (
        <strong style={{ color: value > 0 ? 'green' : 'red' }}>
          {value.toLocaleString()} ₽
        </strong>
      ),
      sorter: (a: any, b: any) => a.profit - b.profit,
    },
    {
      title: 'Маржа',
      dataIndex: 'margin',
      key: 'margin',
      render: (value: number) => (
        <Tag color={value > 0 ? 'green' : 'red'}>
          {value.toFixed(1)}%
        </Tag>
      ),
    },
  ];

  const totalRevenue = mockPnLData.reduce((sum, item) => sum + item.revenue, 0);
  const totalCosts = mockPnLData.reduce((sum, item) => sum + item.total_costs, 0);
  const totalProfit = mockPnLData.reduce((sum, item) => sum + item.profit, 0);
  const avgMargin = (totalProfit / totalRevenue) * 100;

  return (
    <Card
      title="Отчет о прибылях и убытках"
      extra={
        <Space>
          <Select defaultValue="all" style={{ width: 200 }}>
            <Option value="all">Все арендаторы</Option>
            <Option value="1">ООО "Тест"</Option>
            <Option value="2">ИП Иванов</Option>
          </Select>
          <RangePicker
            defaultValue={[dayjs().subtract(1, 'month').startOf('month'), dayjs().subtract(1, 'month').endOf('month')]}
          />
          <Button icon={<DownloadOutlined />}>Экспорт</Button>
        </Space>
      }
    >
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Statistic title="Выручка" value={totalRevenue} suffix="₽" />
        </Col>
        <Col span={6}>
          <Statistic title="Расходы" value={totalCosts} suffix="₽" />
        </Col>
        <Col span={6}>
          <Statistic
            title="Прибыль"
            value={totalProfit}
            suffix="₽"
            valueStyle={{ color: totalProfit > 0 ? '#3f8600' : '#cf1322' }}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="Маржа"
            value={avgMargin}
            precision={1}
            suffix="%"
            valueStyle={{ color: avgMargin > 0 ? '#3f8600' : '#cf1322' }}
          />
        </Col>
      </Row>

      <Table
        dataSource={mockPnLData}
        columns={columns}
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />
    </Card>
  );
};

export default PnLReport;

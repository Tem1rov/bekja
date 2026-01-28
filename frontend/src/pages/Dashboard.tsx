import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Spin, Alert } from 'antd';
import { ShoppingCartOutlined, DollarOutlined, WarningOutlined } from '@ant-design/icons';
import apiClient from '../api/client';

interface DashboardData {
  orders_today: number;
  orders_by_status: Record<string, number>;
  pnl_today: {
    revenue: number;
    margin: number;
    margin_percent: number;
  };
  low_stock_count: number;
  low_stock_items: Array<{
    product_id: string;
    sku: string;
    current_stock: number;
    min_level: number;
  }>;
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await apiClient.get('/dashboard');
        setData(res.data);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка загрузки данных');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <Alert message="Ошибка" description={error} type="error" showIcon />
      </div>
    );
  }

  if (!data) {
    return <div>Нет данных</div>;
  }

  const statusLabels: Record<string, string> = {
    new: 'Новые',
    confirmed: 'Подтверждённые',
    awaiting_stock: 'Ожидают товар',
    picking: 'Сборка',
    packed: 'Упакованы',
    shipped: 'Отправлены',
    delivered: 'Доставлены',
    cancelled: 'Отменены',
  };

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Dashboard</h1>
      <Row gutter={16}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Заказы сегодня"
              value={data.orders_today}
              prefix={<ShoppingCartOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Выручка сегодня"
              value={data.pnl_today.revenue}
              prefix={<DollarOutlined />}
              suffix="₽"
              precision={2}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Маржа"
              value={data.pnl_today.margin}
              prefix="₽"
              precision={2}
              valueStyle={{ color: data.pnl_today.margin > 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Маржинальность"
              value={data.pnl_today.margin_percent}
              suffix="%"
              precision={2}
            />
          </Card>
        </Col>
      </Row>

      {Object.keys(data.orders_by_status).length > 0 && (
        <Card title="Заказы по статусам" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            {Object.entries(data.orders_by_status).map(([status, count]) => (
              <Col xs={12} sm={8} md={6} lg={4} key={status}>
                <Statistic
                  title={statusLabels[status] || status}
                  value={count}
                  valueStyle={{ fontSize: '20px' }}
                />
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {data.low_stock_count > 0 && (
        <Card 
          title={
            <span>
              <WarningOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
              Низкие остатки ({data.low_stock_count})
            </span>
          } 
          style={{ marginTop: 16 }}
        >
          <Table
            dataSource={data.low_stock_items}
            columns={[
              { 
                title: 'SKU', 
                dataIndex: 'sku',
                key: 'sku'
              },
              { 
                title: 'Остаток', 
                dataIndex: 'current_stock',
                key: 'current_stock',
                render: (value: number) => (
                  <Tag color="red">{value}</Tag>
                )
              },
              { 
                title: 'Минимум', 
                dataIndex: 'min_level',
                key: 'min_level'
              },
            ]}
            pagination={false}
            rowKey="product_id"
            size="small"
          />
        </Card>
      )}
    </div>
  );
};

export default Dashboard;

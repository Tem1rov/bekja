import React from 'react';
import { Form, Input, InputNumber, Select, Button, Card, Space } from 'antd';
import { useNavigate } from 'react-router-dom';

const ProductForm: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const onFinish = (values: any) => {
    console.log('Form values:', values);
    // TODO: Отправка данных на сервер
    navigate('/products');
  };

  return (
    <Card title="Новый товар">
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        initialValues={{
          unit: 'шт',
        }}
      >
        <Form.Item
          name="sku"
          label="SKU"
          rules={[{ required: true, message: 'Введите SKU' }]}
        >
          <Input placeholder="SKU-001" />
        </Form.Item>

        <Form.Item
          name="name"
          label="Название"
          rules={[{ required: true, message: 'Введите название товара' }]}
        >
          <Input placeholder="Название товара" />
        </Form.Item>

        <Form.Item
          name="barcode"
          label="Штрихкод"
        >
          <Input placeholder="1234567890123" />
        </Form.Item>

        <Form.Item
          name="category"
          label="Категория"
        >
          <Input placeholder="Категория" />
        </Form.Item>

        <Form.Item
          name="price"
          label="Цена продажи"
          rules={[{ required: true, message: 'Введите цену' }]}
        >
          <InputNumber
            style={{ width: '100%' }}
            placeholder="0"
            min={0}
            formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')}
            parser={(value) => value!.replace(/\s?/g, '')}
          />
        </Form.Item>

        <Form.Item
          name="cost_price"
          label="Себестоимость"
        >
          <InputNumber
            style={{ width: '100%' }}
            placeholder="0"
            min={0}
            formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')}
            parser={(value) => value!.replace(/\s?/g, '')}
          />
        </Form.Item>

        <Form.Item
          name="unit"
          label="Единица измерения"
        >
          <Select>
            <Select.Option value="шт">шт</Select.Option>
            <Select.Option value="кг">кг</Select.Option>
            <Select.Option value="л">л</Select.Option>
            <Select.Option value="м">м</Select.Option>
            <Select.Option value="м²">м²</Select.Option>
            <Select.Option value="м³">м³</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">
              Сохранить
            </Button>
            <Button onClick={() => navigate('/products')}>
              Отмена
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ProductForm;

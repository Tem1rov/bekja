import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { AuthProvider } from './auth/AuthContext';
import ProtectedRoute from './auth/ProtectedRoute';
import MainLayout from './components/Layout/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import NotFound from './pages/NotFound';
import OrderList from './pages/orders/OrderList';
import OrderDetail from './pages/orders/OrderDetail';
import OrderForm from './pages/orders/OrderForm';
import ProductList from './pages/products/ProductList';
import ProductForm from './pages/products/ProductForm';
import WarehouseList from './pages/warehouse/WarehouseList';
import InventoryList from './pages/warehouse/InventoryList';
import ReceiptForm from './pages/warehouse/ReceiptForm';
import TariffList from './pages/finance/TariffList';
import PnLReport from './pages/finance/PnLReport';
import IntegrationList from './pages/integrations/IntegrationList';
import UserList from './pages/users/UserList';
import TenantList from './pages/tenants/TenantList';
import 'antd/dist/reset.css';
import './styles/global.css';

const App = () => (
  <ConfigProvider>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/orders" element={<OrderList />} />
            <Route path="/orders/new" element={<OrderForm />} />
            <Route path="/orders/:id" element={<OrderDetail />} />
            <Route path="/products" element={<ProductList />} />
            <Route path="/products/new" element={<ProductForm />} />
            <Route path="/products/:id/edit" element={<ProductForm />} />
            <Route path="/warehouse" element={<WarehouseList />} />
            <Route path="/warehouse/inventory" element={<InventoryList />} />
            <Route path="/warehouse/receipt" element={<ReceiptForm />} />
            <Route path="/warehouse/:id" element={<WarehouseList />} />
            <Route path="/warehouse/:id/inventory" element={<InventoryList />} />
            <Route path="/finance" element={<TariffList />} />
            <Route path="/finance/pnl" element={<PnLReport />} />
            <Route path="/finance/tariffs" element={<TariffList />} />
            <Route path="/finance/tariffs/new" element={<TariffList />} />
            <Route path="/finance/tariffs/:id" element={<TariffList />} />
            <Route path="/integrations" element={<IntegrationList />} />
            <Route path="/integrations/new" element={<IntegrationList />} />
            <Route path="/integrations/:id" element={<IntegrationList />} />
            <Route path="/users" element={<UserList />} />
            <Route path="/users/new" element={<UserList />} />
            <Route path="/users/:id" element={<UserList />} />
            <Route path="/tenants" element={<TenantList />} />
            <Route path="/tenants/new" element={<TenantList />} />
            <Route path="/tenants/:id" element={<TenantList />} />
            <Route path="/settings" element={<div>Settings (TBD)</div>} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </ConfigProvider>
);

export default App;

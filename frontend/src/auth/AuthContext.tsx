import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  tenant_id: string | null;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      // Try to fetch user info from API
      // For now, we'll create a mock user from email stored in localStorage
      // In production, decode JWT token or fetch user from /auth/me endpoint
      const storedEmail = localStorage.getItem('user_email');
      if (storedEmail) {
        const mockUser: User = {
          id: '1',
          email: storedEmail,
          full_name: storedEmail.split('@')[0],
          role: 'admin',
          tenant_id: null
        };
        setUser(mockUser);
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await apiClient.post('/auth/login', { email, password });
    localStorage.setItem('access_token', res.data.access_token);
    localStorage.setItem('refresh_token', res.data.refresh_token);
    localStorage.setItem('user_email', email);
    
    // Decode token to get user info (simplified - in production use jwt-decode)
    // For now, we'll create a mock user object
    // In production, decode JWT token or fetch user from /auth/me endpoint
    const mockUser: User = {
      id: '1',
      email: email,
      full_name: email.split('@')[0],
      role: 'admin',
      tenant_id: null
    };
    setUser(mockUser);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_email');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

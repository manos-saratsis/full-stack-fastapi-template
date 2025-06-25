```typescript
import React from 'react';
import { render, fireEvent, screen, waitFor } from '@testing-library/react';
import { LoginForm } from '../../components/LoginForm';
import { useAuth } from '../../auth/AuthProvider';

jest.mock('../../auth/AuthProvider');

describe('LoginForm', () => {
  const mockLogin = jest.fn();
  
  beforeEach(() => {
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
      isAuthenticated: false
    });
  });

  it('renders login form correctly', () => {
    render(<LoginForm />);
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('handles form submission correctly', async () => {
    mockLogin.mockResolvedValue(undefined);
    
    render(<LoginForm />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@test.com' }
    });
    
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@test.com', 'password123');
    });
  });

  it('displays validation errors for empty fields', async () => {
    render(<LoginForm />);
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it('handles login error', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid credentials'));
    
    render(<LoginForm />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@test.com' }
    });
    
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrong-password' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});
```
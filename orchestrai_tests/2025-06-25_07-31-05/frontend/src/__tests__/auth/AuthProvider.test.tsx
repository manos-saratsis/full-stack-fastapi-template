```typescript
import React from 'react';
import { render, act, screen, fireEvent } from '@testing-library/react';
import { AuthProvider, useAuth } from '../../auth/AuthProvider';
import { AuthService } from '../../services/AuthService';

jest.mock('../../services/AuthService');

describe('AuthProvider', () => {
  const mockAuthService = AuthService as jest.Mocked<typeof AuthService>;
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should provide authentication context', () => {
    const TestComponent = () => {
      const { isAuthenticated } = useAuth();
      return <div>{isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</div>;
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Not Authenticated')).toBeInTheDocument();
  });

  it('should handle login successfully', async () => {
    mockAuthService.login.mockResolvedValue({ 
      access_token: 'test-token',
      token_type: 'bearer'
    });

    const TestComponent = () => {
      const { login } = useAuth();
      return <button onClick={() => login('test@email.com', 'password')}>Login</button>;
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await act(async () => {
      fireEvent.click(screen.getByText('Login'));
    });

    expect(mockAuthService.login).toHaveBeenCalledWith('test@email.com', 'password');
  });

  it('should handle login failure', async () => {
    mockAuthService.login.mockRejectedValue(new Error('Login failed'));

    const TestComponent = () => {
      const { login, error } = useAuth();
      return (
        <div>
          <button onClick={() => login('test@email.com', 'password')}>Login</button>
          {error && <div>{error}</div>}
        </div>
      );
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await act(async () => {
      fireEvent.click(screen.getByText('Login'));
    });

    expect(screen.getByText('Login failed')).toBeInTheDocument();
  });
});
```
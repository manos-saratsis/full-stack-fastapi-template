```typescript
import React from 'react';
import { render, act, screen } from '@testing-library/react';
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
      const auth = useAuth();
      return <div data-testid="auth-state">{auth.isAuthenticated ? 'authenticated' : 'not authenticated'}</div>;
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('auth-state')).toHaveTextContent('not authenticated');
  });

  it('should handle login successfully', async () => {
    mockAuthService.prototype.login.mockResolvedValue({ 
      access_token: 'test-token',
      token_type: 'bearer'
    });

    const TestComponent = () => {
      const auth = useAuth();
      return (
        <button onClick={() => auth.login('test@test.com', 'password')}>
          Login
        </button>
      );
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await act(async () => {
      screen.getByRole('button').click();
    });

    expect(mockAuthService.prototype.login).toHaveBeenCalledWith('test@test.com', 'password');
  });

  it('should handle logout', async () => {
    const TestComponent = () => {
      const auth = useAuth();
      return (
        <button onClick={() => auth.logout()}>
          Logout
        </button>
      );
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await act(async () => {
      screen.getByRole('button').click();
    });

    expect(screen.getByRole('button')).toBeInTheDocument();
  });
});
```
```typescript
import React from 'react';
import { render, act, screen } from '@testing-library/react';
import { AuthProvider, useAuth } from '../../auth/AuthProvider';
import { AuthService } from '../../services/AuthService';

jest.mock('../../services/AuthService');

describe('AuthProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should provide authentication context', () => {
    const TestComponent = () => {
      const auth = useAuth();
      return <div data-testid="auth-state">{auth.isAuthenticated ? 'authenticated' : 'not-authenticated'}</div>;
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('auth-state')).toHaveTextContent('not-authenticated');
  });

  it('should handle login successfully', async () => {
    const mockToken = 'test-token';
    (AuthService.login as jest.Mock).mockResolvedValue({ access_token: mockToken });

    const TestComponent = () => {
      const auth = useAuth();
      return (
        <button onClick={() => auth.login('test@email.com', 'password')}>
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

    expect(AuthService.login).toHaveBeenCalledWith('test@email.com', 'password');
  });

  it('should handle logout', async () => {
    const TestComponent = () => {
      const auth = useAuth();
      return <button onClick={() => auth.logout()}>Logout</button>;
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await act(async () => {
      screen.getByRole('button').click();
    });

    expect(localStorage.removeItem).toHaveBeenCalledWith('token');
  });
});
```
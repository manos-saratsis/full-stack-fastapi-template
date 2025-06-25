```typescript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from '../../components/auth/LoginForm';
import { AuthProvider } from '../../contexts/AuthContext';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.post('/api/v1/login/access-token', (req, res, ctx) => {
    return res(
      ctx.json({
        access_token: 'fake-token',
        token_type: 'bearer'
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('LoginForm', () => {
  it('renders login form correctly', () => {
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('handles successful login', async () => {
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('fake-token');
    });
  });

  it('handles login error', async () => {
    server.use(
      rest.post('/api/v1/login/access-token', (req, res, ctx) => {
        return res(ctx.status(401));
      })
    );

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'wrong@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpass' },
    });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});
```
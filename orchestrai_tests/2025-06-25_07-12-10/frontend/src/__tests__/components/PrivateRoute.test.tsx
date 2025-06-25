```typescript
import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { PrivateRoute } from '../../components/PrivateRoute';
import { AuthProvider } from '../../auth/AuthProvider';

describe('PrivateRoute', () => {
  const MockProtectedComponent = () => <div>Protected Content</div>;
  const MockLoginComponent = () => <div>Login Page</div>;

  const renderWithRouter = (isAuthenticated: boolean = false) => {
    const mockAuthContext = {
      isAuthenticated,
      login: jest.fn(),
      logout: jest.fn(),
      user: null
    };

    return render(
      <AuthProvider value={mockAuthContext}>
        <MemoryRouter initialEntries={['/protected']}>
          <Routes>
            <Route path="/login" element={<MockLoginComponent />} />
            <Route
              path="/protected"
              element={
                <PrivateRoute>
                  <MockProtectedComponent />
                </PrivateRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );
  };

  it('should render protected component when authenticated', () => {
    renderWithRouter(true);
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should redirect to login when not authenticated', () => {
    renderWithRouter(false);
    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });
});
```
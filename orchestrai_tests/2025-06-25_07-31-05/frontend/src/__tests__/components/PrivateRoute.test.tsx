```typescript
import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { PrivateRoute } from '../../components/PrivateRoute';
import { AuthProvider } from '../../auth/AuthProvider';

describe('PrivateRoute', () => {
  const TestComponent = () => <div>Protected Content</div>;
  
  it('should render protected content when authenticated', () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/protected']}>
          <Routes>
            <Route path="/protected" element={
              <PrivateRoute>
                <TestComponent />
              </PrivateRoute>
            } />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should redirect to login when not authenticated', () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/protected']}>
          <Routes>
            <Route path="/login" element={<div>Login Page</div>} />
            <Route path="/protected" element={
              <PrivateRoute>
                <TestComponent />
              </PrivateRoute>
            } />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });
});
```
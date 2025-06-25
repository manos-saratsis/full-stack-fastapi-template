```typescript
import { api } from '../../api';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/v1/users/me', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User'
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('API Client', () => {
  it('adds authorization header when token exists', async () => {
    localStorage.setItem('token', 'test-token');
    
    const response = await api.get('/api/v1/users/me');
    
    expect(response.config.headers.Authorization).toBe('Bearer test-token');
  });

  it('handles API errors correctly', async () => {
    server.use(
      rest.get('/api/v1/users/me', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    try {
      await api.get('/api/v1/users/me');
    } catch (error) {
      expect(error.response.status).toBe(500);
    }
  });

  it('refreshes token on 401 error', async () => {
    server.use(
      rest.get('/api/v1/users/me', (req, res, ctx) => {
        return res(ctx.status(401));
      }),
      rest.post('/api/v1/login/refresh-token', (req, res, ctx) => {
        return res(
          ctx.json({
            access_token: 'new-token',
            token_type: 'bearer'
          })
        );
      })
    );

    try {
      await api.get('/api/v1/users/me');
    } catch (error) {
      expect(localStorage.getItem('token')).toBe('new-token');
    }
  });
});
```
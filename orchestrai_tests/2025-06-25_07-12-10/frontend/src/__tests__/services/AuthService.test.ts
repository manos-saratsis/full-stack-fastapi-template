```typescript
import { AuthService } from '../../services/AuthService';
import axios from 'axios';

jest.mock('axios');

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should successfully login and return access token', async () => {
      const mockResponse = { data: { access_token: 'test-token' } };
      (axios.post as jest.Mock).mockResolvedValue(mockResponse);

      const result = await AuthService.login('test@email.com', 'password');

      expect(axios.post).toHaveBeenCalledWith('/api/auth/login', {
        email: 'test@email.com',
        password: 'password'
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle login error', async () => {
      const errorMessage = 'Invalid credentials';
      (axios.post as jest.Mock).mockRejectedValue(new Error(errorMessage));

      await expect(AuthService.login('test@email.com', 'wrong-password'))
        .rejects.toThrow(errorMessage);
    });
  });

  describe('register', () => {
    it('should successfully register a new user', async () => {
      const mockResponse = { data: { message: 'User registered successfully' } };
      (axios.post as jest.Mock).mockResolvedValue(mockResponse);

      const result = await AuthService.register({
        email: 'test@email.com',
        password: 'password',
        firstName: 'Test',
        lastName: 'User'
      });

      expect(axios.post).toHaveBeenCalledWith('/api/auth/register', {
        email: 'test@email.com',
        password: 'password',
        firstName: 'Test',
        lastName: 'User'
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle registration error', async () => {
      const errorMessage = 'Email already exists';
      (axios.post as jest.Mock).mockRejectedValue(new Error(errorMessage));

      await expect(AuthService.register({
        email: 'existing@email.com',
        password: 'password',
        firstName: 'Test',
        lastName: 'User'
      })).rejects.toThrow(errorMessage);
    });
  });
});
```
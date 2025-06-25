```typescript
import { AuthService } from '../../services/AuthService';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('AuthService', () => {
  let authService: AuthService;

  beforeEach(() => {
    authService = new AuthService();
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'bearer'
        }
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await authService.login('test@test.com', 'password');

      expect(result).toEqual(mockResponse.data);
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/v1/login/access-token',
        { username: 'test@test.com', password: 'password' }
      );
    });

    it('should handle login failure', async () => {
      mockedAxios.post.mockRejectedValue(new Error('Invalid credentials'));

      await expect(authService.login('test@test.com', 'wrong-password'))
        .rejects.toThrow('Invalid credentials');
    });
  });

  describe('getUser', () => {
    it('should fetch user details successfully', async () => {
      const mockUser = {
        id: 1,
        email: 'test@test.com',
        full_name: 'Test User'
      };
      mockedAxios.get.mockResolvedValue({ data: mockUser });

      const result = await authService.getUser();

      expect(result).toEqual(mockUser);
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/users/me');
    });

    it('should handle user fetch failure', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Unauthorized'));

      await expect(authService.getUser()).rejects.toThrow('Unauthorized');
    });
  });
});
```
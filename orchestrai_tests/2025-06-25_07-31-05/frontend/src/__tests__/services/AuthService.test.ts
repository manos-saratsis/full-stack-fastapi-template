```typescript
import { AuthService } from '../../services/AuthService';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should successfully login and return tokens', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'bearer'
        }
      };
      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await AuthService.login('test@email.com', 'password');

      expect(result).toEqual(mockResponse.data);
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/v1/login/access-token',
        { username: 'test@email.com', password: 'password' }
      );
    });

    it('should handle login failure', async () => {
      mockedAxios.post.mockRejectedValue(new Error('Invalid credentials'));

      await expect(AuthService.login('test@email.com', 'wrong-password'))
        .rejects.toThrow('Invalid credentials');
    });
  });

  describe('logout', () => {
    it('should successfully logout', async () => {
      await AuthService.logout();
      // Add assertions for logout behavior
    });
  });

  describe('getCurrentUser', () => {
    it('should fetch current user details', async () => {
      const mockUser = {
        id: 1,
        email: 'test@email.com',
        full_name: 'Test User'
      };
      mockedAxios.get.mockResolvedValue({ data: mockUser });

      const result = await AuthService.getCurrentUser();

      expect(result).toEqual(mockUser);
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/users/me');
    });

    it('should handle error when fetching user details', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Unauthorized'));

      await expect(AuthService.getCurrentUser()).rejects.toThrow('Unauthorized');
    });
  });
});
```
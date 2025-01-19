import { MemoBaseClient } from '../src/client';
import { User } from '../src/user';
import { projectUrl, apiKey, apiVersion } from './env';

// 模拟 fetch
global.fetch = jest.fn();

describe('MemoBaseClient', () => {
  let client: MemoBaseClient;

  beforeEach(() => {
    // 创建一个新的 client 实例，每次测试前清理
    client = new MemoBaseClient(projectUrl, apiKey, apiVersion);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Constructor', () => {
    it('should correctly initialize with the given parameters', () => {
      expect(client).toBeInstanceOf(MemoBaseClient);
      expect(client['baseUrl']).toBe(`${projectUrl}/${apiVersion}`);
      expect(client['headers']).toEqual({
        Authorization: 'Bearer ' + apiKey,
        'Content-Type': 'application/json',
      });
    });

    it('should throw an error if no apiKey is provided', () => {
      expect(() => new MemoBaseClient(projectUrl)).toThrow(
        'apiKey is required. Pass it as argument or set MEMOBASE_API_KEY environment variable',
      );
    });
  });

  describe('Ping method', () => {
    it('should return true for successful ping', async () => {
      // 模拟 fetch 的成功响应
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue({
          data: 'pong',
          errmsg: '',
          errno: 0,
        }),
      });

      const result = await client.ping();
      expect(result).toBe(true);
      expect(fetch).toHaveBeenCalledWith(`${projectUrl}/${apiVersion}/healthcheck`, expect.any(Object));
    });

    it('should return false for failed ping', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network Error'));

      const result = await client.ping();
      expect(result).toBe(false);
    });
  });

  describe('User management methods', () => {
    it('should add a user and return user id', async () => {
      // 模拟 fetch 的成功响应
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue({ data: { id: '123' }, errmsg: '', errno: 0 }),
      });

      const userId = await client.addUser({ name: 'John' }, 'user123');
      expect(userId).toBe('123');
      expect(fetch).toHaveBeenCalledWith(
        `${projectUrl}/${apiVersion}/users`,
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ data: { name: 'John' }, id: 'user123' }),
        }),
      );
    });

    it('should update a user and return user id', async () => {
      const userId = await client.updateUser('user123', { name: 'Updated Name' });
      expect(userId).toBe('123');
      expect(fetch).toHaveBeenCalledWith(
        `${projectUrl}/${apiVersion}/users/user123`,
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ data: { name: 'Updated Name' } }),
        }),
      );
    });

    it('should get a user', async () => {
      const user = await client.getUser('user123');
      expect(user).toBeInstanceOf(User);
      expect(fetch).toHaveBeenCalledWith(`${projectUrl}/${apiVersion}/users/user123`, expect.any(Object));
    });

    it('should create a user if not exists when calling getOrCreateUser', async () => {
      // 模拟首次未找到用户
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('User not found'));

      const user = await client.getOrCreateUser('user123');
      expect(user).toBeInstanceOf(User);
      expect(fetch).toHaveBeenCalledTimes(2); // 调用两次：一次是 getUser，另一次是 addUser
    });

    it('should delete a user', async () => {
      const result = await client.deleteUser('user123');
      expect(result).toBe(true);
      expect(fetch).toHaveBeenCalledWith(
        `${projectUrl}/${apiVersion}/users/user123`,
        expect.objectContaining({ method: 'DELETE' }),
      );
    });
  });
});

import { User } from '../src/user';
import { MemoBaseClient } from '../src/client';
import type { Blob, BaseResponse, IdResponse, ProfileResponse } from '../src/types';
import { projectUrl, apiKey, apiVersion } from './env';

// 模拟 fetch
global.fetch = jest.fn();

describe('User', () => {
  let client: MemoBaseClient;
  let user: User;

  beforeEach(() => {
    client = new MemoBaseClient(projectUrl, apiKey, apiVersion);
    user = new User('user123', client);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should insert a blob and return its id', async () => {
    const mockBlobData: Blob = { type: 'chat', messages: [{ role: 'user', content: 'Hello' }] };
    const mockResponse: BaseResponse<IdResponse> = { data: { id: 'blob123' }, errmsg: '', errno: 0 };

    // 模拟 fetch 的成功响应
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockResponse),
    });

    const blobId = await user.insert(mockBlobData);

    expect(blobId).toBe('blob123');
    expect(fetch).toHaveBeenCalledWith(
      `${projectUrl}/${apiVersion}/blobs/insert/user123`,
      expect.any(Object),
    );
  });

  it('should get a blob by id', async () => {
    const mockBlob: Blob = { type: 'chat', messages: [{ role: 'user', content: 'Hello' }] };
    const mockResponse: BaseResponse<Blob> = { data: mockBlob, errmsg: '', errno: 0 };

    // 模拟 fetch 的成功响应
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockResponse),
    });

    const blob = await user.get('blob123');

    expect(blob).toEqual(mockBlob);
    expect(fetch).toHaveBeenCalledWith(
      `${projectUrl}/${apiVersion}/blobs/user123/blob123`,
      expect.any(Object),
    );
  });

  it('should get all blobs by type', async () => {
    const mockResponse: BaseResponse<{ ids: string[] }> = {
      data: { ids: ['blob123', 'blob456'] },
      errmsg: '',
      errno: 0,
    };

    // 模拟 fetch 的成功响应
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockResponse),
    });

    const blobIds = await user.getAll('chat');

    expect(blobIds).toEqual(['blob123', 'blob456']);
    expect(fetch).toHaveBeenCalledWith(
      `${projectUrl}/${apiVersion}/users/blobs/user123/chat?page=0&page_size=10`,
      expect.any(Object),
    );
  });

  it('should delete a blob', async () => {
    const mockResponse: BaseResponse<null> = { errmsg: '', errno: 0 };

    // 模拟 fetch 的成功响应
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockResponse),
    });

    const result = await user.delete('blob123');

    expect(result).toBe(true);
    expect(fetch).toHaveBeenCalledWith(
      `${projectUrl}/${apiVersion}/blobs/user123/blob123`,
      expect.objectContaining({ method: 'DELETE' }),
    );
  });

  it('should flush blobs', async () => {
    const mockResponse: BaseResponse<null> = { errmsg: '', errno: 0 };

    // 模拟 fetch 的成功响应
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockResponse),
    });

    const result = await user.flush('chat');

    expect(result).toBe(true);
    expect(fetch).toHaveBeenCalledWith(
      `${projectUrl}/${apiVersion}/users/buffer/user123/chat`,
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('should get user profile', async () => {
    const mockResponse: BaseResponse<ProfileResponse> = {
      data: {
        profiles: [
          {
            updated_at: '2023-01-01T00:00:00Z',
            attributes: { topic: 'Topic1', sub_topic: 'SubTopic1' },
            content: 'Content1',
          },
        ],
      },
      errmsg: '',
      errno: 0,
    };

    // 模拟 fetch 的成功响应
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockResponse),
    });

    const profiles = await user.profile();

    expect(profiles).toEqual([
      {
        updated_at: new Date('2023-01-01T00:00:00Z'),
        topic: 'Topic1',
        sub_topic: 'SubTopic1',
        content: 'Content1',
      },
    ]);
    expect(fetch).toHaveBeenCalledWith(
      `${projectUrl}/${apiVersion}/users/profile/user123`,
      expect.any(Object),
    );
  });

  it('should delete a profile', async () => {
    const mockResponse: BaseResponse<null> = { errmsg: '', errno: 0 };

    // 模拟 fetch 的成功响应
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockResponse),
    });

    const result = await user.deleteProfile('profile123');

    expect(result).toBe(true);
    expect(fetch).toHaveBeenCalledWith(
      `${projectUrl}/${apiVersion}/users/profile/user123/profile123`,
      expect.objectContaining({ method: 'DELETE' }),
    );
  });
});

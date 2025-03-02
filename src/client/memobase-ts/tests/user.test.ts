import { User } from '../src/user';
import { MemoBaseClient } from '../src/client';
import type {
  Blob,
  BaseResponse,
  IdResponse,
  ProfileResponse,
  UserEvent,
  EventResponse,
  ContextResponse,
} from '../src/types';
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

    const result = await user.insert(mockBlobData);

    expect(result).toBe('blob123');
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

    const result = await user.getAll('chat');

    expect(result).toEqual(['blob123', 'blob456']);
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
            id: 'profile123',
            content: 'Content1',
            attributes: { topic: 'Topic1', sub_topic: 'SubTopic1' },
            created_at: '2023-01-01T00:00:00Z',
            updated_at: '2023-01-01T00:00:00Z',
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

    const result = await user.profile();

    expect(result).toEqual(
      mockResponse.data?.profiles.map((p) => ({
        id: p.id,
        content: p.content,
        topic: p.attributes.topic || 'NONE',
        sub_topic: p.attributes.sub_topic || 'NONE',
        created_at: new Date(p.created_at),
        updated_at: new Date(p.updated_at),
      })),
    );
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

  it('should get user events', async () => {
    const events: UserEvent[] = [
      {
        id: 'event123',
        created_at: new Date('2025-03-01T00:00:00Z'),
        updated_at: new Date('2025-03-01T00:00:00Z'),
        event_data: {
          profile_delta: [
            {
              content: 'Content1',
              attributes: { topic: 'Topic1', sub_topic: 'SubTopic1' },
            },
          ],
        },
      },
    ];
    const mockResponse: BaseResponse<EventResponse> = {
      data: {
        events: events,
      },
      errmsg: '',
      errno: 0,
    };

    // 模拟 fetch 的成功响应
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockResponse),
    });

    const result = await user.event(100, 1000);
    expect(result).toEqual(events);

    expect(fetch).toHaveBeenCalledWith(
      `${projectUrl}/${apiVersion}/users/event/user123?topk=100&max_token_size=1000`,
      expect.any(Object),
    );
  });

  it('should get user context', async () => {
    const data: ContextResponse = {
      context: 'context123',
    };
    const mockResponse: BaseResponse<ContextResponse> = {
      data: data,
      errmsg: '',
      errno: 0,
    };

    // 模拟 fetch 的成功响应
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: jest.fn().mockResolvedValue(mockResponse),
    });

    const result = await user.context(
      2000,
      1000,
      ['topic1', 'topic2'],
      ['topic3'],
      { topic1: 5, topic2: 3 },
      0.5,
    );

    expect(result).toBe(data.context);
    expect(fetch).toHaveBeenCalledWith(
      `${projectUrl}/${apiVersion}/users/context/user123?max_token_size=2000&max_subtopic_size=1000&prefer_topics=topic1&prefer_topics=topic2&only_topics=topic3&topic_limits=%7B%22topic1%22%3A5%2C%22topic2%22%3A3%7D&profile_event_ratio=0.5`,
      expect.any(Object),
    );
  });
});

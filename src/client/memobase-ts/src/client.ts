import { User } from './user';
import { unpackResponse } from './network';
import type { BaseResponse, HttpUrl, GetConfigResponse, GetProjectUsersResponse, GetProjectUsageItemResponse } from './types';

export class MemoBaseClient {
  private readonly baseUrl: HttpUrl;
  private readonly headers: HeadersInit;

  constructor(
    projectUrl: string,
    private readonly apiKey?: string,
    private readonly apiVersion: string = 'api/v1',
  ) {
    this.apiKey = apiKey || process.env.MEMOBASE_API_KEY;

    if (!this.apiKey) {
      throw new Error('apiKey is required. Pass it as argument or set MEMOBASE_API_KEY environment variable');
    }

    this.baseUrl = `${projectUrl.replace(/\/$/, '')}/${this.apiVersion.replace(/^\//, '')}`;
    this.headers = {
      Authorization: `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
    };
  }

  async fetch<T>(path: string, init?: RequestInit): Promise<BaseResponse<T>> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers: {
        ...this.headers,
        ...init?.headers,
      },
    });
    return unpackResponse<T>(response);
  }

  async ping(): Promise<boolean> {
    try {
      await this.fetch('/healthcheck');
      return true;
    } catch (error) {
      return false;
    }
  }

  async getConfig(): Promise<string> {
    const response = await this.fetch<GetConfigResponse>('/project/profile_config');
    return response.data!.profile_config;
  }

  async updateConfig(config: string): Promise<boolean> {
    try {
      await this.fetch('/project/profile_config', {
        method: 'POST',
        body: JSON.stringify({ profile_config: config }),
      });
      return true;
    } catch (error) {
      return false;
    }
  }

  async addUser(data?: Record<string, any>, id?: string): Promise<string> {
    const response = await this.fetch<{ id: string }>('/users', {
      method: 'POST',
      body: JSON.stringify({ data, id }),
    });
    return response.data!.id;
  }

  async updateUser(userId: string, data?: Record<string, any>): Promise<string> {
    const response = await this.fetch<{ id: string }>(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify({ data }),
    });
    return response.data!.id;
  }

  async getUsers(search: string = "", order_by: "updated_at" | "profile_count" | "event_count" = "updated_at", order_desc: boolean = true, limit: number = 10, offset: number = 0): Promise<GetProjectUsersResponse> {
    const params = new URLSearchParams();
    params.append('search', search);
    params.append('order_by', order_by);
    params.append('order_desc', order_desc ? 'true' : 'false');
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await this.fetch<GetProjectUsersResponse>(`/project/users?${params.toString()}`);
    if (response.data) {
      return response.data;
    }
    return { users: [], count: 0 };
  }

  async getUser(userId: string, noGet = false): Promise<User> {
    if (!noGet) {
      const response = await this.fetch<Record<string, any>>(`/users/${userId}`);
      return new User(userId, this, response.data);
    }
    return new User(userId, this);
  }

  async getOrCreateUser(userId: string): Promise<User> {
    try {
      return await this.getUser(userId);
    } catch (error) {
      await this.addUser(undefined, userId);
      return new User(userId, this);
    }
  }

  async deleteUser(userId: string): Promise<boolean> {
    await this.fetch(`/users/${userId}`, { method: 'DELETE' });
    return true;
  }

  async getUsage(last_days: number = 7): Promise<GetProjectUsageItemResponse[]> {
    const params = new URLSearchParams();
    params.append('last_days', last_days.toString());

    const response = await this.fetch<GetProjectUsageItemResponse[]>(`/project/usage`);
    if (response.data) {
      return response.data;
    }
    return [];
  }
}

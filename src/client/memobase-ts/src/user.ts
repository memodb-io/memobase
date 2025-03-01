import { MemoBaseClient } from './client';
import { Blob, BlobType, UserProfile, IdResponse, ProfileResponse, EventResponse } from './types';

export class User {
  constructor(
    private readonly userId: string,
    private readonly projectClient: MemoBaseClient,
    public readonly fields?: Record<string, any>,
  ) {}

  async insert(blobData: Blob): Promise<string> {
    const response = await this.projectClient.fetch<IdResponse>(`/blobs/insert/${this.userId}`, {
      method: 'POST',
      body: JSON.stringify({
        blob_type: blobData.type,
        fields: blobData.fields,
        blob_data: blobData,
      }),
    });
    return response.data!.id;
  }

  async get(blobId: string): Promise<Blob> {
    const response = await this.projectClient.fetch<Blob>(`/blobs/${this.userId}/${blobId}`);
    return response.data as Blob;
  }

  async getAll(blobType: BlobType, page = 0, pageSize = 10): Promise<string[]> {
    const response = await this.projectClient.fetch<{ ids: string[] }>(
      `/users/blobs/${this.userId}/${blobType}?page=${page}&page_size=${pageSize}`,
    );
    return response.data!.ids;
  }

  async delete(blobId: string): Promise<boolean> {
    await this.projectClient.fetch(`/blobs/${this.userId}/${blobId}`, { method: 'DELETE' });
    return true;
  }

  async flush(blobType: BlobType = 'chat'): Promise<boolean> {
    await this.projectClient.fetch(`/users/buffer/${this.userId}/${blobType}`, { method: 'POST' });
    return true;
  }

  async profile(): Promise<UserProfile[]> {
    const response = await this.projectClient.fetch<ProfileResponse>(`/users/profile/${this.userId}`);
    return response.data!.profiles.map((p: any) => ({
      updated_at: new Date(p.updated_at),
      topic: p.attributes.topic || 'NONE',
      sub_topic: p.attributes.sub_topic || 'NONE',
      content: p.content,
    }));
  }

  async deleteProfile(profileId: string): Promise<boolean> {
    await this.projectClient.fetch(`/users/profile/${this.userId}/${profileId}`, { method: 'DELETE' });
    return true;
  }

  /**
   * Returns a list of the user’s most recent events, ordered by recency
   * docs: https://docs.memobase.io/api-reference/events/get_events#response-data-events-created-at
   * @param userId - The user ID
   * @param topk - The number of events to return
   * @param max_token_size - The maximum token size
   * @returns The events for the user
   */
  async event(
    userId: string,
    { topk, max_token_size }: { topk?: number; max_token_size?: number } = {},
  ): Promise<EventResponse> {
    const params = new URLSearchParams();
    if (topk != null) params.set('topk', topk.toString());
    if (max_token_size != null) params.set('max_token_size', max_token_size.toString());
    const queryParams = params.toString();
    let path = `/users/event/${userId}`;
    if (queryParams) path += `?${queryParams}`;
    const response = await this.projectClient.fetch<EventResponse>(path);
    return EventResponse.parse(response.data);
  }
}

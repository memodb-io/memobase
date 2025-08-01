import { MemoBaseClient } from './client';
import {
  Blob,
  BlobType,
  UserProfile,
  IdResponse,
  ProfileResponse,
  UserEvent,
  EventResponse,
  UserGistEvent,
  GistEventResponse,
  ContextResponse,
  OpenAICompatibleMessage,
} from './types';

export class User {
  constructor(
    private readonly userId: string,
    private readonly projectClient: MemoBaseClient,
    public readonly fields?: Record<string, any>,
  ) {}

  async insert(blobData: Blob, sync = false): Promise<string> {
    const response = await this.projectClient.fetch<IdResponse>(
      `/blobs/insert/${this.userId}?wait_process=${sync}`,
      {
        method: 'POST',
        body: JSON.stringify({
          blob_type: blobData.type,
          fields: blobData.fields,
          blob_data: blobData,
        }),
      },
    );
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

  async flush(blobType: BlobType = 'chat', sync = false): Promise<boolean> {
    await this.projectClient.fetch(`/users/buffer/${this.userId}/${blobType}?wait_process=${sync}`, {
      method: 'POST',
    });
    return true;
  }

  async addProfile(content: string, topic: string, subTopic: string): Promise<string> {
    const response = await this.projectClient.fetch<IdResponse>(`/users/profile/${this.userId}`, {
      method: 'POST',
      body: JSON.stringify({ content, attributes: { topic, sub_topic: subTopic } }),
    });
    return response.data!.id;
  }

  async profile(
    maxTokenSize = 1000,
    preferTopics?: string[],
    onlyTopics?: string[],
    maxSubtopicSize?: number,
    topicLimits?: Record<string, number>,
  ): Promise<UserProfile[]> {
    const params = new URLSearchParams();

    params.append('max_token_size', maxTokenSize.toString());
    if (preferTopics !== undefined && preferTopics.length > 0) {
      preferTopics.forEach((topic) => {
        params.append('prefer_topics', topic);
      });
    }
    if (onlyTopics !== undefined && onlyTopics.length > 0) {
      onlyTopics.forEach((topic) => {
        params.append('only_topics', topic);
      });
    }
    if (maxSubtopicSize !== undefined) {
      params.append('max_subtopic_size', maxSubtopicSize.toString());
    }
    if (topicLimits !== undefined) {
      params.append('topic_limits', JSON.stringify(topicLimits));
    }

    const response = await this.projectClient.fetch<ProfileResponse>(
      `/users/profile/${this.userId}?${params.toString()}`,
    );
    return response.data!.profiles.reduce((acc, cur) => {
      acc.push({
        id: cur.id,
        content: cur.content,
        topic: cur.attributes.topic || 'NONE',
        sub_topic: cur.attributes.sub_topic || 'NONE',
        created_at: new Date(cur.created_at),
        updated_at: new Date(cur.updated_at),
      });
      return acc;
    }, [] as UserProfile[]);
  }

  async updateProfile(profileId: string, content: string, topic: string, subTopic: string): Promise<boolean> {
    await this.projectClient.fetch(`/users/profile/${this.userId}/${profileId}`, {
      method: 'PUT',
      body: JSON.stringify({ content, attributes: { topic, sub_topic: subTopic } }),
    });
    return true;
  }

  async deleteProfile(profileId: string): Promise<boolean> {
    await this.projectClient.fetch(`/users/profile/${this.userId}/${profileId}`, { method: 'DELETE' });
    return true;
  }

  async event(topk = 10, maxTokenSize?: number): Promise<UserEvent[]> {
    const params = new URLSearchParams();

    params.append('topk', topk.toString());
    if (maxTokenSize !== undefined) {
      params.append('max_token_size', maxTokenSize.toString());
    }

    const response = await this.projectClient.fetch<EventResponse>(
      `/users/event/${this.userId}?${params.toString()}`,
    );

    return response.data!.events.map((e) => UserEvent.parse(e));
  }

  async updateEvent(eventId: string, eventData: UserEvent): Promise<boolean> {
    await this.projectClient.fetch(`/users/event/${this.userId}/${eventId}`, {
      method: 'PUT',
      body: JSON.stringify(eventData),
    });
    return true;
  }

  async deleteEvent(eventId: string): Promise<boolean> {
    await this.projectClient.fetch(`/users/event/${this.userId}/${eventId}`, { method: 'DELETE' });
    return true;
  }

  async searchEvent(
    query: string,
    topk = 10,
    similarityThreshold = 0.2,
    timeRangeInDays = 180,
  ): Promise<UserEvent[]> {
    const params = new URLSearchParams();
    params.append('query', query);
    params.append('topk', topk.toString());
    params.append('similarity_threshold', similarityThreshold.toString());
    params.append('time_range_in_days', timeRangeInDays.toString());

    const response = await this.projectClient.fetch<EventResponse>(
      `/users/event/search/${this.userId}?${params.toString()}`,
    );
    return response.data!.events.map((e) => UserEvent.parse(e));
  }

  async searchEventGist(
    query: string,
    topk = 10,
    similarityThreshold = 0.2,
    timeRangeInDays = 180,
  ): Promise<UserGistEvent[]> {
    const params = new URLSearchParams();
    params.append('query', query);
    params.append('topk', topk.toString());
    params.append('similarity_threshold', similarityThreshold.toString());
    params.append('time_range_in_days', timeRangeInDays.toString());

    const response = await this.projectClient.fetch<GistEventResponse>(
      `/users/event_gist/search/${this.userId}?${params.toString()}`,
    );
    return response.data!.events.map((e) => UserGistEvent.parse(e));
  }

  async context(
    maxTokenSize = 1000,
    maxSubtopicSize?: number,
    preferTopics?: string[],
    onlyTopics?: string[],
    topicLimits?: Record<string, number>,
    profileEventRatio?: number,
    requireEventSummary?: boolean,
    chats?: OpenAICompatibleMessage[],
    eventSimilarityThreshold?: number,
    customizeContextPrompt?: string,
    fullProfileAndOnlySearchEvent?: boolean,
    fillWindowWithEvents?: boolean,
  ): Promise<string> {
    const params = new URLSearchParams();

    params.append('max_token_size', maxTokenSize.toString());
    if (maxSubtopicSize !== undefined) {
      params.append('max_subtopic_size', maxSubtopicSize.toString());
    }
    if (preferTopics !== undefined && preferTopics.length > 0) {
      preferTopics.forEach((topic) => {
        params.append('prefer_topics', topic);
      });
    }
    if (onlyTopics !== undefined && onlyTopics.length > 0) {
      onlyTopics.forEach((topic) => {
        params.append('only_topics', topic);
      });
    }
    if (topicLimits !== undefined) {
      params.append('topic_limits', JSON.stringify(topicLimits));
    }
    if (profileEventRatio !== undefined) {
      params.append('profile_event_ratio', profileEventRatio.toString());
    }
    if (requireEventSummary !== undefined) {
      params.append('require_event_summary', requireEventSummary.toString());
    }
    if (chats !== undefined && chats.length > 0) {
      params.append('chats_str', JSON.stringify(chats));
    }
    if (eventSimilarityThreshold !== undefined) {
      params.append('event_similarity_threshold', eventSimilarityThreshold.toString());
    }
    if (customizeContextPrompt !== undefined) {
      params.append('customize_context_prompt', customizeContextPrompt);
    }
    if (fullProfileAndOnlySearchEvent !== undefined) {
      params.append('full_profile_and_only_search_event', fullProfileAndOnlySearchEvent.toString());
    }
    if (fillWindowWithEvents !== undefined) {
      params.append('fill_window_with_events', fillWindowWithEvents.toString());
    }

    const response = await this.projectClient.fetch<ContextResponse>(
      `/users/context/${this.userId}?${params.toString()}`,
    );
    return response.data!.context;
  }
}

import { Blob, BlobType, UserProfile, IMemoBaseClient, IdResponse, ProfileResponse } from './types';

export class User {
    constructor(
        private readonly userId: string,
        private readonly projectClient: IMemoBaseClient,
        public readonly fields?: Record<string, any>
    ) { }

    async insert(blobData: Blob): Promise<string> {
        const response = await this.projectClient.fetch<IdResponse>(
            `/blobs/insert/${this.userId}`,
            {
                method: 'POST',
                body: JSON.stringify({
                    blob_type: blobData.type,
                    fields: blobData.fields,
                    blob_data: blobData
                })
            }
        );
        return response.data!.id;
    }

    async get(blobId: string): Promise<Blob> {
        const response = await this.projectClient.fetch<Blob>(
            `/blobs/${this.userId}/${blobId}`
        );
        return response.data as Blob;
    }

    async getAll(blobType: BlobType, page = 0, pageSize = 10): Promise<string[]> {
        const response = await this.projectClient.fetch<{ ids: string[] }>(
            `/users/blobs/${this.userId}/${blobType}?page=${page}&page_size=${pageSize}`
        );
        return response.data!.ids;
    }

    async delete(blobId: string): Promise<boolean> {
        await this.projectClient.fetch(
            `/blobs/${this.userId}/${blobId}`,
            { method: 'DELETE' }
        );
        return true;
    }

    async flush(blobType: BlobType = BlobType.Chat): Promise<boolean> {
        await this.projectClient.fetch(
            `/users/buffer/${this.userId}/${blobType}`,
            { method: 'POST' }
        );
        return true;
    }

    async profile(): Promise<UserProfile[]> {
        const response = await this.projectClient.fetch<ProfileResponse>(
            `/users/profile/${this.userId}`
        );
        return response.data!.profiles.map((p: any) => ({
            updated_at: new Date(p.updated_at),
            topic: p.attributes.topic || 'NONE',
            sub_topic: p.attributes.sub_topic || 'NONE',
            content: p.content
        }));
    }

    async deleteProfile(profileId: string): Promise<boolean> {
        await this.projectClient.fetch(
            `/users/profile/${this.userId}/${profileId}`,
            { method: 'DELETE' }
        );
        return true;
    }
} 
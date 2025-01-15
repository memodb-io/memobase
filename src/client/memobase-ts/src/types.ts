import { z } from "zod";

export type HttpUrl = string;

export enum BlobType {
    Chat = "chat",
    Doc = "doc",
    Image = "image",
    Code = "code",
    Transcript = "transcript"
}

export interface OpenAICompatibleMessage {
    role: "user" | "assistant";
    content: string;
    alias?: string;
    created_at?: string;
}

export interface TranscriptStamp {
    content: string;
    start_timestamp_in_seconds: number;
    end_time_timestamp_in_seconds?: number;
    speaker?: string;
}

export interface BaseBlob {
    type: BlobType;
    fields?: Record<string, any>;
    created_at?: Date;
}

export interface ChatBlob extends BaseBlob {
    type: BlobType.Chat;
    messages: OpenAICompatibleMessage[];
}

export interface DocBlob extends BaseBlob {
    type: BlobType.Doc;
    content: string;
}

export interface CodeBlob extends BaseBlob {
    type: BlobType.Code;
    content: string;
    language?: string;
}

export interface ImageBlob extends BaseBlob {
    type: BlobType.Image;
    url?: string;
    base64?: string;
}

export interface TranscriptBlob extends BaseBlob {
    type: BlobType.Transcript;
    transcripts: TranscriptStamp[];
}

export type Blob = ChatBlob | DocBlob | CodeBlob | ImageBlob | TranscriptBlob;

export interface UserProfile {
    updated_at: Date;
    topic: string;
    sub_topic: string;
    content: string;
}

export interface BaseResponse<T = any> {
    data?: T;
    errmsg: string;
    errno: number;
}

export interface IMemoBaseClient {
    fetch<T>(path: string, init?: RequestInit): Promise<BaseResponse<T>>;
}

export interface IdResponse {
    id: string;
}

export interface ProfileResponse {
    profiles: Array<{
        updated_at: string;
        attributes: {
            topic: string;
            sub_topic: string;
        };
        content: string;
    }>;
}
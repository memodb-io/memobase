package blob

import (
	"time"
)

type BlobType string

const (
	ChatType      BlobType = "chat"
	DocType       BlobType = "doc"
	ImageType     BlobType = "image"
	CodeType      BlobType = "code"
	TranscriptType BlobType = "transcript"
)

type OpenAICompatibleMessage struct {
	Role      string     `json:"role"`
	Content   string     `json:"content"`
	Alias     *string    `json:"alias,omitempty"`
	CreatedAt *string    `json:"created_at,omitempty"`
}

type Blob struct {
	Type      BlobType              `json:"type"`
	Fields    map[string]interface{} `json:"fields,omitempty"`
	CreatedAt *time.Time            `json:"created_at,omitempty"`
}

type ChatBlob struct {
	Blob
	Messages []OpenAICompatibleMessage `json:"messages"`
}

type DocBlob struct {
	Blob
	Content string `json:"content"`
}

type CodeBlob struct {
	Blob
	Content  string  `json:"content"`
	Language *string `json:"language,omitempty"`
}

type ImageBlob struct {
	Blob
	URL    *string `json:"url,omitempty"`
	Base64 *string `json:"base64,omitempty"`
}

type TranscriptStamp struct {
	Content                 string   `json:"content"`
	StartTimestampInSeconds float64  `json:"start_timestamp_in_seconds"`
	EndTimeTimestampInSeconds *float64 `json:"end_time_timestamp_in_seconds,omitempty"`
	Speaker                 *string   `json:"speaker,omitempty"`
}

type TranscriptBlob struct {
	Blob
	Transcripts []TranscriptStamp `json:"transcripts"`
}

type BlobData struct {
	BlobType  BlobType               `json:"blob_type"`
	BlobData  map[string]interface{} `json:"blob_data"`
	Fields    map[string]interface{} `json:"fields,omitempty"`
	CreatedAt *time.Time            `json:"created_at,omitempty"`
	UpdatedAt *time.Time            `json:"updated_at,omitempty"`
} 
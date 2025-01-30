package blob

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"
)

type BlobType string

const (
	ChatType       BlobType = "chat"
	DocType        BlobType = "doc"
	ImageType      BlobType = "image"
	CodeType       BlobType = "code"
	TranscriptType BlobType = "transcript"
)

// BlobInterface defines the common behavior for all blob types
type BlobInterface interface {
	GetType() BlobType
	GetFields() map[string]interface{}
	GetCreatedAt() *time.Time
	GetBlobData() map[string]interface{}
}

// BaseBlob contains common fields for all blob types
type BaseBlob struct {
	Type      BlobType               `json:"type"`
	Fields    map[string]interface{} `json:"fields,omitempty"`
	CreatedAt *time.Time             `json:"created_at,omitempty"`
}

func (b *BaseBlob) GetType() BlobType {
	return b.Type
}

func (b *BaseBlob) GetFields() map[string]interface{} {
	return b.Fields
}

func (b *BaseBlob) GetCreatedAt() *time.Time {
	return b.CreatedAt
}

type OpenAICompatibleMessage struct {
	Role      string  `json:"role"`
	Content   string  `json:"content"`
	Alias     *string `json:"alias,omitempty"`
	CreatedAt *string `json:"created_at,omitempty"`
}

type ChatBlob struct {
	BaseBlob
	Messages []OpenAICompatibleMessage `json:"messages"`
}

func (b *ChatBlob) GetBlobData() map[string]interface{} {
	return map[string]interface{}{
		"messages": b.Messages,
	}
}

type DocBlob struct {
	BaseBlob
	Content string `json:"content"`
}

func (b *DocBlob) GetBlobData() map[string]interface{} {
	return map[string]interface{}{
		"content": b.Content,
	}
}

type CodeBlob struct {
	BaseBlob
	Content  string  `json:"content"`
	Language *string `json:"language,omitempty"`
}

func (b *CodeBlob) GetBlobData() map[string]interface{} {
	return map[string]interface{}{
		"content":  b.Content,
		"language": b.Language,
	}
}

type ImageBlob struct {
	BaseBlob
	URL    *string `json:"url,omitempty"`
	Base64 *string `json:"base64,omitempty"`
}

func (b *ImageBlob) GetBlobData() map[string]interface{} {
	return map[string]interface{}{
		"url":    b.URL,
		"base64": b.Base64,
	}
}

type TranscriptStamp struct {
	Content                   string   `json:"content"`
	StartTimestampInSeconds   float64  `json:"start_timestamp_in_seconds"`
	EndTimeTimestampInSeconds *float64 `json:"end_time_timestamp_in_seconds,omitempty"`
	Speaker                   *string  `json:"speaker,omitempty"`
}

type TranscriptBlob struct {
	BaseBlob
	Transcripts []TranscriptStamp `json:"transcripts"`
}

func (b *TranscriptBlob) GetBlobData() map[string]interface{} {
	return map[string]interface{}{
		"transcripts": b.Transcripts,
	}
}

// Add this custom time type
type JSONTime time.Time

func (t *JSONTime) UnmarshalJSON(b []byte) error {
	s := strings.Trim(string(b), "\"")
	if s == "null" {
		return nil
	}

	// Try different time formats
	formats := []string{
		time.RFC3339,
		time.RFC3339Nano,
		"2006-01-02T15:04:05.999999",
	}

	var err error
	for _, format := range formats {
		pt, parseErr := time.Parse(format, s)
		if parseErr == nil {
			*t = JSONTime(pt)
			return nil
		}
		err = parseErr
	}
	return err
}

// Update BlobData to use JSONTime
type BlobData struct {
	BlobType  BlobType               `json:"blob_type"`
	BlobData  map[string]interface{} `json:"blob_data"`
	Fields    map[string]interface{} `json:"fields,omitempty"`
	CreatedAt *JSONTime              `json:"created_at,omitempty"`
	UpdatedAt *JSONTime              `json:"updated_at,omitempty"`
}

// Update ToBlob to convert JSONTime back to time.Time
func (bd *BlobData) ToBlob() (BlobInterface, error) {
	baseBlob := BaseBlob{
		Type:   bd.BlobType,
		Fields: bd.Fields,
	}
	if bd.CreatedAt != nil {
		t := time.Time(*bd.CreatedAt)
		baseBlob.CreatedAt = &t
	}

	blobDataJSON, err := json.Marshal(bd.BlobData)
	if err != nil {
		return nil, err
	}

	switch bd.BlobType {
	case ChatType:
		blob := &ChatBlob{BaseBlob: baseBlob}
		err = json.Unmarshal(blobDataJSON, &blob)
		return blob, err

	case DocType:
		blob := &DocBlob{BaseBlob: baseBlob}
		err = json.Unmarshal(blobDataJSON, &blob)
		return blob, err

	case CodeType:
		blob := &CodeBlob{BaseBlob: baseBlob}
		err = json.Unmarshal(blobDataJSON, &blob)
		return blob, err

	case ImageType:
		blob := &ImageBlob{BaseBlob: baseBlob}
		err = json.Unmarshal(blobDataJSON, &blob)
		return blob, err

	case TranscriptType:
		blob := &TranscriptBlob{BaseBlob: baseBlob}
		err = json.Unmarshal(blobDataJSON, &blob)
		return blob, err

	default:
		return nil, fmt.Errorf("unknown blob type: %s", bd.BlobType)
	}
}

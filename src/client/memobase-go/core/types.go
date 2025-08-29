package core

import (
	"time"

	"github.com/google/uuid"
)

type UserProfileData struct {
	ID         uuid.UUID `json:"id"`
	Content    string    `json:"content"`
	Attributes struct {
		Topic    string `json:"topic"`
		SubTopic string `json:"sub_topic"`
	} `json:"attributes"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type ProfileDelta struct {
	Content    string                 `json:"content"`
	Attributes map[string]interface{} `json:"attributes"`
}

type EventTag struct {
	Tag   string `json:"tag"`
	Value string `json:"value"`
}

type EventData struct {
	ProfileDelta []ProfileDelta `json:"profile_delta"`
	EventTip     string         `json:"event_tip,omitempty"`
	EventTags    []EventTag     `json:"event_tags,omitempty"`
}

type UserEventData struct {
	ID         uuid.UUID `json:"id"`
	EventData  EventData `json:"event_data"`
	CreatedAt  time.Time `json:"created_at"`
	UpdatedAt  time.Time `json:"updated_at"`
	Similarity float64   `json:"similarity,omitempty"`
}

// UserGistEventData represents a gist event with minimal data
type UserGistEventData struct {
	ID         uuid.UUID `json:"id"`
	GistData   struct {
		Content string `json:"content"`
	} `json:"gist_data"`
	CreatedAt  time.Time `json:"created_at"`
	UpdatedAt  time.Time `json:"updated_at"`
	Similarity float64   `json:"similarity,omitempty"`
}

// BufferStatus represents the status of buffer operations
type BufferStatus string

const (
	BufferStatusPending BufferStatus = "pending"
	BufferStatusProcessing BufferStatus = "processing"
	BufferStatusCompleted BufferStatus = "completed"
	BufferStatusFailed    BufferStatus = "failed"
)

// BufferCapacity represents buffer capacity information
type BufferCapacity struct {
	IDs     []string     `json:"ids"`
	Status  BufferStatus `json:"status"`
	Count   int          `json:"count"`
	Capacity int          `json:"capacity"`
}

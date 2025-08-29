package core

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestUserGistEventData(t *testing.T) {
	// Test UserGistEventData structure
	eventID := uuid.New()
	now := time.Now()

	event := UserGistEventData{
		ID: eventID,
		GistData: struct {
			Content string `json:"content"`
		}{
			Content: "test gist content",
		},
		CreatedAt:  now,
		UpdatedAt:  now,
		Similarity: 0.95,
	}

	// Test JSON marshaling
	jsonData, err := json.Marshal(event)
	assert.NoError(t, err)
	assert.Contains(t, string(jsonData), "test gist content")
	assert.Contains(t, string(jsonData), eventID.String())

	// Test JSON unmarshaling
	var unmarshaledEvent UserGistEventData
	err = json.Unmarshal(jsonData, &unmarshaledEvent)
	assert.NoError(t, err)
	assert.Equal(t, event.ID, unmarshaledEvent.ID)
	assert.Equal(t, event.GistData.Content, unmarshaledEvent.GistData.Content)
	assert.Equal(t, event.Similarity, unmarshaledEvent.Similarity)
}

func TestBufferStatus(t *testing.T) {
	// Test BufferStatus constants
	assert.Equal(t, BufferStatus("pending"), BufferStatusPending)
	assert.Equal(t, BufferStatus("processing"), BufferStatusProcessing)
	assert.Equal(t, BufferStatus("completed"), BufferStatusCompleted)
	assert.Equal(t, BufferStatus("failed"), BufferStatusFailed)
}

func TestBufferCapacity(t *testing.T) {
	// Test BufferCapacity structure
	capacity := BufferCapacity{
		IDs:      []string{"id1", "id2", "id3"},
		Status:   BufferStatusCompleted,
		Count:    3,
		Capacity: 10,
	}

	// Test JSON marshaling
	jsonData, err := json.Marshal(capacity)
	assert.NoError(t, err)
	assert.Contains(t, string(jsonData), "completed")
	assert.Contains(t, string(jsonData), "id1")

	// Test JSON unmarshaling
	var unmarshaledCapacity BufferCapacity
	err = json.Unmarshal(jsonData, &unmarshaledCapacity)
	assert.NoError(t, err)
	assert.Equal(t, capacity.IDs, unmarshaledCapacity.IDs)
	assert.Equal(t, capacity.Status, unmarshaledCapacity.Status)
	assert.Equal(t, capacity.Count, unmarshaledCapacity.Count)
	assert.Equal(t, capacity.Capacity, unmarshaledCapacity.Capacity)
}

func TestUserEventData(t *testing.T) {
	// Test existing UserEventData structure
	eventID := uuid.New()
	now := time.Now()

	event := UserEventData{
		ID: eventID,
		EventData: EventData{
			ProfileDelta: []ProfileDelta{
				{
					Content: "test content",
					Attributes: map[string]interface{}{
						"topic": "test",
					},
				},
			},
			EventTip: "test tip",
			EventTags: []EventTag{
				{Tag: "type", Value: "test"},
			},
		},
		CreatedAt:  now,
		UpdatedAt:  now,
		Similarity: 0.85,
	}

	// Test JSON marshaling
	jsonData, err := json.Marshal(event)
	assert.NoError(t, err)
	assert.Contains(t, string(jsonData), "test content")
	assert.Contains(t, string(jsonData), "test tip")

	// Test JSON unmarshaling
	var unmarshaledEvent UserEventData
	err = json.Unmarshal(jsonData, &unmarshaledEvent)
	assert.NoError(t, err)
	assert.Equal(t, event.ID, unmarshaledEvent.ID)
	assert.Equal(t, event.EventData.EventTip, unmarshaledEvent.EventData.EventTip)
	assert.Equal(t, len(event.EventData.ProfileDelta), len(unmarshaledEvent.EventData.ProfileDelta))
	assert.Equal(t, event.Similarity, unmarshaledEvent.Similarity)
}

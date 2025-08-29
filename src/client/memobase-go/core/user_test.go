package core

import (
	"testing"

	"github.com/memodb-io/memobase/src/client/memobase-go/blob"
	"github.com/stretchr/testify/assert"
)

func TestBlobCRUD(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID, _ := client.AddUser(nil, "")
	user, _ := client.GetUser(userID, false)

	// Insert Blob
	doc := &blob.DocBlob{
		BaseBlob: blob.BaseBlob{Type: blob.DocType},
		Content:  "test content",
	}
	blobID, err := user.Insert(doc, false)
	assert.NoError(t, err)
	assert.NotEmpty(t, blobID)

	// Get Blob
	retrievedBlob, err := user.Get(blobID)
	assert.NoError(t, err)
	assert.NotNil(t, retrievedBlob)
	retrievedDoc, ok := retrievedBlob.(*blob.DocBlob)
	assert.True(t, ok)
	assert.Equal(t, "test content", retrievedDoc.Content)

	// Get All Blobs
	blobs, err := user.GetAll(blob.DocType, 0, 10)
	assert.NoError(t, err)
	assert.Len(t, blobs, 1)

	// Delete Blob
	err = user.Delete(blobID)
	assert.NoError(t, err)

	// Verify blob is deleted
	_, err = user.Get(blobID)
	assert.Error(t, err)

	client.DeleteUser(userID)
}

func TestProfileCRUD(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID, _ := client.AddUser(nil, "")
	user, _ := client.GetUser(userID, false)

	// Add Profile
	profileID, err := user.AddProfile("test content", "test_topic", "test_sub_topic")
	assert.NoError(t, err)
	assert.NotEmpty(t, profileID)

	// Get Profile
	profiles, err := user.Profile(nil)
	assert.NoError(t, err)
	assert.Len(t, profiles, 1)
	assert.Equal(t, "test content", profiles[0].Content)

	// Update Profile
	err = user.UpdateProfile(profileID, "updated content", "updated_topic", "updated_sub_topic")
	assert.NoError(t, err)

	// Get Profile again to check update
	profiles, err = user.Profile(nil)
	assert.NoError(t, err)
	assert.Len(t, profiles, 1)
	assert.Equal(t, "updated content", profiles[0].Content)

	// Delete Profile
	err = user.DeleteProfile(profileID)
	assert.NoError(t, err)

	// Verify profile is deleted
	profiles, err = user.Profile(nil)
	assert.NoError(t, err)
	assert.Len(t, profiles, 0)

	client.DeleteUser(userID)
}

func TestEventCRUD(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID, _ := client.AddUser(nil, "")
	user, _ := client.GetUser(userID, false)

	// Insert chat to generate event
	chat := &blob.ChatBlob{
		BaseBlob: blob.BaseBlob{Type: blob.ChatType},
		Messages: []blob.OpenAICompatibleMessage{
			{Role: "user", Content: "Hello"},
			{Role: "assistant", Content: "Hi there"},
		},
	}
	_, err := user.Insert(chat, false)
	assert.NoError(t, err)

	err = user.Flush(blob.ChatType, true)
	assert.NoError(t, err)

	// Get Events
	events, err := user.Event(10, nil, false)
	assert.NoError(t, err)
	assert.NotEmpty(t, events)

	// Update Event
	eventID := events[0].ID.String()
	err = user.UpdateEvent(eventID, map[string]interface{}{"event_tip": "test tip"})
	assert.NoError(t, err)

	// Get Event again to check update
	events, err = user.Event(10, nil, false)
	assert.NoError(t, err)
	assert.Equal(t, "test tip", events[0].EventData.EventTip)

	// Delete Event
	err = user.DeleteEvent(eventID)
	assert.NoError(t, err)

	// Verify event is deleted
	events, err = user.Event(10, nil, false)
	assert.NoError(t, err)
	assert.Empty(t, events)

	client.DeleteUser(userID)
}

func TestContext(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID, _ := client.AddUser(nil, "")
	user, _ := client.GetUser(userID, false)

	// Insert chat to generate context
	chat := &blob.ChatBlob{
		BaseBlob: blob.BaseBlob{Type: blob.ChatType},
		Messages: []blob.OpenAICompatibleMessage{
			{Role: "user", Content: "My name is John"},
			{Role: "assistant", Content: "Nice to meet you John"},
		},
	}
	_, err := user.Insert(chat, true)
	assert.NoError(t, err)

	context, err := user.Context(nil)
	assert.NoError(t, err)
	assert.NotEmpty(t, context)

	client.DeleteUser(userID)
}

func TestSearchEvent(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID, _ := client.AddUser(nil, "")
	user, _ := client.GetUser(userID, false)

	// Insert chat to generate event
	chat := &blob.ChatBlob{
		BaseBlob: blob.BaseBlob{Type: blob.ChatType},
		Messages: []blob.OpenAICompatibleMessage{
			{Role: "user", Content: "I live in New York"},
			{Role: "assistant", Content: "That's great"},
		},
	}
	_, err := user.Insert(chat, false)
	assert.NoError(t, err)

	err = user.Flush(blob.ChatType, true)
	assert.NoError(t, err)

	events, err := user.SearchEvent("New York", 10, 0.2, 7)
	assert.NoError(t, err)
	assert.NotEmpty(t, events)

	client.DeleteUser(userID)
}

func TestSearchEventGist(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID, _ := client.AddUser(nil, "")
	user, _ := client.GetUser(userID, false)

	// Insert chat to generate event
	chat := &blob.ChatBlob{
		BaseBlob: blob.BaseBlob{Type: blob.ChatType},
		Messages: []blob.OpenAICompatibleMessage{
			{Role: "user", Content: "I work as a software engineer"},
			{Role: "assistant", Content: "That's interesting"},
		},
	}
	_, err := user.Insert(chat, false)
	assert.NoError(t, err)

	err = user.Flush(blob.ChatType, true)
	assert.NoError(t, err)

	// Search for event gists
	gistEvents, err := user.SearchEventGist("software engineer", 10, 0.2, 7)
	// Note: This might return empty results in test environment, so we check for no error
	assert.NoError(t, err)
	assert.NotNil(t, gistEvents)

	client.DeleteUser(userID)
}

func TestContextOptions(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID, _ := client.AddUser(nil, "")
	user, _ := client.GetUser(userID, false)

	// Insert chat to generate context
	chat := &blob.ChatBlob{
		BaseBlob: blob.BaseBlob{Type: blob.ChatType},
		Messages: []blob.OpenAICompatibleMessage{
			{Role: "user", Content: "My name is John"},
			{Role: "assistant", Content: "Nice to meet you John"},
		},
	}
	_, err := user.Insert(chat, true)
	assert.NoError(t, err)

	// Test context with options
	options := &ContextOptions{
		MaxTokenSize:        500,
		PreferTopics:        []string{"personal"},
		RequireEventSummary: &[]bool{true}[0],
	}

	context, err := user.Context(options)
	assert.NoError(t, err)
	assert.NotEmpty(t, context)

	client.DeleteUser(userID)
}

func TestAsyncOperations(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID, _ := client.AddUser(nil, "")
	user, _ := client.GetUser(userID, false)

	// Test async insert
	doc := &blob.DocBlob{
		BaseBlob: blob.BaseBlob{Type: blob.DocType},
		Content:  "async test content",
	}

	// Test sync vs async insert
	syncBlobID, err := user.Insert(doc, true) // sync
	assert.NoError(t, err)
	assert.NotEmpty(t, syncBlobID)

	asyncBlobID, err := user.Insert(doc, false) // async
	assert.NoError(t, err)
	assert.NotEmpty(t, asyncBlobID)

	// Test async flush
	err = user.Flush(blob.DocType, false) // async
	assert.NoError(t, err)

	err = user.Flush(blob.DocType, true) // sync
	assert.NoError(t, err)

	client.DeleteUser(userID)
}

func TestBuffer(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID, _ := client.AddUser(nil, "")
	user, _ := client.GetUser(userID, false)

	// Insert chat to buffer
	chat := &blob.ChatBlob{
		BaseBlob: blob.BaseBlob{Type: blob.ChatType},
		Messages: []blob.OpenAICompatibleMessage{
			{Role: "user", Content: "Hello"},
		},
	}
	_, err := user.Insert(chat, false)
	assert.NoError(t, err)

	ids, err := user.Buffer(blob.ChatType, "idle")
	assert.NoError(t, err)
	assert.NotEmpty(t, ids)

	client.DeleteUser(userID)
}

package core

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/memodb-io/memobase/src/client/memobase-go/blob"
)

func TestUser_Insert(t *testing.T) {
	tests := []struct {
		name       string
		blobData   blob.BlobInterface
		statusCode int
		response   map[string]interface{}
		wantID     string
		wantErr    bool
	}{
		{
			name: "successful blob insertion",
			blobData: &blob.ChatBlob{
				BaseBlob: blob.BaseBlob{
					Type: blob.ChatType,
					Fields: map[string]interface{}{
						"test": "value",
					},
				},
				Messages: []blob.OpenAICompatibleMessage{
					{
						Role:    "user",
						Content: "test",
					},
				},
			},
			statusCode: http.StatusOK,
			response: map[string]interface{}{
				"errno":  0,
				"errmsg": "",
				"data":   map[string]interface{}{"id": "test-blob-id"},
			},
			wantID:  "test-blob-id",
			wantErr: false,
		},
		{
			name: "server error",
			blobData: &blob.ChatBlob{
				BaseBlob: blob.BaseBlob{
					Type: blob.ChatType,
					Fields: map[string]interface{}{
						"test": "value",
					},
				},
				Messages: []blob.OpenAICompatibleMessage{
					{
						Role:    "user",
						Content: "test",
					},
				},
			},
			statusCode: http.StatusInternalServerError,
			response: map[string]interface{}{
				"errno":  500,
				"errmsg": "internal server error",
				"data":   nil,
			},
			wantID:  "",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				// Verify request
				if r.Method != http.MethodPost {
					t.Errorf("unexpected method: %s", r.Method)
				}
				expectedPath := "/api/v1/blobs/insert/test-user"
				if r.URL.Path != expectedPath {
					t.Errorf("unexpected path: got %s, want %s", r.URL.Path, expectedPath)
				}

				// Verify request body
				body, _ := io.ReadAll(r.Body)
				var reqBody map[string]interface{}
				if err := json.Unmarshal(body, &reqBody); err != nil {
					t.Errorf("failed to parse request body: %v", err)
				}
				if reqBody["blob_type"] != string(tt.blobData.GetType()) {
					t.Errorf("unexpected blob_type: got %v, want %v", reqBody["blob_type"], tt.blobData.GetType())
				}

				// Send response
				w.WriteHeader(tt.statusCode)
				json.NewEncoder(w).Encode(tt.response)
			}))
			defer server.Close()

			client, _ := NewMemoBaseClient(server.URL, "test-key")
			user := &User{
				UserID:        "test-user",
				ProjectClient: client,
			}

			gotID, err := user.Insert(tt.blobData)
			if (err != nil) != tt.wantErr {
				t.Errorf("User.Insert() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if gotID != tt.wantID {
				t.Errorf("User.Insert() = %v, want %v", gotID, tt.wantID)
			}
		})
	}
}

func TestUser_GetAll(t *testing.T) {
	tests := []struct {
		name       string
		blobType   blob.BlobType
		page       int
		pageSize   int
		statusCode int
		response   map[string]interface{}
		wantIDs    []string
		wantErr    bool
	}{
		{
			name:       "successful get all blobs",
			blobType:   blob.ChatType,
			page:       0,
			pageSize:   10,
			statusCode: http.StatusOK,
			response: map[string]interface{}{
				"errno":  0,
				"errmsg": "",
				"data": map[string]interface{}{
					"ids": []interface{}{"id1", "id2", "id3"},
				},
			},
			wantIDs: []string{"id1", "id2", "id3"},
			wantErr: false,
		},
		{
			name:       "server error",
			blobType:   blob.ChatType,
			page:       0,
			pageSize:   10,
			statusCode: http.StatusInternalServerError,
			response: map[string]interface{}{
				"errno":  500,
				"errmsg": "internal server error",
				"data":   nil,
			},
			wantIDs: nil,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				// Verify request
				if r.Method != http.MethodGet {
					t.Errorf("unexpected method: %s", r.Method)
				}
				expectedPath := fmt.Sprintf("/api/v1/users/blobs/test-user/%s", tt.blobType)
				if r.URL.Path != expectedPath {
					t.Errorf("unexpected path: got %s, want %s", r.URL.Path, expectedPath)
				}

				// Send response
				w.WriteHeader(tt.statusCode)
				json.NewEncoder(w).Encode(tt.response)
			}))
			defer server.Close()

			client, _ := NewMemoBaseClient(server.URL, "test-key")
			user := &User{
				UserID:        "test-user",
				ProjectClient: client,
			}

			gotIDs, err := user.GetAll(tt.blobType, tt.page, tt.pageSize)
			if (err != nil) != tt.wantErr {
				t.Errorf("User.GetAll() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				if len(gotIDs) != len(tt.wantIDs) {
					t.Errorf("User.GetAll() returned %d IDs, want %d", len(gotIDs), len(tt.wantIDs))
					return
				}
				for i, id := range gotIDs {
					if id != tt.wantIDs[i] {
						t.Errorf("User.GetAll()[%d] = %v, want %v", i, id, tt.wantIDs[i])
					}
				}
			}
		})
	}
}

func TestUser_Profile(t *testing.T) {
	tests := []struct {
		name       string
		statusCode int
		response   map[string]interface{}
		want       []UserProfile
		wantErr    bool
	}{
		{
			name:       "successful get profiles",
			statusCode: http.StatusOK,
			response: map[string]interface{}{
				"errno":  0,
				"errmsg": "",
				"data": map[string]interface{}{
					"profiles": []map[string]interface{}{
						{
							"id":         "test-id",
							"updated_at": "2025-01-30T11:24:56.446991",
							"created_at": "2025-01-30T11:24:56.446991",
							"content":    "test content",
							"attributes": map[string]interface{}{
								"topic":     "test topic",
								"sub_topic": "test subtopic",
							},
						},
					},
				},
			},
			want: []UserProfile{
				{
					ID:      "test-id",
					Content: "test content",
					Attributes: struct {
						Topic    string `json:"topic"`
						SubTopic string `json:"sub_topic"`
					}{
						Topic:    "test topic",
						SubTopic: "test subtopic",
					},
				},
			},
			wantErr: false,
		},
		{
			name:       "server error",
			statusCode: http.StatusInternalServerError,
			response: map[string]interface{}{
				"errno":  500,
				"errmsg": "internal server error",
				"data":   nil,
			},
			want:    nil,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				// Verify request
				if r.Method != http.MethodGet {
					t.Errorf("unexpected method: %s", r.Method)
				}
				expectedPath := "/api/v1/users/profile/test-user"
				if r.URL.Path != expectedPath {
					t.Errorf("unexpected path: got %s, want %s", r.URL.Path, expectedPath)
				}

				// Send response
				w.WriteHeader(tt.statusCode)
				json.NewEncoder(w).Encode(tt.response)
			}))
			defer server.Close()

			client, _ := NewMemoBaseClient(server.URL, "test-key")
			user := &User{
				UserID:        "test-user",
				ProjectClient: client,
			}

			got, err := user.Profile()
			if (err != nil) != tt.wantErr {
				t.Errorf("User.Profile() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				if len(got) != len(tt.want) {
					t.Errorf("User.Profile() returned %d profiles, want %d", len(got), len(tt.want))
					return
				}
				for i, profile := range got {
					if profile.ID != tt.want[i].ID {
						t.Errorf("Profile[%d].ID = %v, want %v", i, profile.ID, tt.want[i].ID)
					}
					if profile.Attributes.Topic != tt.want[i].Attributes.Topic {
						t.Errorf("Profile[%d].Attributes.Topic = %v, want %v", i, profile.Attributes.Topic, tt.want[i].Attributes.Topic)
					}
					if profile.Attributes.SubTopic != tt.want[i].Attributes.SubTopic {
						t.Errorf("Profile[%d].Attributes.SubTopic = %v, want %v", i, profile.Attributes.SubTopic, tt.want[i].Attributes.SubTopic)
					}
					if profile.Content != tt.want[i].Content {
						t.Errorf("Profile[%d].Content = %v, want %v", i, profile.Content, tt.want[i].Content)
					}
				}
			}
		})
	}
}

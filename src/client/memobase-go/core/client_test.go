package core

import (
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestNewMemoBaseClient(t *testing.T) {
	tests := []struct {
		name      string
		projectURL string
		apiKey    string
		wantErr   bool
	}{
		{
			name:      "valid initialization",
			projectURL: "https://api.memobase.dev",
			apiKey:    "test-key",
			wantErr:   false,
		},
		{
			name:      "missing api key",
			projectURL: "https://api.memobase.dev",
			apiKey:    "",
			wantErr:   true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			client, err := NewMemoBaseClient(tt.projectURL, tt.apiKey)
			if (err != nil) != tt.wantErr {
				t.Errorf("NewMemoBaseClient() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr && client == nil {
				t.Error("NewMemoBaseClient() returned nil client")
			}
		})
	}
}

func TestMemoBaseClient_Ping(t *testing.T) {
	tests := []struct {
		name       string
		statusCode int
		response   map[string]interface{}
		want       bool
	}{
		{
			name:       "successful ping",
			statusCode: http.StatusOK,
			response: map[string]interface{}{
				"errno":  0,
				"errmsg": "",
				"data":   map[string]interface{}{},
			},
			want: true,
		},
		{
			name:       "server error",
			statusCode: http.StatusInternalServerError,
			response: map[string]interface{}{
				"errno":  500,
				"errmsg": "internal server error",
				"data":   nil,
			},
			want: false,
		},
		{
			name:       "unauthorized",
			statusCode: http.StatusUnauthorized,
			response: map[string]interface{}{
				"errno":  401,
				"errmsg": "unauthorized",
				"data":   nil,
			},
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				// Verify request
				if r.URL.Path != "/api/v1/healthcheck" {
					t.Errorf("unexpected path: %s", r.URL.Path)
				}
				if r.Method != http.MethodGet {
					t.Errorf("unexpected method: %s", r.Method)
				}
				if auth := r.Header.Get("Authorization"); auth != "Bearer test-key" {
					t.Errorf("unexpected authorization header: %s", auth)
				}

				// Send response
				w.WriteHeader(tt.statusCode)
				if tt.response != nil {
					json.NewEncoder(w).Encode(tt.response)
				}
			}))
			defer server.Close()

			client, _ := NewMemoBaseClient(server.URL, "test-key")
			if got := client.Ping(); got != tt.want {
				t.Errorf("MemoBaseClient.Ping() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestMemoBaseClient_AddUser(t *testing.T) {
	tests := []struct {
		name       string
		data       map[string]interface{}
		id         string
		statusCode int
		response   map[string]interface{}
		wantID     string
		wantErr    bool
	}{
		{
			name: "successful user creation",
			data: map[string]interface{}{"name": "test"},
			id:   "test-id",
			statusCode: http.StatusOK,
			response: map[string]interface{}{
				"errno":  0,
				"errmsg": "",
				"data":   map[string]interface{}{"id": "test-id"},
			},
			wantID:  "test-id",
			wantErr: false,
		},
		{
			name: "server error",
			data: map[string]interface{}{"name": "test"},
			id:   "test-id",
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
				if r.URL.Path != "/api/v1/users" {
					t.Errorf("unexpected path: %s", r.URL.Path)
				}
				if auth := r.Header.Get("Authorization"); auth != "Bearer test-key" {
					t.Errorf("unexpected authorization header: %s", auth)
				}

				// Verify request body
				body, _ := io.ReadAll(r.Body)
				var reqBody map[string]interface{}
				if err := json.Unmarshal(body, &reqBody); err != nil {
					t.Errorf("failed to parse request body: %v", err)
				}
				if reqBody["data"] == nil {
					t.Error("missing data field in request")
				}
				if reqBody["id"] != tt.id {
					t.Errorf("unexpected id in request: got %v, want %v", reqBody["id"], tt.id)
				}

				// Send response
				w.WriteHeader(tt.statusCode)
				json.NewEncoder(w).Encode(tt.response)
			}))
			defer server.Close()

			client, _ := NewMemoBaseClient(server.URL, "test-key")
			gotID, err := client.AddUser(tt.data, tt.id)
			if (err != nil) != tt.wantErr {
				t.Errorf("MemoBaseClient.AddUser() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if gotID != tt.wantID {
				t.Errorf("MemoBaseClient.AddUser() = %v, want %v", gotID, tt.wantID)
			}
		})
	}
} 
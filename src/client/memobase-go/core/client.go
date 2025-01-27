package core

import (
	"fmt"
	"net/http"
	"os"
	"time"

)

type MemoBaseClient struct {
	ProjectURL  string
	APIKey      string
	APIVersion  string
	BaseURL     string
	HTTPClient  *http.Client
}

func NewMemoBaseClient(projectURL string, apiKey string) (*MemoBaseClient, error) {
	if apiKey == "" {
		apiKey = os.Getenv("MEMOBASE_API_KEY")
	}
	
	if apiKey == "" {
		return nil, fmt.Errorf("api_key is required, pass it as argument or set MEMOBASE_API_KEY environment variable")
	}

	client := &MemoBaseClient{
		ProjectURL:  projectURL,
		APIKey:      apiKey,
		APIVersion:  "api/v1",
		HTTPClient: &http.Client{
			Timeout: time.Second * 60,
		},
	}
	
	client.BaseURL = fmt.Sprintf("%s/%s", projectURL, client.APIVersion)
	
	return client, nil
}

func (c *MemoBaseClient) Ping() bool {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/healthcheck", c.BaseURL))
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	
	return resp.StatusCode == http.StatusOK
}

func (c *MemoBaseClient) AddUser(data map[string]interface{}, id string) (string, error) {
	// Implementation
	return "", nil
}

func (c *MemoBaseClient) UpdateUser(userID string, data map[string]interface{}) (string, error) {
	// Implementation
	return "", nil
}

func (c *MemoBaseClient) GetUser(userID string, noGet bool) (*User, error) {
	// Implementation
	return nil, nil
}

func (c *MemoBaseClient) GetOrCreateUser(userID string) (*User, error) {
	// Implementation
	return nil, nil
}

func (c *MemoBaseClient) DeleteUser(userID string) error {
	// Implementation
	return nil
} 
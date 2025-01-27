package core

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/memodb-io/memobase/src/client/memobase-go/network"
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
	
	// Add authorization header to all requests
	client.HTTPClient.Transport = &authTransport{
		apiKey: apiKey,
		base:   http.DefaultTransport,
	}
	
	return client, nil
}

// authTransport adds authorization header to all requests
type authTransport struct {
	apiKey string
	base   http.RoundTripper
}

func (t *authTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	req.Header.Add("Authorization", fmt.Sprintf("Bearer %s", t.apiKey))
	return t.base.RoundTrip(req)
}

func (c *MemoBaseClient) Ping() bool {
	resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/healthcheck", c.BaseURL))
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	
	_, err = network.UnpackResponse(resp)
	return err == nil
}

func (c *MemoBaseClient) AddUser(data map[string]interface{}, id string) (string, error) {
	reqBody := map[string]interface{}{
		"data": data,
		"id":   id,
	}
	
	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}
	
	resp, err := c.HTTPClient.Post(
		fmt.Sprintf("%s/users", c.BaseURL),
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	
	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return "", err
	}
	
	return baseResp.Data["id"].(string), nil
}

func (c *MemoBaseClient) UpdateUser(userID string, data map[string]interface{}) (string, error) {
	reqBody := map[string]interface{}{
		"data": data,
	}
	
	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}
	
	req, err := http.NewRequest(
		http.MethodPut,
		fmt.Sprintf("%s/users/%s", c.BaseURL, userID),
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")
	
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	
	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return "", err
	}
	
	return baseResp.Data["id"].(string), nil
}

func (c *MemoBaseClient) GetUser(userID string, noGet bool) (*User, error) {
	if !noGet {
		resp, err := c.HTTPClient.Get(fmt.Sprintf("%s/users/%s", c.BaseURL, userID))
		if err != nil {
			return nil, err
		}
		defer resp.Body.Close()
		
		baseResp, err := network.UnpackResponse(resp)
		if err != nil {
			return nil, err
		}
		
		return &User{
			UserID:        userID,
			ProjectClient: c,
			Fields:        baseResp.Data,
		}, nil
	}
	
	return &User{
		UserID:        userID,
		ProjectClient: c,
	}, nil
}

func (c *MemoBaseClient) GetOrCreateUser(userID string) (*User, error) {
	user, err := c.GetUser(userID, false)
	if err != nil {
		// Try to create user if get fails
		_, err = c.AddUser(nil, userID)
		if err != nil {
			return nil, err
		}
		return &User{
			UserID:        userID,
			ProjectClient: c,
		}, nil
	}
	return user, nil
}

func (c *MemoBaseClient) DeleteUser(userID string) error {
	req, err := http.NewRequest(
		http.MethodDelete,
		fmt.Sprintf("%s/users/%s", c.BaseURL, userID),
		nil,
	)
	if err != nil {
		return err
	}
	
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	_, err = network.UnpackResponse(resp)
	return err
} 
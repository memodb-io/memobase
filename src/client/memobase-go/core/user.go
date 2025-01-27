package core

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
	
	"github.com/memodb-io/memobase/src/client/memobase-go/blob"
	"github.com/memodb-io/memobase/src/client/memobase-go/network"
)

type User struct {
	UserID         string
	ProjectClient  *MemoBaseClient
	Fields         map[string]interface{}
}

type UserProfile struct {
	UpdatedAt time.Time `json:"updated_at"`
	Topic     string    `json:"topic"`
	SubTopic  string    `json:"sub_topic"`
	Content   string    `json:"content"`
}

func (u *User) Insert(blobData blob.Blob) (string, error) {
	// Convert blob data to request format
	reqData := map[string]interface{}{
		"blob_type": blobData.Type,
		"blob_data": blobData,
		"fields":    blobData.Fields,
	}
	if blobData.CreatedAt != nil {
		reqData["created_at"] = blobData.CreatedAt
	}

	jsonData, err := json.Marshal(reqData)
	if err != nil {
		return "", err
	}

	resp, err := u.ProjectClient.HTTPClient.Post(
		fmt.Sprintf("%s/blobs/insert/%s", u.ProjectClient.BaseURL, u.UserID),
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

func (u *User) Get(blobID string) (blob.Blob, error) {
	resp, err := u.ProjectClient.HTTPClient.Get(
		fmt.Sprintf("%s/blobs/%s/%s", u.ProjectClient.BaseURL, u.UserID, blobID),
	)
	if err != nil {
		return blob.Blob{}, err
	}
	defer resp.Body.Close()

	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return blob.Blob{}, err
	}

	var blobData blob.BlobData
	jsonData, err := json.Marshal(baseResp.Data)
	if err != nil {
		return blob.Blob{}, err
	}

	if err := json.Unmarshal(jsonData, &blobData); err != nil {
		return blob.Blob{}, err
	}

	// Convert BlobData back to appropriate Blob type
	// This is a simplified version - you might need to handle different blob types
	return blob.Blob{
		Type:      blobData.BlobType,
		Fields:    blobData.Fields,
		CreatedAt: blobData.CreatedAt,
	}, nil
}

func (u *User) GetAll(blobType blob.BlobType, page int, pageSize int) ([]string, error) {
	resp, err := u.ProjectClient.HTTPClient.Get(
		fmt.Sprintf("%s/users/blobs/%s/%s?page=%d&page_size=%d",
			u.ProjectClient.BaseURL, u.UserID, blobType, page, pageSize),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return nil, err
	}

	// Handle the response data structure correctly
	data, ok := baseResp.Data["ids"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for blob IDs")
	}

	// Convert []interface{} to []string
	ids := make([]string, len(data))
	for i, v := range data {
		if str, ok := v.(string); ok {
			ids[i] = str
		} else {
			return nil, fmt.Errorf("unexpected ID type at index %d", i)
		}
	}

	return ids, nil
}

func (u *User) Delete(blobID string) error {
	req, err := http.NewRequest(
		http.MethodDelete,
		fmt.Sprintf("%s/blobs/%s/%s", u.ProjectClient.BaseURL, u.UserID, blobID),
		nil,
	)
	if err != nil {
		return err
	}

	resp, err := u.ProjectClient.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	_, err = network.UnpackResponse(resp)
	return err
}

func (u *User) Flush(blobType blob.BlobType) error {
	resp, err := u.ProjectClient.HTTPClient.Post(
		fmt.Sprintf("%s/users/buffer/%s/%s", u.ProjectClient.BaseURL, u.UserID, blobType),
		"application/json",
		nil,
	)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	_, err = network.UnpackResponse(resp)
	return err
}

func (u *User) Profile() ([]UserProfile, error) {
	resp, err := u.ProjectClient.HTTPClient.Get(
		fmt.Sprintf("%s/users/profile/%s", u.ProjectClient.BaseURL, u.UserID),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return nil, err
	}

	profiles, ok := baseResp.Data["profiles"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for profiles")
	}

	var result []UserProfile
	for _, p := range profiles {
		profileMap, ok := p.(map[string]interface{})
		if !ok {
			continue
		}

		var profile UserProfile
		jsonData, err := json.Marshal(profileMap)
		if err != nil {
			continue
		}

		if err := json.Unmarshal(jsonData, &profile); err != nil {
			continue
		}

		result = append(result, profile)
	}

	return result, nil
}

func (u *User) DeleteProfile(profileID string) error {
	req, err := http.NewRequest(
		http.MethodDelete,
		fmt.Sprintf("%s/users/profile/%s/%s", u.ProjectClient.BaseURL, u.UserID, profileID),
		nil,
	)
	if err != nil {
		return err
	}

	resp, err := u.ProjectClient.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	_, err = network.UnpackResponse(resp)
	return err
} 
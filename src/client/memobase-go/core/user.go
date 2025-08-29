package core

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"

	"github.com/memodb-io/memobase/src/client/memobase-go/blob"
	"github.com/memodb-io/memobase/src/client/memobase-go/network"
)

type User struct {
	UserID        string
	ProjectClient *MemoBaseClient
	Fields        map[string]interface{}
}

func (u *User) Insert(blob blob.BlobInterface, sync bool) (string, error) {
	reqData := map[string]interface{}{
		"blob_type": blob.GetType(),
		"blob_data": blob.GetBlobData(),
		"fields":    blob.GetFields(),
	}
	if blob.GetCreatedAt() != nil {
		reqData["created_at"] = blob.GetCreatedAt()
	}

	jsonData, err := json.Marshal(reqData)
	if err != nil {
		return "", err
	}

	resp, err := u.ProjectClient.HTTPClient.Post(
		fmt.Sprintf("%s/blobs/insert/%s?wait_process=%t", u.ProjectClient.BaseURL, u.UserID, sync),
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

	dataMap, ok := baseResp.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("unexpected response format for Insert")
	}

	return dataMap["id"].(string), nil
}

func (u *User) Get(blobID string) (blob.BlobInterface, error) {
	resp, err := u.ProjectClient.HTTPClient.Get(
		fmt.Sprintf("%s/blobs/%s/%s", u.ProjectClient.BaseURL, u.UserID, blobID),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return nil, err
	}

	var blobData blob.BlobData
	jsonData, err := json.Marshal(baseResp.Data)
	if err != nil {
		return nil, err
	}

	if err := json.Unmarshal(jsonData, &blobData); err != nil {
		return nil, err
	}

	return blobData.ToBlob()
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

	dataMap, ok := baseResp.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for GetAll")
	}

	data, ok := dataMap["ids"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for blob IDs")
	}

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

func (u *User) Flush(blobType blob.BlobType, sync bool) error {
	resp, err := u.ProjectClient.HTTPClient.Post(
		fmt.Sprintf("%s/users/buffer/%s/%s?wait_process=%t", u.ProjectClient.BaseURL, u.UserID, blobType, sync),
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

func (u *User) AddProfile(content string, topic string, subTopic string) (string, error) {
	reqData := map[string]interface{}{
		"content": content,
		"attributes": map[string]interface{}{
			"topic":     topic,
			"sub_topic": subTopic,
		},
	}

	jsonData, err := json.Marshal(reqData)
	if err != nil {
		return "", err
	}

	resp, err := u.ProjectClient.HTTPClient.Post(
		fmt.Sprintf("%s/users/profile/%s", u.ProjectClient.BaseURL, u.UserID),
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

	dataMap, ok := baseResp.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("unexpected response format for AddProfile")
	}

	return dataMap["id"].(string), nil
}

func (u *User) Buffer(blobType blob.BlobType, status string) ([]string, error) {
	resp, err := u.ProjectClient.HTTPClient.Get(
		fmt.Sprintf("%s/users/buffer/capacity/%s/%s?status=%s", u.ProjectClient.BaseURL, u.UserID, blobType, status),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return nil, err
	}

	dataMap, ok := baseResp.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for Buffer")
	}

	data, ok := dataMap["ids"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for blob IDs")
	}

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

type ProfileOptions struct {
	MaxTokenSize    int                            `json:"max_token_size,omitempty"`
	PreferTopics    []string                       `json:"prefer_topics,omitempty"`
	OnlyTopics      []string                       `json:"only_topics,omitempty"`
	MaxSubtopicSize *int                           `json:"max_subtopic_size,omitempty"`
	TopicLimits     map[string]int                 `json:"topic_limits,omitempty"`
	Chats           []blob.OpenAICompatibleMessage `json:"chats,omitempty"`
}

func (u *User) Profile(options *ProfileOptions) ([]UserProfileData, error) {
	if options == nil {
		options = &ProfileOptions{
			MaxTokenSize: 1000,
		}
	}

	params := url.Values{}
	params.Add("max_token_size", fmt.Sprintf("%d", options.MaxTokenSize))

	if options.PreferTopics != nil {
		for _, t := range options.PreferTopics {
			params.Add("prefer_topics", t)
		}
	}
	if options.OnlyTopics != nil {
		for _, t := range options.OnlyTopics {
			params.Add("only_topics", t)
		}
	}
	if options.MaxSubtopicSize != nil {
		params.Add("max_subtopic_size", fmt.Sprintf("%d", *options.MaxSubtopicSize))
	}
	if options.TopicLimits != nil {
		topicLimitsJSON, err := json.Marshal(options.TopicLimits)
		if err != nil {
			return nil, err
		}
		params.Add("topic_limits_json", string(topicLimitsJSON))
	}
	if options.Chats != nil {
		chatsJSON, err := json.Marshal(options.Chats)
		if err != nil {
			return nil, err
		}
		params.Add("chats_str", string(chatsJSON))
	}

	resp, err := u.ProjectClient.HTTPClient.Get(
		fmt.Sprintf("%s/users/profile/%s?%s", u.ProjectClient.BaseURL, u.UserID, params.Encode()),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return nil, err
	}

	dataMap, ok := baseResp.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for Profile")
	}

	profiles, ok := dataMap["profiles"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for profiles")
	}

	var result []UserProfileData
	for _, p := range profiles {
		profileMap, ok := p.(map[string]interface{})
		if !ok {
			continue
		}

		var profile UserProfileData
		jsonData, err := json.Marshal(profileMap)
		if err != nil {
			continue
		}

		if err := json.Unmarshal(jsonData, &profile); err != nil {
			fmt.Printf("Error unmarshaling profile: %v\nData: %s\n", err, jsonData)
			continue
		}

		result = append(result, profile)
	}

	return result, nil
}

func (u *User) UpdateProfile(profileID string, content string, topic string, subTopic string) error {
	reqData := map[string]interface{}{
		"content": content,
		"attributes": map[string]interface{}{
			"topic":     topic,
			"sub_topic": subTopic,
		},
	}

	jsonData, err := json.Marshal(reqData)
	if err != nil {
		return err
	}

	req, err := http.NewRequest(
		http.MethodPut,
		fmt.Sprintf("%s/users/profile/%s/%s", u.ProjectClient.BaseURL, u.UserID, profileID),
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := u.ProjectClient.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	_, err = network.UnpackResponse(resp)
	return err
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

func (u *User) Event(topk int, maxTokenSize *int, needSummary bool) ([]UserEventData, error) {
	if topk <= 0 {
		topk = 10 // Default value
	}

	params := url.Values{}
	params.Add("topk", fmt.Sprintf("%d", topk))
	if maxTokenSize != nil {
		params.Add("max_token_size", fmt.Sprintf("%d", *maxTokenSize))
	}
	if needSummary {
		params.Add("need_summary", "true")
	}

	resp, err := u.ProjectClient.HTTPClient.Get(
		fmt.Sprintf("%s/users/event/%s?%s", u.ProjectClient.BaseURL, u.UserID, params.Encode()),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return nil, err
	}

	dataMap, ok := baseResp.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for Event")
	}

	events, ok := dataMap["events"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for events")
	}

	var result []UserEventData
	for _, e := range events {
		eventMap, ok := e.(map[string]interface{})
		if !ok {
			continue
		}

		var event UserEventData
		jsonData, err := json.Marshal(eventMap)
		if err != nil {
			continue
		}

		if err := json.Unmarshal(jsonData, &event); err != nil {
			fmt.Printf("Error unmarshaling event: %v\nData: %s\n", err, jsonData)
			continue
		}

		result = append(result, event)
	}

	return result, nil
}

func (u *User) DeleteEvent(eventID string) error {
	req, err := http.NewRequest(
		http.MethodDelete,
		fmt.Sprintf("%s/users/event/%s/%s", u.ProjectClient.BaseURL, u.UserID, eventID),
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

func (u *User) UpdateEvent(eventID string, eventData map[string]interface{}) error {
	jsonData, err := json.Marshal(eventData)
	if err != nil {
		return err
	}

	req, err := http.NewRequest(
		http.MethodPut,
		fmt.Sprintf("%s/users/event/%s/%s", u.ProjectClient.BaseURL, u.UserID, eventID),
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := u.ProjectClient.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	_, err = network.UnpackResponse(resp)
	return err
}

func (u *User) SearchEvent(query string, topk int, similarityThreshold float64, timeRangeInDays int) ([]UserEventData, error) {
	params := url.Values{}
	params.Add("query", query)
	params.Add("topk", fmt.Sprintf("%d", topk))
	params.Add("similarity_threshold", fmt.Sprintf("%f", similarityThreshold))
	params.Add("time_range_in_days", fmt.Sprintf("%d", timeRangeInDays))

	resp, err := u.ProjectClient.HTTPClient.Get(
		fmt.Sprintf("%s/users/event/search/%s?%s", u.ProjectClient.BaseURL, u.UserID, params.Encode()),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return nil, err
	}

	dataMap, ok := baseResp.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for SearchEvent")
	}

	events, ok := dataMap["events"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for events")
	}

	var result []UserEventData
	for _, e := range events {
		eventMap, ok := e.(map[string]interface{})
		if !ok {
			continue
		}

		var event UserEventData
		jsonData, err := json.Marshal(eventMap)
		if err != nil {
			continue
		}

		if err := json.Unmarshal(jsonData, &event); err != nil {
			fmt.Printf("Error unmarshaling event: %v\nData: %s\n", err, jsonData)
			continue
		}

		result = append(result, event)
	}

	return result, nil
}

// SearchEventGist searches for event gists with similarity threshold
func (u *User) SearchEventGist(query string, topk int, similarityThreshold float64, timeRangeInDays int) ([]UserGistEventData, error) {
	params := url.Values{}
	params.Add("query", query)
	params.Add("topk", fmt.Sprintf("%d", topk))
	params.Add("similarity_threshold", fmt.Sprintf("%f", similarityThreshold))
	params.Add("time_range_in_days", fmt.Sprintf("%d", timeRangeInDays))

	resp, err := u.ProjectClient.HTTPClient.Get(
		fmt.Sprintf("%s/users/event_gist/search/%s?%s", u.ProjectClient.BaseURL, u.UserID, params.Encode()),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return nil, err
	}

	dataMap, ok := baseResp.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for SearchEventGist")
	}

	events, ok := dataMap["events"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("unexpected response format for events")
	}

	var result []UserGistEventData
	for _, e := range events {
		eventMap, ok := e.(map[string]interface{})
		if !ok {
			continue
		}

		var event UserGistEventData
		jsonData, err := json.Marshal(eventMap)
		if err != nil {
			continue
		}
		if err := json.Unmarshal(jsonData, &event); err != nil {
			fmt.Printf("Error unmarshaling event gist: %v\nData: %s\n", err, jsonData)
			continue
		}

		result = append(result, event)
	}

	return result, nil
}

type ContextOptions struct {
	MaxTokenSize             int                            `json:"max_token_size,omitempty"`
	PreferTopics             []string                       `json:"prefer_topics,omitempty"`
	OnlyTopics               []string                       `json:"only_topics,omitempty"`
	MaxSubtopicSize          *int                           `json:"max_subtopic_size,omitempty"`
	TopicLimits              map[string]int                 `json:"topic_limits,omitempty"`
	ProfileEventRatio        *float64                       `json:"profile_event_ratio,omitempty"`
	RequireEventSummary      *bool                          `json:"require_event_summary,omitempty"`
	Chats                    []blob.OpenAICompatibleMessage `json:"chats,omitempty"`
	EventSimilarityThreshold *float64                       `json:"event_similarity_threshold,omitempty"`
}

func (u *User) Context(options *ContextOptions) (string, error) {
	if options == nil {
		options = &ContextOptions{
			MaxTokenSize: 1000,
		}
	}

	params := url.Values{}
	params.Add("max_token_size", fmt.Sprintf("%d", options.MaxTokenSize))

	if options.PreferTopics != nil {
		for _, t := range options.PreferTopics {
			params.Add("prefer_topics", t)
		}
	}
	if options.OnlyTopics != nil {
		for _, t := range options.OnlyTopics {
			params.Add("only_topics", t)
		}
	}
	if options.MaxSubtopicSize != nil {
		params.Add("max_subtopic_size", fmt.Sprintf("%d", *options.MaxSubtopicSize))
	}
	if options.TopicLimits != nil {
		topicLimitsJSON, err := json.Marshal(options.TopicLimits)
		if err != nil {
			return "", err
		}
		params.Add("topic_limits_json", string(topicLimitsJSON))
	}
	if options.ProfileEventRatio != nil {
		params.Add("profile_event_ratio", fmt.Sprintf("%f", *options.ProfileEventRatio))
	}
	if options.RequireEventSummary != nil {
		params.Add("require_event_summary", fmt.Sprintf("%t", *options.RequireEventSummary))
	}
	if options.Chats != nil {
		chatsJSON, err := json.Marshal(options.Chats)
		if err != nil {
			return "", err
		}
		params.Add("chats_str", string(chatsJSON))
	}
	if options.EventSimilarityThreshold != nil {
		params.Add("event_similarity_threshold", fmt.Sprintf("%f", *options.EventSimilarityThreshold))
	}

	resp, err := u.ProjectClient.HTTPClient.Get(
		fmt.Sprintf("%s/users/context/%s?%s", u.ProjectClient.BaseURL, u.UserID, params.Encode()),
	)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	baseResp, err := network.UnpackResponse(resp)
	if err != nil {
		return "", err
	}

	dataMap, ok := baseResp.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("unexpected response format for Context")
	}

	contextStr, ok := dataMap["context"].(string)
	if !ok {
		return "", fmt.Errorf("unexpected response format for context")
	}

	return contextStr, nil
}

package core

import (
	"os"
	"testing"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

const (
	TestProjectURL = "http://localhost:8019"
	TestAPIKey     = "secret"
)

func skipIfNoServer(t *testing.T) {
	if os.Getenv("MEMOBASE_TEST_SERVER") != "true" {
		t.Skip("Skipping test that requires live server - set MEMOBASE_TEST_SERVER=true to run")
	}
}

func TestNewMemoBaseClient(t *testing.T) {
	client, err := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	assert.NoError(t, err)
	assert.NotNil(t, client)
	assert.Equal(t, TestProjectURL, client.ProjectURL)
	assert.Equal(t, TestAPIKey, client.APIKey)
	assert.Equal(t, "api/v1", client.APIVersion)
}

func TestPing(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	assert.True(t, client.Ping())
}

func TestConfig(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	config := "language: en"
	err := client.UpdateConfig(config)
	assert.NoError(t, err)

	newConfig, err := client.GetConfig()
	assert.NoError(t, err)
	assert.Equal(t, config, newConfig)
}

func TestUserCRUD(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)

	// Add User
	userID, err := client.AddUser(map[string]interface{}{}, "")
	assert.NoError(t, err)
	assert.NotEmpty(t, userID)

	// Get User
	user, err := client.GetUser(userID, false)
	assert.NoError(t, err)
	assert.NotNil(t, user)
	assert.Equal(t, userID, user.UserID)

	// Update User
	_, err = client.UpdateUser(userID, map[string]interface{}{"test": 123})
	assert.NoError(t, err)

	// Get User again to check update
	user, err = client.GetUser(userID, false)
	assert.NoError(t, err)
	assert.Equal(t, 123.0, user.Fields["data"].(map[string]interface{})["test"])

	// Delete User
	err = client.DeleteUser(userID)
	assert.NoError(t, err)

	// Verify user is deleted
	_, err = client.GetUser(userID, false)
	assert.Error(t, err)
}

func TestGetOrCreateUser(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID := uuid.New().String()

	// Create user
	user, err := client.GetOrCreateUser(userID)
	assert.NoError(t, err)
	assert.NotNil(t, user)
	assert.Equal(t, userID, user.UserID)

	// Get user
	user, err = client.GetOrCreateUser(userID)
	assert.NoError(t, err)
	assert.NotNil(t, user)
	assert.Equal(t, userID, user.UserID)

	client.DeleteUser(userID)
}

func TestGetAllUsers(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	userID, err := client.AddUser(map[string]interface{}{}, "")

	users, err := client.GetAllUsers("", "updated_at", true, 10, 0)
	assert.NoError(t, err)
	assert.NotEmpty(t, users)

	client.DeleteUser(userID)
}

func TestGetUsage(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	usage, err := client.GetUsage()
	assert.NoError(t, err)
	assert.NotNil(t, usage)
}

func TestGetDailyUsage(t *testing.T) {
	skipIfNoServer(t)
	client, _ := NewMemoBaseClient(TestProjectURL, TestAPIKey)
	usage, err := client.GetDailyUsage(7)
	assert.NoError(t, err)
	assert.NotNil(t, usage)
	assert.IsType(t, []map[string]interface{}{}, usage)
}

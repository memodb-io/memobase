package main

import (
	"fmt"
	"log"

	"github.com/google/uuid"
	"github.com/memodb-io/memobase/src/client/memobase-go/blob"
	"github.com/memodb-io/memobase/src/client/memobase-go/core"
)

func main() {
	projectURL := "YOUR_PROJECT_URL"
	apiKey := "YOUR_API_KEY"
	// Initialize the client
	client, err := core.NewMemoBaseClient(
		projectURL,
		apiKey,
	)
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}

	// Check connection
	if !client.Ping() {
		log.Fatal("Failed to connect to server")
	}

	// Create or get a user
	// userid should be a UUIDv4/5
	userid := uuid.New()
	user, err := client.GetOrCreateUser(userid.String())
	if err != nil {
		log.Fatalf("Failed to get/create user: %v", err)
	}
	fmt.Printf("User created with ID: %s\n", userid)

	// Create a chat blob
	chatBlob := &blob.ChatBlob{
		BaseBlob: blob.BaseBlob{
			Type: blob.ChatType,
		},
		Messages: []blob.OpenAICompatibleMessage{
			{
				Role:    "user",
				Content: "Hello, I am Jinjia!",
			},
			{
				Role:    "assistant",
				Content: "Hi there! How can I help you today?",
			},
		},
	}

	// Insert the blob
	blobID, err := user.Insert(chatBlob)
	if err != nil {
		log.Fatalf("Failed to insert blob: %v", err)
	}
	fmt.Printf("Successfully inserted blob with ID: %s\n", blobID)

	// Get the blob back
	retrievedBlob, err := user.Get(blobID)
	if err != nil {
		log.Fatalf("Failed to get blob: %v", err)
	}

	// Type assert to use as ChatBlob
	if chatBlob, ok := retrievedBlob.(*blob.ChatBlob); ok {
		fmt.Printf("Retrieved message: %s\n", chatBlob.Messages[0].Content)
	}

	// Get all chat blobs
	blobIDs, err := user.GetAll(blob.ChatType, 0, 10)
	if err != nil {
		log.Fatalf("Failed to get blobs: %v", err)
	}

	fmt.Printf("Found %d chat blobs\n", len(blobIDs))

	// Flush all blobs to get the latest profile
	user.Flush(blob.ChatType)

	// Get user profile
	profiles, err := user.Profile()
	if err != nil {
		log.Fatalf("Failed to get user profile: %v", err)
	}

	// Print profiles
	fmt.Println("\nUser Profiles:")
	for _, profile := range profiles {
		fmt.Printf("ID: %s\nTopic: %s\nSub-topic: %s\nContent: %s\n\n",
			profile.ID,
			profile.Attributes.Topic,
			profile.Attributes.SubTopic,
			profile.Content,
		)
	}

	// Delete a profile
	err = user.DeleteProfile(profiles[0].ID)
	if err != nil {
		log.Fatalf("Failed to delete profile: %v", err)
	}

	// Delete the user
	err = client.DeleteUser(userid.String())
	if err != nil {
		log.Fatalf("Failed to delete user: %v", err)
	}
}

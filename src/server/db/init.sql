-- Synced from backend 0.1.0.dev1
CREATE TABLE users (
	additional_fields JSONB, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);
CREATE TABLE general_blobs (
	blob_type VARCHAR(255) NOT NULL, 
	blob_data JSONB NOT NULL, 
	user_id UUID NOT NULL, 
	additional_fields JSONB, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE TABLE buffer_zones (
	blob_type VARCHAR(255) NOT NULL, 
	token_size INTEGER NOT NULL, 
	user_id UUID NOT NULL, 
	blob_id UUID NOT NULL, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(blob_id) REFERENCES general_blobs (id) ON DELETE CASCADE
);
CREATE TABLE user_profiles (
	content TEXT NOT NULL, 
	user_id UUID NOT NULL, 
	attributes JSONB, 
	id UUID NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE TABLE user_profile_blobs (
	user_profile_id UUID NOT NULL, 
	blob_id UUID NOT NULL, 
	PRIMARY KEY (user_profile_id, blob_id), 
	FOREIGN KEY(user_profile_id) REFERENCES user_profiles (id) ON DELETE CASCADE, 
	FOREIGN KEY(blob_id) REFERENCES general_blobs (id) ON DELETE CASCADE
);

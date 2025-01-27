package utils

import (
	"github.com/google/uuid"
)

func StringToUUID(s string, salt string) string {
	if salt == "" {
		salt = "memobase_client"
	}
	return uuid.NewSHA1(uuid.NameSpaceDNS, []byte(s+salt)).String()
} 
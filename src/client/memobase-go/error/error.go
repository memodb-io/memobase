package error

type ServerError struct {
    Message string
}

func (e *ServerError) Error() string {
    return e.Message
} 
package cerr

// Error implements the error interface
type Error string

// Error returns a string
func (e Error) Error() string { return string(e) }

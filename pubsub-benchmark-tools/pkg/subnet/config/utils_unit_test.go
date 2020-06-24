// +build unit

package config

import (
	"fmt"
	"testing"
)

func TestTrimExtension(t *testing.T) {
	for i, tt := range []struct {
		in  string
		out string
	}{
		{"config.toml", "config"},
		{"config", "config"},
		{"./config.toml", "./config"},
		{"../config.toml", "../config"},
		{"./config", "./config"},
		{"../config", "../config"},
	} {
		t.Run(fmt.Sprintf("%v", i), func(t *testing.T) {
			result := trimExtension(tt.in)
			if result != tt.out {
				t.Errorf("want %s; got %s", tt.out, result)
			}
		})
	}
}

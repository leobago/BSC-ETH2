package orchestra

import (
	"math/rand"
)

// note: min/max are inclusive
func randBetween(min, max int) int {
	return rand.Intn(max-min+1) + min
}

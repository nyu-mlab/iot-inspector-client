package devid

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func twoFields() Fields { return Fields{OUIFriendly: "Acme", DHCPHostname: "cam"} }

func client(url string) *Client {
	c := New("tok")
	c.Endpoint = url
	return c
}

func TestPredictRateLimited(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Retry-After", "30")
		w.WriteHeader(http.StatusTooManyRequests)
	}))
	defer srv.Close()

	_, err := client(srv.URL).Predict(context.Background(), "aa:bb", twoFields())
	var rl *RateLimitError
	if !errors.As(err, &rl) {
		t.Fatalf("expected *RateLimitError, got %v", err)
	}
	if rl.RetryAfter != 30*time.Second {
		t.Errorf("RetryAfter = %s, want 30s", rl.RetryAfter)
	}
}

func TestPredictRateLimitedNoHeader(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusTooManyRequests)
	}))
	defer srv.Close()

	_, err := client(srv.URL).Predict(context.Background(), "aa:bb", twoFields())
	var rl *RateLimitError
	if !errors.As(err, &rl) || rl.RetryAfter != 0 {
		t.Fatalf("expected *RateLimitError with 0 retry, got %v", err)
	}
}

func TestPredictOK(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_, _ = w.Write([]byte(`{"vendor":"Wyze"}`))
	}))
	defer srv.Close()

	out, err := client(srv.URL).Predict(context.Background(), "aa:bb", twoFields())
	if err != nil {
		t.Fatal(err)
	}
	if out["vendor"] != "Wyze" {
		t.Errorf("vendor = %v, want Wyze", out["vendor"])
	}
}

func TestPredictOtherErrorIsNotRateLimit(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusUnauthorized)
	}))
	defer srv.Close()

	_, err := client(srv.URL).Predict(context.Background(), "aa:bb", twoFields())
	var rl *RateLimitError
	if err == nil || errors.As(err, &rl) {
		t.Errorf("401 should be a generic error, got %v", err)
	}
}

func TestParseRetryAfter(t *testing.T) {
	cases := map[string]time.Duration{"": 0, "45": 45 * time.Second, "-5": 0, "abc": 0}
	for in, want := range cases {
		if got := parseRetryAfter(in); got != want {
			t.Errorf("parseRetryAfter(%q) = %s, want %s", in, got, want)
		}
	}
}

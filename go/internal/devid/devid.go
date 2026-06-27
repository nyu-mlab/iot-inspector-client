// Package devid is the optional cloud device-identification client. It POSTs a
// device's collected metadata to the Modal endpoint that runs the fine-tuned
// LLaMA model (background/device_id_api_thread.py). This is the canonical
// "enhanced feature" — everything else runs fully offline.
package devid

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"
)

// RateLimitError is returned when the endpoint replies 429. RetryAfter is parsed
// from the Retry-After header (0 if absent), so a caller can back off for that
// long instead of hammering the API (#309).
type RateLimitError struct {
	RetryAfter time.Duration
}

func (e *RateLimitError) Error() string {
	if e.RetryAfter > 0 {
		return fmt.Sprintf("device-id API rate limited; retry after %s", e.RetryAfter)
	}
	return "device-id API rate limited"
}

// parseRetryAfter reads a Retry-After value, which RFC 7231 allows to be either
// a number of seconds or an HTTP date.
func parseRetryAfter(h string) time.Duration {
	h = strings.TrimSpace(h)
	if h == "" {
		return 0
	}
	if secs, err := strconv.Atoi(h); err == nil && secs >= 0 {
		return time.Duration(secs) * time.Second
	}
	if t, err := http.ParseTime(h); err == nil {
		if d := time.Until(t); d > 0 {
			return d
		}
	}
	return 0
}

const defaultEndpoint = "https://rameen-mahmood--dev-id-predict.modal.run"

type Client struct {
	Endpoint string
	APIKey   string
	http     *http.Client
}

func New(apiKey string) *Client {
	return &Client{
		Endpoint: defaultEndpoint,
		APIKey:   apiKey,
		http:     &http.Client{Timeout: 120 * time.Second},
	}
}

// Fields are the signals the model identifies a device from (Table A.1 in the
// paper): OUI vendor, DHCP hostname, contacted hostnames, user-agent, mDNS/SSDP.
type Fields struct {
	OUIFriendly     string `json:"oui_friendly"`
	DHCPHostname    string `json:"dhcp_hostname"`
	RemoteHostnames string `json:"remote_hostnames"`
	UserAgentInfo   string `json:"user_agent_info"`
	MDNSInfo        string `json:"mdns_info"`
	SSDPInfo        string `json:"ssdp_info"`
	UserLabels      string `json:"user_labels"`
	TalksToAds      bool   `json:"talks_to_ads"`
}

// nonEmptyCount mirrors the Python guard: refuse to call the API with fewer
// than two populated string fields, to avoid wasting calls on bare devices.
func (f Fields) nonEmptyCount() int {
	n := 0
	for _, v := range []string{f.OUIFriendly, f.DHCPHostname, f.RemoteHostnames, f.UserAgentInfo, f.MDNSInfo, f.SSDPInfo, f.UserLabels} {
		if v != "" {
			n++
		}
	}
	return n
}

type request struct {
	MACAddress string `json:"mac_address"`
	Fields     Fields `json:"fields"`
}

// Predict returns the model's identification result as a generic map (Vendor,
// device type, etc.). Returns an error the caller can ignore to fall back to
// the local OUI/mDNS name.
func (c *Client) Predict(ctx context.Context, mac string, f Fields) (map[string]any, error) {
	if f.nonEmptyCount() < 2 {
		return nil, fmt.Errorf("too little metadata to identify %s yet", mac)
	}
	body, _ := json.Marshal(request{MACAddress: mac, Fields: f})
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.Endpoint, bytes.NewReader(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-api-key", c.APIKey)

	resp, err := c.http.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode == http.StatusTooManyRequests {
		return nil, &RateLimitError{RetryAfter: parseRetryAfter(resp.Header.Get("Retry-After"))}
	}
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("device-id API returned %s", resp.Status)
	}
	var out map[string]any
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, err
	}
	return out, nil
}

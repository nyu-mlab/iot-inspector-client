// Package collect implements the opt-in research data upload (issue #306). It
// streams the full packet capture plus a metadata JSON to a configurable
// endpoint as multipart/form-data.
//
// SAFETY: nothing here decides whether to send. The caller MUST verify explicit
// user consent (store.ShareConsent) before calling Upload. Upload also refuses
// to run with an empty endpoint, so a missing config can never silently send.
package collect

import (
	"context"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

type Client struct {
	Endpoint string
	APIKey   string
	http     *http.Client
}

func New(endpoint, apiKey string) *Client {
	return &Client{
		Endpoint: endpoint,
		APIKey:   apiKey,
		http:     &http.Client{Timeout: 10 * time.Minute}, // pcaps can be large
	}
}

// Upload streams the pcap at pcapPath and the metadata JSON to the endpoint as
// one multipart POST. It errors (without sending) if the endpoint is empty.
func (c *Client) Upload(ctx context.Context, pcapPath string, metadata []byte) error {
	if c.Endpoint == "" {
		return fmt.Errorf("no collection endpoint configured")
	}
	f, err := os.Open(pcapPath)
	if err != nil {
		return fmt.Errorf("open pcap: %w", err)
	}
	defer f.Close()

	// Stream the multipart body through a pipe so a large pcap never has to sit
	// in memory.
	pr, pw := io.Pipe()
	mw := multipart.NewWriter(pw)
	go func() {
		var werr error
		defer func() { _ = pw.CloseWithError(werr) }()
		if werr = mw.WriteField("metadata", string(metadata)); werr != nil {
			return
		}
		var fw io.Writer
		if fw, werr = mw.CreateFormFile("pcap", filepath.Base(pcapPath)); werr != nil {
			return
		}
		if _, werr = io.Copy(fw, f); werr != nil {
			return
		}
		werr = mw.Close()
	}()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.Endpoint, pr)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", mw.FormDataContentType())
	if c.APIKey != "" {
		req.Header.Set("x-api-key", c.APIKey)
	}

	resp, err := c.http.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		b, _ := io.ReadAll(io.LimitReader(resp.Body, 512))
		return fmt.Errorf("collection endpoint returned %s: %s", resp.Status, b)
	}
	return nil
}

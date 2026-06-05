package discovery

import (
	"encoding/xml"
	"testing"
)

func TestParseSSDP(t *testing.T) {
	resp := "HTTP/1.1 200 OK\r\n" +
		"LOCATION: http://192.168.1.5:80/desc.xml\r\n" +
		"SERVER: Hue/1.0 UPnP/1.0\r\n" +
		"ST: upnp:rootdevice\r\n\r\n"
	h := parseSSDP(resp)
	if h["LOCATION"] != "http://192.168.1.5:80/desc.xml" {
		t.Errorf("LOCATION = %q", h["LOCATION"])
	}
	if h["SERVER"] != "Hue/1.0 UPnP/1.0" {
		t.Errorf("SERVER = %q", h["SERVER"])
	}
}

func TestXMLToMap(t *testing.T) {
	const doc = `<root xmlns="urn:schemas-upnp-org:device-1-0">` +
		`<device><friendlyName>Hue Bridge</friendlyName><manufacturer>Signify</manufacturer></device></root>`
	var n xmlNode
	if err := xml.Unmarshal([]byte(doc), &n); err != nil {
		t.Fatal(err)
	}
	got := xmlToMap(n)

	// root -> device -> device -> {friendlyName, manufacturer}, namespace stripped
	root := got.(map[string]any)["root"].(map[string]any)
	dev := root["device"].(map[string]any)["device"].(map[string]any)
	if dev["friendlyName"] != "Hue Bridge" {
		t.Errorf("friendlyName = %v, want Hue Bridge", dev["friendlyName"])
	}
	if dev["manufacturer"] != "Signify" {
		t.Errorf("manufacturer = %v, want Signify", dev["manufacturer"])
	}
}

// Package report renders a single static HTML summary from the SQLite data.
// This replaces the Streamlit dashboard for the offline use case: no server, no
// JS, just one self-contained file the user can open or share.
package report

import (
	"fmt"
	"html/template"
	"os"
	"sort"
	"strings"

	"github.com/nyu-mlab/inspector-go/internal/store"
)

// deviceRow is one line in the report: who the device is, who it talked to most,
// and how much data it sent vs received. No raw "flow" counts — end users care
// about bytes up/down, not internal flow records (issue #305).
type deviceRow struct {
	Name, MAC, VendorType, TopDest string
	Up, Down                       int64
}

type page struct {
	Devices []deviceRow
}

var funcs = template.FuncMap{"bytes": humanBytes}

// humanBytes formats a byte count as B/KB/MB/GB/TB.
func humanBytes(n int64) string {
	const u = 1024
	if n < u {
		return fmt.Sprintf("%d B", n)
	}
	div, exp := int64(u), 0
	for x := n / u; x >= u; x /= u {
		div *= u
		exp++
	}
	return fmt.Sprintf("%.1f %cB", float64(n)/float64(div), "KMGT"[exp])
}

var tmpl = template.Must(template.New("report").Funcs(funcs).Parse(`<!doctype html>
<html><head><meta charset="utf-8"><title>inspector-go report</title>
<style>
 body{font:14px system-ui,sans-serif;margin:2rem;max-width:64rem;color:#1f2430}
 h1{font-size:1.3rem;margin:0 0 .2rem}
 table{border-collapse:collapse;width:100%;margin:1rem 0}
 th,td{border-bottom:1px solid #e3e8ef;padding:.5rem .6rem;text-align:left;vertical-align:top}
 th{background:#f5f6f8;font-size:.8rem;text-transform:uppercase;letter-spacing:.03em;color:#6b7280}
 td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
 .mut{color:#6b7280}
 code{background:#f0f2f5;padding:.05rem .3rem;border-radius:.3rem;font-size:.85em}
</style></head><body>
<h1>Network report</h1>
<p class="mut">{{len .Devices}} device(s). Upload is data the device sent; download is data it received.</p>
{{if .Devices}}
<table>
<tr><th>Device</th><th>MAC</th><th>Vendor / Type</th><th>Top destination</th><th class="num">↑ Uploaded</th><th class="num">↓ Downloaded</th></tr>
{{range .Devices}}<tr>
 <td>{{.Name}}</td>
 <td><code>{{.MAC}}</code></td>
 <td>{{if .VendorType}}{{.VendorType}}{{else}}<span class="mut">—</span>{{end}}</td>
 <td>{{if .TopDest}}{{.TopDest}}{{else}}<span class="mut">—</span>{{end}}</td>
 <td class="num">{{bytes .Up}}</td>
 <td class="num">{{bytes .Down}}</td>
</tr>{{end}}
</table>
{{else}}<p class="mut">No devices captured.</p>{{end}}
</body></html>`))

// Generate writes a single-table HTML report to path.
func Generate(st *store.Store, path string) error {
	db := st.DB()
	var p page

	rows, err := db.Query(`
		SELECT d.mac_address,
		  COALESCE(json_extract(d.metadata_json,'$.name'),''),
		  COALESCE(json_extract(d.metadata_json,'$.dhcp_hostname'),''),
		  COALESCE((SELECT hostname FROM hostnames WHERE ip_address = d.ip_address),''),
		  COALESCE(json_extract(d.metadata_json,'$.vendor_confirmed'), json_extract(d.metadata_json,'$.oui_vendor'),''),
		  COALESCE(json_extract(d.metadata_json,'$.type_confirmed'),''),
		  COALESCE((SELECT SUM(byte_count) FROM network_flows WHERE src_mac_address = d.mac_address),0),
		  COALESCE((SELECT SUM(byte_count) FROM network_flows WHERE dest_mac_address = d.mac_address),0),
		  COALESCE((SELECT COALESCE(NULLIF(dest_hostname,''),dest_ip_address) AS h
		            FROM network_flows WHERE src_mac_address = d.mac_address
		            GROUP BY h ORDER BY SUM(byte_count) DESC LIMIT 1),'')
		FROM devices d WHERE d.is_gateway = 0`)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		var mac, name, dhcp, hostname, vendor, typ, topDest string
		var up, down int64
		if err := rows.Scan(&mac, &name, &dhcp, &hostname, &vendor, &typ, &up, &down, &topDest); err != nil {
			return err
		}
		p.Devices = append(p.Devices, deviceRow{
			Name:       displayName(name, dhcp, hostname, vendor, mac),
			MAC:        mac,
			VendorType: vendorType(vendor, typ),
			TopDest:    topDest,
			Up:         up,
			Down:       down,
		})
	}
	if err := rows.Err(); err != nil {
		return err
	}
	// Most active device first, by total bytes moved.
	sort.SliceStable(p.Devices, func(i, j int) bool {
		return p.Devices[i].Up+p.Devices[i].Down > p.Devices[j].Up+p.Devices[j].Down
	})

	out, err := os.Create(path)
	if err != nil {
		return err
	}
	defer out.Close()
	return tmpl.Execute(out, p)
}

// displayName picks the friendliest label available, falling back to a stable
// "Unnamed Device XX" from the last MAC octet.
func displayName(name, dhcp, hostname, vendor, mac string) string {
	for _, c := range []string{name, dhcp, hostname, vendor} {
		if c != "" {
			return c
		}
	}
	h := strings.ReplaceAll(mac, ":", "")
	if len(h) >= 2 {
		return "Unnamed Device " + strings.ToUpper(h[len(h)-2:])
	}
	return "Unknown"
}

func vendorType(vendor, typ string) string {
	switch {
	case vendor != "" && typ != "":
		return vendor + " · " + typ
	case vendor != "":
		return vendor
	default:
		return typ
	}
}

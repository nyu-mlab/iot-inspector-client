// Package report renders a single static HTML summary from the SQLite data.
// This replaces the Streamlit dashboard for the offline use case: no server, no
// JS, just one self-contained file the user can open or share.
package report

import (
	"html/template"
	"os"

	"github.com/nyu-mlab/inspector-go/internal/store"
)

type deviceRow struct {
	MAC, IP, Vendor, Hostname string
	FlowCount                 int
}

type topFlow struct {
	Device, Dest string
	Bytes        int64
}

type page struct {
	Devices []deviceRow
	Flows   []topFlow
}

var tmpl = template.Must(template.New("report").Parse(`<!doctype html>
<html><head><meta charset="utf-8"><title>inspector-go report</title>
<style>
 body{font:14px system-ui,sans-serif;margin:2rem;max-width:60rem}
 table{border-collapse:collapse;width:100%;margin:1rem 0}
 th,td{border-bottom:1px solid #ddd;padding:.4rem .6rem;text-align:left}
 th{background:#f5f5f5}
</style></head><body>
<h1>Network report</h1>
<h2>Devices ({{len .Devices}})</h2>
<table><tr><th>Device</th><th>IP</th><th>MAC</th><th>Vendor</th><th>Flows</th></tr>
{{range .Devices}}<tr><td>{{.Hostname}}</td><td>{{.IP}}</td><td>{{.MAC}}</td><td>{{.Vendor}}</td><td>{{.FlowCount}}</td></tr>{{end}}
</table>
<h2>Top destinations by bytes</h2>
<table><tr><th>Device</th><th>Destination</th><th>Bytes</th></tr>
{{range .Flows}}<tr><td>{{.Device}}</td><td>{{.Dest}}</td><td>{{.Bytes}}</td></tr>{{end}}
</table>
</body></html>`))

// Generate writes an HTML report to path, summarizing the captured data.
func Generate(st *store.Store, path string) error {
	db := st.DB()

	var p page

	devRows, err := db.Query(`
		SELECT d.mac_address, d.ip_address,
		       COALESCE(json_extract(d.metadata_json,'$.oui_vendor'),''),
		       COALESCE((SELECT hostname FROM hostnames WHERE ip_address = d.ip_address),''),
		       (SELECT COUNT(*) FROM network_flows f
		         WHERE f.src_mac_address = d.mac_address OR f.dest_mac_address = d.mac_address)
		FROM devices d WHERE d.is_gateway = 0
		ORDER BY d.ip_address`)
	if err != nil {
		return err
	}
	for devRows.Next() {
		var r deviceRow
		if err := devRows.Scan(&r.MAC, &r.IP, &r.Vendor, &r.Hostname, &r.FlowCount); err != nil {
			devRows.Close()
			return err
		}
		p.Devices = append(p.Devices, r)
	}
	devRows.Close()

	flowRows, err := db.Query(`
		SELECT src_mac_address,
		       COALESCE(NULLIF(dest_hostname,''), dest_ip_address),
		       SUM(byte_count) AS bytes
		FROM network_flows
		GROUP BY src_mac_address, dest_ip_address
		ORDER BY bytes DESC LIMIT 50`)
	if err != nil {
		return err
	}
	for flowRows.Next() {
		var f topFlow
		if err := flowRows.Scan(&f.Device, &f.Dest, &f.Bytes); err != nil {
			flowRows.Close()
			return err
		}
		p.Flows = append(p.Flows, f)
	}
	flowRows.Close()

	out, err := os.Create(path)
	if err != nil {
		return err
	}
	defer out.Close()
	return tmpl.Execute(out, p)
}

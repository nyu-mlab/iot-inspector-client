package web

import (
	"fmt"
	"html/template"
	"strings"
)

// lineChart renders a 60-second traffic line panel as inline SVG, copying the
// original IoT Inspector burst-style look (PR #275): a thin matplotlib-blue line
// over a white grid, newest on the right. series is indexed 0=now .. 59=60s ago.
// This is the server-rendered twin of the dashboard's JS chart() (used on the
// device detail page).
func lineChart(series []int64, label string) template.HTML {
	const (
		W, H       = 640.0, 128.0
		padL, padR = 46.0, 10.0
		padT, padB = 15.0, 16.0
		line       = "#1f77b4"
	)
	n := len(series)
	plotW, plotH := W-padL-padR, H-padT-padB

	var max int64
	for _, v := range series {
		if v > max {
			max = v
		}
	}

	var b strings.Builder
	fmt.Fprintf(&b, `<svg viewBox="0 0 %.0f %.0f" class="chart" preserveAspectRatio="none">`, W, H)
	fmt.Fprintf(&b, `<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" fill="#ffffff"/>`, padL, padT, plotW, plotH)
	for i := 0; i <= 3; i++ {
		y := padT + plotH*float64(i)/3
		val := float64(max) * (1 - float64(i)/3)
		fmt.Fprintf(&b, `<line x1="%.0f" y1="%.1f" x2="%.0f" y2="%.1f" stroke="#e3e8ef"/>`, padL, y, W-padR, y)
		fmt.Fprintf(&b, `<text x="%.0f" y="%.1f" text-anchor="end" class="tick">%s/s</text>`, padL-5, y+3, humanBytes(int64(val)))
	}
	if max > 0 {
		var pts strings.Builder
		for i := 0; i < n; i++ {
			x := padL + plotW*(1-float64(i)/float64(n-1))
			y := padT + plotH*(1-float64(series[i])/float64(max))
			fmt.Fprintf(&pts, "%.1f,%.1f ", x, y)
		}
		fmt.Fprintf(&b, `<polygon points="%.0f,%.0f %s %.0f,%.0f" fill="%s" opacity="0.10"/>`,
			padL, padT+plotH, strings.TrimSpace(pts.String()), W-padR, padT+plotH, line)
		fmt.Fprintf(&b, `<polyline points="%s" fill="none" stroke="%s" stroke-width="1.3"/>`, strings.TrimSpace(pts.String()), line)
	} else {
		fmt.Fprintf(&b, `<text x="%.0f" y="%.0f" text-anchor="middle" class="tick">no traffic in last 60s</text>`, padL+plotW/2, padT+plotH/2)
	}
	fmt.Fprintf(&b, `<text x="%.0f" y="%.0f" class="ctitle-svg">%s</text>`, padL, padT-4, template.HTMLEscapeString(label))
	fmt.Fprintf(&b, `<text x="%.0f" y="%.0f" class="tick">−60s</text>`, padL, H-4)
	fmt.Fprintf(&b, `<text x="%.0f" y="%.0f" text-anchor="end" class="tick">now</text>`, W-padR, H-4)
	b.WriteString(`</svg>`)
	return template.HTML(b.String())
}

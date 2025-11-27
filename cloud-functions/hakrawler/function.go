package function

import (
	"crypto/tls"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/gocolly/colly/v2"
	"net/http"
	"net/url"
	"regexp"
	"sync"

	"github.com/GoogleCloudPlatform/functions-framework-go/functions"
)

func init() {
	functions.HTTP("CrawlHandler", crawlHandler)
}

type CrawlRequest struct {
	URL      string `json:"url"`
	Depth    int    `json:"depth"`    // Max depth, default 2
	Subs     bool   `json:"subs"`     // Include subdomains
	Insecure bool   `json:"insecure"` // Disable TLS verify
	Timeout  int    `json:"timeout"`  // Seconds per URL
}

type CrawlResponse struct {
	URLs []string `json:"urls"`
}

// thread-safe set for uniqueness
var seen sync.Map

func crawlHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req CrawlRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON payload: "+err.Error(), http.StatusBadRequest)
		return
	}

	if req.URL == "" {
		http.Error(w, "Missing url field", http.StatusBadRequest)
		return
	}

	// header := make(map[string]string)
	// (optional: parse headers from payload)

	hostname, err := extractHostname(req.URL)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	allowed := []string{hostname}

	c := colly.NewCollector(
		colly.MaxDepth(req.Depth),
		colly.Async(true),
	)

	// configure TLS
	transport := &http.Transport{TLSClientConfig: &tls.Config{InsecureSkipVerify: req.Insecure}}
	c.WithTransport(transport)

	// subdomains
	if req.Subs {
		c.AllowedDomains = nil
		pattern := ".*(\\.|\\/\\/)" + regexp.QuoteMeta(hostname) + "((#|\\/|\\?).*)?$"
		c.URLFilters = []*regexp.Regexp{regexp.MustCompile(pattern)}
	} else {
		c.AllowedDomains = allowed
	}

	// results channel
	results := make(chan string)
	go func() {
		c.OnHTML("a[href]", makeCallback("href", results, hostname))
		c.OnHTML("script[src]", makeCallback("src", results, hostname))
		c.OnHTML("form[action]", makeCallback("action", results, hostname))

		// start crawl
		c.Visit(req.URL)
		c.Wait()
		close(results)
	}()

	// collect
	var out CrawlResponse
	for url := range results {
		// enforce uniqueness
		if _, loaded := seen.LoadOrStore(url, true); !loaded {
			out.URLs = append(out.URLs, url)
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(out)
}

func makeCallback(attrName string, ch chan<- string, targetHostname string) func(*colly.HTMLElement) {
	return func(e *colly.HTMLElement) {
		abs := e.Request.AbsoluteURL(e.Attr(attrName))
		if abs == "" {
			return
		}

		// Extract hostname from the found URL
		foundHostname, err := extractHostname(abs)
		if err != nil {
			return
		}

		// Only keep URLs from the same domain
		if foundHostname == targetHostname {
			ch <- abs
		}

		// Continue crawling if it's a link
		if attrName == "href" {
			e.Request.Visit(e.Attr(attrName))
		}
	}
}

func extractHostname(raw string) (string, error) {
	u, err := url.Parse(raw)
	if err != nil || !u.IsAbs() {
		return "", errors.New("Invalid absolute URL")
	}
	return u.Hostname(), nil
}

// helloWorld writes "Hello, World!" to the HTTP response.
func helloWorld(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Hello, World!")
}

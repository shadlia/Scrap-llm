package main

import (
	"log"

	// Blank-import the function package so the init() runs
	"github.com/GoogleCloudPlatform/functions-framework-go/funcframework"
	_ "hakrawler/hakrawler"
)

func main() {

	port := "8081"
	hostname := "127.0.0.1"

	if err := funcframework.StartHostPort(hostname, port); err != nil {
		log.Fatalf("funcframework.StartHostPort: %v\n", err)
	}
}

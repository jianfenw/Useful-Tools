
package main

import (
	"log"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"strings"
)


func getListenAddress() string {
	port := os.Getenv("PORT")
	return ":" + port
}


func SetupLog() {
	a_condtion_url := os.Getenv("A_CONDITION_URL")
	b_condtion_url := os.Getenv("B_CONDITION_URL")
	default_condtion_url := os.Getenv("DEFAULT_CONDITION_URL")

	log.Printf("Server will run on: %s\n", getListenAddress())
	log.Printf("Redirecting to A url: %s\n", a_condtion_url)
	log.Printf("Redirecting to B url: %s\n", b_condtion_url)
	log.Printf("Redirecting to Default url: %s\n", default_condtion_url)
}


// This function receives a HTTP request and forwards
// it to the appropriate url.
func HandleRequestAndRedirect(res http.ResponseWriter, req *http.Request) {
}


func main() {
	SetupLog()

	// Starts the HTTP server.
	http.HandlerFunc("/", HandleRequestAndRedirect)
}


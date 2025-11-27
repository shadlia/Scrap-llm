export class ServerApi {
  static async fetch(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${process.env.BACKEND_API_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  }

  static async crawl(
    url: string,
    skipSitemap: boolean = false,
    skipTrim: boolean = false,
    useAgent: boolean = false,
    useHakrawler: boolean = false
  ) {
    return this.fetch("/crawl", {
      method: "POST",
      body: JSON.stringify({
        url,
        skip_sitemap: skipSitemap,
        skip_trim: skipTrim,
        use_agent: useAgent,
        use_hakrawler: useHakrawler,
      }),
    });
  }

  static async filter(urls: string[], method: string, model: string) {
    return this.fetch("/filter", {
      method: "POST",
      body: JSON.stringify({ urls, method, model }),
    });
  }

  static async extract(
    productUrls: string[],
    domain: string,
    models: string[],
    clientId: string
  ) {
    return this.fetch("/extract", {
      method: "POST",
      body: JSON.stringify({
        product_urls: productUrls,
        domain,
        models,
        client_id: clientId,
      }),
    });
  }

  static async extract_single_product(
    clientId: string,
    processId: string,
    productUrl: string,
    domain: string,
    method: string,
    models: string[]
  ) {
    return this.fetch("/enqueue-extract-single-product", {
      method: "POST",
      body: JSON.stringify({
        client_id: clientId,
        process_id: processId,
        product_url: productUrl,
        domain,
        method,
        models,
      }),
    });
  }

  static async fetch_extractions(processId: string, numberOfUrls: number) {
    return this.fetch("/fetch-extractions", {
      method: "POST",
      body: JSON.stringify({
        process_id: processId,
        number_of_urls: numberOfUrls,
      }),
    });
  }

  static async fullPipeline(
    url: string,
    filterMethod: string,
    extractionMethod: string,
    model: string,
    skipSitemap: boolean
  ) {
    return this.fetch("/full-pipeline", {
      method: "POST",
      body: JSON.stringify({
        url,
        filter_method: filterMethod,
        extraction_method: extractionMethod,
        model,
        skip_sitemap: skipSitemap,
      }),
    });
  }

  static async getProducts() {
    return this.fetch("/products");
  }

  static async updateProduct(id: string, product: any) {
    return this.fetch(`/products/${id}`, {
      method: "PUT",
      body: JSON.stringify(product),
    });
  }

  static async deleteProduct(id: string) {
    return this.fetch(`/products/${id}`, {
      method: "DELETE",
    });
  }
}

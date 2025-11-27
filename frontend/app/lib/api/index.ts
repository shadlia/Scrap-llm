import { Product, Products } from "@/app/features/product-extractor/types";
import { FilterMode } from "@/app/features/url-filter/types";

export type ApiResponse<T> = {
  data: T;
  status: number;
  message?: string;
};

export type ApiError = {
  message: string;
  status: number;
  code?: string;
};

// Use relative URL for internal routing
const API_BASE_URL = "http://localhost:8000";

class ApiClient {
  private static instance: ApiClient;
  private baseUrl: string;

  private constructor() {
    this.baseUrl = API_BASE_URL;
  }

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      // Create fetch options with CORS settings
      const fetchOptions: RequestInit = {
        ...options,
        mode: "cors",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          ...options.headers,
        },
      };

      console.log(
        `Making request to: ${this.baseUrl}${endpoint}`,
        fetchOptions
      );

      const response = await fetch(`${this.baseUrl}${endpoint}`, fetchOptions);
      console.log("Response received:", response);

      const data = await response.json();
      console.log("Response data:", data);

      if (!response.ok) {
        throw {
          message: data.detail || data.message || "An error occurred",
          status: response.status,
          code: data.code,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      console.error("API request error:", error);
      throw {
        message: error instanceof Error ? error.message : "An error occurred",
        status: 500,
      };
    }
  }

  // URL Crawling
  public async crawlUrl(
    url: string,
    skipSitemap: boolean = false,
    skipTrim: boolean = false,
    useAgent: boolean = false,
    useHakrawler: boolean = false
  ) {
    return this.request<{ urls: string[]; status: string; message: string }>(
      "/crawl",
      {
        method: "POST",
        body: JSON.stringify({
          url,
          skip_sitemap: skipSitemap,
          skip_trim: skipTrim,
          use_agent: useAgent,
          use_hakrawler: useHakrawler,
        }),
      }
    );
  }

  // URL Filtering
  public async filterUrls(
    urls: string[],
    method: FilterMode = "regex",
    model: string = "gemini-2.5-flash"
  ) {
    return this.request<{
      product_urls: string[];
      status: string;
      message: string;
    }>("/filter", {
      method: "POST",
      body: JSON.stringify({ urls, method, model }),
    });
  }

  // Product Extraction
  public async extractProducts(
    productUrls: string[],
    domain: string,
    models: string[],
    clientId: string
  ) {
    return this.request<{
      status: string;
      message: string;
      domain: string;
      products: Product[];
    }>("/extract", {
      method: "POST",
      body: JSON.stringify({
        product_urls: productUrls,
        domain,
        models,
        client_id: clientId,
      }),
    });
  }

  // Single Product Extraction
  public async extractSingleProduct(
    clientId: string,
    processId: string,
    productUrl: string,
    domain: string,
    models: string[]
  ) {
    return this.request("/extract-single-product", {
      method: "POST",
      body: JSON.stringify({
        client_id: clientId,
        process_id: processId,
        product_url: productUrl,
        domain,
        models,
        verbose: false, // Assuming verbose is false by default for this mode
      }),
    });
  }

  // Fetch Extractions
  public async fetchExtractions(processId: string, numberOfUrls: number) {
    return this.request<{
      status: string;
      message: string;
      products: Product[];
      missing_keys: string[];
    }>("/fetch-extractions", {
      method: "POST",
      body: JSON.stringify({
        process_id: processId,
        number_of_urls: numberOfUrls,
      }),
    });
  }

  // Full Pipeline
  public async runFullPipeline(
    url: string,
    filterMethod: FilterMode = "regex",
    model: string = "gpt-4o",
    skipSitemap: boolean = false,
    clientId: string
  ) {
    return this.request<{
      status: string;
      message: string;
      crawl_results?: { total_urls: number };
      filter_results?: { product_urls_count: number };
    }>("/full-pipeline", {
      method: "POST",
      body: JSON.stringify({
        url,
        filter_method: filterMethod,
        model,
        skip_sitemap: skipSitemap,
        client_id: clientId,
      }),
    });
  }

  // Product Management
  public async getProducts() {
    return this.request<{
      products: Product[];
      status: string;
      message: string;
    }>("/products");
  }

  public async updateProduct(id: string, product: Partial<Product>) {
    return this.request<{ product: Product; status: string; message: string }>(
      `/products/${id}`,
      {
        method: "PUT",
        body: JSON.stringify(product),
      }
    );
  }

  public async deleteProduct(id: string) {
    return this.request<{ status: string; message: string }>(
      `/products/${id}`,
      {
        method: "DELETE",
      }
    );
  }
}

export const api = ApiClient.getInstance();

export const useApi = () => {
  return api;
};

import { useState } from "react";
import { Url } from "../types";
import { api } from "@/app/lib/api";

export const useUrlCrawler = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const crawlUrls = async (
    url: string,
    skipSitemap: boolean = false
  ): Promise<Url[]> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.crawlUrl(url, skipSitemap);
      // Convert string URLs to Url objects
      const urls: Url[] = response.data.urls.map((urlString: string) => ({
        url: urlString,
        isProduct: false,
      }));
      return urls;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to crawl URLs");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    crawlUrls,
    isLoading,
    error,
  };
};

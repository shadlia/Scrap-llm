"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, Search, Zap } from "lucide-react";
import type { Url } from "../types";
import { Card, CardContent } from "@/components/ui/card";
import { useUrlCrawler } from "../hooks/useUrlCrawler";
import { api } from "@/app/lib/api";

interface UrlCrawlerProps {
  onComplete: (urls: Url[]) => void;
  setIsLoading: (loading: boolean) => void;
  isLoading: boolean;
  reset?: boolean;
}

export default function UrlCrawler({
  onComplete,
  setIsLoading,
  isLoading,
  reset = false,
}: UrlCrawlerProps) {
  const [url, setUrl] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [crawlDepth, setCrawlDepth] = useState<number>(1);
  const [maxUrls, setMaxUrls] = useState<number>(20);
  const [crawledUrls, setCrawledUrls] = useState<Url[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [newUrl, setNewUrl] = useState<string>("");

  useEffect(() => {
    if (reset) {
      setUrl("");
      setError("");
      setCrawledUrls([]);
      setShowResults(false);
      setNewUrl("");
    }
  }, [reset]);

  const startCrawl = async (
    useAgent: boolean = false,
    useHakrawler: boolean = false
  ) => {
    setError("");

    if (!url) {
      setError("Please enter a URL");
      return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      setError("Please enter a valid URL starting with http:// or https://");
      return;
    }

    setIsLoading(true);

    try {
      const response = await api.crawlUrl(
        url,
        false, // skipSitemap default to false
        false, // skipTrim default to false
        useAgent,
        useHakrawler
      );
      const fetchedUrls = response.data.urls.map((urlString: string) => ({
        url: urlString,
        isProduct: false,
      }));

      setCrawledUrls(fetchedUrls);
      setShowResults(true);
    } catch (err: any) {
      setError(err.message || "Failed to crawl URL. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await startCrawl();
  };

  const handleUseAgentClick = () => {
    startCrawl(true, false);
  };

  const handleUseHakrawlerClick = () => {
    startCrawl(false, true);
  };

  const handleAddUrl = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUrl) return;

    if (!newUrl.startsWith("http://") && !newUrl.startsWith("https://")) {
      setError("Please enter a valid URL starting with http:// or https://");
      return;
    }

    setCrawledUrls([...crawledUrls, { url: newUrl, isProduct: false }]);
    setNewUrl("");
  };

  const handleRemoveUrl = (index: number) => {
    setCrawledUrls(crawledUrls.filter((_, i) => i !== index));
  };

  const handleProceedToFilter = () => {
    onComplete(crawledUrls);
  };

  return (
    <Card className="border-0 shadow-none">
      <CardContent className="p-0">
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-4">URL Crawler</h2>
            <p className="text-muted-foreground mb-4">
              Enter a website URL to crawl and discover all linked pages.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="url">Website URL</Label>
              <Input
                id="url"
                type="text"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isLoading}
              />
              {error && <p className="text-sm text-destructive">{error}</p>}
            </div>

            <div className="flex items-center flex-wrap gap-4">
              <Button
                type="submit"
                disabled={isLoading || !url}
                className="bg-black dark:bg-gray-800 hover:bg-gray-800 dark:hover:bg-gray-700 text-white"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Crawling...
                  </>
                ) : (
                  "Start Crawling"
                )}
              </Button>

              <Button
                type="button"
                onClick={handleUseAgentClick}
                disabled={isLoading || !url}
                className="bg-green-600 hover:bg-green-700 text-white flex items-center"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Using Agent...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Use Agent
                  </>
                )}
              </Button>

              <Button
                type="button"
                onClick={handleUseHakrawlerClick}
                disabled={isLoading || !url}
                className="bg-purple-600 hover:bg-purple-700 text-white flex items-center"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Using Hakrawler...
                  </>
                ) : (
                  <>
                    <Zap className="mr-2 h-4 w-4" />
                    Use Hakrawler
                  </>
                )}
              </Button>
            </div>
          </form>

          {showResults && (
            <div className="space-y-4 mt-8">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">
                  Found {crawledUrls.length} URLs
                </h3>
                <Button
                  onClick={handleProceedToFilter}
                  className="bg-black dark:bg-gray-800 hover:bg-gray-800 dark:hover:bg-gray-700 text-white"
                >
                  Proceed to Filter
                </Button>
              </div>

              <form onSubmit={handleAddUrl} className="flex gap-2">
                <Input
                  type="text"
                  placeholder="Add new URL"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                  className="flex-1"
                />
                <Button
                  type="submit"
                  variant="outline"
                  className="border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100"
                >
                  Add URL
                </Button>
              </form>

              <div className="border rounded-lg p-4">
                <div className="max-h-[400px] overflow-y-auto space-y-2">
                  {crawledUrls.map((url, index) => (
                    <div
                      key={index}
                      className="flex items-center space-x-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
                    >
                      <div className="text-sm text-muted-foreground">
                        {index + 1}.
                      </div>
                      <a
                        href={url.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm truncate flex-1 text-gray-900 dark:text-gray-100 hover:text-gray-900 dark:hover:text-gray-100 hover:underline"
                      >
                        {url.url}
                      </a>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveUrl(index)}
                        className="text-destructive hover:text-destructive"
                      >
                        Remove
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

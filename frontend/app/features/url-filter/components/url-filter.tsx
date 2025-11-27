"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Loader2,
  ArrowLeft,
  FileText,
  Hash,
  SendHorizonal,
} from "lucide-react";
import type { Url } from "@/features/url-crawler/types";
import type { ExtractionMode } from "@/features/product-extractor/types";
import type { FilterMode } from "../types";
import { Card, CardContent } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { api } from "@/app/lib/api";

interface UrlFilterProps {
  urls: Url[];
  onComplete: (urls: Url[]) => void;
  setIsLoading: (loading: boolean) => void;
  isLoading: boolean;
  onGoBack: () => void;
  extractionMode: ExtractionMode;
  setExtractionMode: (mode: ExtractionMode) => void;
  filterMode: FilterMode;
  setFilterMode: (mode: FilterMode) => void;
  onUrlsUpdate: (urls: Url[]) => void;
}

export default function UrlFilter({
  urls,
  onComplete,
  setIsLoading,
  isLoading,
  onGoBack,
  extractionMode,
  setExtractionMode,
  filterMode,
  setFilterMode,
  onUrlsUpdate,
}: UrlFilterProps) {
  const [selectedUrls, setSelectedUrls] = useState<Url[]>([]);
  const [filteredUrls, setFilteredUrls] = useState<Url[]>([]);
  const [filterApplied, setFilterApplied] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [newUrl, setNewUrl] = useState<string>("");
  const [jsonUrlsList, setJsonUrlsList] = useState<string>("");

  // Reset filtered URLs when the URL list changes
  useEffect(() => {
    setFilteredUrls([]);
    setSelectedUrls([]);
    setFilterApplied(false);
    setError(null);
  }, [urls]);

  // Auto-select filtered URLs when they're updated
  useEffect(() => {
    if (filteredUrls.length > 0) {
      setSelectedUrls(filteredUrls);
    }
  }, [filteredUrls]);

  const handleToggleUrl = (url: Url) => {
    if (selectedUrls.some((u) => u.url === url.url)) {
      setSelectedUrls(selectedUrls.filter((u) => u.url !== url.url));
    } else {
      setSelectedUrls([...selectedUrls, url]);
    }
  };

  const selectAll = () => {
    setSelectedUrls([...urls]);
  };

  const deselectAll = () => {
    setSelectedUrls([]);
  };

  const applyFilter = async () => {
    setIsLoading(true);
    setFilterApplied(false);
    setError(null);

    try {
      // Get the URLs as strings
      const urlStrings = urls.map((url) => url.url);

      // Call the API to filter URLs
      const response = await api.filterUrls(urlStrings, filterMode);

      // Convert the filtered URLs back to Url objects
      const filtered: Url[] = response.data.product_urls.map((url) => ({
        url,
        isProduct: true,
      }));

      setFilteredUrls(filtered);
      setFilterApplied(true);
    } catch (error: any) {
      console.error("Error applying filter:", error);
      setError(error.message || "Failed to filter URLs. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (selectedUrls.length === 0) {
      return;
    }

    setIsLoading(true);

    try {
      // No need for API call here, just pass the selected URLs to the next step
      onComplete(selectedUrls);
    } catch (error) {
      console.error("Error filtering URLs:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddUrl = () => {
    if (!newUrl.trim()) return;

    // Basic URL validation
    try {
      new URL(newUrl);
      const updatedUrls = [...urls, { url: newUrl.trim(), isProduct: false }];
      onUrlsUpdate(updatedUrls);
      setNewUrl(""); // Clear the input field
      setError(null);
    } catch (e) {
      setError("Please enter a valid URL");
      return;
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleAddUrl();
    }
  };

  const handleDirectExtraction = () => {
    if (!jsonUrlsList.trim()) {
      setError("Please enter a list of URLs");
      return;
    }

    try {
      // Parse the JSON array
      let urlArray: string[];
      try {
        urlArray = JSON.parse(jsonUrlsList);
        if (!Array.isArray(urlArray)) {
          throw new Error("Input is not a valid array");
        }
      } catch (e) {
        // If not valid JSON, try parsing as comma-separated list
        urlArray = jsonUrlsList
          .split("'")
          .filter((item) => item.includes("http"))
          .map((item) => item.trim())
          .filter(Boolean);

        if (urlArray.length === 0) {
          throw new Error("Could not parse URL list");
        }
      }

      // Convert to Url objects
      const directUrls: Url[] = urlArray.map((url) => ({
        url: url.trim(),
        isProduct: true,
      }));

      if (directUrls.length === 0) {
        setError("No valid URLs found");
        return;
      }

      // Send directly to extraction
      setIsLoading(true);
      onComplete(directUrls);
      setError(null);
    } catch (e: any) {
      console.error("Error parsing URLs:", e);
      setError(
        "Failed to parse URL list. Make sure it's a valid JSON array or properly formatted list."
      );
    }
  };

  return (
    <Card className="border-0 shadow-none">
      <CardContent className="p-0">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold mb-4">URL Filter</h2>
              <p className="text-muted-foreground mb-4">
                Filter URLs to identify product pages.
              </p>
            </div>
            <Button variant="outline" onClick={onGoBack} className="h-9">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Crawler
            </Button>
          </div>

          <Tabs defaultValue="filter">
            <TabsList className="mb-4">
              <TabsTrigger value="filter">Filter URLs</TabsTrigger>
              <TabsTrigger value="direct">Direct Extraction</TabsTrigger>
            </TabsList>

            <TabsContent value="filter">
              <div className="bg-muted p-4 rounded-md mb-4">
                <h3 className="text-sm font-medium mb-2">
                  Select Filtering Method
                </h3>
                <RadioGroup
                  value={filterMode}
                  onValueChange={(value) => setFilterMode(value as FilterMode)}
                  className="flex space-x-4"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="regex" id="regex-mode" />
                    <Label htmlFor="regex-mode" className="flex items-center">
                      <Hash className="h-4 w-4 mr-1" />
                      Regex Mode
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="llm" id="llm-filter-mode" />
                    <Label
                      htmlFor="llm-filter-mode"
                      className="flex items-center"
                    >
                      <FileText className="h-4 w-4 mr-1" />
                      LLM Mode
                    </Label>
                  </div>
                </RadioGroup>
                <p className="text-xs text-muted-foreground mt-2">
                  Regex Mode uses pattern matching to identify product URLs. LLM
                  Mode uses AI to analyze and identify product URLs.
                </p>

                {error && (
                  <p className="text-sm text-destructive mt-2">{error}</p>
                )}

                <div className="mt-4">
                  <Button
                    onClick={applyFilter}
                    disabled={isLoading}
                    className="bg-black hover:bg-gray-800 text-white"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Filtering URLs...
                      </>
                    ) : (
                      "Start Filtering"
                    )}
                  </Button>
                </div>
              </div>

              <div className="flex justify-between items-center mb-2">
                <div className="text-sm font-medium">
                  URL List{" "}
                  {filterApplied && (
                    <Badge variant="outline" className="ml-2">
                      {filteredUrls.length} products identified
                    </Badge>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={selectAll}>
                    Select All
                  </Button>
                  <Button variant="outline" size="sm" onClick={deselectAll}>
                    Deselect All
                  </Button>
                </div>
              </div>

              <div className="flex gap-2 mb-4">
                <Input
                  placeholder="Enter URL to add"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="flex-1"
                />
                <Button
                  onClick={handleAddUrl}
                  disabled={!newUrl.trim() || isLoading}
                  variant="outline"
                >
                  Add URL
                </Button>
              </div>

              <div className="border rounded-md p-4 max-h-[300px] overflow-y-auto">
                {urls.length > 0 ? (
                  <ul className="space-y-2">
                    {urls.map((url, index) => {
                      const isProduct = filteredUrls.some(
                        (u) => u.url === url.url
                      );
                      return (
                        <li key={index} className="flex items-start space-x-2">
                          <Checkbox
                            id={`url-${index}`}
                            checked={selectedUrls.some(
                              (u) => u.url === url.url
                            )}
                            onCheckedChange={() => handleToggleUrl(url)}
                          />
                          <Label
                            htmlFor={`url-${index}`}
                            className="text-sm cursor-pointer"
                          >
                            {url.url}
                            {filterApplied && isProduct && (
                              <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">
                                Product
                              </span>
                            )}
                          </Label>
                        </li>
                      );
                    })}
                  </ul>
                ) : (
                  <p className="text-center text-muted-foreground py-4">
                    No URLs found. Please go back to the crawler step.
                  </p>
                )}
              </div>
            </TabsContent>

            <TabsContent value="direct">
              <div className="space-y-4">
                <div className="bg-muted p-4 rounded-md">
                  <h3 className="text-sm font-medium mb-2">
                    Direct URL Extraction
                  </h3>
                  <p className="text-xs text-muted-foreground mb-4">
                    Paste a list of URLs in JSON array format or as a formatted
                    list and send directly to extraction.
                  </p>

                  <Textarea
                    placeholder={`Paste your URLs here in format like:\n['https://example.com/product1', 'https://example.com/product2']`}
                    value={jsonUrlsList}
                    onChange={(e) => setJsonUrlsList(e.target.value)}
                    rows={10}
                    className="w-full mb-4"
                  />

                  {error && (
                    <p className="text-sm text-destructive mb-4">{error}</p>
                  )}

                  <Button
                    onClick={handleDirectExtraction}
                    disabled={!jsonUrlsList.trim() || isLoading}
                    className="bg-black hover:bg-gray-800 text-white w-full"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <SendHorizonal className="mr-2 h-4 w-4" />
                        Send Directly to Extraction
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <div className="flex justify-between">
            <div className="text-sm text-muted-foreground">
              {selectedUrls.length} of {urls.length} URLs selected
            </div>
            <Button
              onClick={handleSubmit}
              disabled={selectedUrls.length === 0 || isLoading}
              className="bg-black hover:bg-gray-800 text-white"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                "Continue to Extraction"
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

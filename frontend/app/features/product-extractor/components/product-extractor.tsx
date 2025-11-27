"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Loader2,
  ArrowLeft,
  ArrowRight,
  FileText,
  Hash,
  Plus,
  Trash2,
  RefreshCw,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Url } from "@/features/url-crawler/types";
import { Product, ExtractionMode } from "../types";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { api } from "@/app/lib/api";
import { useToast } from "@/app/components/ui/use_toast";
import { ExtractionProgress } from "./extraction-progress";
import { ExtractionProgressSingle } from "./extraction-progress-single";
import { v4 as uuidv4 } from "uuid";
import { Checkbox } from "@/components/ui/checkbox";

interface ProductExtractorProps {
  urls: Url[];
  onComplete: (products: Product[]) => void;
  setIsLoading: (loading: boolean) => void;
  isLoading: boolean;
  onGoBack: () => void;
  extractionMode: ExtractionMode;
}

export default function ProductExtractor({
  urls,
  onComplete,
  setIsLoading,
  isLoading,
  onGoBack,
  extractionMode,
}: ProductExtractorProps) {
  const [clientId] = useState(() => uuidv4());
  const { toast } = useToast();
  const [extractionProgress, setExtractionProgress] = useState<number>(0);
  const [currentUrl, setCurrentUrl] = useState<string>("");
  const [extractedProducts, setExtractedProducts] = useState<Product[]>([]);
  const [completedUrls, setCompletedUrls] = useState<string[]>([]);
  const [failedUrls, setFailedUrls] = useState<string[]>([]);
  const [currentUrlIndex, setCurrentUrlIndex] = useState<number>(0);
  const [productDoneCount, setProductDoneCount] = useState<number>(0);
  const [selectedMode, setSelectedMode] =
    useState<ExtractionMode>(extractionMode);
  const [modeSelected, setModeSelected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [extractionDomain, setExtractionDomain] = useState<string | null>(null);

  const [selectedLLMs, setSelectedLLMs] = useState<string[]>([
    "gemini-2.0-flash-001",
  ]);

  const [extractionType, setExtractionType] = useState<"bulk" | "sequential">(
    "bulk"
  );

  const availableLLMs = [
    {
      id: "gemini-2.5-flash-lite-preview-06-17",
      name: "Gemini 2.5 Flash Lite",
      description: "Default",
    },
    {
      id: "gemini-2.5-flash",
      name: "Gemini 2.5 Flash",
      description: "Default",
    },
    {
      id: "gemini-2.0-flash-001",
      name: "Gemini 2.0 Flash",
      description: "Default",
    },
    {
      id: "ft:gpt-4.1-mini-2025-04-14:choose:10-samples:BXrWEC3a",
      name: "GPT-4.1-mini finetuned (v1)",
      description: "Fallback",
    },
    {
      id: "gpt-4.1-mini",
      name: "GPT-4.1-mini",
      description: "Fallback",
    },
    {
      id: "gpt-4o-mini",
      name: "GPT-4o-Mini",
      description: "Extreme cases",
    },
    {
      id: "claude-3-5-haiku-20241022",
      name: "Claude haiku",
      description: "Fallback",
    },
  ];

  const handleProductDone = useCallback((product: Product) => {
    console.log("PRODUCT DONE in product extractor", product);
    setExtractedProducts((prev) => [...prev, product]);
  }, []);

  const handleProductDoneSingle = useCallback((productData: any) => {
    console.log(
      "PRODUCT DONE in sequential mode (received via SSE):",
      productData
    );

    setExtractedProducts((prev) => {
      const productsToAdd: Product[] = [];
      if (productData) {
        if (
          Array.isArray(productData.variants) &&
          productData.variants.length > 0
        ) {
          productData.variants.forEach((variant: any) => {
            if (
              typeof variant === "object" &&
              variant !== null &&
              variant.url
            ) {
              productsToAdd.push(variant as Product);
            }
          });
        } else if (
          typeof productData === "object" &&
          productData !== null &&
          productData.url
        ) {
          productsToAdd.push(productData as Product);
        }
      }
      const currentIds = new Set(prev.map((p) => p.id || p.url));
      const newProducts = productsToAdd.filter(
        (p) =>
          !(p.id && currentIds.has(p.id)) && !(p.url && currentIds.has(p.url))
      );

      return [...prev, ...newProducts];
    });
  }, []);

  const startExtraction = async () => {
    if (urls.length === 0) return;

    setIsLoading(true);
    setExtractionProgress(0);
    setExtractedProducts([]);
    setError(null);
    setCompletedUrls([]);
    setFailedUrls([]);
    setCurrentUrlIndex(0);
    setProductDoneCount(0);

    try {
      const domainMatch = urls[0].url.match(/^https?:\/\/([^\/]+)/);
      const domain = domainMatch ? domainMatch[0] : "";

      if (!domain) {
        throw new Error("Could not determine the domain from URLs");
      }

      setExtractionDomain(domain);

      const urlStrings = urls.map((url) => url.url);

      const sortedLLMs = [...selectedLLMs].sort((a, b) => {
        const priorityA = selectedLLMs.indexOf(a);
        const priorityB = selectedLLMs.indexOf(b);
        return priorityA - priorityB;
      });

      let finalProducts: Product[] = [];

      if (extractionType === "bulk") {
        setCurrentUrl(
          `Sending bulk extraction request to server for ${urlStrings.length} URLs...`
        );
        console.log("selectedLLMs (sorted by priority):", sortedLLMs);
        const response = await api.extractProducts(
          urlStrings,
          domain,
          sortedLLMs,
          clientId
        );

        setCurrentUrl("Processing extracted product data...");

        if (response.data.products && Array.isArray(response.data.products)) {
          console.log("response.data", response.data);
          const apiProducts = response.data.products;

          finalProducts = apiProducts.map((product: any, index) => {
            return {
              id: `product-${index + 1}`,
              url: product.url,
              product_name: product.product_name || `Product ${index + 1}`,
              product_subname: product.product_subname || "",
              product_sku: product.product_sku || "",
              product_gtin: product.product_gtin || "",
              product_public_price_ttc: product.product_public_price_ttc || "",
              product_price_after_discount_ttc:
                product.product_price_after_discount_ttc || "",
              product_inci_composition: product.product_inci_composition || "",
              product_option: product.product_option || "",
              product_color: product.product_color || "",
              product_size: product.product_size || "",
              product_stock: product.product_stock || "",
              product_country_of_manufacture:
                product.product_country_of_manufacture || "",
              product_image_url:
                product.product_image_url || "/app/image-break.png",
            };
          });
        }

        setExtractedProducts(finalProducts);
        onComplete(finalProducts);
      }
      setCurrentUrl(
        `Starting sequential extraction for ${urlStrings.length} URLs...`
      );
      const strippedDomain = domain.split("://")[1];

      for (let i = 0; i < urlStrings.length; i++) {
        const url = urlStrings[i];
        setCurrentUrlIndex(i);
        setCurrentUrl(`Processing URL ${i + 1}/${urlStrings.length}: ${url}`);

        try {
          await api.extractSingleProduct(
            clientId,
            `${strippedDomain}_${clientId}_${i}`,
            url,
            domain,
            sortedLLMs
          );

          setCompletedUrls((prev) => [...prev, url]);
        } catch (error) {
          console.error(`Error processing URL ${url}:`, error);
          setFailedUrls((prev) => [...prev, url]);
        }
      }
    } catch (error: any) {
      console.error("Error extracting products:", error);
      setError(
        error.message || "Failed to extract products. Please try again."
      );
    } finally {
      setIsLoading(false);
      if (extractionType !== "sequential") {
        setIsLoading(false);
      }
    }
  };

  const handleSequentialCompletion = useCallback(async () => {
    console.log(
      "Sequential extraction process complete based on SSE signals. Fetching final results..."
    );

    if (!extractionDomain) {
      console.error(
        "Extraction domain is not set. Cannot fetch final results."
      );
      toast({
        title: "Internal Error",
        description:
          "Extraction domain was not available for fetching results.",
        variant: "destructive",
      });
      setIsLoading(false);
      onComplete(extractedProducts);
      return;
    }

    try {
      const strippedDomain = extractionDomain.split("://")[1];
      const processId = `${strippedDomain}_${clientId}`;
      console.log(
        `Calling fetchExtractions with processId: ${processId}, numberOfUrls: ${urls.length}`
      );
      const response = await api.fetchExtractions(processId, urls.length);

      console.log("fetchExtractions response:", response);

      if (response.data && response.data.products) {
        console.log(
          `Fetched ${response.data.products.length} products from the backend.`
        );
        if (
          response.data.missing_keys &&
          response.data.missing_keys.length > 0
        ) {
          console.warn(
            "Missing keys reported by fetchExtractions:",
            response.data.missing_keys
          );
        }
        onComplete(response.data.products);
      } else {
        console.error("fetchExtractions did not return expected product data.");
        toast({
          title: "Extraction Partially Complete",
          description:
            "Could not fetch final results from the server. Displaying locally gathered data.",
          variant: "destructive",
        });
        onComplete(extractedProducts);
      }
    } catch (error: any) {
      console.error("Error calling fetchExtractions:", error);
      toast({
        title: "Error Fetching Results",
        description: `Failed to fetch final extraction results: ${
          error.message || "Unknown error"
        }. Please check console.`,
        variant: "destructive",
      });
      onComplete(extractedProducts);
    } finally {
      setIsLoading(false);
    }
  }, [
    clientId,
    urls.length,
    onComplete,
    toast,
    extractedProducts,
    setIsLoading,
    extractionDomain,
  ]);

  const handleLLMSelection = (llmId: string) => {
    setSelectedLLMs((prev) => {
      if (prev.includes(llmId)) {
        return prev.filter((id) => id !== llmId);
      } else {
        return [...prev, llmId];
      }
    });
  };

  const getLLMPriority = (llmId: string) => {
    const index = selectedLLMs.indexOf(llmId);
    return index === -1 ? null : index + 1;
  };

  return (
    <Card className="border-0 shadow-none">
      <CardContent className="p-0">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold mb-4">Product Extraction</h2>
              <p className="text-muted-foreground mb-4">
                Extract detailed product information from the selected URLs.
              </p>
              {error && (
                <p className="text-sm text-destructive mb-4">{error}</p>
              )}
            </div>
            <Button variant="outline" onClick={onGoBack} className="h-9">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Filter
            </Button>
          </div>

          {!modeSelected ? (
            <div className="space-y-6">
              <RadioGroup
                value={selectedMode}
                onValueChange={(value) =>
                  setSelectedMode(value as ExtractionMode)
                }
                className="space-y-4"
              >
                <div className="flex items-start space-x-3 p-4 border rounded-md bg-background hover:bg-accent/50 cursor-pointer">
                  <RadioGroupItem value="llm" id="llm-mode" className="mt-1" />
                  <div className="flex-grow">
                    <Label
                      htmlFor="llm-mode"
                      className="text-base font-medium flex items-center cursor-pointer"
                    >
                      <FileText className="h-5 w-5 mr-2" />
                      Brute Force Mode
                    </Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      Use AI to automatically detect and extract product
                      information. Works on most websites without configuration.
                    </p>
                    {selectedMode === "llm" && (
                      <div className="mt-4 space-y-4">
                        <div>
                          <Label className="text-sm font-medium mb-2 block">
                            Extraction Type
                          </Label>
                          <RadioGroup
                            value={extractionType}
                            onValueChange={(value) =>
                              setExtractionType(value as "bulk" | "sequential")
                            }
                            className="flex space-x-4"
                          >
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem value="bulk" id="bulk" />
                              <Label htmlFor="bulk" className="text-sm">
                                Bulk
                              </Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <RadioGroupItem
                                value="sequential"
                                id="sequential"
                              />
                              <Label htmlFor="sequential" className="text-sm">
                                Sequential
                              </Label>
                            </div>
                          </RadioGroup>
                          <p className="text-xs text-muted-foreground mt-1">
                            {extractionType === "bulk"
                              ? "Process all URLs in a single batch (faster but may be less reliable)"
                              : "Process URLs one by one (slower but more reliable)"}
                          </p>
                        </div>
                        <div className="space-y-2 border rounded-md p-3 bg-muted/50">
                          <Label className="text-sm font-medium mb-2 block">
                            Select AI Models
                          </Label>
                          {availableLLMs.map((llm) => {
                            const priority = getLLMPriority(llm.id);
                            return (
                              <div
                                key={llm.id}
                                className="flex items-start space-x-3"
                              >
                                <Checkbox
                                  id={llm.id}
                                  checked={selectedLLMs.includes(llm.id)}
                                  onCheckedChange={() =>
                                    handleLLMSelection(llm.id)
                                  }
                                />
                                <div className="space-y-1 flex-grow">
                                  <div className="flex items-center justify-between">
                                    <Label
                                      htmlFor={llm.id}
                                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                                    >
                                      {llm.name}
                                    </Label>
                                    {priority && (
                                      <Badge variant="outline" className="ml-2">
                                        Priority #{priority}
                                      </Badge>
                                    )}
                                  </div>
                                  <p className="text-sm text-muted-foreground">
                                    {llm.description}
                                  </p>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </RadioGroup>
              <div className="mt-6 flex justify-end">
                <Button
                  onClick={() => {
                    setModeSelected(true);
                    startExtraction();
                  }}
                  className="bg-black hover:bg-gray-800 text-white"
                  disabled={selectedMode === "llm" && selectedLLMs.length === 0}
                >
                  Continue with Brute Force Mode
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {extractionType === "bulk" ? (
                <ExtractionProgress
                  progress={extractionProgress}
                  currentUrl={currentUrl}
                  isLoading={isLoading}
                  onProgressUpdate={(newProgress, newUrl) => {
                    setExtractionProgress(newProgress);
                    setCurrentUrl(newUrl);
                  }}
                  onProductDone={handleProductDone}
                  clientId={clientId}
                />
              ) : (
                <ExtractionProgressSingle
                  progress={extractionProgress}
                  currentUrl={currentUrl}
                  isLoading={isLoading}
                  onProgressUpdate={(newProgress, newUrl) => {
                    setExtractionProgress(newProgress);
                    setCurrentUrl(newUrl);
                  }}
                  onProductDone={handleProductDoneSingle}
                  clientId={clientId}
                  totalUrls={urls.length}
                  currentUrlIndex={currentUrlIndex}
                  completedUrls={completedUrls}
                  failedUrls={failedUrls}
                  onCompletionReached={handleSequentialCompletion}
                />
              )}
            </div>
          )}

          {!isLoading && extractedProducts.length > 0 && (
            <div className="flex justify-end">
              <Button
                onClick={() => onComplete(extractedProducts)}
                className="bg-black hover:bg-gray-800 text-white"
              >
                View Results
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

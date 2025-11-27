import { Progress } from "@/components/ui/progress";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";
import { useEffect, useCallback, useState, useRef } from "react";
import useSSE from "../hooks/useSSE";
import { Product } from "../types";
import { formatTime } from "@/lib/utils";
import { generateWebSocketToken } from "@/lib/jwt";

// Helper function to extract URL from product data, handling single product or variants
const getUrlFromProductData = (productData: any): string | null => {
  if (!productData) return null;
  // If variants exist and contain product info, use the first variant's URL as context
  if (
    Array.isArray(productData.variants) &&
    productData.variants.length > 0 &&
    productData.variants[0].url
  ) {
    return productData.variants[0].url;
  }
  // Fallback to the main product URL
  return productData.url;
};

interface ExtractionProgressSingleProps {
  progress: number;
  currentUrl: string;
  isLoading: boolean;
  onProgressUpdate?: (progress: number, currentUrl: string) => void;
  onProductDone?: (product: Product) => void; // Receives the raw product structure from SSE
  clientId: string;
  totalUrls: number;
  currentUrlIndex: number;
  completedUrls: string[]; // URLs whose API call succeeded
  failedUrls: string[]; // URLs whose API call failed
  onCompletionReached: () => void; // Callback when all expected URLs are processed via SSE
}

export function ExtractionProgressSingle({
  progress,
  currentUrl,
  isLoading,
  onProgressUpdate,
  onProductDone,
  clientId,
  totalUrls,
  currentUrlIndex,
  completedUrls,
  failedUrls,
  onCompletionReached,
}: ExtractionProgressSingleProps) {
  const [extractedProducts, setExtractedProducts] = useState<Product[]>([]);
  const [completedProductUrls, setCompletedProductUrls] = useState<Set<string>>(
    new Set()
  );
  const onProductDoneRef = useRef(onProductDone);
  const onCompletionReachedRef = useRef(onCompletionReached);
  const processedMessagesRef = useRef<Set<string>>(new Set());
  const [token, setToken] = useState<string | null>(null);
  const sseUrl = `${process.env.NEXT_PUBLIC_SSE_URL}/events?topic=${clientId}`;

  useEffect(() => {
    async function initToken() {
      const generatedToken = await generateWebSocketToken(clientId);
      setToken(generatedToken);
    }
    if (clientId) {
      initToken();
    }
  }, [clientId]);

  const { messages, disconnect } = useSSE({
    url: sseUrl,
    token: token ?? undefined,
  });
  const disconnectRef = useRef(disconnect); // Use ref for stable callback in effect
  const [elapsedTime, setElapsedTime] = useState(0);

  // Update refs when props change
  useEffect(() => {
    onProductDoneRef.current = onProductDone;
  }, [onProductDone]);

  useEffect(() => {
    onCompletionReachedRef.current = onCompletionReached;
  }, [onCompletionReached]);

  useEffect(() => {
    disconnectRef.current = disconnect;
  }, [disconnect]);

  // Reset state when loading starts
  useEffect(() => {
    if (isLoading) {
      setCompletedProductUrls(new Set());
      processedMessagesRef.current.clear();
      setExtractedProducts([]); // Clear local display products
      setElapsedTime(0); // Reset timer
    }
  }, [isLoading]);

  // Process WebSocket messages
  useEffect(() => {
    if (messages && messages.length > 0) {
      //console.log("Total messages received:", messages.length);

      const newMessages = messages.filter(
        (message) => !processedMessagesRef.current.has(message)
      );

      let urlAddedInBatch = false; // Flag to update state only once per batch if needed

      newMessages.forEach((message) => {
        processedMessagesRef.current.add(message); // Mark as processed immediately
        try {
          const data = JSON.parse(message);
          if (data.type === "product_done") {
            //console.log("Product done response:", data.product);
            const productUrl = getUrlFromProductData(data.product);

            // Update local state for display
            if (data.product) {
              if (
                data.product.variants &&
                Array.isArray(data.product.variants)
              ) {
                // Ensure variants is an array of Product-like objects before adding
                const validVariants = data.product.variants.filter(
                  (v: any) => typeof v === "object" && v !== null
                );
                if (validVariants.length > 0) {
                  setExtractedProducts((prev) => [...prev, ...validVariants]);
                }
              } else {
                // Ensure it's a valid product object before adding
                if (
                  typeof data.product === "object" &&
                  data.product !== null &&
                  data.product.url
                ) {
                  setExtractedProducts((prev) => [...prev, data.product]);
                }
              }
              // Call parent's handler with the raw structure received
              onProductDoneRef.current?.(data.product);
            }

            // Track completed URL if valid URL found and not already tracked
            if (productUrl && !completedProductUrls.has(productUrl)) {
              setCompletedProductUrls((prev) => {
                const newSet = new Set(prev);
                newSet.add(productUrl);
                return newSet;
              });
              urlAddedInBatch = true; // Indicate state update occurred
            }
          }
          // else if (data.type === 'error' || data.type === 'url_failed') {
          //    // Optional: Handle specific failure messages from SSE if backend sends them
          //    // You might want to track failed URLs here as well for completion logic
          // }
        } catch (error) {
          console.error(
            "Error parsing WebSocket message:",
            error,
            "Message content:",
            message
          );
        }
      });

      // This check was moved outside the loop, potentially unnecessary if setCompletedProductUrls triggers the effect correctly
      // if (urlAddedInBatch) {
      // The useEffect depending on completedProductUrls handles the completion check
      // }
    }
  }, [messages, completedProductUrls]); // Depend on completedProductUrls to ensure has check is up-to-date

  // Check for completion based on SSE messages
  useEffect(() => {
    // Only check if we expect URLs and the count is reached
    if (totalUrls > 0 && completedProductUrls.size >= totalUrls) {
      console.log(
        `SSE Completion Check: ${completedProductUrls.size}/${totalUrls} unique URLs processed via SSE. Triggering completion.`
      );
      onCompletionReachedRef.current();
      disconnectRef.current(); // Disconnect SSE stream
    }
  }, [completedProductUrls, totalUrls]); // Dependencies: count, total

  // Start timer when loading begins
  useEffect(() => {
    let timer: NodeJS.Timeout | null = null;

    if (isLoading) {
      const startTime = Date.now();
      // Ensure timer starts only once
      if (!timer) {
        timer = setInterval(() => {
          const elapsed = Math.floor((Date.now() - startTime) / 1000);
          setElapsedTime(elapsed);
        }, 1000);
      }
    } else {
      // Clear timer if loading stops for any reason before completion is reached
      if (timer) clearInterval(timer);
    }

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isLoading]);

  // Use currentUrlIndex passed from parent for overall progress
  const overallProgress =
    totalUrls > 0 ? (currentUrlIndex / totalUrls) * 100 : 0;

  // Calculate processed count based on completed/failed *API calls* for display
  const processedApiCallCount = completedUrls.length + failedUrls.length;

  return (
    <div className="space-y-4">
      {/* Overall Progress based on API calls initiated */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Overall Request Progress</span>
          <span>
            {processedApiCallCount} / {totalUrls} URLs requested
          </span>
        </div>
        <Progress
          value={totalUrls > 0 ? (processedApiCallCount / totalUrls) * 100 : 0}
          className="h-2"
        />
      </div>

      {/* Current URL being processed (from parent loop) */}
      {isLoading && currentUrlIndex < totalUrls && (
        <div className="border rounded-md p-4 bg-muted/50">
          <div className="flex items-center space-x-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm truncate" title={currentUrl}>
              Processing request for: {currentUrl}
            </span>
          </div>
        </div>
      )}
      {/* Display when all requests sent but waiting for SSE completion */}
      {isLoading && currentUrlIndex >= totalUrls && (
        <div className="border rounded-md p-4 bg-muted/50">
          <div className="flex items-center space-x-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">
              All requests sent. Waiting for final results (
              {completedProductUrls.size}/{totalUrls})...
            </span>
          </div>
        </div>
      )}

      {/* URL Status List (based on API call status from parent) */}
      {(completedUrls.length > 0 || failedUrls.length > 0) && (
        <div className="border rounded-md p-4">
          <h3 className="text-sm font-medium mb-2">URL Request Status</h3>
          <div className="space-y-2 max-h-[200px] overflow-y-auto">
            {completedUrls.map((url, index) => (
              <div
                key={`comp-${index}`}
                className="flex items-center space-x-2 text-sm"
              >
                <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />
                <span className="truncate" title={url}>
                  {url}
                </span>
              </div>
            ))}
            {failedUrls.map((url, index) => (
              <div
                key={`fail-${index}`}
                className="flex items-center space-x-2 text-sm"
              >
                <XCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                <span className="truncate" title={url}>
                  {url}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extracted Products (live updates from SSE) */}
      <div className="border rounded-md p-4 max-h-[250px] overflow-y-auto">
        <h3 className="text-sm font-medium mb-2">
          Extracted Products ({extractedProducts.length} found so far)
        </h3>
        {extractedProducts.length > 0 ? (
          <ul className="space-y-3 divide-y">
            {extractedProducts
              .slice()
              .reverse()
              .map((product, index) => (
                <li
                  key={product.id || `${product.url}-${index}`}
                  className="pt-3 first:pt-0 flex gap-4"
                >
                  <div className="w-20 h-20 flex-shrink-0 overflow-hidden rounded bg-muted">
                    <img
                      // Use a placeholder if image URL is missing or invalid
                      src={product.product_image_url || "/app/image-break.png"}
                      alt={product.product_name || "Product Image"}
                      className="w-full h-full object-cover"
                      onError={(e) =>
                        (e.currentTarget.src = "/app/image-break.png")
                      } // Fallback image on error
                    />
                  </div>
                  <div className="flex-grow min-w-0">
                    {" "}
                    {/* Added min-w-0 for better truncation */}
                    <div
                      className="font-medium truncate"
                      title={product.product_name}
                    >
                      {product.product_name || "N/A"}
                    </div>
                    {product.product_subname && (
                      <div
                        className="text-sm text-muted-foreground truncate"
                        title={product.product_subname}
                      >
                        {product.product_subname}
                      </div>
                    )}
                    <div
                      className="text-sm text-muted-foreground truncate"
                      title={product.url}
                    >
                      {product.url}
                    </div>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      {" "}
                      {/* Added flex-wrap */}
                      {product.product_public_price_ttc && (
                        <span className="text-sm line-through text-muted-foreground whitespace-nowrap">
                          {product.product_public_price_ttc}
                        </span>
                      )}
                      {product.product_price_after_discount_ttc && (
                        <span className="text-sm font-semibold whitespace-nowrap">
                          {product.product_price_after_discount_ttc}
                        </span>
                      )}
                      {!product.product_price_after_discount_ttc && (
                        <span className="text-sm font-semibold whitespace-nowrap">
                          Price N/A
                        </span>
                      )}
                    </div>
                  </div>
                </li>
              ))}
          </ul>
        ) : (
          <p className="text-center text-muted-foreground py-4">
            {isLoading
              ? "Waiting for extraction results..."
              : "No products extracted yet."}
          </p>
        )}
      </div>

      {/* Time Elapsed */}
      <div className="flex justify-between items-center mb-2">
        <div className="text-sm text-muted-foreground">
          Time elapsed: {formatTime(elapsedTime)}
        </div>
        <div className="text-sm text-muted-foreground">
          SSE Processed: {completedProductUrls.size} / {totalUrls}
        </div>
      </div>
    </div>
  );
}

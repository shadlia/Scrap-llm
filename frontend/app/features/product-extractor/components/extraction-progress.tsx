import { Progress } from "@/components/ui/progress";
import { Loader2 } from "lucide-react";
import { useEffect, useCallback, useState, useRef } from "react";
import useSSE from "../hooks/useSSE";
import { v4 as uuidv4 } from "uuid";
import { Product } from "../types";
import { formatTime } from "@/lib/utils";
import { generateWebSocketToken } from "@/lib/jwt";

interface ExtractionProgressProps {
  progress: number;
  currentUrl: string;
  isLoading: boolean;
  onProgressUpdate?: (progress: number, currentUrl: string) => void;
  onProductDone?: (product: Product) => void;
  onComplete?: (elapsedTime: number) => void;
  clientId: string;
}

export function ExtractionProgress({
  progress,
  currentUrl,
  isLoading,
  onProgressUpdate,
  onProductDone,
  onComplete,
  clientId,
}: ExtractionProgressProps) {
  const [extractedProducts, setExtractedProducts] = useState<Product[]>([]);
  const onProductDoneRef = useRef(onProductDone);
  const lastProcessedMessageRef = useRef<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const sseUrl = `${process.env.NEXT_PUBLIC_SSE_URL}/events?topic=${clientId}`;

  useEffect(() => {
    async function initToken() {
      const generatedToken = await generateWebSocketToken(clientId);
      setToken(generatedToken);
    }
    initToken();
  }, [clientId]);

  const { messages, disconnect } = useSSE({
    url: sseUrl,
    token: token ?? undefined,
  });
  const [elapsedTime, setElapsedTime] = useState(0);

  // Update ref when onProductDone changes
  useEffect(() => {
    onProductDoneRef.current = onProductDone;
  }, [onProductDone]);

  const handleProductDone = useCallback((product: Product) => {
    setExtractedProducts((prev: Product[]) => {
      // Check if product with same name already exists
      const exists = prev.some(
        (p: Product) => p.product_name === product.product_name
      );
      if (exists) return prev;
      return [...prev, product];
    });
    onProductDoneRef.current?.(product);
  }, []);

  // Process WebSocket messages
  useEffect(() => {
    if (messages && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];

      // Skip if we've already processed this message
      if (lastMessage === lastProcessedMessageRef.current) {
        return;
      }

      lastProcessedMessageRef.current = lastMessage;

      try {
        const data = JSON.parse(lastMessage);

        if (data.type === "progress") {
          onProgressUpdate?.(data.progress, data.currentUrl);
        } else if (data.type === "product_done") {
          handleProductDone(data.product);
        } else if (data.type === "complete") {
          onComplete?.(elapsedTime);
          disconnect();
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    }
  }, [
    messages,
    onProgressUpdate,
    disconnect,
    handleProductDone,
    elapsedTime,
    onComplete,
  ]);

  // Start timer when loading begins
  useEffect(() => {
    let timer: NodeJS.Timeout;

    if (isLoading) {
      const startTime = Date.now();
      timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        setElapsedTime(elapsed);
      }, 1000);
    }

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isLoading]);

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Extraction Progress</span>
          <span>{progress}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {isLoading && (
        <div className="border rounded-md p-4 bg-muted/50">
          <div className="flex items-center space-x-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Currently processing: {currentUrl}</span>
          </div>
        </div>
      )}

      <div className="border rounded-md p-4 max-h-[250px] overflow-y-auto">
        {extractedProducts.length > 0 ? (
          <ul className="space-y-3 divide-y">
            {extractedProducts
              .slice()
              .reverse()
              .map((product, index) => (
                <li key={index} className="pt-3 first:pt-0 flex gap-4">
                  <div className="w-20 h-20 flex-shrink-0 overflow-hidden rounded">
                    <img
                      src={
                        product.product_image_url ||
                        `/placeholder.svg?height=80&width=80&text=${encodeURIComponent(
                          product.product_name.substring(0, 10)
                        )}`
                      }
                      alt={product.product_name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="flex-grow">
                    <div className="font-medium">{product.product_name}</div>
                    {product.product_subname && (
                      <div className="text-sm text-muted-foreground">
                        {product.product_subname}
                      </div>
                    )}
                    <div className="text-sm text-muted-foreground truncate">
                      {product.url}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      {product.product_public_price_ttc && (
                        <span className="text-sm line-through text-muted-foreground">
                          {product.product_public_price_ttc}
                        </span>
                      )}
                      <div className="text-sm font-semibold">
                        {product.product_price_after_discount_ttc}
                      </div>
                    </div>
                  </div>
                </li>
              ))}
          </ul>
        ) : (
          <p className="text-center text-muted-foreground py-4">
            {isLoading
              ? "Starting extraction..."
              : "No products extracted yet."}
          </p>
        )}
      </div>

      <div className="flex justify-between items-center mb-2">
        <div className="text-sm text-muted-foreground">
          Time elapsed: {formatTime(elapsedTime)}
        </div>
      </div>
    </div>
  );
}

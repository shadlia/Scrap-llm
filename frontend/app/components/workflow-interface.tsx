"use client";

import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Search,
  Plus,
  Code,
  BookOpen,
  BookX,
  Menu,
  X,
  ChevronDown,
  Check,
} from "lucide-react";
import { Url } from "@/features/url-crawler/types";
import { Product, ExtractionMode } from "@/features/product-extractor/types";
import { FilterMode } from "@/features/url-filter/types";
import UrlCrawler from "@/features/url-crawler/components/url-crawler";
import UrlFilter from "@/features/url-filter/components/url-filter";
import ProductExtractor from "@/features/product-extractor/components/product-extractor";
import ResultsDisplay from "@/features/results/components/results-display";
import { Logo } from "@/components/shared/logo";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/app/components/ui/dropdown-menu";
import confetti from "canvas-confetti";
import { ConfettiButton } from "@/components/ui/confetti-button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Textarea } from "@/components/ui/textarea";

export default function WorkflowInterface() {
  // Workflow state
  const [step, setStep] = useState<"crawl" | "filter" | "extract" | "results">(
    "crawl"
  );
  const [isLoading, setIsLoading] = useState(false);
  const [urls, setUrls] = useState<Url[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [extractionMode, setExtractionMode] = useState<ExtractionMode>("llm");
  const [filterMode, setFilterMode] = useState<FilterMode>("regex");
  const [reset, setReset] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    isOpen: boolean;
    productId: string | null;
  }>({ isOpen: false, productId: null });
  const [confettiInterval, setConfettiInterval] =
    useState<NodeJS.Timeout | null>(null);
  const [manualUrls, setManualUrls] = useState("");

  // Cleanup confetti when component unmounts or step changes
  useEffect(() => {
    return () => {
      if (confettiInterval) {
        clearInterval(confettiInterval);
      }
    };
  }, [confettiInterval]);

  const startConfetti = () => {
    const duration = 5 * 1000; // 5 seconds
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

    function randomInRange(min: number, max: number) {
      return Math.random() * (max - min) + min;
    }

    const interval = window.setInterval(() => {
      const timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        clearInterval(interval);
        setConfettiInterval(null);
        return;
      }

      const particleCount = 50 * (timeLeft / duration);

      // Fireworks from multiple angles
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
        colors: ["#FFD700", "#FFA500", "#FF69B4", "#87CEEB", "#98FB98"],
      });

      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
        colors: ["#FFD700", "#FFA500", "#FF69B4", "#87CEEB", "#98FB98"],
      });

      // Add some fireworks from the bottom
      confetti({
        ...defaults,
        particleCount: particleCount * 0.5,
        origin: { x: randomInRange(0.3, 0.7), y: 0.8 },
        colors: ["#FFD700", "#FFA500", "#FF69B4", "#87CEEB", "#98FB98"],
      });
    }, 250);

    setConfettiInterval(interval as unknown as NodeJS.Timeout);
  };

  const stopConfetti = () => {
    if (confettiInterval) {
      clearInterval(confettiInterval);
      setConfettiInterval(null);
    }
  };

  // Update step handler to manage confetti
  const handleStepChange = (
    newStep: "crawl" | "filter" | "extract" | "results"
  ) => {
    if (newStep === "results") {
      startConfetti();
      // Add side cannons effect
      const end = Date.now() + 1 * 1000; // 3 seconds
      const colors = ["#a786ff", "#fd8bbc", "#eca184", "#f8deb1"];

      // Frame function to trigger confetti cannons
      function frame() {
        if (Date.now() > end) return;

        // Left side confetti cannon
        confetti({
          particleCount: 2,
          angle: 60,
          spread: 55,
          startVelocity: 60,
          origin: { x: 0, y: 0.5 },
          colors: colors,
        });

        // Right side confetti cannon
        confetti({
          particleCount: 2,
          angle: 120,
          spread: 55,
          startVelocity: 60,
          origin: { x: 1, y: 0.5 },
          colors: colors,
        });

        requestAnimationFrame(frame); // Keep calling the frame function
      }

      frame();
    } else {
      stopConfetti();
    }
    setStep(newStep);
  };

  // Step handlers
  const handleCrawlComplete = (crawledUrls: Url[]) => {
    setUrls(crawledUrls);
    handleStepChange("filter");
  };

  const handleFilterComplete = (filteredUrls: Url[]) => {
    setUrls(filteredUrls);
    handleStepChange("extract");
  };

  const handleExtractionComplete = (extractedProducts: Product[]) => {
    setProducts(extractedProducts);
    handleStepChange("results");
  };

  const handleManualUrlsSubmit = () => {
    const urlList = manualUrls
      .split("\n")
      .map((u) => u.trim())
      .filter((u) => u);
    if (urlList.length > 0) {
      const formattedUrls: Url[] = urlList.map((url) => ({
        url,
        isProduct: false,
      }));
      setUrls(formattedUrls);
      handleStepChange("filter");
    }
  };

  const handleProductUpdate = (updatedProduct: Product) => {
    setProducts(
      products.map((p) =>
        p.id === updatedProduct.id ? { ...updatedProduct, edited: true } : p
      )
    );
  };

  const handleReset = () => {
    setStep("crawl");
    setUrls([]);
    setProducts([]);
    setSearchTerm("");
    setExtractionMode("llm");
    setFilterMode("regex");
    setReset(true);
    setTimeout(() => setReset(false), 0);
  };

  const handleUrlSubmit = async (urls: string[]) => {
    setIsLoading(true);

    try {
      // Simulate progress updates
      for (let i = 0; i <= 100; i += 20) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    } catch (error: any) {
    } finally {
      setIsLoading(false);
    }
  };

  const handleProductDelete = (productId: string) => {
    setDeleteConfirmation({ isOpen: true, productId });
  };

  const confirmDelete = () => {
    if (deleteConfirmation.productId) {
      setProducts(
        products.filter((p) => p.id !== deleteConfirmation.productId)
      );
      setDeleteConfirmation({ isOpen: false, productId: null });
    }
  };

  const cancelDelete = () => {
    setDeleteConfirmation({ isOpen: false, productId: null });
  };

  const handleUrlsUpdate = (updatedUrls: Url[]) => {
    setUrls(updatedUrls);
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 p-4 lg:p-6">
      {/* Main content */}
      <div className="flex-1 space-y-8 relative">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between z-[100] relative gap-4">
          <div className="flex items-center justify-between w-full sm:w-auto">
            <div className="flex items-center space-x-4">
              <Logo />
            </div>

            {/* Mobile Menu */}
            <div className="sm:hidden">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="icon" className="h-8 w-8">
                    <Menu className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuItem onClick={handleReset}>
                    <X className="h-4 w-4 mr-2" />
                    Reset Workflow
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <div className="px-3 py-1.5">
                    <ThemeToggle />
                  </div>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-2 sm:gap-4">
            <Button
              variant="outline"
              onClick={handleReset}
              className="border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
            >
              Reset Workflow
            </Button>
            <ThemeToggle />
          </div>
        </div>

        <div className="space-y-6">
          {/* Steps */}
          <div className="flex items-center justify-between overflow-x-auto pb-4">
            <div
              className="flex items-center space-x-2 cursor-pointer min-w-[80px]"
              onClick={() => handleStepChange("crawl")}
            >
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center ${
                  step === "crawl"
                    ? "bg-black dark:bg-white text-white dark:text-black"
                    : "bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
                }`}
              >
                1
              </div>
              <div className="text-sm font-medium whitespace-nowrap">Crawl</div>
            </div>
            <div className="flex-1 h-px bg-gray-200 dark:bg-gray-600 mx-2 sm:mx-4" />
            <div
              className="flex items-center space-x-2 cursor-pointer min-w-[80px]"
              onClick={() => urls.length > 0 && handleStepChange("filter")}
            >
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center ${
                  step === "filter"
                    ? "bg-black dark:bg-white text-white dark:text-black"
                    : urls.length > 0
                    ? "bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
                    : "bg-gray-100 dark:bg-gray-700 opacity-50"
                }`}
              >
                2
              </div>
              <div className="text-sm font-medium whitespace-nowrap">
                Filter
              </div>
            </div>
            <div className="flex-1 h-px bg-gray-200 dark:bg-gray-600 mx-2 sm:mx-4" />
            <div
              className="flex items-center space-x-2 cursor-pointer min-w-[80px]"
              onClick={() => urls.length > 0 && handleStepChange("extract")}
            >
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center ${
                  step === "extract"
                    ? "bg-black dark:bg-white text-white dark:text-black"
                    : urls.length > 0
                    ? "bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
                    : "bg-gray-100 dark:bg-gray-700 opacity-50"
                }`}
              >
                3
              </div>
              <div className="text-sm font-medium whitespace-nowrap">
                Extract
              </div>
            </div>
            <div className="flex-1 h-px bg-gray-200 dark:bg-gray-600 mx-2 sm:mx-4" />
            <div
              className="flex items-center space-x-2 cursor-pointer min-w-[80px]"
              onClick={() => products.length > 0 && handleStepChange("results")}
            >
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center ${
                  step === "results"
                    ? "bg-black dark:bg-white text-white dark:text-black"
                    : products.length > 0
                    ? "bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
                    : "bg-gray-100 dark:bg-gray-700 opacity-50"
                }`}
              >
                4
              </div>
              <div className="text-sm font-medium whitespace-nowrap">
                Results
              </div>
            </div>
          </div>

          {/* Headers */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-1 sm:space-y-0 sm:space-x-4">
              <h1 className="text-xl sm:text-2xl font-bold">
                Product Extraction Workflow
              </h1>
              <div className="text-sm text-muted-foreground">
                {step === "crawl" &&
                  "Start by crawling a website to find product URLs"}
                {step === "filter" &&
                  "Filter the crawled URLs to identify product pages"}
                {step === "extract" &&
                  "Extract product information from the filtered URLs"}
                {step === "results" && "View and manage the extracted products"}
              </div>
            </div>
            {step === "results" && (
              <div className="flex gap-4">
                <ConfettiButton
                  options={{
                    particleCount: 100,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: [
                      "#FFD700",
                      "#FFA500",
                      "#FF69B4",
                      "#87CEEB",
                      "#98FB98",
                    ],
                  }}
                  className="bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white"
                >
                  🎉 Celebrate Results!
                </ConfettiButton>
              </div>
            )}
          </div>

          {/* Feature Components */}
          {step === "crawl" && (
            <Tabs defaultValue="crawler" className="w-full">
              <TabsList>
                <TabsTrigger value="crawler">Crawler</TabsTrigger>
                <TabsTrigger value="manual">Enter URLs Manually</TabsTrigger>
              </TabsList>
              <TabsContent value="crawler">
                <UrlCrawler
                  onComplete={handleCrawlComplete}
                  setIsLoading={setIsLoading}
                  isLoading={isLoading}
                  reset={reset}
                />
              </TabsContent>
              <TabsContent value="manual">
                <div className="space-y-4 pt-4">
                  <Label htmlFor="manual-urls">Enter URLs (one per line)</Label>
                  <Textarea
                    id="manual-urls"
                    value={manualUrls}
                    onChange={(e) => setManualUrls(e.target.value)}
                    rows={10}
                    placeholder="https://example.com/product-1&#10;https://example.com/product-2"
                  />
                  <Button
                    onClick={handleManualUrlsSubmit}
                    disabled={!manualUrls.trim()}
                  >
                    Proceed to Filter
                  </Button>
                </div>
              </TabsContent>
            </Tabs>
          )}

          {step === "filter" && (
            <UrlFilter
              urls={urls}
              onComplete={handleFilterComplete}
              setIsLoading={setIsLoading}
              isLoading={isLoading}
              onGoBack={() => handleStepChange("crawl")}
              extractionMode={extractionMode}
              setExtractionMode={setExtractionMode}
              filterMode={filterMode}
              setFilterMode={setFilterMode}
              onUrlsUpdate={handleUrlsUpdate}
            />
          )}

          {step === "extract" && (
            <ProductExtractor
              urls={urls}
              onComplete={handleExtractionComplete}
              setIsLoading={setIsLoading}
              isLoading={isLoading}
              onGoBack={() => handleStepChange("filter")}
              extractionMode={extractionMode}
            />
          )}

          {step === "results" && (
            <ResultsDisplay
              products={products}
              onReset={handleReset}
              onGoBack={() => handleStepChange("extract")}
              onUpdateProduct={handleProductUpdate}
              onDeleteProduct={handleProductDelete}
              searchTerm={searchTerm}
            />
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmation.isOpen} onOpenChange={cancelDelete}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Product</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p>
              Are you sure you want to delete this product? This action cannot
              be undone.
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={cancelDelete}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export interface JournalEntry {
  id: string;
  timestamp: Date;
  type: "info" | "success" | "error" | "warning";
  message: string;
  details?: {
    url?: string;
    selector?: string;
    productCount?: number;
    error?: string;
    originalCount?: number;
    urlCount?: number;
    method?: string;
    duration?: string;
    successRate?: string;
    reason?: string;
    previousState?: {
      step?: string;
      urlCount?: number;
      productCount?: number;
    };
    attemptedUrls?: string;
    urls?: string;
    progress?: number;
    currentStatus?: string;
    filteredCount?: number;
  };
}

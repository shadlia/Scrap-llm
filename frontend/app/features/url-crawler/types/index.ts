export type Url = {
  url: string;
  isProduct: boolean;
};

export type CrawlerResponse = {
  urls: Url[];
  status: "success" | "error";
  message?: string;
};

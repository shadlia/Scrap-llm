import { Url } from "../../url-crawler/types";

export type FilterMode = "llm" | "regex";

export type FilterResponse = {
  filteredUrls: Url[];
  status: "success" | "error";
  message?: string;
};

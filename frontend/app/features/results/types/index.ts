import { Product } from "../../product-extractor/types";

export type ResultsResponse = {
  products: Product[];
  status: "success" | "error";
  message?: string;
};

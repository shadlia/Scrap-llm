import { useState } from "react";
import { Product } from "../../product-extractor/types";
import { api } from "@/app/lib/api";

export const useResults = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getProducts = async (): Promise<Product[]> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.getProducts();
      return response.data.products;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch products");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const deleteProduct = async (id: string): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      await api.deleteProduct(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete product");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    getProducts,
    deleteProduct,
    isLoading,
    error,
  };
};

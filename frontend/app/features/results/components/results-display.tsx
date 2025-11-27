"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import {
  Download,
  RefreshCw,
  ArrowLeft,
  Edit,
  Check,
  X,
  Sparkles,
  Trash2,
} from "lucide-react";
import type { Product } from "@/features/product-extractor/types";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useResults } from "../hooks/useResults";
import { Badge } from "@/components/ui/badge";

interface ResultsDisplayProps {
  products: Product[];
  onReset: () => void;
  onGoBack: () => void;
  onUpdateProduct: (product: Product) => void;
  onDeleteProduct: (productId: string) => void;
  searchTerm: string;
}

export default function ResultsDisplay({
  products,
  onReset,
  onGoBack,
  onUpdateProduct,
  onDeleteProduct,
  searchTerm,
}: ResultsDisplayProps) {
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [editedProductName, setEditedProductName] = useState("");
  const [editedProductSubname, setEditedProductSubname] = useState("");
  const [editedProductSku, setEditedProductSku] = useState("");
  const [editedProductGtin, setEditedProductGtin] = useState("");
  const [editedProductPublicPrice, setEditedProductPublicPrice] = useState("");
  const [editedProductPriceAfterDiscount, setEditedProductPriceAfterDiscount] =
    useState("");
  const [editedProductInciComposition, setEditedProductInciComposition] =
    useState("");
  const [editedProductOption, setEditedProductOption] = useState("");
  const [editedProductColor, setEditedProductColor] = useState("");
  const [editedProductSize, setEditedProductSize] = useState("");
  const [editedProductType, setEditedProductType] = useState("");
  const [editedProductStock, setEditedProductStock] = useState("");
  const [
    editedProductCountryOfManufacture,
    setEditedProductCountryOfManufacture,
  ] = useState("");
  const [editedProductImageUrl, setEditedProductImageUrl] = useState("");
  const [activeView, setActiveView] = useState<"grid" | "table" | "json">(
    "grid"
  );
  const [aspirerDialogOpen, setAspirerDialogOpen] = useState(false);
  const [viewingProduct, setViewingProduct] = useState<Product | null>(null);

  const handleProductDelete = (productId: string) => {
    onDeleteProduct(productId);
  };

  const handleProductEdit = (product: Product) => {
    openEditDialog(product);
  };

  const handleProductView = (product: Product) => {
    openProductDetails(product);
  };

  const handleExportCSV = () => {
    // Create CSV content
    const headers = [
      "Nom Produit",
      "Couleur",
      "Taille",
      "Option",
      "URL",
      "SKU",
      "GTIN",
      "Stock",
      "Country of Manufacture",
      "Prix Public Conseillé TTC",
      "Prix Après Remise TTC",
    ];
    const csvContent = [
      headers.join(","),
      ...products.map((product) =>
        [
          `"${product.product_name?.replace(/"/g, '""') || ""}"`,
          `"${product.product_color || ""}"`,
          `"${product.product_size || ""}"`,
          `"${product.product_option || ""}"`,
          `"${product.url || ""}"`,
          `"${product.product_sku || ""}"`,
          `"${product.product_gtin || ""}"`,
          `"${product.product_stock || ""}"`,
          `"${product.product_country_of_manufacture || ""}"`,
          `"${(product.product_public_price_ttc || "").replace(/\./g, ",")}"`,
          `"${(product.product_price_after_discount_ttc || "").replace(
            /\./g,
            ","
          )}"`,
        ].join(",")
      ),
    ].join("\n");

    // Extract domain name from the first product's URL
    const domain = products[0]?.url
      ? new URL(products[0].url).hostname
          .replace(/^www\./, "")
          .replace(/\.com$/, "")
      : "extracted";

    // Create download link
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${domain}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportJSON = () => {
    const jsonContent = JSON.stringify(products, null, 2);
    const blob = new Blob([jsonContent], {
      type: "application/json;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "extracted_products.json");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const openEditDialog = (product: Product) => {
    setEditingProduct(product);
    setEditedProductName(product.product_name);
    setEditedProductSubname(product.product_subname);
    setEditedProductSku(product.product_sku);
    setEditedProductGtin(product.product_gtin);
    setEditedProductPublicPrice(product.product_public_price_ttc);
    setEditedProductPriceAfterDiscount(
      product.product_price_after_discount_ttc
    );
    setEditedProductInciComposition(product.product_inci_composition);
    setEditedProductOption(product.product_option);
    setEditedProductColor(product.product_color);
    setEditedProductSize(product.product_size);
    setEditedProductStock(product.product_stock);
    setEditedProductCountryOfManufacture(
      product.product_country_of_manufacture
    );
    setEditedProductImageUrl(product.product_image_url);
  };

  const saveProductChanges = () => {
    if (editingProduct) {
      onUpdateProduct({
        ...editingProduct,
        product_name: editedProductName,
        product_sku: editedProductSku,
        product_gtin: editedProductGtin,
        product_public_price_ttc: editedProductPublicPrice,
        product_price_after_discount_ttc: editedProductPriceAfterDiscount,
        product_option: editedProductOption,
        product_color: editedProductColor,
        product_size: editedProductSize,
        product_stock: editedProductStock,
        product_country_of_manufacture: editedProductCountryOfManufacture,
        product_image_url: editedProductImageUrl,
        edited: true,
      });
      setEditingProduct(null);
    }
  };

  const handleAspirer = () => {
    setAspirerDialogOpen(true);
  };

  const openProductDetails = (product: Product) => {
    setViewingProduct(product);
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">Extracted Products</h2>
            <p className="text-muted-foreground">
              {products.length} products extracted
            </p>
          </div>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <Button variant="outline" onClick={onGoBack} className="h-9">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Extractor
            </Button>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={handleExportJSON}
                className="h-9"
              >
                <Download className="h-4 w-4 mr-2" />
                Export JSON
              </Button>
              <Button
                variant="outline"
                onClick={handleExportCSV}
                className="bg-gradient-to-r from-purple-600 to-blue-500 hover:from-purple-700 hover:to-blue-600 text-white h-9"
              >
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>
        </div>

        {/* Product Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <Card
              key={product.id || product.url}
              className="flex flex-col justify-between"
            >
              <CardContent className="p-4 space-y-4">
                {/* Product Image */}
                {product.product_image_url && (
                  <div className="relative aspect-square overflow-hidden rounded-lg">
                    <img
                      src={product.product_image_url}
                      alt={product.product_name}
                      className="object-cover w-full h-full"
                    />
                  </div>
                )}

                {/* Product Info */}
                <div className="space-y-2">
                  <h3 className="font-semibold line-clamp-2">
                    {product.product_name}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {product.product_color && (
                      <Badge variant="secondary">{product.product_color}</Badge>
                    )}
                    {product.product_size && (
                      <Badge variant="secondary">{product.product_size}</Badge>
                    )}
                  </div>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    {product.product_sku && <p>SKU: {product.product_sku}</p>}
                    {product.product_gtin && (
                      <p>GTIN: {product.product_gtin}</p>
                    )}
                    {product.product_stock && (
                      <p>Stock: {product.product_stock}</p>
                    )}
                  </div>
                  <div className="space-y-1">
                    {product.product_public_price_ttc && (
                      <p className="text-sm font-medium">
                        Price: {product.product_public_price_ttc}
                      </p>
                    )}
                    {product.product_price_after_discount_ttc && (
                      <p className="text-sm font-medium text-green-600 dark:text-green-400">
                        After Discount:{" "}
                        {product.product_price_after_discount_ttc}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>

              <CardFooter className="p-4 pt-0 flex justify-between gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={() => handleProductView(product)}
                >
                  View Details
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={() => handleProductEdit(product)}
                >
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={() => handleProductDelete(product.id || product.url)}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>

      {/* Edit Dialog */}
      <Dialog
        open={!!editingProduct}
        onOpenChange={() => setEditingProduct(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Product</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Product Name</Label>
              <Input
                id="name"
                value={editedProductName}
                onChange={(e) => setEditedProductName(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="sku">SKU</Label>
              <Input
                id="sku"
                value={editedProductSku}
                onChange={(e) => setEditedProductSku(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="gtin">GTIN</Label>
              <Input
                id="gtin"
                value={editedProductGtin}
                onChange={(e) => setEditedProductGtin(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="price">Public Price</Label>
              <Input
                id="price"
                value={editedProductPublicPrice}
                onChange={(e) => setEditedProductPublicPrice(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="discountPrice">Price After Discount</Label>
              <Input
                id="discountPrice"
                value={editedProductPriceAfterDiscount}
                onChange={(e) =>
                  setEditedProductPriceAfterDiscount(e.target.value)
                }
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="option">Option</Label>
              <Input
                id="option"
                value={editedProductOption}
                onChange={(e) => setEditedProductOption(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="color">Color</Label>
              <Input
                id="color"
                value={editedProductColor}
                onChange={(e) => setEditedProductColor(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="size">Size</Label>
              <Input
                id="size"
                value={editedProductSize}
                onChange={(e) => setEditedProductSize(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="stock">Stock</Label>
              <Input
                id="stock"
                value={editedProductStock}
                onChange={(e) => setEditedProductStock(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="country">Country of Manufacture</Label>
              <Input
                id="country"
                value={editedProductCountryOfManufacture}
                onChange={(e) =>
                  setEditedProductCountryOfManufacture(e.target.value)
                }
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="imageUrl">Image URL</Label>
              <Input
                id="imageUrl"
                value={editedProductImageUrl}
                onChange={(e) => setEditedProductImageUrl(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingProduct(null)}>
              Cancel
            </Button>
            <Button onClick={saveProductChanges}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Details Dialog */}
      <Dialog
        open={!!viewingProduct}
        onOpenChange={() => setViewingProduct(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Product Details</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {viewingProduct?.product_image_url && (
              <div className="relative aspect-square overflow-hidden rounded-lg">
                <img
                  src={viewingProduct.product_image_url}
                  alt={viewingProduct.product_name}
                  className="object-cover w-full h-full"
                />
              </div>
            )}
            <div className="space-y-2">
              <h3 className="font-semibold">{viewingProduct?.product_name}</h3>
              {viewingProduct?.product_subname && (
                <p className="text-muted-foreground">
                  {viewingProduct.product_subname}
                </p>
              )}
              <div className="flex flex-wrap gap-2">
                {viewingProduct?.product_color && (
                  <Badge variant="secondary">
                    {viewingProduct.product_color}
                  </Badge>
                )}
                {viewingProduct?.product_size && (
                  <Badge variant="secondary">
                    {viewingProduct.product_size}
                  </Badge>
                )}
              </div>
              <div className="space-y-1 text-sm">
                {viewingProduct?.product_sku && (
                  <p>SKU: {viewingProduct.product_sku}</p>
                )}
                {viewingProduct?.product_gtin && (
                  <p>GTIN: {viewingProduct.product_gtin}</p>
                )}
                {viewingProduct?.product_stock && (
                  <p>Stock: {viewingProduct.product_stock}</p>
                )}
                {viewingProduct?.product_country_of_manufacture && (
                  <p>
                    Country of Manufacture:{" "}
                    {viewingProduct.product_country_of_manufacture}
                  </p>
                )}
              </div>
              <div className="space-y-1">
                {viewingProduct?.product_public_price_ttc && (
                  <p className="text-sm font-medium">
                    Price: {viewingProduct.product_public_price_ttc}
                  </p>
                )}
                {viewingProduct?.product_price_after_discount_ttc && (
                  <p className="text-sm font-medium text-green-600 dark:text-green-400">
                    After Discount:{" "}
                    {viewingProduct.product_price_after_discount_ttc}
                  </p>
                )}
              </div>
              {viewingProduct?.product_inci_composition && (
                <div>
                  <h4 className="font-medium mb-1">INCI Composition</h4>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {viewingProduct.product_inci_composition}
                  </p>
                </div>
              )}
              <div className="pt-4">
                <a
                  href={viewingProduct?.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:underline"
                >
                  View on Website
                </a>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewingProduct(null)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

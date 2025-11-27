"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Code, Database, FileJson, Users } from "lucide-react";
import type {
  CssSelector,
  Product,
  ExtractionMode,
} from "@/features/product-extractor/types";
import type { UserRole } from "@/app/lib/types/index";
import type { FilterMode } from "@/features/url-filter/types";

interface DevConsoleProps {
  activeStep: string;
  cssSelectors: CssSelector[];
  extractionMode: ExtractionMode;
  products: Product[];
  userRole: UserRole;
  filterMode: FilterMode;
}

export function DevConsole({
  activeStep,
  cssSelectors,
  extractionMode,
  products,
  userRole,
  filterMode,
}: DevConsoleProps) {
  const [activeTab, setActiveTab] = useState<string>("selectors");

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-md flex items-center">
          <Code className="h-4 w-4 mr-2" />
          Developer Console
          <span className="ml-2 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-0.5 rounded-full">
            {userRole.charAt(0).toUpperCase() + userRole.slice(1)}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-4 mb-4 mx-4">
            <TabsTrigger value="selectors" className="text-xs">
              CSS Selectors
            </TabsTrigger>
            <TabsTrigger value="data" className="text-xs">
              Data
            </TabsTrigger>
            <TabsTrigger value="logs" className="text-xs">
              Logs
            </TabsTrigger>
            <TabsTrigger value="permissions" className="text-xs">
              Permissions
            </TabsTrigger>
          </TabsList>

          <TabsContent value="selectors" className="px-4 pb-4">
            {extractionMode === "css" ? (
              <div className="space-y-4">
                <div className="text-sm">
                  <p className="text-muted-foreground mb-2">
                    CSS selectors defined for extraction:
                  </p>
                  <div className="bg-muted p-3 rounded-md overflow-x-auto">
                    <pre className="text-xs">
                      {cssSelectors.length > 0
                        ? JSON.stringify(cssSelectors, null, 2)
                        : "No CSS selectors defined yet."}
                    </pre>
                  </div>
                </div>
                <div className="text-sm">
                  <p className="text-muted-foreground mb-2">
                    Example selector usage:
                  </p>
                  <div className="bg-muted p-3 rounded-md overflow-x-auto">
                    <code className="text-xs block">
                      {`// Example JavaScript to use these selectors
document.querySelector('${
                        cssSelectors[0]?.selector || ".product-title"
                      }').textContent
// Returns: "${cssSelectors[0]?.example || "Product Title"}"

document.querySelector('${
                        cssSelectors[1]?.selector || ".product-price"
                      }').textContent
// Returns: "${cssSelectors[1]?.example || "$99.99"}"
`}
                    </code>
                  </div>
                </div>
                <div className="text-sm">
                  <p className="text-muted-foreground mb-2">
                    Common CSS selectors:
                  </p>
                  <div className="bg-muted p-3 rounded-md overflow-x-auto">
                    <code className="text-xs block">
                      {`.product-name, .product-title, h1.title   // Product name
.price, .product-price, span.price    // Product price
.product-image, img.main              // Product image
.description, .product-description    // Product description`}
                    </code>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-muted-foreground text-sm">
                <div className="text-center">
                  <p>CSS Selector mode is not active.</p>
                  <p>
                    Switch to CSS Selector mode in the URL Filter step to define
                    selectors.
                  </p>
                </div>
              </div>
            )}
          </TabsContent>

          <TabsContent value="data" className="px-4 pb-4">
            <div className="space-y-4">
              <div className="flex items-center text-sm">
                <Database className="h-4 w-4 mr-2" />
                <span>Extracted Products: {products.length}</span>
              </div>
              <div className="bg-muted p-3 rounded-md overflow-auto max-h-[400px]">
                <pre className="text-xs">
                  {products.length > 0
                    ? JSON.stringify(products, null, 2)
                    : "No products extracted yet."}
                </pre>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="logs" className="px-4 pb-4">
            <div className="space-y-4">
              <div className="flex items-center text-sm">
                <FileJson className="h-4 w-4 mr-2" />
                <span>Extraction Logs</span>
              </div>
              <div className="bg-black dark:bg-gray-900 text-green-400 dark:text-green-300 p-3 rounded-md overflow-auto max-h-[400px] font-mono">
                <div className="text-xs">
                  {activeStep === "crawl" && (
                    <>
                      <div>[INFO] Waiting for URL input...</div>
                      <div>[INFO] Current user role: {userRole}</div>
                    </>
                  )}
                  {activeStep === "filter" && (
                    <>
                      <div>[INFO] URLs crawled successfully</div>
                      <div>[INFO] Filter mode: {filterMode.toUpperCase()}</div>
                      <div>
                        [INFO] Extraction mode: {extractionMode.toUpperCase()}
                      </div>
                      <div>[INFO] Current user role: {userRole}</div>
                      {filterMode === "regex" && (
                        <div>[DEBUG] Using regex pattern: product|item</div>
                      )}
                      {filterMode === "llm" && (
                        <div>[DEBUG] Using LLM to identify product URLs</div>
                      )}
                    </>
                  )}
                  {activeStep === "extract" && (
                    <>
                      <div>
                        [INFO] Starting extraction with mode:{" "}
                        {extractionMode.toUpperCase()}
                      </div>
                      <div>[INFO] Current user role: {userRole}</div>
                      <div>
                        [INFO] Previous filter mode: {filterMode.toUpperCase()}
                      </div>
                      {extractionMode === "css" && (
                        <>
                          <div>
                            [INFO] Using {cssSelectors.length} CSS selectors for
                            extraction
                          </div>
                          <div>
                            [DEBUG] Selectors:{" "}
                            {JSON.stringify(
                              cssSelectors.map((s) => s.selector)
                            )}
                          </div>
                        </>
                      )}
                      {products.length > 0 && (
                        <>
                          <div>
                            [INFO] Extracted {products.length} products
                            successfully
                          </div>
                          <div>
                            [DEBUG] Sample product:{" "}
                            {JSON.stringify(products[0]?.product_name)}
                          </div>
                        </>
                      )}
                    </>
                  )}
                  {activeStep === "results" && (
                    <>
                      <div>[INFO] Extraction completed</div>
                      <div>[INFO] Total products: {products.length}</div>
                      <div>
                        [INFO] Extraction mode used:{" "}
                        {extractionMode.toUpperCase()}
                      </div>
                      <div>
                        [INFO] Filter mode used: {filterMode.toUpperCase()}
                      </div>
                      <div>[INFO] Current user role: {userRole}</div>
                      <div>
                        [DEBUG] Products with multiple images:{" "}
                        {
                          products.filter(
                            (p) => p.product_image_url && p.product_image_url.length > 1
                          ).length
                        }
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="permissions" className="px-4 pb-4">
            <div className="space-y-4">
              <div className="flex items-center text-sm">
                <Users className="h-4 w-4 mr-2" />
                <span>Role Permissions</span>
              </div>
              <div className="bg-muted p-3 rounded-md overflow-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Feature</th>
                      <th className="text-center py-2">Viewer</th>
                      <th className="text-center py-2">Editor</th>
                      <th className="text-center py-2">Developer</th>
                      <th className="text-center py-2">Admin</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="py-2">View Results</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2">Edit Products</td>
                      <td className="text-center">✗</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2">Export Data</td>
                      <td className="text-center">✗</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2">Advanced Filters</td>
                      <td className="text-center">✗</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2">Developer Console</td>
                      <td className="text-center">✗</td>
                      <td className="text-center">✗</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                    </tr>
                    <tr className="border-b">
                      <td className="py-2">Custom Scripts</td>
                      <td className="text-center">✗</td>
                      <td className="text-center">✗</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                    </tr>
                    <tr>
                      <td className="py-2">Crawl Configuration</td>
                      <td className="text-center">✗</td>
                      <td className="text-center">✗</td>
                      <td className="text-center">✓</td>
                      <td className="text-center">✓</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

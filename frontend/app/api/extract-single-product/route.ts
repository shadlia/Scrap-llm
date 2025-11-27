import { NextRequest, NextResponse } from "next/server";
import { ServerApi } from "@/app/lib/server/api";

export async function POST(request: NextRequest) {
  try {
    const { client_id, process_id, product_url, domain, method, models } =
      await request.json();

    const data = await ServerApi.extract_single_product(
      client_id,
      process_id,
      product_url,
      domain,
      method,
      models
    );
    return NextResponse.json(data);
  } catch (error) {
    console.error(error);
    return NextResponse.json(
      {
        message: "Internal server error",
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

import { NextRequest, NextResponse } from "next/server";
import { ServerApi } from "@/app/lib/server/api";

export async function POST(request: NextRequest) {
  try {
    const { product_urls, domain, models, client_id } = await request.json();

    const data = await ServerApi.extract(
      product_urls,
      domain,
      models,
      client_id
    );
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      {
        message: "Internal server error",
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

import { NextRequest, NextResponse } from "next/server";
import { ServerApi } from "@/app/lib/server/api";

export async function POST(request: NextRequest) {
  try {
    const { url, skip_sitemap, skip_trim, use_agent, use_hakrawler } =
      await request.json();

    const data = await ServerApi.crawl(
      url,
      skip_sitemap,
      skip_trim,
      use_agent,
      use_hakrawler
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

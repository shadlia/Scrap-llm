import { NextRequest, NextResponse } from "next/server";
import { ServerApi } from "@/app/lib/server/api";

export async function POST(request: NextRequest) {
  try {
    const { process_id, number_of_urls } = await request.json();

    const data = await ServerApi.fetch_extractions(process_id, number_of_urls);
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

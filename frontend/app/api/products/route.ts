import { NextResponse } from 'next/server';
import { ServerApi } from '@/app/lib/server/api';

export async function GET() {
  try {
    const data = await ServerApi.getProducts();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { message: 'Internal server error', error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

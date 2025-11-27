import { NextResponse } from "next/server";
import * as jose from "jose";

const JWT_SECRET = process.env.JWT_SECRET ?? "";

export async function POST(request: Request) {
  try {
    const { clientId } = await request.json();

    if (!clientId) {
      return NextResponse.json(
        { error: "clientId is required" },
        { status: 400 }
      );
    }

    const secret = new TextEncoder().encode(JWT_SECRET);

    const payload = {
      "x-fastly-read": [`${clientId}`],
    };

    const token = await new jose.SignJWT(payload)
      .setProtectedHeader({
        alg: "HS256",
        kid: process.env.JWT_KEY_ID,
      })
      .setExpirationTime("1h")
      .sign(secret);

    return NextResponse.json({ token });
  } catch (error) {
    console.error("Error generating token:", error);
    return NextResponse.json(
      { error: "Error generating token" },
      { status: 500 }
    );
  }
}

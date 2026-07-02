import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Define public routes that don't require authentication
const publicRoutes = ['/login', '/register'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Note: We are using Zustand localStorage for auth state. 
  // For true Edge middleware auth, the token needs to be synced to cookies.
  // Assuming a 'token' cookie is set upon login for edge checks:
  const token = request.cookies.get('token')?.value;

  const isPublicRoute = publicRoutes.some((route) => pathname.startsWith(route));

  if (!token && !isPublicRoute && pathname !== '/') {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (token && isPublicRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};

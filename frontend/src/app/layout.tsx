import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "../contexts/AuthContext";

const geistSans = Geist({
	variable: "--font-geist-sans",
	subsets: ["latin"],
});

const geistMono = Geist_Mono({
	variable: "--font-geist-mono",
	subsets: ["latin"],
});

export const metadata: Metadata = {
	title: "NASA ZEUS",
	description: "An AI-powered air quality forecasting platform using NASA data.",
	metadataBase: new URL('https://nasazeus.org'),
	icons: {
		icon: [
			{ url: '/favicon.ico' },
			{ url: '/logo.png', sizes: '512x512', type: 'image/png' },
		],
		apple: '/logo.png',
		shortcut: '/favicon.ico',
	},
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en">
			<body
				className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
				<AuthProvider>{children}</AuthProvider>
			</body>
		</html>
	);
}

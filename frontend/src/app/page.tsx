"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../contexts/AuthContext";
import dynamic from "next/dynamic";

// Dynamically import the Map component with no SSR
const Map = dynamic(() => import("./components/Map"), {
	ssr: false,
	loading: () => (
		<div
			style={{
				height: "100vh",
				width: "100%",
				display: "flex",
				alignItems: "center",
				justifyContent: "center",
				backgroundColor: "#f0f0f0",
			}}>
			<p>Loading map...</p>
		</div>
	),
});

export default function Home() {
	const { isAuthenticated, loading } = useAuth();
	const router = useRouter();

	useEffect(() => {
		if (!loading) {
			if (isAuthenticated) {
				router.push("/dashboard");
			} else {
				router.push("/auth/login");
			}
		}
	}, [isAuthenticated, loading, router]);

	if (loading) {
		return (
			<div
				style={{
					height: "100vh",
					width: "100%",
					display: "flex",
					alignItems: "center",
					justifyContent: "center",
					backgroundColor: "#f0f0f0",
				}}>
				<div className="text-center">
					<div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600 mx-auto"></div>
					<p className="mt-4 text-gray-600">
						Loading Zeus Air Quality System...
					</p>
				</div>
			</div>
		);
	}

	// Show map for non-authenticated users as fallback
	return <Map />;
}

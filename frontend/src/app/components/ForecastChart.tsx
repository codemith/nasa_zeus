"use client";

import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
	Chart as ChartJS,
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
	Title,
	Tooltip,
	Legend,
	Filler,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
	Title,
	Tooltip,
	Legend,
	Filler
);

interface ForecastChartProps {
	lat: number;
	lon: number;
}

interface ForecastItem {
	dt: number;
	main: {
		aqi: number;
	};
	components: {
		co: number;
		no: number;
		no2: number;
		o3: number;
		so2: number;
		pm2_5: number;
		pm10: number;
		nh3: number;
	};
}

export default function ForecastChart({ lat, lon }: ForecastChartProps) {
	const [chartData, setChartData] = useState<any>(null);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const fetchForecast = async () => {
			try {
				const apiBaseUrl =
					process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
				const response = await fetch(
					`${apiBaseUrl}/api/forecast?lat=${lat}&lon=${lon}`
				);

				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`);
				}

				const data = await response.json();

				// Check if there's an error in the response
				if (data.error) {
					throw new Error(data.error);
				}

				// Check if data is an array
				if (!Array.isArray(data) || data.length === 0) {
					throw new Error("No forecast data available");
				}

				// Process the data for the chart
				const labels = data.map((item: ForecastItem) => {
					const date = new Date(item.dt * 1000); // Convert Unix timestamp to milliseconds
					return date.toLocaleTimeString("en-US", {
						hour: "numeric",
						hour12: true,
					});
				});

				const aqiValues = data.map(
					(item: ForecastItem) => item.main.aqi
				);

				// Set up chart data
				setChartData({
					labels,
					datasets: [
						{
							label: "Air Quality Index (AQI)",
							data: aqiValues,
							borderColor: "rgb(59, 130, 246)",
							backgroundColor: "rgba(59, 130, 246, 0.1)",
							tension: 0.4,
							fill: true,
							pointRadius: 4,
							pointHoverRadius: 6,
						},
					],
				});
				setError(null);
			} catch (error) {
				console.error("Error fetching forecast data:", error);
				setError(
					error instanceof Error
						? error.message
						: "Failed to load forecast data"
				);
				setChartData(null);
			}
		};

		if (lat && lon) {
			fetchForecast();
		}
	}, [lat, lon]);

	if (error) {
		return (
			<div
				style={{
					padding: "20px",
					textAlign: "center",
					color: "#EF4444",
					fontSize: "14px",
					backgroundColor: "#FEE2E2",
					borderRadius: "8px",
				}}>
				⚠️ {error}
			</div>
		);
	}

	if (!chartData) {
		return (
			<div
				style={{
					padding: "20px",
					textAlign: "center",
					color: "#6B7280",
					fontSize: "14px",
				}}>
				Loading forecast...
			</div>
		);
	}

	const options = {
		responsive: true,
		maintainAspectRatio: false,
		plugins: {
			legend: {
				position: "top" as const,
				labels: {
					font: {
						size: 12,
						family: "system-ui, -apple-system, sans-serif",
					},
				},
			},
			title: {
				display: true,
				text: "24-Hour AQI Forecast",
				font: {
					size: 16,
					weight: "bold" as const,
					family: "system-ui, -apple-system, sans-serif",
				},
				color: "#1F2937",
			},
			tooltip: {
				callbacks: {
					label: function (context: any) {
						let label = context.dataset.label || "";
						if (label) {
							label += ": ";
						}
						label += context.parsed.y;

						// Add AQI interpretation
						const aqi = context.parsed.y;
						let quality = "";
						if (aqi === 1) quality = " (Good)";
						else if (aqi === 2) quality = " (Fair)";
						else if (aqi === 3) quality = " (Moderate)";
						else if (aqi === 4) quality = " (Poor)";
						else if (aqi === 5) quality = " (Very Poor)";

						return label + quality;
					},
				},
			},
		},
		scales: {
			y: {
				beginAtZero: true,
				max: 5,
				ticks: {
					stepSize: 1,
					callback: function (value: any) {
						const labels = [
							"",
							"Good",
							"Fair",
							"Moderate",
							"Poor",
							"Very Poor",
						];
						return labels[value] || value;
					},
					font: {
						size: 11,
					},
				},
				grid: {
					color: "rgba(0, 0, 0, 0.05)",
				},
			},
			x: {
				ticks: {
					maxRotation: 45,
					minRotation: 45,
					font: {
						size: 10,
					},
				},
				grid: {
					display: false,
				},
			},
		},
	};

	return (
		<div
			style={{
				height: "300px",
				width: "100%",
				padding: "15px",
				backgroundColor: "white",
				borderRadius: "8px",
			}}>
			<Line
				data={chartData}
				options={options}
			/>
		</div>
	);
}
